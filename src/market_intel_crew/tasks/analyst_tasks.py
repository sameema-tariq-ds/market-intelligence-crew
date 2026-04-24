"""
Task definitions for both agents.
 
A CrewAI Task tells an agent:
  - WHAT to do (description)
  - WHAT to produce (expected_output)
  - WHO does it (agent)
 
The framework handles this automatically in Process.SEQUENTIAL mode.
"""
 
from crewai import Task, Agent
from src.market_intel_crew.utils.utils import validate_crew_config, CrewComponentType, render_template
 
from src.market_intel_crew.utils.logger import get_logger
 
logger = get_logger(__name__)
 

def build_market_analyst_task(industry: str, tasks_config: dict, agent: Agent) -> Task:
    """
    Task 2 — Competitive Analysis Task.
 
    Uses the output of Task 1 (research_task) as its context and produces the final strategic intelligence report.
 
    Args:
        industry: The industry being analysed.
        agent: The Competitive Analysis Agent instance.
        tasks_config: Task configuration from tasks.yaml
 
    Returns:
        A configured CrewAI Task.
    """
    logger.info(f"Initializing Market Analyst Task | industry={industry}")

    try:
        # Validate the task.yaml file
        validated_config = validate_crew_config(tasks_config, crew_type=CrewComponentType.TASK)

        context = {"industry": industry}
        
        task = Task(
            description=render_template(validated_config["description"], context),
            expected_output=render_template(validated_config["expected_output"], context),
            output_file=render_template(validated_config["output_file"], context),
            agent=agent,  # MUST be Agent object (not string)
            verbose=False,
        )
 
        logger.info(f"Market Analyst Task for {industry} created successfully")

        return task
    
    except Exception as e:
        logger.error(f"Failed to create Market Analyst Task for {industry} | error={str(e)}", exc_info=True)
        raise RuntimeError(f"Task creation failed: {str(e)}") from e
