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
    
    def get_random_user(self):
        return self.db.execute_query(f"SELECT user_id FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
    
    
    def execute(self):
        self.run_range_query_created_at()
        self.run_order_by_username()
        
    def run_range_query_created_at(self):
        console.print("\n[bold yellow]📊 Test: Range Query (WHERE created_at BETWEEN X AND Y)[/bold yellow]")
        
        start_date = datetime.now() - timedelta(days=30)
        end_date = start_date + timedelta(days=7)
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE created_at BETWEEN %s AND %s", (start_date, end_date))
        console.print(f"[red]⏱️  Time without index:[/red] [bold]{time1:.4f}[/bold] seconds")
        
        self.db.execute_query(f"CREATE INDEX IF NOT EXISTS idx_users_created_at ON {self.TABLE_NAME}(created_at)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE created_at BETWEEN %s AND %s", (start_date, end_date))
        console.print(f"[green]⚡ Time with index:[/green] [bold]{time2:.4f}[/bold] seconds")
    
    def run_order_by_username(self):
        console.print("\n[bold yellow]📊 Test: ORDER BY Operations[/bold yellow]")
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT * FROM {self.TABLE_NAME} ORDER BY username LIMIT 100", None)
        console.print(f"[red]⏱️  Time without index:[/red] [bold]{time1:.4f}[/bold] seconds")
        
        self.db.execute_query(f"CREATE INDEX IF NOT EXISTS idx_users_username ON {self.TABLE_NAME}(username)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT * FROM {self.TABLE_NAME} ORDER BY username LIMIT 100", None)
        console.print(f"[green]⚡ Time with index:[/green] [bold]{time2:.4f}[/bold] seconds")