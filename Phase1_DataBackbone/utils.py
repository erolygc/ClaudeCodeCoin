"""
Utility functions for Phase 1: Data Backbone
Includes configuration loading, logging setup, and common helpers
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from loguru import logger


class Config:
    """Configuration manager for loading YAML config and environment variables"""

    _instance: Optional["Config"] = None
    _config: Dict[str, Any] = {}
    _secrets: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._config:  # Only load once
            self._load_config()

    def _load_config(self):
        """Load configuration from YAML and environment variables"""
        # Determine environment
        env = os.getenv("ENVIRONMENT", "development")

        # Load environment variables from secrets.env
        project_root = Path(__file__).parent.parent
        secrets_path = project_root / "config" / "secrets.env"
        if secrets_path.exists():
            load_dotenv(secrets_path)
            logger.info(f"Loaded secrets from: {secrets_path}")
        else:
            logger.warning(f"Secrets file not found: {secrets_path}")

        # Load YAML configuration
        config_path = project_root / "config" / f"{env}.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                self._config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from: {config_path}")
        else:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)

        # Override with environment variables where applicable
        self._load_secrets_from_env()

    def _load_secrets_from_env(self):
        """Load sensitive data from environment variables"""
        self._secrets = {
            "database_password": os.getenv("DATABASE_PASSWORD"),
            "database_url": os.getenv("DATABASE_URL"),
            "redis_password": os.getenv("REDIS_PASSWORD"),
            "binance_api_key": os.getenv("BINANCE_API_KEY"),
            "binance_secret_key": os.getenv("BINANCE_SECRET_KEY"),
            "binance_testnet": os.getenv("BINANCE_TESTNET", "true").lower() == "true",
            "bybit_api_key": os.getenv("BYBIT_API_KEY"),
            "bybit_secret_key": os.getenv("BYBIT_SECRET_KEY"),
            "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get('kafka.bootstrap_servers')
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret value from environment variables"""
        return self._secrets.get(key, default)

    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration dictionary"""
        return self._config

    @property
    def secrets(self) -> Dict[str, Any]:
        """Get full secrets dictionary"""
        return self._secrets


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "text",
    rotation: str = "100 MB",
    retention: str = "30 days",
):
    """
    Setup loguru logger with custom configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        log_format: "text" or "json"
        rotation: Log rotation policy
        retention: Log retention policy
    """
    # Remove default logger
    logger.remove()

    # Determine format
    if log_format == "json":
        fmt = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
        serialize = True
    else:
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        serialize = False

    # Add console handler
    logger.add(
        sys.stderr,
        format=fmt,
        level=log_level,
        colorize=True,
        serialize=False,  # Console always uses text format
    )

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=fmt,
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            serialize=serialize,
        )

    logger.info(f"Logger initialized with level: {log_level}, format: {log_format}")


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(__file__).parent.parent


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, create if not"""
    path.mkdir(parents=True, exist_ok=True)
    return path
