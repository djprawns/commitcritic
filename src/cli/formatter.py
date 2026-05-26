"""
Rich terminal output formatting for CommitCritic.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from src.models.suggestion import CommitSuggestion, ChangeSummary
from src.models.analysis import CommitAnalysis, AnalysisReport


console = Console()


def format_staged_summary(summary: ChangeSummary) -> None:
    """Display a summary of staged changes."""
    console.print(f"\n[dim]Analyzing staged changes... ({summary.files_changed} files changed, +{summary.insertions} -{summary.deletions} lines)[/dim]\n")

    if summary.change_descriptions:
        console.print("[bold]Changes detected:[/bold]")
        for desc in summary.change_descriptions:
            console.print(f"  [cyan]•[/cyan] {desc}")
        console.print()


def format_commit_suggestion(suggestion: CommitSuggestion) -> None:
    """Display a suggested commit message in a nice panel."""
    # Build the message content
    message_lines = [f"[bold green]{suggestion.conventional_title}[/bold green]"]

    if suggestion.body:
        message_lines.append("")
        for line in suggestion.body.split("\n"):
            message_lines.append(f"[white]{line}[/white]")

    message_content = "\n".join(message_lines)

    console.print(Panel(
        message_content,
        title="[bold]Suggested commit message[/bold]",
        border_style="green",
        box=box.HEAVY,
        padding=(1, 2),
    ))


def format_no_staged_changes() -> None:
    """Display message when there are no staged changes."""
    console.print(Panel(
        "[yellow]No staged changes found.[/yellow]\n\n"
        "Stage your changes first:\n"
        "  [cyan]git add <files>[/cyan]\n"
        "  [cyan]git add .[/cyan]",
        title="⚠️ Nothing to commit",
        border_style="yellow",
    ))


def format_commit_success(sha: str, message: str) -> None:
    """Display success message after committing."""
    title = message.split("\n")[0]
    console.print(f"\n[bold green]✓[/bold green] Committed: [cyan]{sha}[/cyan] {title}")


def format_commit_cancelled() -> None:
    """Display message when user cancels the commit."""
    console.print("\n[dim]Commit cancelled.[/dim]")


def format_analysis_report(report: AnalysisReport) -> None:
    """Display a complete analysis report."""
    console.print(f"\n[bold]Analyzing commits from [cyan]{report.repository_name}[/cyan]...[/bold]\n")

    # Bad commits section
    bad_commits = report.bad_commits
    if bad_commits:
        console.print(Panel(
            "[bold]💩 COMMITS THAT NEED WORK[/bold]",
            border_style="red",
            box=box.HEAVY,
        ))
        console.print()

        for analysis in bad_commits[:10]:  # Limit to top 10
            _format_bad_commit(analysis)

    # Good commits section
    good_commits = report.good_commits
    if good_commits:
        console.print(Panel(
            "[bold]💎 WELL-WRITTEN COMMITS[/bold]",
            border_style="green",
            box=box.HEAVY,
        ))
        console.print()

        for analysis in good_commits[:5]:  # Show top 5
            _format_good_commit(analysis)

    # Stats section
    _format_stats(report)


def _format_bad_commit(analysis: CommitAnalysis) -> None:
    """Format a single bad commit."""
    title = analysis.original_message.split("\n")[0][:60]

    console.print(f'[bold]Commit:[/bold] "{title}"')
    console.print(f'[bold]Score:[/bold] [red]{analysis.score}/10[/red]')

    if analysis.issues:
        console.print(f'[bold]Issue:[/bold] {analysis.issues[0]}')

    if analysis.suggestions:
        console.print(f'[bold green]Better:[/bold green] "{analysis.suggestions}"')

    console.print()


def _format_good_commit(analysis: CommitAnalysis) -> None:
    """Format a single good commit."""
    title = analysis.original_message.split("\n")[0][:60]

    console.print(f'[bold]Commit:[/bold] "{title}"')
    console.print(f'[bold]Score:[/bold] [green]{analysis.score}/10[/green]')

    if analysis.praise:
        console.print(f'[bold]Why it\'s good:[/bold] {analysis.praise}')

    console.print()


def _format_stats(report: AnalysisReport) -> None:
    """Format the statistics section."""
    console.print(Panel(
        "[bold]📊 YOUR STATS[/bold]",
        border_style="blue",
        box=box.HEAVY,
    ))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Average score:", f"{report.average_score:.1f}/10")
    table.add_row("Vague commits:", f"{report.vague_count} ({report.vague_percentage:.0f}%)")
    table.add_row("One-word commits:", f"{report.one_word_count} ({report.one_word_percentage:.0f}%)")
    table.add_row("Good commits:", f"{len(report.good_commits)} ({len(report.good_commits)/report.total_commits*100:.0f}%)")

    console.print(table)
    console.print()


def format_progress(current: int, total: int) -> None:
    """Display progress during analysis."""
    console.print(f"[dim]Analyzed {current}/{total} commits...[/dim]", end="\r")


def format_error(message: str) -> None:
    """Display an error message."""
    console.print(f"\n[bold red]Error:[/bold red] {message}")

