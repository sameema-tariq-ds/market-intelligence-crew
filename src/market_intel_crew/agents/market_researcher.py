"""
Agent 1 — Market Research Agent
================================
ROLE   : Gather raw intelligence about an industry.
GOAL   : Produce a structured MarketResearchOutput (defined in models/).
TOOLS  : fetch_market_data, find_competitors
OUTPUT : Feeds directly into the Competitive Analysis Agent.

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
from src.market_intel_crew.tools.research_tools import MarketDataFetcherTool
from src.market_intel_crew.utils.utils import validate_crew_config, validate_max_iter, CrewComponentType
from src.market_intel_crew.utils.logger import get_logger

logger = get_logger(__name__)


def build_market_researcher(llm, agents_config: Dict, app_config: AppSettings) -> Agent:
    """
    Factory function that builds and returns the Market Research Agent.

    Using a factory function (instead of a bare Agent object) means we can
    inject the LLM easily and write unit tests without hitting real APIs.

    Args:
        llm: A configured ChatOpenAI (or compatible) LLM instance.
        app_config: Agent configuration from agents.yaml

    Returns:
        A CrewAI Agent ready to be added to a Crew.
    """
    logger.info("Creating Market Research Agent")

    try:

        # Validate agents.yaml
        validated_config = validate_crew_config(agents_config, crew_type=CrewComponentType.AGENT)

        agent = Agent(
            **validated_config,                         # Agent Identity
            tools=[MarketDataFetcherTool(serper_api_key=app_config.secrets.serper_api_key)],            # Agent Capabilities: Gets market size, growth rate, segments
            llm=llm,                                    # LLM
            verbose=False,                              # Logs every reasoning step (great for learning!)
            allow_delegation=False,                     # This agent works alone; no sub-agents
            max_iter=validate_max_iter(app_config.agents.research_max_iter),      # Max reasoning loops before giving up
            memory=False,                               # Stateless — keeps things simple for beginners
        )

        logger.info("Market Research Agent created successfully")
        return agent
    
    except ValueError as ve:
        # Safe, expected failures (bad config/input)
        logger.error(f"Configuration validation error: {ve}")
        raise

    except Exception as e:
            logger.exception("Failed to initialize market_researcher agent")
            raise RuntimeError(f"Agent creation failed: {str(e)}") from e

