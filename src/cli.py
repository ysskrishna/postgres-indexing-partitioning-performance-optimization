"""
PostgreSQL Indexing and Partitioning Performance Optimization CLI
"""

import typer
from rich.console import Console
from rich.panel import Panel

from scenario_manager import ScenarioManager

app = typer.Typer(
    name="postgres-performance",
    help="PostgreSQL Indexing and Partitioning Performance Optimization Tool",
    add_completion=False
)

console = Console()
scenario_manager = ScenarioManager()

@app.command()
def list():
    """List all available scenarios."""
    console.print(Panel.fit("[bold cyan]Available Scenarios[/bold cyan]", border_style="cyan"))
    for folder in scenario_manager.list_scenarios():
        console.print(f"[green]{folder}[/green]")

@app.command()
def run(
    scenario: str = typer.Argument(..., help="Scenario folder name (e.g., S01_basic_indexes)")
):
    """Setup and run a given scenario."""
    try:
        console.print(f"[yellow]⚙️  Running {scenario}...[/yellow]")
        scenario_manager.run(scenario)
        console.print(f"[green]✅ {scenario} completed successfully![/green]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 