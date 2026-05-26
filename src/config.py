"""
Configuration management for CommitCritic.
Handles environment variables and default settings.
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_model: str = Field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o")
    )

    # Analysis settings
    default_commit_limit: int = Field(
        default_factory=lambda: int(os.getenv("DEFAULT_COMMIT_LIMIT", "50"))
    )
    batch_size: int = Field(
        default_factory=lambda: int(os.getenv("BATCH_SIZE", "10"))
    )

    def validate_api_key(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key and self.openai_api_key != "your_openai_api_key_here")


# Global settings instance
settings = Settings()

