from core.database import DatabaseConnection
from datasets.generator import DataGenerator
from core.benchmark import SimpleBenchmark
from core.logger import console
from core.base import BaseSetup

class S01Setup(BaseSetup):
    def __init__(self):
        self.db = DatabaseConnection()
        self.generator = DataGenerator()
        self.TABLE_NAME = "users"
    
    def setup(self, users: int = 1_000_000):
        """Setup tables and data for basic index demonstrations with 1M users."""
        try:
            self.db.drop_table_if_exists(self.TABLE_NAME)
            
            console.print(f"Creating {self.TABLE_NAME} table...")
            self.db.execute_query(self.generator.create_users_table(self.TABLE_NAME))
            batch_size = 50000
            columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country', 'created_at')

            for i in range(0, users, batch_size):
                generation_time, users_data = SimpleBenchmark.timed(self.generator.generate_users_data, batch_size, i)
                insertion_time, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, self.TABLE_NAME, columns, users_data)
                
                console.print(
                    f"[bold cyan]Progress:[/bold cyan] [green]{i+batch_size:,}/{users:,}[/green] | "
                    f"[bold magenta]Generation:[/bold magenta] {generation_time:.2f}s | "
                    f"[bold blue]Insertion:[/bold blue] {insertion_time:.2f}s"
                )
                
            console.print("[yellow]Basic Indexes Scenario setup completed![/yellow]")
            
        except Exception as e:
            console.print(f"Error: Setup failed: {e}")
            raise
