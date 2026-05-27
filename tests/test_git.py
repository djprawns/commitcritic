"""
Tests for Git module (Commit, StagedChanges).
"""

import pytest
from datetime import datetime
from src.git.commit import Commit
from src.git.diff import StagedChanges


class TestCommit:
    """Tests for Commit model."""

    def test_commit_creation(self, sample_commit):
        """Test commit object creation."""
        assert sample_commit.sha == "abc123def456789"
        assert sample_commit.short_sha == "abc123d"
        assert sample_commit.author_name == "Test User"

    def test_commit_title(self, sample_commit):
        """Test extracting commit title (first line)."""
        assert sample_commit.title == "feat(auth): add user login endpoint"

    def test_commit_body(self, sample_commit):
        """Test extracting commit body."""
        body = sample_commit.body
        assert body is not None
        assert "Add POST /login route" in body

    def test_commit_body_none(self):
        """Test commit with no body returns None."""
        commit = Commit(
            sha="abc123",
            short_sha="abc123",
            message="single line commit",
            author_name="Test",
            author_email="test@test.com",
            authored_date=datetime.now(),
        )
        assert commit.body is None

    def test_is_one_word_true(self):
        """Test detection of one-word commits."""
        commit = Commit(
            sha="abc123",
            short_sha="abc123",
            message="wip",
            author_name="Test",
            author_email="test@test.com",
            authored_date=datetime.now(),
        )
        assert commit.is_one_word is True

    def test_is_one_word_false(self, sample_commit):
        """Test multi-word commits are not flagged."""
        assert sample_commit.is_one_word is False

    def test_str_representation(self, sample_commit):
        """Test string representation."""
        str_repr = str(sample_commit)
        assert "abc123d" in str_repr
        assert "feat(auth)" in str_repr


class TestStagedChanges:
    """Tests for StagedChanges model."""

    def test_has_changes_true(self, sample_staged_changes):
        """Test detection of staged changes."""
        assert sample_staged_changes.has_changes is True

    def test_has_changes_false(self):
        """Test detection when no changes."""
        staged = StagedChanges(
            diff="",
            files_changed=[],
            insertions=0,
            deletions=0,
        )
        assert staged.has_changes is False

    def test_has_changes_whitespace_only(self):
        """Test detection with whitespace-only diff."""
        staged = StagedChanges(
            diff="   \n\t  ",
            files_changed=[],
            insertions=0,
            deletions=0,
        )
        assert staged.has_changes is False

    def test_summary_format(self, sample_staged_changes):
        """Test summary string format."""
        summary = sample_staged_changes.summary
        assert "2 files changed" in summary
        assert "+15" in summary
        assert "-3" in summary

    def test_files_changed_list(self, sample_staged_changes):
        """Test files changed list."""
        assert len(sample_staged_changes.files_changed) == 2
        assert "src/auth.py" in sample_staged_changes.files_changed

