"""
Prompts for the CommitWriterAgent.
"""

SYSTEM_PROMPT = """You are an expert software developer who writes excellent Git commit messages.

You follow the Conventional Commits specification and best practices:
- Use clear, descriptive commit messages
- Start with a type: feat, fix, refactor, docs, test, chore, style, perf, ci, build
- Optionally include a scope in parentheses
- Write a concise subject line (50 chars or less preferred, 72 max)
- Use imperative mood ("add feature" not "added feature")
- Include a body with bullet points for complex changes

Your task is to analyze code changes and suggest well-crafted commit messages."""


ANALYZE_DIFF_PROMPT = """Analyze the following git diff and identify the key changes.

GIT DIFF:
```
{diff}
```

FILES CHANGED: {files_changed}
STATS: +{insertions} -{deletions} lines

Respond with a JSON object containing:
{{
    "change_descriptions": ["list of 2-5 high-level descriptions of what changed"],
    "primary_change_type": "feat|fix|refactor|docs|test|chore|style|perf|ci|build",
    "suggested_scope": "the area/module affected, or null if unclear",
    "complexity": "simple|moderate|complex"
}}"""


SUGGEST_MESSAGE_PROMPT = """Based on the following analysis of code changes, generate a well-crafted commit message.

CHANGES DETECTED:
{change_descriptions}

PRIMARY CHANGE TYPE: {change_type}
SUGGESTED SCOPE: {scope}
COMPLEXITY: {complexity}

DIFF SUMMARY:
{diff_summary}

Respond with a JSON object containing:
{{
    "title": "the commit subject line (50 chars or less, imperative mood)",
    "body": "bullet points explaining the changes (or null for simple changes)",
    "commit_type": "feat|fix|refactor|docs|test|chore|style|perf|ci|build",
    "scope": "the scope, or null"
}}

Guidelines:
- Title should be concise and descriptive
- Use imperative mood ("add" not "added")
- Body should have bullet points starting with "-" for moderate/complex changes
- Body can be null for very simple, single-purpose changes
- Title should NOT include the type prefix (e.g., write "add user auth" not "feat: add user auth")"""

