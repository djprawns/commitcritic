"""
Git repository operations for CommitCritic.
"""

import tempfile
import shutil
from pathlib import Path

from git import Repo, GitCommandError
from git.exc import InvalidGitRepositoryError

from .commit import Commit


class GitRepository:
    """
    Wrapper for Git repository operations.
    Supports both local repositories and remote URLs.
    """

    def __init__(self, repo: Repo, temp_dir: Path | None = None):
        """
        Initialize with a GitPython Repo instance.

        Args:
            repo: GitPython Repo object
            temp_dir: Temporary directory path (for cleanup of cloned repos)
        """
        self._repo = repo
        self._temp_dir = temp_dir

    @classmethod
    def open_local(cls, path: str | Path = ".") -> "GitRepository":
        """
        Open a local Git repository.

        Args:
            path: Path to the repository (default: current directory)

        Returns:
            GitRepository instance

        Raises:
            InvalidGitRepositoryError: If path is not a valid Git repository
        """
        repo = Repo(path, search_parent_directories=True)
        return cls(repo)

    @classmethod
    def clone_remote(cls, url: str) -> "GitRepository":
        """
        Clone a remote repository to a temporary directory.

        Args:
            url: Remote repository URL (HTTPS or SSH)

        Returns:
            GitRepository instance

        Raises:
            GitCommandError: If cloning fails
        """
        temp_dir = Path(tempfile.mkdtemp(prefix="commitcritic_"))
        try:
            # Shallow clone for faster operation (we only need commit messages)
            repo = Repo.clone_from(
                url,
                temp_dir,
                depth=100,  # Get last 100 commits
                no_single_branch=True,
            )
            return cls(repo, temp_dir)
        except Exception:
            # Clean up on failure
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise

    def get_commits(self, limit: int = 50) -> list[Commit]:
        """
        Get the most recent commits from the repository.

        Args:
            limit: Maximum number of commits to retrieve

        Returns:
            List of Commit objects, most recent first
        """
        commits = []

        for git_commit in self._repo.iter_commits(max_count=limit):
            commit = Commit(
                sha=git_commit.hexsha,
                short_sha=git_commit.hexsha[:7],
                message=git_commit.message.strip(),
                author_name=git_commit.author.name,
                author_email=git_commit.author.email,
                authored_date=git_commit.authored_datetime,
            )
            commits.append(commit)

        return commits

    def get_commit_count(self) -> int:
        """Get total number of commits in the repository."""
        return sum(1 for _ in self._repo.iter_commits())

    @property
    def name(self) -> str:
        """Get the repository name (directory name or remote URL basename)."""
        if self._repo.remotes:
            remote_url = self._repo.remotes.origin.url
            # Extract name from URL (handle both .git and non-.git URLs)
            name = remote_url.rstrip("/").split("/")[-1]
            if name.endswith(".git"):
                name = name[:-4]
            return name
        return Path(self._repo.working_dir).name

    @property
    def working_dir(self) -> Path:
        """Get the working directory path."""
        return Path(self._repo.working_dir)

    def cleanup(self) -> None:
        """
        Clean up temporary resources.
        Only needed for cloned repositories.
        """
        if self._temp_dir and self._temp_dir.exists():
            shutil.rmtree(self._temp_dir, ignore_errors=True)

    def __enter__(self) -> "GitRepository":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()

