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
        self.run_multi_column_where()
        self.run_ordering_with_where()
        self.run_column_order_impact()
        self.run_pagination_performance()

    def run_multi_column_where(self):
        console.print("\n[bold yellow]📊 Test: Multi-column WHERE (age + city)[/bold yellow]")
        
        # Get random age and city from existing data
        sample = self.db.execute_query(f"SELECT age, city FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_age, test_city = sample[0]
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE age = %s AND city = %s", (test_age, test_city))
        console.print(f"[red]⏱️  Without composite index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_age_city ON {self.TABLE_NAME}(age, city)")
        
        # Get random age and city from existing data
        sample = self.db.execute_query(f"SELECT age, city FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_age, test_city = sample[0]
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE age = %s AND city = %s", (test_age, test_city))
        console.print(f"[green]⚡ With composite index:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_age_city")

    def run_ordering_with_where(self):
        console.print("\n[bold yellow]📊 Test: ORDER BY with WHERE (country filter + age sort)[/bold yellow]")
        
        # Get random country from existing data
        country_result = self.db.execute_query(f"SELECT country FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_country = country_result[0][0]
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT user_id, age FROM {self.TABLE_NAME} WHERE country = %s ORDER BY age LIMIT 100", (test_country,))
        console.print(f"[red]⏱️  Without composite index:[/red] [white]{time1:.4f}s[/white]")
        
        self.db.execute_query(f"CREATE INDEX idx_users_country_age ON {self.TABLE_NAME}(country, age)")
        
        # Get random country from existing data
        country_result = self.db.execute_query(f"SELECT country FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_country = country_result[0][0]
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT user_id, age FROM {self.TABLE_NAME} WHERE country = %s ORDER BY age LIMIT 100", (test_country,))
        console.print(f"[green]⚡ With composite index:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query(f"DROP INDEX idx_users_country_age")

    def run_column_order_impact(self):
        console.print("\n[bold yellow]📊 Test: Column Order Impact (city,age vs age,city)[/bold yellow]")
        
        # Get random values
        sample = self.db.execute_query(f"SELECT age, city FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_age, test_city = sample[0]
        
        # Test with city first
        self.db.execute_query(f"CREATE INDEX idx_city_age ON {self.TABLE_NAME}(city, age)")
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE city = %s AND age = %s", (test_city, test_age))
        console.print(f"[blue]📊 Index (city,age):[/blue] [white]{time1:.4f}s[/white]")
        self.db.execute_query(f"DROP INDEX idx_city_age")
        
        # Test with age first  
        self.db.execute_query(f"CREATE INDEX idx_age_city ON {self.TABLE_NAME}(age, city)")
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE city = %s AND age = %s", (test_city, test_age))
        console.print(f"[blue]📊 Index (age,city):[/blue] [white]{time2:.4f}s[/white]")
        self.db.execute_query(f"DROP INDEX idx_age_city")

    def run_pagination_performance(self):
        console.print("\n[bold yellow]📊 Test: Pagination Performance (ORDER BY + OFFSET/LIMIT)[/bold yellow]")
        
        # Get total count to calculate meaningful offsets
        total_count = self.db.execute_query(f"SELECT COUNT(*) FROM {self.TABLE_NAME}")[0][0]
        
        # Test different pagination scenarios
        offsets = [0, total_count // 4, total_count // 2, total_count - 100]
        
        for offset in offsets:
            if offset < 0:
                continue
                
            console.print(f"\n[dim]🔍 Testing offset {offset:,} (page {offset//50 + 1})[/dim]")
            
            # Without index - needs to sort entire dataset before applying OFFSET
            time1, _ = SimpleBenchmark.timed(
                self.db.execute_query, 
                f"SELECT user_id, age, email FROM {self.TABLE_NAME} ORDER BY age, user_id OFFSET %s LIMIT 50", 
                (offset,)
            )
            console.print(f"[red]⏱️  Without composite index:[/red] [white]{time1:.4f}s[/white]")
            
            # With composite index - can seek directly to the right position
            self.db.execute_query(f"CREATE INDEX idx_users_age_userid ON {self.TABLE_NAME}(age, user_id)")
            
            time2, _ = SimpleBenchmark.timed(
                self.db.execute_query, 
                f"SELECT user_id, age, email FROM {self.TABLE_NAME} ORDER BY age, user_id OFFSET %s LIMIT 50", 
                (offset,)
            )
            console.print(f"[green]⚡ With composite index:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
            
            self.db.execute_query(f"DROP INDEX idx_users_age_userid")