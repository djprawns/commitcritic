#!/usr/bin/env python3
"""
CommitCritic - AI-powered commit message analyzer and writer.

Usage:
    python commit_critic.py analyze              # Analyze current repo
    python commit_critic.py analyze --url=URL   # Analyze remote repo
    python commit_critic.py write               # Interactive commit writer
"""

from src.cli import app

if __name__ == "__main__":
    app()

