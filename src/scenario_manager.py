from pathlib import Path
from core.logger import console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from scenarios.S01_basic_indexes.setup import setup_basic_index_scenario
from scenarios.S01_basic_indexes.execute import run_basic_index_executor


SCENARIOS_PATH = Path(__file__).parent / "scenarios"

class ScenarioManager:
    def __init__(self):
        self._scenarios = {
            "S01_basic_indexes": self._run_S01,
        }

    def list_scenarios(self):
        return list(self._scenarios.keys())

    def run(self, name):
        """Dispatch to scenario-specific run method."""
        if name not in self._scenarios:
            raise ValueError(f"Scenario {name} not found")
        
        self._scenarios[name]()

    def _run_S01(self):
        console.print(Panel.fit(
            "[bold blue]Setting up and running S01_basic_indexes[/bold blue]",
            border_style="blue"
        ))

        # --- Setup Phase ---
        console.print("[yellow]⚙️  Setting up S01_basic_indexes...[/yellow]")
        setup_basic_index_scenario(users=1_000_000)

        # --- Execute Phase ---
        console.print("[yellow]🚀 Running executor for S01_basic_indexes...[/yellow]")
        run_basic_index_executor()