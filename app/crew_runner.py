# crew_runner.py

from src.market_intel_crew.main import run 
from src.market_intel_crew.utils.config_loader import load_config


def run_market_intel_crew(industry: str, output_path: str):
    try:
        app_config = load_config()

        result_file = run(
            app_config=app_config,
            inputs={"industry": industry}
        )

        return result_file

    except Exception as e:
        print("Crew execution failed:", e)
        raise