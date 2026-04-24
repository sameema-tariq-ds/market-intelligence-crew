from pathlib import Path
from typing import Any, Dict
from enum import Enum

import yaml
from typing import Any, Dict, List, Callable
from dataclasses import dataclass

from crewai import Agent

from src.market_intel_crew.utils.logger import get_logger

logger = get_logger(__name__)


class CrewComponentType(str, Enum):
    AGENT = "agent"
    TASK = "task"


@dataclass
class ValidationErrorDetail:
    """Represents a single validation error."""
    field: str
    message: str


class ConfigValidationError(Exception):
    """Raised when one or more validation checks fail."""

    def __init__(self, errors: List[ValidationErrorDetail]):
        self.errors = errors
        message = "\n".join([f"{e.field}: {e.message}" for e in errors])
        super().__init__(message)


class ConfigFileNotFoundError(Exception):
    """Raised when config file is missing."""


class ConfigStructureError(Exception):
    """Raised when YAML structure is invalid."""


class YAMLConfigError(Exception):
    """Raised when YAML parsing fails."""

# Safe YAML Loader (Prevents file issues)
def load_yaml_config(path: str, loader: Callable = yaml.safe_load) -> Dict[str, Any]:
    """
    Safely load YAML configuration file.

    Raises:
        ConfigFileNotFoundError
        YAMLConfigError
        ConfigStructureError
    """

    file_path = Path(path)

    # ── File existence check ───────────────────
    if not file_path.exists():
        logger.error(f"Config file not found: {path}")
        raise ConfigFileNotFoundError(f"Config file not found: {path}")

    try:
        # ── Load YAML ──────────────────────────
        with file_path.open("r", encoding="utf-8") as f:
            data = loader(f)

    except yaml.YAMLError as e:
        logger.exception("YAML parsing failed")
        raise YAMLConfigError("Invalid YAML format") from e

    except OSError as e:
        logger.exception("File read failed")
        raise ConfigFileNotFoundError("Unable to read config file") from e

    # ── Empty file check ───────────────────────
    if data is None:
        logger.error("YAML file is empty")
        raise ConfigStructureError("YAML file is empty")

    # ── Type validation ────────────────────────
    if not isinstance(data, dict):
        logger.error("Invalid YAML structure (expected dict)")
        raise ConfigStructureError("YAML root must be a dictionary")

    logger.debug(f"YAML config loaded successfully from {path}")

    return data


def validate_crew_config(config: Dict[str, Any], crew_type: CrewComponentType) -> None:
    """
    Validate agent + task configuration structure.

    Raises:
        ConfigValidationError if invalid
    """
    errors: List[ValidationErrorDetail] = []

    print(config)

    if not isinstance(config, dict):
        raise ConfigValidationError([
            ValidationErrorDetail("config", "Must be a dictionary")
        ])

    if crew_type == CrewComponentType.AGENT:
        required_keys = ["role", "goal", "backstory"]

    elif crew_type == CrewComponentType.TASK:
        required_keys = ["description", "expected_output", "agent", "output_file"]

    else:
        raise ConfigValidationError([
            ValidationErrorDetail("crew_type", "Invalid component type")
        ])


    normalized_config = {}

    for key in required_keys:
        if key not in config:
            errors.append(ValidationErrorDetail(key, "Missing required key"))
            continue

        value = config[key]

        if key == "agent":
            if not isinstance(value, (str, Agent)):
                errors.append(
                    ValidationErrorDetail(key, "Must be a string or Agent instance")
                )
            continue

        if not isinstance(value, str):
            errors.append(ValidationErrorDetail(key, "Must be a string"))
            continue

        cleaned = value.strip()

        if not cleaned:
            errors.append(ValidationErrorDetail(key, "Cannot be empty"))
            continue

        normalized_config[key] = cleaned

    if errors:
        logger.error("Agent config validation failed", extra={"errors": [e.__dict__ for e in errors]})
        raise ConfigValidationError(errors)

    logger.debug("Agent config validation passed")

    return normalized_config


def validate_max_iter(value: Any) -> int:
    """
    Validate and enforce safe bounds for max_iter.

    Raises:
        ConfigValidationError if invalid
    """
    errors: List[ValidationErrorDetail] = []

    try:
        val = int(value)
    except Exception:
        raise ConfigValidationError([
            ValidationErrorDetail("max_iter", "Must be an integer")
        ])

    if val < 1:
        errors.append(ValidationErrorDetail("max_iter", "Must be >= 1"))

    if val > 20:
        errors.append(
            ValidationErrorDetail(
                "max_iter",
                "Too large (max allowed is 20 to prevent cost explosion)"
            )
        )

    if errors:
        logger.error("max_iter validation failed", extra={"errors": [e.__dict__ for e in errors]})
        raise ConfigValidationError(errors)

    logger.debug(f"max_iter validation passed (value={val})")
    return val


def render_template(value: str, context: Dict[str, Any]) -> str:
    """Safely render YAML templates with runtime variables."""
    if not isinstance(value, str):
        return value

    try:
        return value.format(**context)
    except KeyError as e:
        raise ValueError(f"Missing template variable: {e}")