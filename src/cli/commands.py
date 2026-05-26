"""
CLI commands for CommitCritic.
Defines the analyze and write commands.
"""

from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from git.exc import InvalidGitRepositoryError, GitCommandError

from src.config import settings
from src.git import GitRepository, get_staged_diff
from src.git.diff import execute_commit
from src.agents import CommitWriterAgent, CommitAnalyzerAgent
from src.cli.formatter import (
    format_staged_summary,
    format_commit_suggestion,
    format_no_staged_changes,
    format_commit_success,
    format_commit_cancelled,
    format_analysis_report,
    format_progress,
    format_error,
)

# Initialize Typer app and Rich console
app = typer.Typer(
    name="commit-critic",
    help="🔍 AI-powered commit message analyzer and writer",
    add_completion=False,
)
console = Console()


def validate_environment() -> bool:
    """Validate that required environment variables are set."""
    if not settings.validate_api_key():
        console.print(
            Panel(
                "[red]Error:[/red] OpenAI API key not configured.\n\n"
                "Please set your API key:\n"
                "  1. Copy .env.example to .env\n"
                "  2. Add your OpenAI API key to .env\n\n"
                "Or set the environment variable:\n"
                "  export OPENAI_API_KEY='your-key-here'",
                title="⚠️ Configuration Error",
                border_style="red",
            )
        )
        return False
    return True


@app.command()
def analyze(
    url: Optional[str] = typer.Option(
        None,
        "--url",
        "-u",
        help="URL of a remote Git repository to analyze",
    ),
    limit: int = typer.Option(
        None,
        "--limit",
        "-n",
        help="Number of commits to analyze (default: 50)",
    ),
) -> None:
    """
    Analyze commit messages from a Git repository.

    Reviews the commit history and provides AI-generated critique,
    scoring each commit and suggesting improvements.

    Examples:
        python commit_critic.py analyze
        python commit_critic.py analyze --url="https://github.com/user/repo"
        python commit_critic.py analyze --limit=100
    """
    if not validate_environment():
        raise typer.Exit(code=1)

    # Use default limit from settings if not provided
    commit_limit = limit or settings.default_commit_limit

    try:
        # Open or clone repository
        if url:
            console.print(f"\n[bold blue]🔍 Cloning remote repository:[/bold blue] {url}")
            console.print("[dim]This may take a moment...[/dim]\n")
            repo = GitRepository.clone_remote(url)
        else:
            console.print("\n[bold blue]🔍 Analyzing current repository...[/bold blue]")
            repo = GitRepository.open_local()

        with repo:
            console.print(f"[dim]Fetching last {commit_limit} commits from {repo.name}...[/dim]\n")

            # Fetch commits
            commits = repo.get_commits(limit=commit_limit)

            if not commits:
                console.print("[yellow]No commits found in this repository.[/yellow]")
                raise typer.Exit(code=0)

            console.print(f"[dim]Analyzing {len(commits)} commits...[/dim]\n")

            # Analyze with LLM
            analyzer = CommitAnalyzerAgent()
            report = analyzer.create_report(
                repository_name=repo.name,
                commits=commits,
                batch_size=settings.batch_size,
                progress_callback=format_progress,
            )

            # Clear progress line
            console.print(" " * 50, end="\r")

            # Display results
            format_analysis_report(report)

    except InvalidGitRepositoryError:
        format_error("Not a Git repository. Please run this command from within a Git repository.")
        raise typer.Exit(code=1)
    except GitCommandError as e:
        format_error(f"Git error: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        format_error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


@app.command()
def write() -> None:
    """
    Interactive commit message writer.

    Analyzes staged changes and suggests a well-formatted
    commit message based on the diff.

    Examples:
        git add .
        python commit_critic.py write
    """
    if not validate_environment():
        raise typer.Exit(code=1)

    console.print("\n[bold blue]✍️ Interactive Commit Writer[/bold blue]")

    try:
        # Get staged changes
        staged = get_staged_diff()

        if not staged.has_changes:
            format_no_staged_changes()
            raise typer.Exit(code=0)

        # Analyze changes and generate suggestion
        writer = CommitWriterAgent()
        summary, suggestion = writer.generate_suggestion(staged)

        # Display summary and suggestion
        format_staged_summary(summary)
        format_commit_suggestion(suggestion)

        # Interactive prompt
        console.print("\n[dim]Press Enter to accept, or type your own message (empty to cancel):[/dim]")
        user_input = console.input("[bold green]> [/bold green]").strip()

        if user_input == "":
            # User pressed Enter - accept suggestion
            message = suggestion.full_message
        elif user_input.lower() in ("q", "quit", "exit", "cancel"):
            format_commit_cancelled()
            raise typer.Exit(code=0)
        else:
            # User provided their own message
            message = user_input

        # Execute the commit
        sha = execute_commit(message)
        format_commit_success(sha, message)

    except InvalidGitRepositoryError:
        format_error("Not a Git repository. Please run this command from within a Git repository.")
        raise typer.Exit(code=1)
    except GitCommandError as e:
        format_error(f"Git error: {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        format_commit_cancelled()
        raise typer.Exit(code=0)
    except Exception as e:
        format_error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information",
    ),
) -> None:
    """
    🔍 CommitCritic - AI-powered commit message analyzer

    Analyze your commit history or get help writing better commits.
    """
    if version:
        console.print("[bold]CommitCritic[/bold] version 0.1.0")
        raise typer.Exit()

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())

