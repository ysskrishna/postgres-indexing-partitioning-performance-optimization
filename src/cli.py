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
def setup(
    scenario: str = typer.Argument(..., help="Scenario folder name (e.g., S01_basic_indexes)")
):
    """Setup database tables and sample data for performance testing."""
    
    if scenario not in discover_scenarios():
        console.print(f"[red]❌ Unknown scenario: {scenario}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel.fit(
        f"[bold blue]Setting up {scenario} scenario[/bold blue]",
        border_style="blue"
    ))
    
    if scenario == "S01_basic_indexes":
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Setting up S01_basic_indexes scenario...", total=None)
            setup_basic_index_scenario(users=1000, orders=5000)
            progress.update(task, completed=True)
    else:
        console.print(f"[red]❌ Unknown scenario: {scenario}[/red]")
        raise typer.Exit(1)



@app.command()
def demo(
    scenario: str = typer.Argument(..., help="Scenario to demonstrate (e.g., S01_basic_indexes)")
):
    """Run performance demonstrations."""
    
    if scenario not in discover_scenarios():
        console.print(f"[red]❌ Unknown scenario: {scenario}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel.fit(
        f"[bold blue]Running {scenario} Demo[/bold blue]",
        border_style="blue"
    ))
    
    if scenario == "S01_basic_indexes":
        run_basic_index_demo()
    else:
        console.print(f"[red]❌ Unknown scenario: {scenario}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app() 