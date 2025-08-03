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
        self.run_duplicate_prevention()
        self.run_lookup_performance()

    def run_duplicate_prevention(self):
        console.print("\n[bold yellow]📊 Test: Duplicate Prevention (email uniqueness)[/bold yellow]")
        
        # Get existing email
        email_result = self.db.execute_query(f"SELECT email FROM {self.TABLE_NAME} LIMIT 1")
        existing_email = email_result[0][0]
        
        console.print(f"[blue]📊 Testing duplicate email insertion...[/blue]")
        try:
            self.db.execute_query(f"INSERT INTO {self.TABLE_NAME} (username, email, first_name) VALUES ('test_user', %s, 'Test')", (existing_email,))
            console.print(f"[red]❌ Duplicate allowed (unexpected)[/red]")
        except Exception as e:
            console.print(f"[green]✅ Duplicate prevented by unique constraint[/green]")

    def run_lookup_performance(self):
        console.print("\n[bold yellow]📊 Test: Lookup Performance (unique vs non-unique index)[/bold yellow]")
        
        # Get random email for testing
        email_result = self.db.execute_query(f"SELECT email FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_email = email_result[0][0]
        
        # Test with existing unique index on email
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT user_id, first_name FROM {self.TABLE_NAME} WHERE email = %s", (test_email,))
        console.print(f"[green]⚡ Unique index lookup:[/green] [white]{time1:.4f}s[/white]")
        
        # Test non-unique index performance on city
        city_result = self.db.execute_query(f"SELECT city FROM {self.TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
        test_city = city_result[0][0]
        
        self.db.execute_query(f"CREATE INDEX idx_users_city_nonunique ON {self.TABLE_NAME}(city)")
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT user_id, first_name FROM {self.TABLE_NAME} WHERE city = %s LIMIT 1", (test_city,))
        console.print(f"[blue]📊 Non-unique index lookup:[/blue] [white]{time2:.4f}s[/white]")
        
        self.db.execute_query(f"DROP INDEX idx_users_city_nonunique")