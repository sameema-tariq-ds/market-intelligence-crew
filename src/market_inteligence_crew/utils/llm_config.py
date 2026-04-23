from crewai import LLM

from src.market_inteligence_crew.utils.config_loader import cfg


def get_crewai_cerebras_llm() -> LLM:
    """
    Return a CrewAI `LLM` configured for Cerebras.

    CrewAI agents expect a `crewai.LLM` (or a model string), not a LangChain chat model.
    """

    return LLM(
        model=cfg.llm.provider + "/" + cfg.llm.model,
        api_key=cfg.secrets.cerebras_api_key,
        temperature=cfg.llm.temperature,
        max_tokens=cfg.llm.max_tokens,
    )
