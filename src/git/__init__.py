"""Git module for CommitCritic."""

from .repository import GitRepository
from .commit import Commit
from .diff import get_staged_diff

__all__ = ["GitRepository", "Commit", "get_staged_diff"]
