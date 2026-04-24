"""
config_loader.py
---------------
Configuration loader for application settings.
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, Literal, Callable

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict, ValidationError, conint, confloat

from src.market_intel_crew.utils.utils import load_yaml_config as _load_yaml


# Exceptions (granular error handling)
class ConfigError(Exception):
    """Base configuration error."""


class YAMLConfigError(ConfigError):
    """Raised when YAML parsing fails."""


class EnvironmentConfigError(ConfigError):
    """Raised when environment variables are invalid or missing."""


class ValidationConfigError(ConfigError):
    """Raised when config validation fails."""

# Enums
class AppEnv(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    STAGING = "staging"


class PathsConfig(BaseModel):
    """Filesystem paths configuration."""
    logs: str
    output: str
    crewai_storage: str


class LoggingConfig(BaseModel):
    """Logging configuration."""
    format: Optional[str] = None
    level: str = "INFO"


class SecretsConfig(BaseModel):
    """Holds sensitive API credentials loaded from environment variables."""
    cerebras_api_key: str = Field(..., min_length=1)
    serper_api_key: str = Field(..., min_length=1)


class LLMConfig(BaseModel):
    """LLM runtime configuration."""
    provider: str
    model: str
    max_tokens: conint(gt=0)
    temperature: confloat(ge=0, le=1)


class AgentsConfig(BaseModel):
    """Agent execution configuration."""
    research_max_iter: conint(gt=0)


class AppConfig(BaseModel):
    """Application metadata."""
    app_name: str


class AppSettings(BaseModel):
    """Root application configuration schema."""
    app_env: AppEnv
    paths: PathsConfig
    logging: LoggingConfig
    secrets: SecretsConfig
    llm: LLMConfig
    agents: AgentsConfig
    app: AppConfig

    model_config = {
            "extra": "forbid",   # 🚨 no unknown keys allowed
            "frozen": True       # 🚨 immutable after load
        }
    

def load_config(
        config_path: str = "src/market_intel_crew/config/settings.yaml",
        load_env: bool = True,
        env_loader: Callable = load_dotenv,
        env_provider: Callable = os.getenv,
    ) -> AppSettings:

    """Load and validate application configuration."""

    # ── Load environment ─────────────────────
    if load_env:
        env_loader()

    # ── YAML load ────────────────────────────
    raw_config = _load_yaml(Path(config_path))

    # ── Environment ──────────────────────────
    try:
        app_env = AppEnv(env_provider("APP_ENV", "development"))
    except ValueError as e:
        raise EnvironmentConfigError("Invalid APP_ENV value") from e

    # ── Secrets (NO DEFAULTS → critical fix) ─
    secrets = {
        "cerebras_api_key": env_provider("CEREBRAS_API_KEY"),
        "serper_api_key": env_provider("SERPER_API_KEY"),
    }

    if not all(secrets.values()):
        raise EnvironmentConfigError("Missing required environment secrets")

    raw_config["secrets"] = secrets
    
    # ── Validation ───────────────────────────
    try:
        config = AppSettings(**raw_config)
    except ValidationError as e:
        raise ValidationConfigError("Invalid configuration schema (check YAML + env)") from e

    return config

# ─────────────────────────────────────────────
# Safe accessor (optional)
# ─────────────────────────────────────────────
def get_config(config_path: str) -> AppSettings:
    """Explicit config loader (recommended entrypoint)."""
    return load_config(config_path)