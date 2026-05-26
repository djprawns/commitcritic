"""
Analysis models for commit critique.
"""

from pydantic import BaseModel, Field


class CommitAnalysis(BaseModel):
    """Analysis result for a single commit."""

    sha: str = Field(description="Short SHA of the commit")
    original_message: str = Field(description="The original commit message")
    score: int = Field(ge=1, le=10, description="Quality score from 1-10")
    issues: list[str] = Field(
        default_factory=list,
        description="List of issues with the commit message"
    )
    suggestions: str | None = Field(
        default=None,
        description="Suggested improved commit message"
    )
    praise: str | None = Field(
        default=None,
        description="What's good about this commit (for high scores)"
    )

    @property
    def is_good(self) -> bool:
        """Check if this is a well-written commit (score >= 7)."""
        return self.score >= 7

    @property
    def is_one_word(self) -> bool:
        """Check if the commit message is just one word."""
        return len(self.original_message.split()) == 1

    @property
    def is_vague(self) -> bool:
        """Check if the commit is considered vague (score <= 4)."""
        return self.score <= 4


class AnalysisReport(BaseModel):
    """Complete analysis report for a repository."""

    repository_name: str
    total_commits: int
    analyses: list[CommitAnalysis]

    @property
    def average_score(self) -> float:
        """Calculate the average score across all commits."""
        if not self.analyses:
            return 0.0
        return sum(a.score for a in self.analyses) / len(self.analyses)

    @property
    def good_commits(self) -> list[CommitAnalysis]:
        """Get commits with good scores (>= 7)."""
        return [a for a in self.analyses if a.is_good]

    @property
    def bad_commits(self) -> list[CommitAnalysis]:
        """Get commits that need work (< 7)."""
        return [a for a in self.analyses if not a.is_good]

    @property
    def vague_count(self) -> int:
        """Count commits that are vague (score <= 4)."""
        return sum(1 for a in self.analyses if a.is_vague)

    @property
    def one_word_count(self) -> int:
        """Count one-word commit messages."""
        return sum(1 for a in self.analyses if a.is_one_word)

    @property
    def vague_percentage(self) -> float:
        """Get percentage of vague commits."""
        if not self.analyses:
            return 0.0
        return (self.vague_count / len(self.analyses)) * 100

    @property
    def one_word_percentage(self) -> float:
        """Get percentage of one-word commits."""
        if not self.analyses:
            return 0.0
        return (self.one_word_count / len(self.analyses)) * 100

