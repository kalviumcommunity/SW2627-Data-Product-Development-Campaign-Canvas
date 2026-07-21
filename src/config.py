"""
Configuration management for Campaign Canvas application.

This module provides centralized configuration management with support for
multiple environments (development, staging, production) and secure secret
management through environment variables.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


class AppConfig:
    """Base application configuration."""

    # Application metadata
    APP_NAME: str = "CampaignCanvas"
    APP_VERSION: str = "1.0.0"
    
    # Paths
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    
    # Database
    DB_PATH: Path = PROCESSED_DATA_DIR / "marketing.db"
    DB_ECHO: bool = False  # Log SQL statements
    DB_TIMEOUT: int = 30  # Connection timeout in seconds
    DB_CHECK_SAME_THREAD: bool = False  # Allow multiple threads
    
    # Authentication
    CLERK_CLIENT_ID: Optional[str] = os.getenv("CLERK_CLIENT_ID")
    CLERK_CLIENT_SECRET: Optional[str] = os.getenv("CLERK_CLIENT_SECRET")
    CLERK_DOMAIN: Optional[str] = os.getenv("CLERK_DOMAIN")
    CLERK_REDIRECT_URI: Optional[str] = os.getenv("CLERK_REDIRECT_URI", "http://localhost:8501/")
    SESSION_TIMEOUT: int = 3600  # 1 hour in seconds
    
    # Feature flags
    ENABLE_MOCK_DATA_GENERATION: bool = os.getenv("ENABLE_MOCK_DATA_GENERATION", "True").lower() == "true"
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "True").lower() == "true"
    ENABLE_DETAILED_LOGGING: bool = os.getenv("ENABLE_DETAILED_LOGGING", "False").lower() == "true"
    
    # Performance
    CACHE_TTL: int = 300  # 5 minutes in seconds
    MAX_ROWS_PER_QUERY: int = 100000
    QUERY_TIMEOUT: int = 60  # seconds
    
    # Validation
    MIN_REQUIRED_ACTIVATIONS: int = 10
    MIN_ACTIVATION_RATE: float = 0.10  # 10%
    MAX_EMAIL_LENGTH: int = 255
    
    # UI/UX
    DEFAULT_THEME: str = os.getenv("DEFAULT_THEME", "dark")
    PAGE_SIZE: int = 50
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_environment(cls) -> str:
        """Get current environment (development, staging, production)."""
        return os.getenv("ENVIRONMENT", "development").lower()
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.get_environment() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.get_environment() == "development"


class DevelopmentConfig(AppConfig):
    """Development environment configuration."""

    DB_ECHO = True
    ENABLE_DETAILED_LOGGING = True
    ENABLE_MOCK_DATA_GENERATION = True
    CACHE_TTL = 60  # Shorter cache for development


class ProductionConfig(AppConfig):
    """Production environment configuration."""

    DB_ECHO = False
    ENABLE_DETAILED_LOGGING = False
    CACHE_TTL = 600  # Longer cache for production
    
    @classmethod
    def validate_secrets(cls) -> bool:
        """Validate that all required secrets are configured."""
        required_secrets = [
            "CLERK_CLIENT_ID",
            "CLERK_CLIENT_SECRET",
            "CLERK_DOMAIN",
        ]
        
        missing_secrets = [
            secret for secret in required_secrets
            if not getattr(cls, secret)
        ]
        
        if missing_secrets:
            raise ValueError(f"Missing required secrets: {', '.join(missing_secrets)}")
        
        return True


class StagingConfig(AppConfig):
    """Staging environment configuration."""

    DB_ECHO = False
    ENABLE_DETAILED_LOGGING = True
    CACHE_TTL = 300


def get_config() -> AppConfig:
    """Get configuration object based on current environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "staging": StagingConfig,
        "production": ProductionConfig,
    }
    
    config_class = config_map.get(environment, DevelopmentConfig)
    config = config_class()
    
    # Validate production configuration
    if config.is_production():
        config_class.validate_secrets()
    
    # Ensure directories exist
    config.ensure_directories()
    
    return config


# Global configuration instance
config = get_config()
