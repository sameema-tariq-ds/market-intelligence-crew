from __future__ import annotations

import os

from crewai import Crew, Process, Task
from crewai.project import CrewBase, crew, agent, task

from langchain_openai import ChatOpenAI

from src.market_intel_crew.agents.market_researcher import build_market_researcher
from src.market_intel_crew.agents.competitive_analyst import build_market_analyst
from src.market_intel_crew.tasks.research_tasks import build_market_research_task
from src.market_intel_crew.tasks.analyst_tasks import build_market_analyst_task

from src.market_intel_crew.utils.config_loader import AppSettings
from src.market_intel_crew.utils.logger import get_logger


logger = get_logger(__name__)


@CrewBase
class MarketInteligenceCrew():
    """MarketInteligenceCrew crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, llm: ChatOpenAI, industry: str, app_config: AppSettings):
        """
        Args:
            llm: LLM instance
            industry: target industry
            config: validated AppSettings object
        """
        self.llm = llm
        self.industry = industry
        self.app_config = app_config


        logger.info(f"Crew initialized for industry={industry}")


    # ── Market Research Agent registration ─────────────────
    
    @agent
    def market_researcher(self):
        return build_market_researcher(
            llm=self.llm,
            agents_config=self.agents_config['market_researcher'],
            app_config=self.app_config
        )
    
    @agent
    def competitive_analyst(self):
        return build_market_analyst(
            llm=self.llm,
            agents_config=self.agents_config['market_analyst'],
            app_config=self.app_config,
        )
    

    # ── Task ───────────────────────────────
    @task
    def market_research_task(self) -> Task:
        return build_market_research_task(
            industry=self.industry,
            tasks_config=self.tasks_config['market_research_task'],
            agent=self.market_researcher()
        )
    
    @task
    def market_analyst_task(self) -> Task:
        task = build_market_analyst_task(
            industry=self.industry,
            tasks_config=self.tasks_config['market_analyst_task'],
            agent=self.competitive_analyst(),
        )
        task.context = [self.market_research_task()]
        return task
    


    # ── Crew ───────────────────────────────   
    @crew
    def crew(self) -> Crew:
        """Creates the MarketInteligenceCrew crew"""

        try:
            crew_instance = Crew(
                agents=[
                    self.market_researcher(),
                    self.competitive_analyst()
                ],
                tasks=[
                    self.market_research_task(),
                    self.market_analyst_task()
                ],
                process=Process.sequential,
                verbose=os.getenv("CREW_VERBOSE", "false").lower() == "true",
                memory=False  # Enables safer contextual continuity if supported
            )

            logger.info("Crew successfully created")
            return crew_instance

        except Exception as e:
            logger.exception("Crew initialization failed")
            raise RuntimeError(f"Crew creation failed: {str(e)}") from e
