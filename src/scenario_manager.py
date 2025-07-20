from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from scenarios.S01_basic_indexes.setup import setup_basic_index_scenario
from scenarios.S01_basic_indexes.demo import run_basic_index_demo


SCENARIOS_PATH = Path(__file__).parent / "scenarios"
console = Console()

class ScenarioManager:
    def __init__(self):
        self._scenarios = self._discover_scenarios()        

    def _discover_scenarios(self):
        return [
            folder.name for folder in SCENARIOS_PATH.iterdir()
            if folder.is_dir() and not folder.name.startswith("__")
        ]
    
    def list_scenarios(self):
        return self._scenarios

    
    def run(self, name):
        if name not in self._scenarios:
            raise ValueError(f"Scenario {name} not found")

        console.print(Panel.fit(
            f"[bold blue]Setting up and running {name}[/bold blue]",
            border_style="blue"
        ))

        # --- Setup Phase ---
        console.print(f"[yellow]⚙️  Setting up {name}...[/yellow]")
        if name == "S01_basic_indexes":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                task = progress.add_task(f"Setting up {name}...", total=None)
                setup_basic_index_scenario(users=1000, orders=5000)
                progress.update(task, completed=True)
        else:
            console.print(f"[red]❌ No setup defined for {name}[/red]")
            raise ValueError(f"No setup defined for {name}")

        # --- Demo Phase ---
        console.print(f"[yellow]🚀 Running demo for {name}...[/yellow]")
        if name == "S01_basic_indexes":
            run_basic_index_demo()
        else:
            console.print(f"[red]❌ No demo defined for {name}[/red]")
            raise ValueError(f"No demo defined for {name}")