"""Data models for CommitCritic."""

from .suggestion import CommitSuggestion
from .analysis import CommitAnalysis, AnalysisReport

__all__ = ["CommitSuggestion", "CommitAnalysis", "AnalysisReport"]

