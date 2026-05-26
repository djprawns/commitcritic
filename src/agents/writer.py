"""
CommitWriterAgent - Generates commit messages from staged changes.
"""

from src.models.suggestion import CommitSuggestion, ChangeSummary
from src.git.diff import StagedChanges

from .base import BaseAgent
from .prompts.writer import (
    SYSTEM_PROMPT,
    ANALYZE_DIFF_PROMPT,
    SUGGEST_MESSAGE_PROMPT,
)


class CommitWriterAgent(BaseAgent):
    """
    Agent that analyzes diffs and generates commit message suggestions.
    """

    def analyze_changes(self, staged: StagedChanges) -> ChangeSummary:
        """
        Analyze staged changes and extract key information.

        Args:
            staged: StagedChanges object with diff and stats

        Returns:
            ChangeSummary with descriptions of what changed
        """
        # Truncate diff if too long (to fit in context window)
        diff_text = staged.diff
        if len(diff_text) > 8000:
            diff_text = diff_text[:8000] + "\n... [diff truncated]"

        prompt = ANALYZE_DIFF_PROMPT.format(
            diff=diff_text,
            files_changed=", ".join(staged.files_changed),
            insertions=staged.insertions,
            deletions=staged.deletions,
        )

        response = self._chat_json(SYSTEM_PROMPT, prompt)

        # Store analysis for use in suggestion
        self._last_analysis = response

        return ChangeSummary(
            files_changed=len(staged.files_changed),
            insertions=staged.insertions,
            deletions=staged.deletions,
            change_descriptions=response.get("change_descriptions", []),
        )

    def suggest_message(self, staged: StagedChanges, summary: ChangeSummary) -> CommitSuggestion:
        """
        Generate a commit message suggestion based on the analysis.

        Args:
            staged: StagedChanges object with diff and stats
            summary: ChangeSummary from analyze_changes

        Returns:
            CommitSuggestion with the suggested commit message
        """
        # Use cached analysis if available
        analysis = getattr(self, '_last_analysis', {})

        prompt = SUGGEST_MESSAGE_PROMPT.format(
            change_descriptions="\n".join(f"- {d}" for d in summary.change_descriptions),
            change_type=analysis.get("primary_change_type", "chore"),
            scope=analysis.get("suggested_scope", "none"),
            complexity=analysis.get("complexity", "moderate"),
            diff_summary=f"{summary.files_changed} files, +{summary.insertions} -{summary.deletions} lines",
        )

        response = self._chat_json(SYSTEM_PROMPT, prompt)

        return CommitSuggestion(
            title=response.get("title", "update code"),
            body=response.get("body"),
            commit_type=response.get("commit_type", "chore"),
            scope=response.get("scope"),
        )

    def generate_suggestion(self, staged: StagedChanges) -> tuple[ChangeSummary, CommitSuggestion]:
        """
        Convenience method to analyze changes and generate suggestion in one call.

        Args:
            staged: StagedChanges object with diff and stats

        Returns:
            Tuple of (ChangeSummary, CommitSuggestion)
        """
        summary = self.analyze_changes(staged)
        suggestion = self.suggest_message(staged, summary)
        return summary, suggestion

