from core.database import DatabaseConnection
from core.benchmark import SimpleBenchmark
from core.base import BaseExecute
from core.logger import console
from datetime import datetime, timedelta

class Execute(BaseExecute):
    def __init__(self):
        self.db = DatabaseConnection()
        self.benchmark = SimpleBenchmark()
        self.TABLE_NAME = "users"
    
    def execute(self):
        self.run_function_based()
        self.run_calculated_field()

    def run_function_based(self):
        console.print("\n[bold yellow]📊 Test: Function-based Index (LOWER(first_name))[/bold yellow]")
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE LOWER(first_name) = 'john'")
        console.print(f"[red]⏱️  Without expression index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_lower_firstname ON {self.TABLE_NAME}(LOWER(first_name))")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE LOWER(first_name) = 'john'")
        console.print(f"[green]⚡ With expression index:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_lower_firstname")

    def run_calculated_field(self):
        console.print("\n[bold yellow]📊 Test: Calculated Field Index (age groups)[/bold yellow]")
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE (age / 10) * 10 = 30")
        console.print(f"[red]⏱️  Without expression index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_age_group ON {self.TABLE_NAME} (((age / 10) * 10))")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE (age / 10) * 10 = 30")
        console.print(f"[green]⚡ With expression index:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_age_group")