from pathlib import Path
from core.logger import console
from rich.panel import Panel
import importlib

SCENARIOS_PATH = Path(__file__).parent / "scenarios"

class ScenarioManager:
    def __init__(self):
        self._scenarios = self._load_scenarios()
    
    def _load_scenarios(self):
        scenarios = {}
        
        for scenario_dir in SCENARIOS_PATH.iterdir():
            scenario = {"setup": False,"execute": False}
            if scenario_dir.is_dir() and (scenario_dir / "setup.py").exists():
                scenario["setup"] = f"{SCENARIOS_PATH.name}.{scenario_dir.name}.setup"
            else:
                scenario["setup"] = f"{SCENARIOS_PATH.name}.base_data_setup"
            
            if scenario_dir.is_dir() and (scenario_dir / "execute.py").exists():
                scenario["execute"] = f"{SCENARIOS_PATH.name}.{scenario_dir.name}.execute"
            scenarios[scenario_dir.name] = scenario
        return scenarios
        
    def list_scenarios(self):
        return list(self._scenarios.keys())

    def run(self, name):
        """Dispatch to scenario-specific run method."""
        if name not in self._scenarios:
            raise ValueError(f"Scenario {name} not found")
        
        
        console.print(Panel.fit(
            f"[bold blue] Running Scenario {name}[/bold blue]",
            border_style="blue"
        ))
        
        if self._scenarios[name]["setup"]:
            console.print(f"[bold blue] Setting up Scenario {name}[/bold blue]")
            setup_module = importlib.import_module(self._scenarios[name]["setup"])
            setup_class = getattr(setup_module, "Setup")
            setup_instance = setup_class()
            setup_instance.setup()
        
        if self._scenarios[name]["execute"]:
            console.print(f"[bold blue] Executing Scenario {name}[/bold blue]")
            execute_module = importlib.import_module(self._scenarios[name]["execute"])
            execute_class = getattr(execute_module, "Execute")
            execute_instance = execute_class()
            execute_instance.execute()
        
        console.print(Panel.fit(
            f"[bold blue]Scenario {name} completed[/bold blue]",
            border_style="blue"
        ))