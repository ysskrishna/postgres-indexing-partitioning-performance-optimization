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
        self.run_filtered_index()
        self.run_age_range_index()
        self.run_storage_comparison()

    def run_filtered_index(self):
        console.print("\n[bold yellow]📊 Test: Filtered Index (recent users only)[/bold yellow]")
        
        recent_date = datetime.now() - timedelta(days=365)
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE created_at > %s AND age = 30", (recent_date,))
        console.print(f"[red]⏱️  Without partial index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_recent_age ON {self.TABLE_NAME}(age) WHERE created_at > '{recent_date}'")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE created_at > %s AND age = 30", (recent_date,))
        console.print(f"[green]⚡ With partial index:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_recent_age")

    def run_age_range_index(self):
        console.print("\n[bold yellow]📊 Test: Age Range Index (working age 25-65 only)[/bold yellow]")
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*), AVG(age) FROM {self.TABLE_NAME} WHERE age BETWEEN 30 AND 40")
        console.print(f"[red]⏱️  Without partial index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_working_age ON {self.TABLE_NAME}(age) WHERE age BETWEEN 25 AND 65")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*), AVG(age) FROM {self.TABLE_NAME} WHERE age BETWEEN 35 AND 45")
        console.print(f"[green]⚡ With partial index:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        # Test query outside index range (should not use index)
        time3, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE age > 70")
        console.print(f"[blue]📊 Query outside range (age > 70):[/blue] [white]{time3:.4f}s[/white] (won't use partial index)")
        
        self.db.execute_query(f"DROP INDEX idx_users_working_age")

    def run_storage_comparison(self):
        console.print("\n[bold yellow]📊 Test: Storage Comparison (partial vs full index)[/bold yellow]")
        
        # Create full index
        self.db.execute_query(f"CREATE INDEX idx_users_full_city ON {self.TABLE_NAME}(city)")
        full_size = self.db.execute_query("SELECT pg_size_pretty(pg_relation_size('idx_users_full_city'))")
        console.print(f"[red]📊 Full index size:[/red] [white]{full_size[0][0]}[/white]")
        
        # Get list of frequent cities (those having count > 1000)
        frequent_cities = self.db.execute_query(f"""
            SELECT city 
            FROM {self.TABLE_NAME}
            GROUP BY city 
            HAVING COUNT(*) > 1000
        """)
        city_list = [f"'{row[0]}'" for row in frequent_cities]
        city_condition = ", ".join(city_list)

        if not city_list:
            console.print("[yellow]⚠️ No cities found with count > 1000. Skipping partial index creation.[/yellow]")
            return

        # Drop full index and create partial index
        self.db.execute_query(f"DROP INDEX idx_users_full_city")
        self.db.execute_query(f"""
            CREATE INDEX idx_users_partial_city 
            ON {self.TABLE_NAME}(city)
            WHERE city IN ({city_condition})
        """)
        
        partial_size = self.db.execute_query("SELECT pg_size_pretty(pg_relation_size('idx_users_partial_city'))")
        console.print(f"[green]📊 Partial index size:[/green] [white]{partial_size[0][0]}[/white]")
        
        # Show coverage
        total_records = self.db.execute_query(f"SELECT COUNT(*) FROM {self.TABLE_NAME}")[0][0]
        covered_records = self.db.execute_query(f"""
            SELECT COUNT(*) FROM {self.TABLE_NAME} 
            WHERE city IN ({city_condition})
        """)[0][0]
        
        coverage_pct = (covered_records / total_records) * 100
        console.print(f"[cyan]📊 Partial index covers {coverage_pct:.1f}% of records with smaller storage[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_partial_city")

    def cleanup(self):
        self.db.execute_query(f"DROP INDEX IF EXISTS idx_users_recent_age")
        self.db.execute_query(f"DROP INDEX IF EXISTS idx_users_working_age")
        self.db.execute_query(f"DROP INDEX IF EXISTS idx_users_full_city")
        self.db.execute_query(f"DROP INDEX IF EXISTS idx_users_partial_city")
        self.db.execute_query(f"DROP TABLE IF EXISTS {self.TABLE_NAME}")