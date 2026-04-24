"""
Agent 2 — Strategic Competitive Intelligence Analyst Agent
================================
ROLE   : Gather raw intelligence about an competitors of industry.
TOOLS  : find_competitors

How CrewAI agents work (beginner note):
  - `role`  : The persona the LLM adopts.
  - `goal`  : What the agent is trying to achieve.
  - `backstory`: Extra context that shapes the agent's reasoning style.
  - `tools` : Python functions the agent can call autonomously.
  - `verbose`: Set True during development to watch the agent's thinking.
"""


from typing import Dict

from crewai import Agent

from src.market_intel_crew.utils.config_loader import AppSettings
from src.market_intel_crew.tools.analyst_tools import MarketCompetitorsFetcherTool, MarketPriceFetcherTool
from src.market_intel_crew.utils.utils import validate_crew_config, validate_max_iter, CrewComponentType
from src.market_intel_crew.utils.logger import get_logger

logger = get_logger(__name__)


def build_market_analyst(llm, agents_config: Dict, app_config: AppSettings) -> Agent:
    """
    Factory function that builds and returns the Strategic Competitive Intelligence Analyst.

    Args:
        llm: A configured Cerebras/llama3.1-8b LLM instance.
        agents_config: Agent configuration from agents.yaml
        app_config: provides max retries agent can do for calling a tool

    Returns:
        A CrewAI Agent ready to be added to a Crew.
    """
    logger.info("Creating Competitive Analysis Agent")

    try:

        # Validate agents.yaml
        validated_config = validate_crew_config(agents_config, crew_type=CrewComponentType.AGENT)

        list_tools = [
            MarketCompetitorsFetcherTool(serper_api_key=app_config.secrets.serper_api_key),
            MarketPriceFetcherTool(serper_api_key=app_config.secrets.serper_api_key)
            ]

        agent = Agent(
            **validated_config,          # Agent Identity
            tools=list_tools,            # Agent Capabilities: Gets market size, growth rate, segments
            llm=llm,                     # LLM
            verbose=False,               # Logs every reasoning step (great for learning!)
            allow_delegation=False,      # This agent works alone; no sub-agents
            max_iter=validate_max_iter(app_config.agents.research_max_iter),      # Max reasoning loops before giving up
            memory=False,                # Stateless — keeps things simple for beginners
        )

        logger.info("Competitive Analysis Agent created successfully")
        return agent
    
    except ValueError as ve:
        # Safe, expected failures (bad config/input)
        logger.error(f"Configuration validation error: {ve}")
        raise

    except Exception as e:
            logger.exception("Failed to initialize Competitive Analysis agent")
            raise RuntimeError(f"Agent creation failed: {str(e)}") from e

