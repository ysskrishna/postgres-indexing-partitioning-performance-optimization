from pathlib import Path
from core.logger import console
from rich.panel import Panel

from scenarios.S01_basic_indexes.setup import S01Setup
from scenarios.S01_basic_indexes.execute import S01Execute


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
        
        console.print(Panel.fit(
            f"[bold blue]Setting up and running {name}[/bold blue]",
            border_style="blue"
        ))
        self._scenarios[name]()

    def _run_S01(self):
        # --- Setup Phase ---
        console.print("[yellow]⚙️  Setting up S01_basic_indexes...[/yellow]")
        S01Setup().setup(users=1_000_000)

        # --- Execute Phase ---
        console.print("[yellow]🚀 Running executor for S01_basic_indexes...[/yellow]")
        S01Execute().execute()