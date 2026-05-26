"""
CommitAnalyzerAgent - Analyzes and scores commit messages.
"""

from src.models.analysis import CommitAnalysis, AnalysisReport
from src.git.commit import Commit

from .base import BaseAgent
from .prompts.analyzer import SYSTEM_PROMPT, BATCH_ANALYZE_PROMPT


class CommitAnalyzerAgent(BaseAgent):
    """
    Agent that analyzes commit messages and provides scores and feedback.
    """

    def analyze_batch(self, commits: list[Commit]) -> list[CommitAnalysis]:
        """
        Analyze a batch of commits.

        Args:
            commits: List of Commit objects to analyze

        Returns:
            List of CommitAnalysis results
        """
        if not commits:
            return []

        # Format commits for the prompt
        commits_text = "\n".join(
            f"[{c.short_sha}] {c.message}" for c in commits
        )

        prompt = BATCH_ANALYZE_PROMPT.format(commits=commits_text)

        response = self._chat_json(SYSTEM_PROMPT, prompt, max_tokens=2048)

        analyses = []
        for item in response.get("analyses", []):
            analysis = CommitAnalysis(
                sha=item.get("sha", ""),
                original_message=self._get_message_for_sha(commits, item.get("sha", "")),
                score=item.get("score", 5),
                issues=item.get("issues", []),
                suggestions=item.get("suggestion"),
                praise=item.get("praise"),
            )
            analyses.append(analysis)

        return analyses

    def analyze_all(
        self,
        commits: list[Commit],
        batch_size: int = 10,
        progress_callback=None,
    ) -> list[CommitAnalysis]:
        """
        Analyze all commits in batches.

        Args:
            commits: List of all commits to analyze
            batch_size: Number of commits per LLM call
            progress_callback: Optional callback(current, total) for progress updates

        Returns:
            List of all CommitAnalysis results
        """
        all_analyses = []
        total = len(commits)

        for i in range(0, total, batch_size):
            batch = commits[i:i + batch_size]
            batch_analyses = self.analyze_batch(batch)
            all_analyses.extend(batch_analyses)

            if progress_callback:
                progress_callback(min(i + batch_size, total), total)

        return all_analyses

    def create_report(
        self,
        repository_name: str,
        commits: list[Commit],
        batch_size: int = 10,
        progress_callback=None,
    ) -> AnalysisReport:
        """
        Create a complete analysis report for a repository.

        Args:
            repository_name: Name of the repository
            commits: List of commits to analyze
            batch_size: Number of commits per LLM call
            progress_callback: Optional callback for progress updates

        Returns:
            AnalysisReport with all analyses and statistics
        """
        analyses = self.analyze_all(commits, batch_size, progress_callback)

        return AnalysisReport(
            repository_name=repository_name,
            total_commits=len(commits),
            analyses=analyses,
        )

    def _get_message_for_sha(self, commits: list[Commit], sha: str) -> str:
        """Find the original message for a given SHA."""
        for commit in commits:
            if commit.short_sha == sha or commit.sha.startswith(sha):
                return commit.message
        return ""

