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
        self.run_select_specific_columns()
        self.run_count_with_where()
        self.run_partial_vs_full_coverage()

    def run_select_specific_columns(self):
        console.print("\n[bold yellow]📊 Test: SELECT Specific Columns (age, first_name)[/bold yellow]")
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT age, first_name FROM {self.TABLE_NAME} WHERE age BETWEEN 25 AND 35 LIMIT 1000")
        console.print(f"[red]⏱️  Without covering index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_age_covering ON {self.TABLE_NAME}(age) INCLUDE (first_name)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT age, first_name FROM {self.TABLE_NAME} WHERE age BETWEEN 25 AND 35 LIMIT 1000")
        console.print(f"[green]⚡ With covering index:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_age_covering")

    def run_count_with_where(self):
        console.print("\n[bold yellow]📊 Test: COUNT with WHERE (covering eliminates table access)[/bold yellow]")
        
        # Get random city for testing
        city_result = self.db.execute_query(f"SELECT city FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_city = city_result[0][0]
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE city = %s", (test_city,))
        console.print(f"[red]⏱️  Without covering index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_city_covering ON {self.TABLE_NAME}(city) INCLUDE (age)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE city = %s", (test_city,))
        console.print(f"[green]⚡ With covering index:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_city_covering")

    def run_partial_vs_full_coverage(self):
        console.print("\n[bold yellow]📊 Test: Partial vs Full Coverage (SELECT age, city, country)[/bold yellow]")
        
        # Get random cities for testing
        cities_result = self.db.execute_query(f"SELECT DISTINCT ON (city) city FROM {self.TABLE_NAME} ORDER BY city, RANDOM() LIMIT 3")
        no_cov_city, partial_cov_city, full_cov_city = [row[0] for row in cities_result]
        
        # Test with no covering index
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT age, city, country FROM {self.TABLE_NAME} WHERE city = %s LIMIT 100", (no_cov_city,))
        console.print(f"[red]⏱️  Without covering index:[/red] [white]{time1:.4f}s[/white]")
        
        # Test with partial coverage (only city in index)
        self.db.execute_query(f"CREATE INDEX idx_users_partial_cover ON {self.TABLE_NAME}(city)")
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT age, city, country FROM {self.TABLE_NAME} WHERE city = %s LIMIT 100", (partial_cov_city,))
        console.print(f"[red]⏱️  Partial coverage (city only):[/red] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        self.db.execute_query(f"DROP INDEX idx_users_partial_cover")
        
        # Test with full coverage
        self.db.execute_query(f"CREATE INDEX idx_users_full_cover ON {self.TABLE_NAME}(city) INCLUDE (age, country)")
        time3, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT age, city, country FROM {self.TABLE_NAME} WHERE city = %s LIMIT 100", (full_cov_city,))
        console.print(f"[green]⚡ Full coverage (all columns):[/green] [white]{time3:.4f}s[/white] | [cyan]Speedup: {time1/time3:.1f}x[/cyan]")
        self.db.execute_query(f"DROP INDEX idx_users_full_cover")