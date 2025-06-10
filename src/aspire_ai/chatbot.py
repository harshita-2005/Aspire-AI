import os
import json
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

from langchain_ollama import OllamaEmbeddings# Initialize the embedding model
embedding_model = OllamaEmbeddings(model="bge-m3")
def generate_bge_embeddings(text):
    """Generates embeddings using BGE-M3 for given text."""
    response = embedding_model.embed_query(text)  # ✅ Correct method for embeddings
    return response  # Returns embedding vector
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "rag"
# Storing Job Data in Pinecone (Metadata + Embeddings)
pinecone_index = pc.Index(index_name)
vector_store = PineconeVectorStore(index=pinecone_index, embedding=embedding_model)

# ✅ Create a retriever from the vector store
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})

llm = ChatOllama(
    model="llama3.1",  # ✅ Correct
    temperature=0.4,
    max_tokens=500
)

class AgentState(TypedDict):
    messages: Annotated[Sequence[str], operator.add]
    memory: any
    user_data: any  # Add user data to state


from pydantic import BaseModel , Field
class TopicSelectionParser(BaseModel):
    Topic: str = Field(description='Selected Topic')
    Reasoning: str = Field(description='Reasoning behind topic selection')

from langchain.output_parsers import PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=TopicSelectionParser)

def check_personalization(state: AgentState) -> AgentState:
    question = state["messages"][0]
    template = """
You are a smart assistant that determines if a user's query benefits from personalization.
Decide whether user-specific details (like age, current education, full name, or career background) are necessary to provide a better answer.
your task is to classify the following user query into one of two categories:
1. "personalize"
   - If answering the question **correctly or more usefully** depends on who the user is.
   - Examples:
     - "What certifications should I take to become a cloud engineer?" (Depends on current skills or education)
     - "Am I eligible for UPSC?" (Age, nationality, education matter)
     - "What are the best jobs for a BCom graduate?" (Requires degree context)

2. "general"
   - The question is generic and doesn't depend on user data.
   - Examples:
     - "What is AI?"
     - "What does a data analyst do?"
     - "What is the salary of a software engineer in India?"

Respond only with one valid JSON object using the format schema:
{format_instructions}

User query: {question}
"""
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | llm | parser
    response = chain.invoke({"question": question})
    return {"messages": [response.Topic]}




def search_job_role_1(query, user_summary):
    """Performs Pinecone search and retrieves structured job data based on user query and user profile summary."""
    try:
        # Step 1: Generate embeddings for the user's query
        query_embedding = generate_bge_embeddings(query)

        # Step 2: Query Pinecone index with the embedding
        results = pinecone_index.query(
            vector=query_embedding,
            top_k=1,
            include_metadata=True
        )

        # Convert results to dictionary format
        results_dict = results.to_dict()

        # Step 3: Filter matches based on score threshold > 0.45
        filtered_results = [
            match for match in results_dict.get("matches", [])
            if match.get("score", 0) > 0.45
        ]
        
        # Step 4: Update the results with filtered matches
        results_dict["matches"] = filtered_results
        
        # Step 5: Extract structured job data
        structured_data = extract_job_data(results_dict)

        # Step 6: Construct the final LLM prompt using both the query and the user summary
        llm_prompt = f"""
You are a career assistant that provides direct, accurate answers based on Indian education and job market context.

The user asked:
"{query}"

Here is your profile summary:
"{user_summary}"

You are given some structured job-related data (may or may not be relevant):
{structured_data}

Your task is as follows:

1. **Relevance Check** (INTERNAL ONLY — do not mention this step in your reply):
   - Determine if the structured job data is directly and clearly related to the user's question.
   - If the job data is not relevant (e.g., refers to a different job domain, country, or context), **ignore it completely** and use your expert knowledge to generate an appropriate answer based on the user profile.
   - If the job data **is relevant**, proceed to personalize the answer using the user's profile summary.

2. **Answer Construction** (INTERNAL):
   - If structured data is relevant, **incorporate the user's profile** to create a personalized response. Use the information from the profile to tailor the answer, aligning with the user's skills, background, and career aspirations.
   - If the data is not relevant, construct the answer based on your expert understanding of the Indian education system and job market, and ignore the structured data.

3. **Answer Output**:
   - Provide a direct, concise, and professional answer that aligns with Indian industry norms and academic trends.
   - **Personalize the answer** (if the data is relevant) based on your profile, such as your skills, qualifications, and career goals.
   - **Address the user directly as 'you'** (not in third person).
   - Do not include your reasoning or internal checks — only give the answer clearly.
   - Do not reference the data source, process, or yourself (no "I think" or "based on...").
"""
        
        # Use LLM to process the data and return a refined result
        llm_response = llm.predict(llm_prompt)
        
        return llm_response

    except Exception as e:
        print(f"Error occurred during job search: {e}")
        return []

def summarize_user_data(user_data):
    summarization_prompt = f"""
You are an AI assistant that helps summarize raw user profile data into clean, grammatically correct, human-readable text for career guidance purposes.

Below is a raw dictionary-like user profile. Your task is to:
1. Extract relevant details such as education level and domain, skills, certifications, internships, preferred role, industry, expected salary range, extracurricular activities, and location.
2. Write a well-structured and natural-sounding paragraph summarizing the user's background.
3. Maintain a professional and informative tone.
4. Format the summary in **second person** (e.g., 'You have a background in...').

Raw user data:
------------------
{user_data}
------------------

Output summary (in a single paragraph, using 'you'):
"""
    summary = llm.predict(summarization_prompt)
    return summary


def rag_with_personalization(state: AgentState) -> AgentState:
    if state["messages"][1] == "reform":
        question = state["messages"][2]
    else:
        question = state["messages"][0]

    user_data = state.get("user_data", "No user profile provided.")
    user_summary = summarize_user_data(user_data) # Only pass the summarization prompt here
    print("user_summary",user_summary)      
    # Step 2: Now send the question and summary to search_job_role
    response = search_job_role_1(question, user_summary)  # Pass both question and summary here

    return {
        "messages": [response]
    }



# After personalization_check
def router_personalization(state: AgentState) -> str:
    print("-> checks if the query is personalized or general ->")
    print(state["messages"])
    last_message = state["messages"][-1]
    if last_message == "personalize":
        return "personalize"
    else:
        return "general"


def function_1(state: AgentState) -> AgentState:
    messages = state["messages"]
    if state["messages"][1] == "reform":
        question = messages[2]
    else:
        question = messages[0]
    
    template = """
You are a career guidance assistant. Your task is to classify the following user query into one of two categories:

1. "career"
   - The query is about:
     - Job roles, skills, certifications
     - Career paths, salaries, or education for jobs
     - Professional development
     - Industry-specific job trends
     - Basic understanding of technologies as they relate to jobs or careers
   - INCLUDE vague or ambiguous questions (e.g., "How do I start in this field?", "What is the average salary for it?")
     **IF** they could be interpreted as career-related when context is available.

2. "non_career"
   - The query is clearly unrelated to career guidance. This includes:
     - General knowledge (e.g., history, geography, politics, economy)
     - Entertainment, news, weather
     - Personal questions, chit-chat
     - Anything that cannot reasonably be interpreted as career-related even with context

Only respond with a valid JSON object that follows the format schema:
{format_instructions}

User query: {question}
"""
    
    prompt = PromptTemplate(template=template,
                                    input_variables=["question"],
                                    partial_variables={
                                        "format_instructions" : parser.get_format_instructions()}
                                    )
    chain = prompt | llm | parser
    response = chain.invoke({"question": question})
        
            # ✅ Keep original user question AND append classification
    return {
        "messages": [response.Topic]  # not full list!
    }

# Router decides which function to call
def router(state: AgentState) -> str:
    print("-> checks if the query is career or non-career ->")
    print(state["messages"])

    last_message = state["messages"][-1]
    
    if last_message == "career":
        return "career"
    else:
        return "non_career"
    
import json
import pinecone

def extract_job_data(job_results):
    """Extract structured job data from Pinecone query results."""
    
    # Parse if job_results is still a JSON string
    if isinstance(job_results, str):
        job_results = json.loads(job_results)

    matches = job_results.get("matches", [])
    
    if not matches:
        print("No relavant data found in RAG,switching to LLM Knowledge")
        return []
    
    structured_data = []
    for match in matches:
        metadata = match.get("metadata", {})

        # Parse skills properly (remove the "(score: XX)" parts if needed)
        skills_raw = metadata.get("skills", "")
        skills = []
        if skills_raw:
            skills_list = skills_raw.split(",")
            for skill in skills_list:
                # Only take the skill name before "(score: XX)"
                clean_skill = skill.split("(score:")[0].strip()
                if clean_skill:
                    skills.append(clean_skill)

        # Parse career path properly
        career_path_raw = metadata.get("career_path", "")
        career_stages = []
        if career_path_raw:
            stages = career_path_raw.split("->")
            for stage in stages:
                career_stages.append(stage.strip())

        job_data = {
            "job_id": metadata.get("job_id", "N/A"),
            "title": metadata.get("title", "Unknown Job Title"),
            "level": metadata.get("level", "N/A"),
            "industry": metadata.get("industry", "N/A"),
            "sub_industry": metadata.get("sub_industry", "N/A"),
            "job_description": metadata.get("job_description", "N/A"),
            "education": metadata.get("education", "N/A"),
            "skills": skills,
            "certifications": [cert.strip() for cert in metadata.get("certificates", "").split(",") if cert.strip()],
            "key_competencies": [comp.strip() for comp in metadata.get("key_competencies", "").split(",") if comp.strip()],
            "salary_range": f"₹{metadata.get('salary_min', 'N/A')} - ₹{metadata.get('salary_max', 'N/A')}",
            "career_path": career_stages,
            "training_link": metadata.get("training", "N/A"),
            "scholarship_link": metadata.get("scholarships", "N/A"),
        }
        
        structured_data.append(job_data)
    
    return structured_data

def search_job_role(query):
    """Performs Pinecone search and retrieves structured job data based on user query."""
    try:
        # Step 1: Generate embeddings for the user's query
        query_embedding = generate_bge_embeddings(query)

        # Step 2: Query Pinecone index with the embedding
        results = pinecone_index.query(
            vector=query_embedding,
            top_k=1,
            include_metadata=True
        )

        # Convert results to dictionary format
        results_dict = results.to_dict()

        # Step 3: Filter matches based on score threshold > 0.45
        filtered_results = [
            match for match in results_dict.get("matches", [])
            if match.get("score", 0) > 0.45
        ]
        
        # Step 4: Update the results with filtered matches
        results_dict["matches"] = filtered_results
        
        # Step 5: Extract structured job data
        structured_data = extract_job_data(results_dict)

        # Step 6: Use the LLM model to format or process the structured data
        llm_prompt = f"""
You are a career assistant that provides direct, accurate answers based on Indian education and job market context.

The user asked:
"{query}"

You are given some structured job-related data (may or may not be relevant):
{structured_data}

Your task involves three internal steps, but only the final answer should be shown to the user:

1. **Relevance Check** (INTERNAL ONLY — do not mention this step in your reply):
   - Determine if the structured data is directly and clearly related to the user's question.
   - If it's not relevant (e.g., refers to a different job domain, country, or context), ignore it completely and rely only on your expert knowledge.

2. **Answer Construction** (INTERNAL):
   - If structured data is relevant, use it silently.
   - If not, construct the answer based solely on your expert understanding of the Indian education system and job market.
   - Do not mention whether the answer is based on data or knowledge — just respond authoritatively.

3. **Answer Output**:
   - Provide a direct, concise, and professional answer.
   - Align the answer with Indian industry norms and academic trends.
   - Do not include your reasoning or internal checks — only give the answer clearly.
   - Do not reference the data source, process, or yourself (no "I think" or "based on...").

Only the final answer should be visible to the user.
"""
        
        # Use LLM to process the data and return a refined result
        llm_response = llm.predict(llm_prompt)
        
        return llm_response

    except Exception as e:
        print(f"Error occurred during job search: {e}")
        return []


def rag_general(state: AgentState) -> AgentState:
    if state["messages"][1] == "reform":
        question = state["messages"][2]
    else:
        question = state["messages"][0]
        # ✅ Use your custom logic instead of LangChain's retriever
    print("question sent to RAG",question)
    response = search_job_role(question)

    return {
        "messages": [response]  # only the final formatted job answer
    }

def function_3(state: AgentState) -> AgentState:
    messages = state["messages"]
    question = messages[0]  # original user query

    template = """
You are a helpful assistant. Your task is to classify the user's query into one of these categories:

1. "greetings"
   - If the user is just saying hello, hi, greetings, etc.

2. "out_of_scope"
   - If the query is unrelated to career guidance, such as:
     - General knowledge, trivia
     - Entertainment, movies, politics, weather
     - Personal or random questions not tied to careers

Only respond with a valid JSON object that follows the format schema:
{format_instructions}

User query: {question}
"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    response = chain.invoke({"question": question})

    return {
        "messages": [response.Topic]  # not full list!
    }

# Router for greeting or out_of_scope classification
def router_function_3(state: AgentState) -> str:
    print("-> checks if the query is greeting or out_of_scope ->")
    print(state["messages"])
    last_message = state["messages"][-1]  # Last message from the state
    
    # Check the classification from function_3 (either greeting or out_of_scope)
    if last_message == "greetings":
        return "greetings"  # Call function_4 for greeting
    else:
        return "out_of_scope"  # Call function_5 for out_of_scope
  # Catch-all in case the classification is unknown

def handle_greeting(query: str, memory, user_data, llm):
    if user_data and isinstance(user_data, list) and len(user_data) > 0 and user_data[0].get('full_name'):
        response = f"Hi {user_data[0]['full_name']}! How can I help you today?"
    else:
        response = "Hello! How can I help you today?"

    memory.save_context({"input": query}, {"output": response})
    return response

def function_4(state: AgentState) -> AgentState:
    # Extract the last user message from the state
    messages = state["messages"]
    query = messages[-1]  # The query will be the most recent message
    memory = state["memory"]
    user_data = state.get("user_data", [])
    
    # Use the handle_greeting function to generate the personalized response
    response = handle_greeting(query, memory, user_data, llm)
    
    # Append the personalized response to the message history
    return {
        "messages":[response]  # Add the personalized greeting response
    }

def function_5(state: AgentState) -> AgentState:
    messages = state["messages"]
    out_of_scope_response = "I'm sorry, I can only assist with career-related questions. Please ask something related to career guidance."

    # Respond to the user out-of-scope query
    return {
        "messages":[out_of_scope_response]  # Append the out-of-scope response to the conversation
    }

def reform(state: AgentState) -> AgentState:
    messages = state["messages"]
    question = messages[0]  # original user query

    template = """
You are a helpful assistant. Your task is to classify whether the user's query needs reformulation.

Classify into one of the following two categories:

1. "reform"
   - If the query is vague, incomplete, uses unclear pronouns (like 'it', 'this', 'that'), or lacks context or specific intent.
   Example queries needing reformulation:
    - "what certifications to learn for it?" (What does 'it' refer to?)
    - "what skills to learn for it?" (What does 'it' refer to?)
    - "how to achieve this?" (What is 'this'?)
    - "what is the meaning of this?" (What does 'this' refer to?)

2. "no_reform"
   - If the query is clearly stated, has context, or is a greeting, chit-chat, or does not require changes for better understanding.
   Example queries that do not need reformulation:
    - "What is AI?"
    - "what is the average salary of a data scientist in India?"
    - "what skills are required to become a Cardiologist?"
    - "What certifications should I pursue to become a data scientist?"
    - "How do I get started with Python?"
    - "hi"
    - "hello"
    - "good morning"
    - "hey"

Do not include any explanations or extra text. Respond only with a valid JSON object that follows the format schema:
{format_instructions}

User query: {question}
"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    response = chain.invoke({"question": question})

    return {
        "messages": [response.Topic]
    }


def reformulate_with_memory(state: AgentState) -> AgentState:
    memory = state["memory"]
    return reformulate(state, memory)


def reformulate(state: AgentState, memory) -> AgentState:
    question = state["messages"][0]

    mem = memory.load_memory_variables({})
    history_messages = mem.get("history", [])
    context = "\n".join([f"{msg.type.capitalize()}: {msg.content}" for msg in history_messages]).strip()

    prompt = f"""
You are a helpful assistant that rewrites vague or context-dependent user questions into clear, concise, and self-contained ones.

Guidelines:
- Use the most recent relevant topic from the conversation to resolve ambiguous references like "this", "that", "it", or "this field".
- Stick to the user's language style and intent, but clarify what "it" refers to when necessary.
- Keep the reformulated question short and natural — avoid overly long or formal rewrites.
- If the original question is already clear or no relevant context exists, return it unchanged.
- Output only the reformulated question — no extra commentary.

Examples:

Context: "I'm thinking of studying data science."  
Question: "Is it a good option in 2025?"  
→ Reformulated: "Is data science a good option in 2025?"

Context: "I'm in BTech 3rd year and I am 20."  
Question: "Can I apply for it?"  
→ Reformulated: "Can I apply for the GRE at 20 while in BTech 3rd year?"

Context: "I'm learning cloud computing."  
Question: "What are the best certifications in this field?"  
→ Reformulated: "What are the best certifications in cloud computing?"

---

Now, apply this to the input below.

Conversation context:
{context}

Original question: "{question}"

Reformulated:
"""

    # ✅ Invoke the LLM to generate the reformulated query
    reformulated_query = llm.predict(prompt).strip()

    return {
        "messages": [reformulated_query]
    }


# Router for reformulation classification
def router_reformulation(state: AgentState) -> str:
    print("-> checks if reformulation is needed ->")
    print(state["messages"])
    last_message = state["messages"][-1]  # Last classification message

    if last_message == "reform":
        return "reform"  # Route to the reformulation function
    elif last_message == "no_reform":
        return "no_reform"  # Route directly to RAG
    else:
        return "Unknown"  # Fallback for unexpected cases


workflow5 = StateGraph(AgentState)

# Add nodes
workflow5.add_node("reform_check", reform)  # Classifies whether reformulation is needed
workflow5.add_node("reformulation", reformulate_with_memory)  # Actually reformulates the query
workflow5.add_node("classifier", function_1)  # Classifies as career/non_career
workflow5.add_node("greeting_or_scope", function_3)
workflow5.add_node("Greeting Response", function_4)
workflow5.add_node("Out of Scope Response", function_5)
workflow5.add_node("personalization_check", check_personalization)
workflow5.add_node("rag_personalized", rag_with_personalization)
workflow5.add_node("rag_general", rag_general)

# Set entry point to reform_check
workflow5.set_entry_point("reform_check")

# Add conditional edges for reformulation
workflow5.add_conditional_edges(
    "reform_check",
    router_reformulation,
    {
        "reform": "reformulation",
        "no_reform": "classifier",
    }
)
workflow5.add_edge("reformulation", "classifier")

# Add conditional edges for classification
workflow5.add_conditional_edges(
    "classifier",
    router,
    {
        "career": "personalization_check",
        "non_career": "greeting_or_scope"
    }
)

workflow5.add_conditional_edges(
    "personalization_check",
    router_personalization,
    {
        "personalize": "rag_personalized",
        "general": "rag_general"
    }
)

# Add conditional edges for greeting/out_of_scope
workflow5.add_conditional_edges(
    "greeting_or_scope",
    router_function_3,
    {
        "greetings": "Greeting Response",
        "out_of_scope": "Out of Scope Response",
    }
)

# End edges
workflow5.add_edge("rag_personalized", END)
workflow5.add_edge("rag_general", END)
workflow5.add_edge("Greeting Response", END)
workflow5.add_edge("Out of Scope Response", END)

# Compile the graph into a callable app
app5 = workflow5.compile()

def get_assistant_response(user_message, session_id, ollama_llm, memory, user_data):
    state = {
        "messages": [user_message],
        "memory": memory,
        "user_data": user_data  # Include user_data
    }
    output = app5.invoke(state)
    return output["messages"][-1]
