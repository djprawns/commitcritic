"""
Commit data model for CommitCritic.
"""

from datetime import datetime
from pydantic import BaseModel


class Commit(BaseModel):
    """Represents a Git commit with its metadata."""

    sha: str
    short_sha: str
    message: str
    author_name: str
    author_email: str
    authored_date: datetime

    @property
    def title(self) -> str:
        """Get the first line of the commit message (title/subject)."""
        return self.message.split("\n")[0].strip()

    @property
    def body(self) -> str | None:
        """Get the commit message body (everything after the first line)."""
        lines = self.message.split("\n", 1)
        if len(lines) > 1:
            return lines[1].strip() or None
        return None

    @property
    def is_one_word(self) -> bool:
        """Check if the commit title is a single word."""
        return len(self.title.split()) == 1

    def __str__(self) -> str:
        return f"{self.short_sha}: {self.title}"

