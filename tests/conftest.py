"""
Pytest configuration and shared fixtures for CommitCritic tests.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

from src.git.commit import Commit
from src.git.diff import StagedChanges
from src.models.analysis import CommitAnalysis, AnalysisReport
from src.models.suggestion import CommitSuggestion, ChangeSummary


# ============================================================================
# Git Fixtures
# ============================================================================

@pytest.fixture
def sample_commit():
    """Create a sample commit for testing."""
    return Commit(
        sha="abc123def456789",
        short_sha="abc123d",
        message="feat(auth): add user login endpoint\n\n- Add POST /login route\n- Implement JWT token generation",
        author_name="Test User",
        author_email="test@example.com",
        authored_date=datetime(2024, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def sample_commits():
    """Create a list of sample commits for testing."""
    return [
        Commit(
            sha="abc123def456789",
            short_sha="abc123d",
            message="feat(auth): add user login endpoint",
            author_name="Test User",
            author_email="test@example.com",
            authored_date=datetime(2024, 1, 15, 10, 30, 0),
        ),
        Commit(
            sha="def456abc789012",
            short_sha="def456a",
            message="fix bug",
            author_name="Test User",
            author_email="test@example.com",
            authored_date=datetime(2024, 1, 14, 9, 0, 0),
        ),
        Commit(
            sha="ghi789def012345",
            short_sha="ghi789d",
            message="wip",
            author_name="Test User",
            author_email="test@example.com",
            authored_date=datetime(2024, 1, 13, 8, 0, 0),
        ),
    ]


@pytest.fixture
def sample_staged_changes():
    """Create sample staged changes for testing."""
    return StagedChanges(
        diff="""diff --git a/src/auth.py b/src/auth.py
index 1234567..abcdefg 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,6 +10,15 @@ def login(username, password):
+    # Validate credentials
+    if not username or not password:
+        raise ValueError("Username and password required")
+    return generate_token(username)
""",
        files_changed=["src/auth.py", "tests/test_auth.py"],
        insertions=15,
        deletions=3,
    )


# ============================================================================
# Model Fixtures
# ============================================================================

@pytest.fixture
def sample_analysis():
    """Create a sample commit analysis for testing."""
    return CommitAnalysis(
        sha="abc123d",
        original_message="feat(auth): add user login endpoint",
        score=9,
        issues=[],
        suggestions=None,
        praise="Clear, specific, follows conventional commits",
    )


@pytest.fixture
def sample_bad_analysis():
    """Create a sample bad commit analysis for testing."""
    return CommitAnalysis(
        sha="def456a",
        original_message="fix bug",
        score=2,
        issues=["Too vague", "Which bug?"],
        suggestions="fix(auth): resolve token expiration issue",
        praise=None,
    )


@pytest.fixture
def sample_suggestion():
    """Create a sample commit suggestion for testing."""
    return CommitSuggestion(
        title="add user authentication",
        body="- Implement login endpoint\n- Add JWT token generation",
        commit_type="feat",
        scope="auth",
    )


@pytest.fixture
def sample_change_summary():
    """Create a sample change summary for testing."""
    return ChangeSummary(
        files_changed=2,
        insertions=15,
        deletions=3,
        change_descriptions=[
            "Add user authentication",
            "Implement JWT tokens",
        ],
    )


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for analysis."""
    return {
        "analyses": [
            {
                "sha": "abc123d",
                "score": 9,
                "issues": [],
                "suggestion": None,
                "praise": "Clear and specific",
            },
            {
                "sha": "def456a",
                "score": 2,
                "issues": ["Too vague"],
                "suggestion": "fix(auth): resolve login bug",
                "praise": None,
            },
        ]
    }


@pytest.fixture
def mock_openai_writer_response():
    """Mock OpenAI API response for writer."""
    return {
        "title": "add user authentication",
        "body": "- Implement login\n- Add JWT tokens",
        "commit_type": "feat",
        "scope": "auth",
    }


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Create a mock OpenAI client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = str(mock_openai_response).replace("'", '"').replace("None", "null")
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client

