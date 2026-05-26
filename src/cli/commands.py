"""
CLI commands for CommitCritic.
Defines the analyze and write commands.
"""

from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

from src.config import settings

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

    if url:
        console.print(f"\n[bold blue]🔍 Analyzing remote repository:[/bold blue] {url}")
    else:
        console.print("\n[bold blue]🔍 Analyzing current repository...[/bold blue]")

    console.print(f"[dim]Fetching last {commit_limit} commits...[/dim]\n")

    # TODO: Implement analysis logic
    # 1. Open/clone repository
    # 2. Fetch commits
    # 3. Batch analyze with LLM
    # 4. Format and display results

    console.print("[yellow]⚠️ Analysis mode not yet implemented[/yellow]")


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
    console.print("[dim]Analyzing staged changes...[/dim]\n")

    # TODO: Implement write logic
    # 1. Get staged diff
    # 2. Analyze changes with LLM
    # 3. Generate commit message suggestion
    # 4. Interactive prompt for user acceptance
    # 5. Execute git commit

    console.print("[yellow]⚠️ Write mode not yet implemented[/yellow]")


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

