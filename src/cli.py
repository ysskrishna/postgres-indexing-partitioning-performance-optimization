"""
PostgreSQL Indexing and Partitioning Performance Optimization CLI
"""

import typer
from core.logger import console
from rich.panel import Panel

from scenario_manager import ScenarioManager

app = typer.Typer(
    name="postgres-performance",
    help="CLI Tool for running performance tests on PostgreSQL",
    add_completion=False
)

scenario_manager = ScenarioManager()

@app.command()
def list():
    """List all available scenarios."""
    console.print(Panel.fit("[bold cyan]Available Scenarios[/bold cyan]", border_style="cyan"), console_only=True)
    for folder in scenario_manager.list_scenarios():
        console.print(f"[green]{folder}[/green]", console_only=True)

@app.command()
def run(
    scenario: str = typer.Argument(..., help="Scenario folder name")
):
    """Setup and run a given scenario."""
    try:
        console.print(f"[yellow]⚙️  Running {scenario}...[/yellow]")
        scenario_manager.run(scenario)
        console.print(f"[green]✅ {scenario} completed successfully![/green]")
        console.save_html("report.html")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def run_all():
    """Setup and run all available scenarios."""
    scenarios = scenario_manager.list_scenarios()
    total_scenarios = len(scenarios)
    
    console.print(Panel.fit(
        f"[bold cyan]Running All Scenarios ({total_scenarios} total)[/bold cyan]", 
        border_style="cyan"
    ))
    
    successful_scenarios = []
    failed_scenarios = []
    
    for i, scenario in enumerate(scenarios, 1):
        try:
            console.print(f"[yellow]⚙️  Running {scenario} ({i}/{total_scenarios})...[/yellow]")
            scenario_manager.run(scenario)
            console.print(f"[green]✅ {scenario} completed successfully![/green]")
            successful_scenarios.append(scenario)
        except Exception as e:
            console.print(f"[red]❌ {scenario} failed: {e}[/red]")
            failed_scenarios.append(scenario)
            # Continue with next scenario instead of stopping
    
    # Summary
    console.print(Panel.fit(
        f"[bold]Test Summary:[/bold]\n"
        f"[green]✅ Successful: {len(successful_scenarios)}[/green]\n"
        f"[red]❌ Failed: {len(failed_scenarios)}[/red]\n"
        f"[blue]📊 Total: {total_scenarios}[/blue]",
        border_style="blue"
    ))
    
    if failed_scenarios:
        console.print("[red]Failed scenarios:[/red]")
        for scenario in failed_scenarios:
            console.print(f"  [red]• {scenario}[/red]")
        console.save_html("report.html")
        raise typer.Exit(1)
    else:
        console.print("[green]🎉 All scenarios completed successfully![/green]")
        console.save_html("report.html")

if __name__ == "__main__":
    app() 