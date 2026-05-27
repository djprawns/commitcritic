"""
Tests for configuration management.
"""

import pytest
import os
from unittest.mock import patch


class TestConfig:
    """Tests for configuration settings."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-123"})
    def test_api_key_from_env(self):
        """Test loading API key from environment."""
        # Need to reimport to pick up env var
        from src.config import Settings
        settings = Settings()
        assert settings.openai_api_key == "sk-test-key-123"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-123"})
    def test_validate_api_key_valid(self):
        """Test API key validation with valid key."""
        from src.config import Settings
        settings = Settings()
        assert settings.validate_api_key() is True

    @patch.dict(os.environ, {"OPENAI_API_KEY": "your_openai_api_key_here"})
    def test_validate_api_key_placeholder(self):
        """Test API key validation with placeholder value."""
        from src.config import Settings
        settings = Settings()
        assert settings.validate_api_key() is False

    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    def test_validate_api_key_empty(self):
        """Test API key validation with empty value."""
        from src.config import Settings
        settings = Settings()
        assert settings.validate_api_key() is False

    @patch.dict(os.environ, {"OPENAI_MODEL": "gpt-3.5-turbo"})
    def test_model_from_env(self):
        """Test loading model from environment."""
        from src.config import Settings
        settings = Settings()
        assert settings.openai_model == "gpt-3.5-turbo"

    @patch.dict(os.environ, {}, clear=True)
    def test_default_values(self):
        """Test default configuration values."""
        from src.config import Settings
        settings = Settings()
        assert settings.openai_model == "gpt-4o"
        assert settings.default_commit_limit == 50
        assert settings.batch_size == 10

    @patch.dict(os.environ, {"DEFAULT_COMMIT_LIMIT": "100", "BATCH_SIZE": "5"})
    def test_custom_limits(self):
        """Test custom limit values from environment."""
        from src.config import Settings
        settings = Settings()
        assert settings.default_commit_limit == 100
        assert settings.batch_size == 5

