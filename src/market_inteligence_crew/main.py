#!/usr/bin/env python
import os
import sys
import warnings

from pathlib import Path

from market_inteligence_crew.crew import MarketInteligenceCrew
from src.market_inteligence_crew.utils.llm_config import get_crewai_cerebras_llm
from src.market_inteligence_crew.utils.config_loader import cfg


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    inputs = {"industry": "uber", "topic": "uber"}

    try:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

        # Some environments inject a dead local proxy (e.g. 127.0.0.1:9) which breaks API calls.
        for key in (
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
        ):
            os.environ.pop(key, None)

        # CrewAI stores latest task outputs in a SQLite DB under an OS data dir by default.
        # In some restricted environments, writing to that location fails.
        # Patch the storage path to a local folder inside this repo.
        import crewai.memory.storage.kickoff_task_outputs_storage as kickoff_storage

        local_storage_dir = Path.cwd() / cfg.paths.crewai_storage
        local_storage_dir.mkdir(parents=True, exist_ok=True)
        kickoff_storage.db_storage_path = lambda: str(local_storage_dir)

        llm = get_crewai_cerebras_llm()

        MarketInteligenceCrew.llm = llm
        MarketInteligenceCrew.industry = inputs["industry"]

        crew_obj = MarketInteligenceCrew()

        crew_obj.crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'industry': 'uber',
    }
    try:
        MarketInteligenceCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MarketInteligenceCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
       'industry': 'uber',
    }

    try:
        MarketInteligenceCrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = MarketInteligenceCrew().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
    

if __name__ == "__main__":
    run()
