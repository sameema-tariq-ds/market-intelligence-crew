#!/usr/bin/env python
"""Entry point for running the Market Intelligence Crew system."""

from __future__ import annotations

import os
import sys
import warnings
import argparse
from typing import Any, Dict
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from market_intel_crew.crew import MarketInteligenceCrew
from src.market_intel_crew.utils.config_loader import load_config, AppSettings
from src.market_intel_crew.utils.llm_config import get_crewai_cerebras_llm
from src.market_intel_crew.utils.logger import get_logger


logger = get_logger(__name__)


class ArgsInputConfig(BaseModel):
    """Validates runtime inputs injected into the Crew."""
    industry: str = Field(..., min_length=2, max_length=100)

    @field_validator("industry")
    @classmethod
    def validate_industry(cls, v: str) -> str:
        v = v.strip()

        if not v:
            logger.error("Industry cannot be empty")
            raise ValueError("Industry cannot be empty")

        if not v.replace(" ", "").isalnum():
            logger.error("Industry must be alphanumeric (spaces allowed)")
            raise ValueError("Industry must be alphanumeric (spaces allowed)")

        return v
    

# Environment Hardening
def _sanitize_environment() -> None:
    """Remove proxy variables that may break API calls."""
    proxy_keys = (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    )

    for key in proxy_keys:
        os.environ.pop(key, None)


def _configure_stdio() -> None:
    """Ensure UTF-8 output in constrained environments."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        logger.debug("STDIO reconfiguration not supported in this environment")


def _configure_warnings() -> None:
    """Suppress known third-party warnings safely."""
    warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


# Crew Execution Context
def _prepare_storage(app_config: AppSettings) -> None:
    """
    Configure CrewAI local storage path safely.
    Avoids writing to system directories in restricted environments.
    """
    import crewai.memory.storage.kickoff_task_outputs_storage as kickoff_storage

    storage_dir = Path.cwd() / app_config.paths.crewai_storage
    storage_dir.mkdir(parents=True, exist_ok=True)

    kickoff_storage.db_storage_path = lambda: str(storage_dir)


# Core Runner
def run(app_config: AppSettings, inputs: Dict[str, Any]) -> None:
    """
    Execute the CrewAI pipeline.

    Args:
        config: validated application configuration
        inputs: runtime inputs for the crew
    """

    logger.info("Starting Market Intelligence Crew execution")

    _configure_stdio()
    _sanitize_environment()
    _configure_warnings()
    _prepare_storage(app_config)

    try:
        # ── LLM setup ─────────────────────────
        llm = get_crewai_cerebras_llm(app_config=app_config)

        # ── Crew instantiation (NO CLASS MUTATION) ──
        crew = MarketInteligenceCrew(
            llm=llm,
            industry=inputs.get("industry"),
            app_config=app_config       
        )
        
        # ── Execute crew ──────────────────────
        result = crew.crew().kickoff(inputs=inputs)

        logger.info("Crew execution completed successfully")
        return result

    except KeyError as e:
        logger.exception(f"Missing required input field: {e}",exc_info=True)
        raise RuntimeError("Missing required input field") from e

    except Exception as e:
        logger.exception(f"Crew execution failed: {e}")
        raise RuntimeError("Crew execution failed") from e
    

def parse_args() -> Dict[str, Any]:
    """Parse CLI arguments for the crew runner."""

    parser = argparse.ArgumentParser(
        description="Run Market Intelligence Crew"
    )

    parser.add_argument(
        "--industry",
        type=str,
        required=True,
        help="Industry to analyze (e.g., uber, fintech, healthcare)",
    )

    args = parser.parse_args()

    return {
        "industry": args.industry,
    }



    
# CLI Entry Point
def main() -> None:
    """Application entrypoint."""
    try:
        # 1. Load config first
        app_config = load_config()

        # 2. Setup logging second (IMPORTANT)
        from src.market_intel_crew.utils.logger import setup_logging

        setup_logging(
            env=app_config.app_env.value,
            log_level=app_config.logging.level,
            log_dir=app_config.paths.logs,
            format_type=getattr(app_config.logging, "format", "pretty"),
        )

        logger = get_logger(__name__)
        logger.info("System initialized")

        # 3. Run app
        raw_inputs = parse_args()

        # Step 4: Validate inputs (critical security boundary)
        validated_inputs = ArgsInputConfig(**raw_inputs)
        
        logger.info("CLI inputs validated successfully", extra={"industry": validated_inputs.industry},)

        # Step 5: Run application logic
        run(app_config=app_config, inputs=validated_inputs.model_dump())

        logger.info("System execution completed successfully")

        sys.exit(0)

    except ValueError as ve:
        # User-level input errors (safe to expose)
        logger = get_logger(__name__)
        logger.error(f"Invalid input: {ve}")
        sys.exit(2)

    except Exception as e:
        # System-level failures (do NOT expose internals)
        logger = get_logger(__name__)
        logger.exception("Fatal system error occurred")
        sys.exit(1)


# Script Execution Guard
if __name__ == "__main__":
    main()