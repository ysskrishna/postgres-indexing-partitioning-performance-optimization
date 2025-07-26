import time
from core.database import DatabaseConnection
from datasets.generator import DataGenerator
from core.logger import console

def setup_basic_index_scenario(users: int = 1_000_000):
    """Setup tables and data for basic index demonstrations with 1M users."""    
    db = DatabaseConnection()
    generator = DataGenerator()
    TABLE_NAME = "users"
    
    try:
        # Drop and recreate users table
        db.drop_table_if_exists(TABLE_NAME)
        
        # Create table
        console.print(f"Creating {TABLE_NAME} table...")
        db.execute_query(generator.create_users_table(TABLE_NAME))
        batch_size = 50000
        columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country')

        total_generation_time = 0
        total_insertion_time = 0
        total_batches = 0

        for i in range(0, users, batch_size):
            batch_start = time.time()
            
            # Measure data generation time
            generation_start = time.time()
            users_data = generator.generate_users_data(batch_size, i)
            generation_time = time.time() - generation_start
            total_generation_time += generation_time
            
            # Measure bulk insertion time
            insertion_start = time.time()
            db.bulk_insert_copy(TABLE_NAME, columns, users_data)
            insertion_time = time.time() - insertion_start
            total_insertion_time += insertion_time
            
            total_batches += 1
            batch_time = time.time() - batch_start
            
            console.print(
                f"[bold cyan]Progress:[/bold cyan] [green]{i+batch_size:,}/{users:,}[/green] | "
                f"[bold yellow]Batch:[/bold yellow] {batch_time:.2f}s | "
                f"[bold magenta]Generation:[/bold magenta] {generation_time:.2f}s | "
                f"[bold blue]Insertion:[/bold blue] {insertion_time:.2f}s"
            )
            
        console.print("[yellow]Basic Indexes Scenario setup completed![/yellow]")
        
    except Exception as e:
        console.print(f"Error: Setup failed: {e}")
        raise
