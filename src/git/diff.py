"""
Git diff operations for CommitCritic write mode.
"""

from dataclasses import dataclass
from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError


@dataclass
class StagedChanges:
    """Represents staged changes in a Git repository."""

    diff: str
    files_changed: list[str]
    insertions: int
    deletions: int

    @property
    def has_changes(self) -> bool:
        """Check if there are any staged changes."""
        return bool(self.diff.strip())

    @property
    def summary(self) -> str:
        """Get a one-line summary of the changes."""
        return f"{len(self.files_changed)} files changed, +{self.insertions} -{self.deletions} lines"


def get_staged_diff(path: str | Path = ".") -> StagedChanges:
    """
    Get the staged diff from a Git repository.

    Args:
        path: Path to the repository (default: current directory)

    Returns:
        StagedChanges object with diff content and stats

    Raises:
        InvalidGitRepositoryError: If path is not a valid Git repository
    """
    repo = Repo(path, search_parent_directories=True)

    # Get the staged diff
    # diff between HEAD and index (staged changes)
    diff_text = repo.git.diff("--cached")

    # Get list of staged files
    staged_files = [item.a_path for item in repo.index.diff("HEAD")]

    # Also include newly added files (not in HEAD)
    for item in repo.index.diff(None):
        if item.a_path not in staged_files:
            staged_files.append(item.a_path)

    # Get stats
    if staged_files:
        stat_output = repo.git.diff("--cached", "--stat")
        # Parse insertions/deletions from stat output
        insertions = 0
        deletions = 0
        for line in stat_output.split("\n"):
            if "insertion" in line or "deletion" in line:
                parts = line.split(",")
                for part in parts:
                    if "insertion" in part:
                        insertions = int(part.strip().split()[0])
                    elif "deletion" in part:
                        deletions = int(part.strip().split()[0])
    else:
        insertions = 0
        deletions = 0

    return StagedChanges(
        diff=diff_text,
        files_changed=staged_files,
        insertions=insertions,
        deletions=deletions,
    )


def execute_commit(message: str, path: str | Path = ".") -> str:
    """
    Execute a git commit with the given message.

    Args:
        message: Commit message
        path: Path to the repository (default: current directory)

    Returns:
        The commit SHA

    Raises:
        InvalidGitRepositoryError: If path is not a valid Git repository
        GitCommandError: If commit fails
    """
    repo = Repo(path, search_parent_directories=True)
    commit = repo.index.commit(message)
    return commit.hexsha[:7]

