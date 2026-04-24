"""
Task definitions for both agents.
 
A CrewAI Task tells an agent:
  - WHAT to do (description)
  - WHAT to produce (expected_output)
  - WHO does it (agent)
 
Tasks in this file are chained: Task 1's output becomes Task 2's context.
The framework handles this automatically in Process.SEQUENTIAL mode.
"""
 
from crewai import Task, Agent
from src.market_intel_crew.utils.utils import validate_crew_config, CrewComponentType, render_template
 
from src.market_intel_crew.utils.logger import get_logger
 
logger = get_logger(__name__)
 

def build_market_research_task(industry: str, tasks_config: dict, agent: Agent) -> Task:
    """
    Task 1 — Market Research Task.
 
    Instructs the Market Research Agent to gather all raw intelligence
    about the target industry. The output will be passed to Task 2.
 
    Args:
        industry: The industry to research (e.g. "no-code app builders").
        researcher_agent: The Market Research Agent instance.
 
    Returns:
        A configured CrewAI Task.
    """
    logger.info("Initializing Market Research Task | industry=industry")

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
 
        logger.info(f"Market Research Task for {industry} created successfully")

        return task
    
    except Exception as e:
        logger.error(f"Failed to create Market Research Task for {industry} | error={str(e)}", exc_info=True)
        raise RuntimeError(f"Task creation failed: {str(e)}") from e
