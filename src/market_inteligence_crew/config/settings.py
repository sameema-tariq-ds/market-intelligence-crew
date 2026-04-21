# config/settings.py

import os
from typing import Optional


class SettingsError(Exception):
    """Raised when there is a configuration error."""

    def __init__(self, message: str, var_name: str = None, code: str = "CONFIG_ERROR"):
        self.var_name = var_name
        self.code = code
        super().__init__(message)

    def __str__(self):
        base = super().__str__()
        if self.var_name:
            return f"[{self.code}] ({self.var_name}) {base}"
        return f"[{self.code}] {base}"


def get_env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    """Fetch an environment variable with optional default and required validation."""
    value = os.getenv(name, default)

    if required and (value is None or str(value).strip() == ""):
        raise SettingsError(
            f"Environment variable '{name}' is required but not set.",
            var_name=name,
            code="MISSING_ENV"
        )

    return value


def get_int(name: str, default: Optional[int] = None, required: bool = False) -> int:
    """Fetch and parse an environment variable as an integer."""
    raw = get_env(name, default=None if default is None else str(default), required=required)

    if raw is None:
        return None

    try:
        return int(raw)
    except ValueError:
        raise SettingsError(
            f"Environment variable '{name}' must be an integer. Got: {raw}",
            var_name=name,
            code="INVALID_TYPE"
        )


def get_float(name: str, default: Optional[float] = None, required: bool = False) -> float:
    """Fetch and parse an environment variable as a float."""
    raw = get_env(name, default=None if default is None else str(default), required=required)

    if raw is None:
        return None

    try:
        return float(raw)
    except ValueError:
        raise SettingsError(
            f"Environment variable '{name}' must be a float. Got: {raw}",
            var_name=name,
            code="INVALID_TYPE"
        )


class Settings:
    """Centralized application configuration loaded from environment variables."""
    
    # --- Core API ---
    CEREBRAS_API_KEY: str = get_env("CEREBRAS_API_KEY", required=True)
    CEREBRAS_MODEL: str = get_env("CEREBRAS_MODEL", default="openai/gpt-4o")

    # --- Model tuning ---
    CEREBRAS_TEMPERATURE: float = get_float("CEREBRAS_TEMPERATURE", default=0.7)
    CEREBRAS_MAX_TOKENS: int = get_int("CEREBRAS_MAX_TOKENS", default=1024)

    # --- App metadata ---
    APP_URL: str = get_env("APP_URL", default="http://localhost:8000")
    APP_NAME: str = get_env("APP_NAME", default="MyApp")

    # --- Environment ---
    ENV: str = get_env("ENV", default="development")

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"


# Singleton instance
settings = Settings()