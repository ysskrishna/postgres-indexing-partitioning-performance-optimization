from core.database import DatabaseConnection
from core.benchmark import SimpleBenchmark
from core.base import BaseExecute
from core.logger import console

class Execute(BaseExecute):
    def __init__(self):
        self.db = DatabaseConnection()
        self.benchmark = SimpleBenchmark()
        self.TABLE_NAME = "users"
    
    def execute(self):
        self.run_array_search()
        self.run_text_search()
        self.run_multiple_array_elements()

    def run_array_search(self):
        console.print("\n[bold yellow]📊 Test: Array Search (tags @> ARRAY['active'])[/bold yellow]")
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE tags @> ARRAY['active']")
        console.print(f"[red]⏱️  Without GIN index:[/red] [bold]{time1:.4f}s[/bold]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_tags_gin ON {self.TABLE_NAME} USING GIN(tags)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE tags @> ARRAY['active']")
        console.print(f"[green]⚡ With GIN index:[/green] [bold]{time2:.4f}s[/bold] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_tags_gin")

    def run_text_search(self):
        console.print("\n[bold yellow]📊 Test: Text Search (first_name || last_name)[/bold yellow]")
        
        self.db.execute_query(f"ALTER TABLE {self.TABLE_NAME} ADD COLUMN IF NOT EXISTS full_text_search tsvector")
        self.db.execute_query(f"UPDATE {self.TABLE_NAME} SET full_text_search = to_tsvector('english', first_name || ' ' || last_name || ' ' || city)")
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE full_text_search @@ to_tsquery('english', 'John & New')")
        console.print(f"[red]⏱️  Without GIN index:[/red] [bold]{time1:.4f}s[/bold]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_fulltext_gin ON {self.TABLE_NAME} USING GIN(full_text_search)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE full_text_search @@ to_tsquery('english', 'John & New')")
        console.print(f"[green]⚡ With GIN index:[/green] [bold]{time2:.4f}s[/bold] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_fulltext_gin")
        self.db.execute_query(f"ALTER TABLE {self.TABLE_NAME} DROP COLUMN IF EXISTS full_text_search")

    def run_multiple_array_elements(self):
        console.print("\n[bold yellow]📊 Test: Multiple Array Elements (tags && ARRAY['user','premium'])[/bold yellow]")
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE tags && ARRAY['user','premium']")
        console.print(f"[red]⏱️  Without GIN index:[/red] [bold]{time1:.4f}s[/bold]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_tags_overlap_gin ON {self.TABLE_NAME} USING GIN(tags)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE tags && ARRAY['user','premium']")
        console.print(f"[green]⚡ With GIN index:[/green] [bold]{time2:.4f}s[/bold] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_tags_overlap_gin")