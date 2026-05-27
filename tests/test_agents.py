"""
Tests for AI agents (CommitAnalyzerAgent, CommitWriterAgent).
Uses mocking to avoid actual API calls.
"""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from src.agents.analyzer import CommitAnalyzerAgent
from src.agents.writer import CommitWriterAgent
from src.git.commit import Commit
from src.git.diff import StagedChanges


class TestCommitAnalyzerAgent:
    """Tests for CommitAnalyzerAgent."""

    @patch('src.agents.base.OpenAI')
    @patch('src.agents.base.AsyncOpenAI')
    def test_analyze_batch(self, mock_async_openai, mock_openai, sample_commits, mock_openai_response):
        """Test batch analysis of commits."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(mock_openai_response)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create agent and analyze
        agent = CommitAnalyzerAgent()
        agent._client = mock_client

        results = agent.analyze_batch(sample_commits[:2])

        # Verify
        assert len(results) == 2
        assert results[0].score == 9
        assert results[1].score == 2

    @patch('src.agents.base.OpenAI')
    @patch('src.agents.base.AsyncOpenAI')
    def test_analyze_batch_empty(self, mock_async_openai, mock_openai):
        """Test batch analysis with empty list."""
        agent = CommitAnalyzerAgent()
        results = agent.analyze_batch([])
        assert results == []

    @patch('src.agents.base.OpenAI')
    @patch('src.agents.base.AsyncOpenAI')
    def test_parse_response(self, mock_async_openai, mock_openai, sample_commits, mock_openai_response):
        """Test parsing of LLM response."""
        agent = CommitAnalyzerAgent()

        results = agent._parse_response(mock_openai_response, sample_commits[:2])

        assert len(results) == 2
        assert results[0].sha == "abc123d"
        assert results[0].is_good is True
        assert results[1].sha == "def456a"
        assert results[1].is_vague is True

    @patch('src.agents.base.OpenAI')
    @patch('src.agents.base.AsyncOpenAI')
    def test_get_message_for_sha(self, mock_async_openai, mock_openai, sample_commits):
        """Test finding original message by SHA."""
        agent = CommitAnalyzerAgent()

        msg = agent._get_message_for_sha(sample_commits, "abc123d")
        assert "feat(auth)" in msg

        msg = agent._get_message_for_sha(sample_commits, "def456a")
        assert msg == "fix bug"

        msg = agent._get_message_for_sha(sample_commits, "nonexistent")
        assert msg == ""

    @patch('src.agents.base.OpenAI')
    @patch('src.agents.base.AsyncOpenAI')
    def test_create_report(self, mock_async_openai, mock_openai, sample_commits, mock_openai_response):
        """Test creating analysis report."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(mock_openai_response)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = CommitAnalyzerAgent()
        agent._client = mock_client

        report = agent.create_report(
            repository_name="test-repo",
            commits=sample_commits[:2],
            batch_size=10,
            parallel=False,  # Use sequential for simpler testing
        )

        assert report.repository_name == "test-repo"
        assert report.total_commits == 2
        assert len(report.analyses) == 2


class TestCommitWriterAgent:
    """Tests for CommitWriterAgent."""

    @patch('src.agents.base.OpenAI')
    @patch('src.agents.base.AsyncOpenAI')
    def test_analyze_changes(self, mock_async_openai, mock_openai, sample_staged_changes):
        """Test analyzing staged changes."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "change_descriptions": ["Add authentication", "Update tests"],
            "primary_change_type": "feat",
            "suggested_scope": "auth",
            "complexity": "moderate",
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = CommitWriterAgent()
        agent._client = mock_client

        summary = agent.analyze_changes(sample_staged_changes)

        assert summary.files_changed == 2
        assert summary.insertions == 15
        assert summary.deletions == 3
        assert len(summary.change_descriptions) == 2

    @patch('src.agents.base.OpenAI')
    @patch('src.agents.base.AsyncOpenAI')
    def test_suggest_message(self, mock_async_openai, mock_openai, sample_staged_changes, sample_change_summary):
        """Test generating commit message suggestion."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "title": "add user authentication",
            "body": "- Implement login\n- Add JWT tokens",
            "commit_type": "feat",
            "scope": "auth",
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = CommitWriterAgent()
        agent._client = mock_client
        agent._last_analysis = {
            "primary_change_type": "feat",
            "suggested_scope": "auth",
            "complexity": "moderate",
        }

        suggestion = agent.suggest_message(sample_staged_changes, sample_change_summary)

        assert suggestion.title == "add user authentication"
        assert suggestion.commit_type == "feat"
        assert suggestion.scope == "auth"

    @patch('src.agents.base.OpenAI')
    @patch('src.agents.base.AsyncOpenAI')
    def test_generate_suggestion(self, mock_async_openai, mock_openai, sample_staged_changes):
        """Test combined analyze + suggest flow."""
        # Setup mock for both calls
        mock_client = MagicMock()
        mock_response1 = MagicMock()
        mock_response1.choices = [MagicMock()]
        mock_response1.choices[0].message.content = json.dumps({
            "change_descriptions": ["Add auth"],
            "primary_change_type": "feat",
            "suggested_scope": "auth",
            "complexity": "simple",
        })

        mock_response2 = MagicMock()
        mock_response2.choices = [MagicMock()]
        mock_response2.choices[0].message.content = json.dumps({
            "title": "add authentication",
            "body": None,
            "commit_type": "feat",
            "scope": "auth",
        })

        mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]
        mock_openai.return_value = mock_client

        agent = CommitWriterAgent()
        agent._client = mock_client

        summary, suggestion = agent.generate_suggestion(sample_staged_changes)

        assert len(summary.change_descriptions) == 1
        assert suggestion.commit_type == "feat"

    @patch('src.agents.base.OpenAI')
    @patch('src.agents.base.AsyncOpenAI')
    def test_truncate_large_diff(self, mock_async_openai, mock_openai):
        """Test that large diffs are truncated."""
        large_diff = "+" * 10000  # Very large diff
        staged = StagedChanges(
            diff=large_diff,
            files_changed=["large_file.py"],
            insertions=10000,
            deletions=0,
        )

        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "change_descriptions": ["Large change"],
            "primary_change_type": "feat",
            "suggested_scope": None,
            "complexity": "complex",
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = CommitWriterAgent()
        agent._client = mock_client

        # Should not raise an error
        summary = agent.analyze_changes(staged)
        assert summary is not None

