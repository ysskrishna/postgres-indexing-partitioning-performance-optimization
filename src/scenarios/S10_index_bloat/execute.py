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
        self.run_bloat_measurement()
        self.run_performance_degradation()
        self.run_reindex_benefits()

    def run_bloat_measurement(self):
        console.print("\n[bold yellow]📊 Test: Bloat Measurement (index size analysis)[/bold yellow]")
        
        # Create index and measure initial size
        self.db.execute_query(f"CREATE INDEX idx_users_bloat_test ON {self.TABLE_NAME}(age)")
        
        initial_size = self.db.execute_query("SELECT pg_size_pretty(pg_relation_size('idx_users_bloat_test'))")
        console.print(f"[blue]📊 Initial index size:[/blue] [white]{initial_size[0][0]}[/white]")
        
        # Simulate bloat with updates
        console.print("[blue]📊 Simulating bloat with updates...[/blue]")
        update_count = 50000
        for i in range(0, update_count, 10000):
            self.db.execute_query(f"UPDATE {self.TABLE_NAME} SET age = age + 1 WHERE user_id BETWEEN %s AND %s", (i + 1, i + 10000))
            console.print(f"[yellow]⚙️  Updated {i + 10000:,} records...[/yellow]")
        
        bloated_size = self.db.execute_query("SELECT pg_size_pretty(pg_relation_size('idx_users_bloat_test'))")
        console.print(f"[red]📊 Bloated index size:[/red] [white]{bloated_size[0][0]}[/white]")
        
        # Calculate bloat percentage estimate
        console.print("[cyan]📊 Index bloat created through updates[/cyan]")
        
        self.db.execute_query("DROP INDEX idx_users_bloat_test")

    def run_performance_degradation(self):
        console.print("\n[bold yellow]📊 Test: Performance Degradation (fresh vs bloated)[/bold yellow]")
        
        # Create fresh index and test performance
        self.db.execute_query(f"CREATE INDEX idx_users_perf_test ON {self.TABLE_NAME}(city)")
        
        # Get random city for testing
        city_result = self.db.execute_query(f"SELECT city FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_city = city_result[0][0]
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE city = %s", (test_city,))
        console.print(f"[green]⚡ Fresh index performance:[/green] [white]{time1:.4f}s[/white]")
        
        # Create bloat by updating many records
        console.print("[blue]📊 Creating index bloat...[/blue]")
        self.db.execute_query(f"UPDATE {self.TABLE_NAME} SET city = city || '' WHERE user_id % 5 = 0")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE city = %s", (test_city,))
        console.print(f"[red]⏱️  Bloated index performance:[/red] [white]{time2:.4f}s[/white]")
        
        if time2 > time1:
            console.print(f"[cyan]📊 Performance degraded by {((time2-time1)/time1)*100:.1f}%[/cyan]")
        else:
            console.print(f"[cyan]📊 No significant degradation detected[/cyan]")
        
        self.db.execute_query("DROP INDEX idx_users_perf_test")

    def run_reindex_benefits(self):
        console.print("\n[bold yellow]📊 Test: Reindex Benefits (before/after reindex)[/bold yellow]")
        
        # Create index and bloat it
        self.db.execute_query(f"CREATE INDEX idx_users_reindex_test ON {self.TABLE_NAME}(first_name)")
        
        # Create some bloat
        self.db.execute_query(f"UPDATE {self.TABLE_NAME} SET first_name = first_name || '' WHERE user_id % 3 = 0")
        
        # Test performance before reindex
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE first_name LIKE 'J%'")
        console.print(f"[red]⏱️  Before reindex:[/red] [white]{time1:.4f}s[/white]")
        
        # Reindex
        console.print("[blue]📊 Performing REINDEX...[/blue]")
        reindex_time, _ = SimpleBenchmark.timed(self.db.execute_query, "REINDEX INDEX idx_users_reindex_test")
        console.print(f"[yellow]⚙️  Reindex time:[/yellow] [white]{reindex_time:.4f}s[/white]")
        
        # Test performance after reindex
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE first_name LIKE 'J%'")
        console.print(f"[green]⚡ After reindex:[/green] [white]{time2:.4f}s[/white] | [cyan]Improvement: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query("DROP INDEX idx_users_reindex_test")