from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, crew, agent, task

from langchain_openai import ChatOpenAI

from src.market_inteligence_crew.agents.market_researcher import build_market_researcher
from src.market_inteligence_crew.tasks.research_tasks import build_market_research_task

@CrewBase
class MarketInteligenceCrew():
    """MarketInteligenceCrew crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    llm: ChatOpenAI  # ✅ Injected here
    industry: str    # ✅ Injected here


    # ── Market Research Agent registration ─────────────────
    @agent
    def market_researcher(self):
        return build_market_researcher(
            llm=self.llm,
            config=self.agents_config['market_researcher']
        )

    # ── Task ───────────────────────────────
    @task
    def market_research_task(self) -> Task:
        return build_market_research_task(
            industry=self.industry,
            researcher_agent=self.market_researcher(),
            config=self.tasks_config['market_research_task']
        )

    # ── Crew ───────────────────────────────   
    @crew
    def crew(self) -> Crew:
        """Creates the MarketInteligenceCrew crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
