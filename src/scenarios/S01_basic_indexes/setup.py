from core.database import DatabaseConnection
from datasets.generator import DataGenerator
from core.benchmark import SimpleBenchmark
from core.logger import console

def setup_basic_index_scenario(users: int = 1_000_000):
    """Setup tables and data for basic index demonstrations with 1M users."""    
    db = DatabaseConnection()
    generator = DataGenerator()
    TABLE_NAME = "users"
    
    try:
        db.drop_table_if_exists(TABLE_NAME)
        
        console.print(f"Creating {TABLE_NAME} table...")
        db.execute_query(generator.create_users_table(TABLE_NAME))
        batch_size = 50000
        columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country')

        for i in range(0, users, batch_size):            
            users_data, generation_time = SimpleBenchmark.timed(generator.generate_users_data, batch_size, i)
            insertion_time, _ = SimpleBenchmark.timed(db.bulk_insert_copy, TABLE_NAME, columns, users_data)
            
            console.print(
                f"[bold cyan]Progress:[/bold cyan] [green]{i+batch_size:,}/{users:,}[/green] | "
                f"[bold magenta]Generation:[/bold magenta] {generation_time:.2f}s | "
                f"[bold blue]Insertion:[/bold blue] {insertion_time:.2f}s"
            )
            
        console.print("[yellow]Basic Indexes Scenario setup completed![/yellow]")
        
    except Exception as e:
        console.print(f"Error: Setup failed: {e}")
        raise
