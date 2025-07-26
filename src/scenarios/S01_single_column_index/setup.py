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
            
            console.print(f"[bold green]📋 Creating {self.TABLE_NAME} table...[/bold green]")
            self.db.execute_query(self.generator.create_users_table(self.TABLE_NAME))
            batch_size = 50000
            columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country', 'created_at')

            for i in range(0, users, batch_size):
                generation_time, users_data = SimpleBenchmark.timed(self.generator.generate_users_data, batch_size, i)
                insertion_time, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, self.TABLE_NAME, columns, users_data)
                
                console.print(
                    f"[bold cyan]📊 Progress:[/bold cyan] [green]{i+batch_size:,}[/green]/[bold]{users:,}[/bold] | "
                    f"[bold magenta]⚙️  Generation:[/bold magenta] [yellow]{generation_time:.2f}s[/yellow] | "
                    f"[bold blue]💾 Insertion:[/bold blue] [yellow]{insertion_time:.2f}s[/yellow]"
                )
                
            console.print("[bold green]✅ Basic Indexes Scenario setup completed![/bold green]")
            
        except Exception as e:
            console.print(f"[bold red]❌ Error: Setup failed: {e}[/bold red]")
            raise
