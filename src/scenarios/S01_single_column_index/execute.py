from core.database import DatabaseConnection
from core.benchmark import SimpleBenchmark
from core.logger import console
from core.base import BaseExecute
from datetime import datetime, timedelta

class S01Execute(BaseExecute):
    def __init__(self):
        self.db = DatabaseConnection()
        self.benchmark = SimpleBenchmark()
        self.TABLE_NAME = "users"
    
    def execute(self):
        self.run_range_query_created_at()
        self.run_equality_search_age()
        self.run_in_clause_age()
        
    def run_range_query_created_at(self):
        console.print("\n[bold]📊 Test: Range Query (created_at BETWEEN)[/bold]")

        # Get date range from existing data
        date_result = self.db.execute_query(f"SELECT MIN(created_at), MAX(created_at) FROM {self.TABLE_NAME}")
        min_date, max_date = date_result[0]
        mid_date = min_date + (max_date - min_date) / 2
        end_date = mid_date + timedelta(days=30)
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE created_at BETWEEN %s AND %s", (mid_date, end_date))
        console.print(f"[red]⏱️  Without index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_created_at ON {self.TABLE_NAME}(created_at)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE created_at BETWEEN %s AND %s", (mid_date, end_date))
        console.print(f"[green]⚡ With index:[/green] [white]{time2:.4f}s[/white] | [white]Speedup: {time1/time2:.1f}x[/white]")
        
        self.db.execute_query(f"DROP INDEX idx_users_created_at")
    
    def run_equality_search_age(self):
        console.print("\n[bold]📊 Test: Equality Search (age = X)[/bold]")
        
        # Get random age from existing data
        age_result = self.db.execute_query(f"SELECT age FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_age = age_result[0][0]
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE age = %s", (test_age,))
        console.print(f"[red]⏱️  Without index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_age ON {self.TABLE_NAME}(age)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE age = %s", (test_age,))
        console.print(f"[green]⚡ With index:[/green] [white]{time2:.4f}s[/white] | [white]Speedup: {time1/time2:.1f}x[/white]")
        
        self.db.execute_query(f"DROP INDEX idx_users_age")
    
    def run_in_clause_age(self):
        console.print("\n[bold]📊 Test: IN Clause (age IN (...))[/bold]")
        ages = [20, 25, 30, 35]
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE age IN %s", (tuple(ages),))
        console.print(f"[red]⏱️  Without index:[/red] [white]{time1:.4f}s[/white]")

        self.db.execute_query(f"CREATE INDEX idx_users_age_in ON {self.TABLE_NAME}(age)")
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE age IN %s", (tuple(ages),))
        console.print(f"[green]⚡ With index:[/green] [white]{time2:.4f}s[/white] | [white]Speedup: {time1/time2:.1f}x[/white]")

        self.db.execute_query(f"DROP INDEX idx_users_age_in")