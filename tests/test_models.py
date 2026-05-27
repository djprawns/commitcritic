"""
Tests for data models (CommitAnalysis, AnalysisReport, CommitSuggestion).
"""

import pytest
from src.models.analysis import CommitAnalysis, AnalysisReport
from src.models.suggestion import CommitSuggestion, ChangeSummary


class TestCommitAnalysis:
    """Tests for CommitAnalysis model."""

    def test_is_good_high_score(self, sample_analysis):
        """Test that high scores are considered good."""
        assert sample_analysis.is_good is True

    def test_is_good_low_score(self, sample_bad_analysis):
        """Test that low scores are not considered good."""
        assert sample_bad_analysis.is_good is False

    def test_is_vague_low_score(self, sample_bad_analysis):
        """Test that low scores are considered vague."""
        assert sample_bad_analysis.is_vague is True

    def test_is_vague_high_score(self, sample_analysis):
        """Test that high scores are not considered vague."""
        assert sample_analysis.is_vague is False

    def test_is_one_word_true(self):
        """Test detection of one-word commit messages."""
        analysis = CommitAnalysis(
            sha="abc123",
            original_message="wip",
            score=1,
            issues=["One word"],
        )
        assert analysis.is_one_word is True

    def test_is_one_word_false(self, sample_analysis):
        """Test that multi-word messages are not flagged."""
        assert sample_analysis.is_one_word is False


class TestAnalysisReport:
    """Tests for AnalysisReport model."""

    def test_average_score(self, sample_analysis, sample_bad_analysis):
        """Test average score calculation."""
        report = AnalysisReport(
            repository_name="test-repo",
            total_commits=2,
            analyses=[sample_analysis, sample_bad_analysis],
        )
        # (9 + 2) / 2 = 5.5
        assert report.average_score == 5.5

    def test_average_score_empty(self):
        """Test average score with no analyses."""
        report = AnalysisReport(
            repository_name="test-repo",
            total_commits=0,
            analyses=[],
        )
        assert report.average_score == 0.0

    def test_good_commits(self, sample_analysis, sample_bad_analysis):
        """Test filtering good commits."""
        report = AnalysisReport(
            repository_name="test-repo",
            total_commits=2,
            analyses=[sample_analysis, sample_bad_analysis],
        )
        assert len(report.good_commits) == 1
        assert report.good_commits[0].sha == "abc123d"

    def test_bad_commits(self, sample_analysis, sample_bad_analysis):
        """Test filtering bad commits."""
        report = AnalysisReport(
            repository_name="test-repo",
            total_commits=2,
            analyses=[sample_analysis, sample_bad_analysis],
        )
        assert len(report.bad_commits) == 1
        assert report.bad_commits[0].sha == "def456a"

    def test_vague_count(self, sample_analysis, sample_bad_analysis):
        """Test counting vague commits."""
        report = AnalysisReport(
            repository_name="test-repo",
            total_commits=2,
            analyses=[sample_analysis, sample_bad_analysis],
        )
        assert report.vague_count == 1

    def test_vague_percentage(self, sample_analysis, sample_bad_analysis):
        """Test vague percentage calculation."""
        report = AnalysisReport(
            repository_name="test-repo",
            total_commits=2,
            analyses=[sample_analysis, sample_bad_analysis],
        )
        assert report.vague_percentage == 50.0


class TestCommitSuggestion:
    """Tests for CommitSuggestion model."""

    def test_full_message_with_body(self, sample_suggestion):
        """Test full message includes title and body."""
        full_msg = sample_suggestion.full_message
        assert "add user authentication" in full_msg
        assert "Implement login endpoint" in full_msg

    def test_full_message_without_body(self):
        """Test full message with no body."""
        suggestion = CommitSuggestion(
            title="fix typo",
            body=None,
            commit_type="fix",
            scope=None,
        )
        assert suggestion.full_message == "fix typo"

    def test_conventional_title_with_scope(self, sample_suggestion):
        """Test conventional title format with scope."""
        assert sample_suggestion.conventional_title == "feat(auth): add user authentication"

    def test_conventional_title_without_scope(self):
        """Test conventional title format without scope."""
        suggestion = CommitSuggestion(
            title="fix typo",
            body=None,
            commit_type="fix",
            scope=None,
        )
        assert suggestion.conventional_title == "fix: fix typo"


class TestChangeSummary:
    """Tests for ChangeSummary model."""

    def test_summary_format(self, sample_change_summary):
        """Test change summary has correct values."""
        assert sample_change_summary.files_changed == 2
        assert sample_change_summary.insertions == 15
        assert sample_change_summary.deletions == 3
        assert len(sample_change_summary.change_descriptions) == 2

