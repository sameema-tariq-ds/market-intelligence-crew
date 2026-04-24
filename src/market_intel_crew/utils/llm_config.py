from crewai import LLM

from src.market_intel_crew.utils.config_loader import AppSettings


def get_crewai_cerebras_llm(app_config: AppSettings) -> LLM:
    """
    Create and return a CrewAI LLM configured for Cerebras.

    Args:
        app_config (AppSettings): validated application configuration

    Returns:
        LLM: CrewAI-compatible LLM instance
    """

    llm_model = f"{app_config.llm.provider}/{app_config.llm.model}"

    return LLM(
        model=llm_model,
        api_key=app_config.secrets.cerebras_api_key,
        temperature=app_config.llm.temperature,
        max_tokens=app_config.llm.max_tokens,
    )
