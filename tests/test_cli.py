"""
Tests for CLI commands.
"""

import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from src.cli.commands import app


runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_help(self):
        """Test help command."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "AI-powered commit message analyzer" in result.output

    def test_version(self):
        """Test version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_analyze_help(self):
        """Test analyze command help."""
        result = runner.invoke(app, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "--url" in result.output
        assert "--limit" in result.output

    def test_write_help(self):
        """Test write command help."""
        result = runner.invoke(app, ["write", "--help"])
        assert result.exit_code == 0
        assert "Interactive commit message writer" in result.output

    @patch('src.cli.commands.settings')
    def test_analyze_no_api_key(self, mock_settings):
        """Test analyze command fails without API key."""
        mock_settings.validate_api_key.return_value = False

        result = runner.invoke(app, ["analyze"])

        assert result.exit_code == 1
        assert "API key not configured" in result.output

    @patch('src.cli.commands.settings')
    def test_write_no_api_key(self, mock_settings):
        """Test write command fails without API key."""
        mock_settings.validate_api_key.return_value = False

        result = runner.invoke(app, ["write"])

        assert result.exit_code == 1
        assert "API key not configured" in result.output

    @patch('src.cli.commands.settings')
    @patch('src.cli.commands.get_staged_diff')
    def test_write_no_staged_changes(self, mock_get_staged_diff, mock_settings):
        """Test write command with no staged changes."""
        from src.git.diff import StagedChanges

        mock_settings.validate_api_key.return_value = True
        mock_get_staged_diff.return_value = StagedChanges(
            diff="",
            files_changed=[],
            insertions=0,
            deletions=0,
        )

        result = runner.invoke(app, ["write"])

        # When no staged changes, should show message and exit cleanly
        assert "No staged changes" in result.output or result.exit_code == 0


class TestCLIFormatter:
    """Tests for CLI formatter functions."""

    def test_format_no_staged_changes(self):
        """Test formatting of no staged changes message."""
        from src.cli.formatter import format_no_staged_changes
        # Should not raise
        format_no_staged_changes()

    def test_format_commit_suggestion(self, sample_suggestion):
        """Test formatting of commit suggestion."""
        from src.cli.formatter import format_commit_suggestion
        # Should not raise
        format_commit_suggestion(sample_suggestion)

    def test_format_staged_summary(self, sample_change_summary):
        """Test formatting of staged summary."""
        from src.cli.formatter import format_staged_summary
        # Should not raise
        format_staged_summary(sample_change_summary)

