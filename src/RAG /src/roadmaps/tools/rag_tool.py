from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_ollama import OllamaEmbeddings
from pydantic import field_validator

class JobSearchInput(BaseModel):
    query: str = Field(..., description="The job search query to look up.")

    @field_validator("query", mode="before")
    @classmethod
    def ensure_string(cls, v):
        if isinstance(v, dict):
            return v.get("query") or v.get("description") or str(v)
        return v

class JobSearchTool(BaseTool):
    name: str = "JobSearch"
    description: str = (
        "A tool for searching job details and career information. "
        "Useful for finding career paths, required skills, and job requirements. "
        "Input should be a job search query string."
    )
    args_schema: Type[BaseModel] = JobSearchInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize connection to existing Pinecone index
        load_dotenv()
        PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        
        # Connect to existing index
        self._pc = Pinecone(api_key=PINECONE_API_KEY)
        self._pinecone_index = self._pc.Index("rag")
        self._embedding_model = OllamaEmbeddings(model="bge-m3")

    def _split_and_classify_skills(self, skills):
        """Sort skills by score and split them equally into top and other skills."""
        # Sort skills in descending order by score
        sorted_skills = sorted(skills, key=lambda x: x.get('score', 0), reverse=True)
        
        # Split the sorted list into two halves
        mid_point = len(sorted_skills) // 2
        
        # Top skills will be the first half, other skills will be the second half
        top_skills = sorted_skills[:mid_point]
        other_skills = sorted_skills[mid_point:]

        return top_skills, other_skills

    def _run(self, query: str) -> str:
        """Search for job information based on query."""
        try:
            # Clean the query input - simplified handling
            if isinstance(query, str):
                query = query.replace("Create a career roadmap for ", "").strip()
            else:
                query = str(query)

            # Generate embeddings for the query
            query_embedding = self._embedding_model.embed_query(query)

            # Query existing Pinecone index
            results = self._pinecone_index.query(
                vector=query_embedding,
                top_k=1,  # Get top 1 relevant job role
                include_metadata=True
            )

            # Extract metadata from results
            matches = results.matches
            if not matches:
                return json.dumps({"error": "No relevant job information found."})

            # Get the metadata from the first match
            metadata = matches[0].metadata

            # Parse skills from string if they're in string format
            skills_list = []
            if isinstance(metadata.get("skills"), str):
                # Split the skills string and create skill objects
                skills_parts = metadata["skills"].split(", ")
                for part in skills_parts:
                    if "(score:" in part:
                        skill, score = part.rsplit(" (score:", 1)
                        score = float(score.rstrip(")"))
                        skills_list.append({"skill": skill, "score": score})
            else:
                skills_list = metadata.get("skills", [])

            # Split and classify the skills
            top_skills, other_skills = self._split_and_classify_skills(skills_list)

            # Display only the skills categorization in the terminal
            print("\n=== Skills Categorization ===")
            print("\nTop Skills:")
            for skill in top_skills:
                print(f"• {skill['skill']} (Score: {skill.get('score', 'N/A')})")

            print("\nOther Skills:")
            for skill in other_skills:
                print(f"• {skill['skill']} (Score: {skill.get('score', 'N/A')})")
            print("\n===========================")

            # Structure the job data
            job_data = {
                "job_id": metadata.get("job_id", "N/A"),
                "title": metadata.get("title", "Unknown Job Title"),
                "industry": metadata.get("industry", "N/A"),
                "sub_industry": metadata.get("sub_industry", "N/A"),
                "level": metadata.get("level", "N/A"),
                "education": metadata.get("education", "No education requirements listed"),
                "training": metadata.get("training", "No training information listed"),
                "skills": {
                    "top_skills": top_skills,
                    "other_skills": other_skills
                },
                "certifications": metadata.get("certificates", []),
                "key_competencies": metadata.get("key_competencies", []),
                "salary_range": f"₹{metadata.get('salary_min', 'N/A')} - ₹{metadata.get('salary_max', 'N/A')}",
                "career_path": metadata.get("career_path", []),
                "scholarships": metadata.get("scholarships", "No scholarships listed")
            }

            return json.dumps(job_data, indent=2)

        except Exception as e:
            print(f"Error in _run: {str(e)}")  # Add detailed error logging
            return json.dumps({"error": f"Error performing job search: {str(e)}"})
