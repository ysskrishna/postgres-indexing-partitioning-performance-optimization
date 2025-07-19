"""
PostgreSQL Indexing and Partitioning Performance Optimization CLI
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from scenarios.S01_basic_indexes.setup import setup_basic_index_scenario
from scenarios.S01_basic_indexes.demo import run_basic_index_demo

app = typer.Typer(
    name="postgres-performance",
    help="PostgreSQL Indexing and Partitioning Performance Optimization Tool",
    add_completion=False
)

console = Console()
SCENARIOS_PATH = Path(__file__).parent / "scenarios"


def discover_scenarios():
    """Discover scenario folders in the scenarios directory."""
    return [
        folder.name for folder in SCENARIOS_PATH.iterdir()
        if folder.is_dir() and not folder.name.startswith("__")
    ]

@app.command()
def list():
    """List all available scenarios."""
    console.print(Panel.fit("[bold cyan]Available Scenarios[/bold cyan]", border_style="cyan"))
    for folder in discover_scenarios():
        console.print(f"[green]{folder}[/green]")

@app.command()
def run(
    scenario: str = typer.Argument(..., help="Scenario folder name (e.g., S01_basic_indexes)")
):
    """Setup and run demo for a given scenario."""

    # Validate scenario
    scenarios = discover_scenarios()
    if scenario not in scenarios:
        console.print(f"[red]❌ Unknown scenario: {scenario}[/red]")
        raise typer.Exit(1)

    console.print(Panel.fit(
        f"[bold blue]Setting up and running {scenario}[/bold blue]",
        border_style="blue"
    ))

    # --- Setup Phase ---
    console.print(f"[yellow]⚙️  Setting up {scenario}...[/yellow]")
    if scenario == "S01_basic_indexes":
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Setting up {scenario}...", total=None)
            setup_basic_index_scenario(users=1000, orders=5000)
            progress.update(task, completed=True)
    else:
        console.print(f"[red]❌ No setup defined for {scenario}[/red]")
        raise typer.Exit(1)

    # --- Demo Phase ---
    console.print(f"[yellow]🚀 Running demo for {scenario}...[/yellow]")
    if scenario == "S01_basic_indexes":
        run_basic_index_demo()
    else:
        console.print(f"[red]❌ No demo defined for {scenario}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app() 