from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from tools.rag_tool import JobSearchTool

load_dotenv()

@CrewBase
class Day5:
    """Day5 crew for career information"""
    
    ollama_llm = LLM(model="ollama/llama3.1",base_url="http://localhost:11434")
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def career_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['career_advisor'],
            tools=[JobSearchTool()],
            llm=self.ollama_llm,
            verbose=True
        )

    @task
    def career_info_task(self) -> Task:
        return Task(
            config=self.tasks_config['career_info_task'],
            output_file='career_info.md'  # Will contain either roadmap or specific info
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Day5 crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
