from core.database import DatabaseConnection
from datasets.generator import DataGenerator
from core.benchmark import SimpleBenchmark
from core.logger import console
from core.base import BaseSetup
import datetime

class Setup(BaseSetup):
    def __init__(self):
        self.db = DatabaseConnection()
        self.generator = DataGenerator()
        self.TABLE_NAME = "users"
    
    def setup(self, users: int = 1_000_000):
        """Setup tables and data for all scenarios with 1M users."""
        try:
            self.db.drop_table_if_exists(self.TABLE_NAME)
            
            console.print(f"[bold]📋 Creating {self.TABLE_NAME} table...[/bold]")
            self.db.execute_query(self.generator.create_users_table(self.TABLE_NAME))
            batch_size = 50000
            columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country', 'created_at')

            for i in range(0, users, batch_size):
                generation_time, users_data = SimpleBenchmark.timed(self.generator.generate_users_data, batch_size, i)
                insertion_time, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, self.TABLE_NAME, columns, users_data)
                
                console.print(
                    f"📊 Progress: {i+batch_size:,}/{users:,} | "
                    f"⚙️  Generation: [white]{generation_time:.2f}s[/white] | "
                    f"💾 Insertion: [white]{insertion_time:.2f}s[/white]"
                )
            
            # Setup range partitioning
            console.print(f"[bold]🔧 Setting up range partitioning...[/bold]")
            self._setup_range_partitioning()
                
        except Exception as e:
            console.print(f"[bold red]❌ Error: Setup failed: {e}[/bold red]")
            raise

    def _setup_range_partitioning(self):
        """Create partitioned table by created_at ranges with monthly partitions."""
        try:
            # Drop existing partitioned table if it exists
            self.db.execute_query("DROP TABLE IF EXISTS users_partitioned CASCADE")
            
            # Create partitioned table
            self.db.execute_query("""
                CREATE TABLE users_partitioned (
                    user_id INT,
                    username VARCHAR,
                    email VARCHAR,
                    first_name VARCHAR,
                    last_name VARCHAR,
                    age INTEGER,
                    city VARCHAR,
                    country VARCHAR,
                    created_at TIMESTAMP
                ) PARTITION BY RANGE (created_at)
            """)

            # Get date range from existing data
            date_range = self.db.execute_query("SELECT MIN(created_at), MAX(created_at) FROM users")
            start_date, end_date = date_range[0]

            # Create monthly partitions covering the entire date range
            current_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            partition_count = 0
            while current_date <= end_date:
                next_date = (current_date + datetime.timedelta(days=32)).replace(day=1)
                partition_name = f"users_part_{current_date.strftime('%Y_%m')}"
                
                self.db.execute_query(f"""
                    CREATE TABLE {partition_name} PARTITION OF users_partitioned
                    FOR VALUES FROM ('{current_date}') TO ('{next_date}')
                """)
                current_date = next_date
                partition_count += 1

            console.print(f"[bold]📊 Created {partition_count} monthly partitions[/bold]")

            # Insert data into partitioned table
            console.print(f"[bold]📥 Copying data to partitioned table...[/bold]")
            self.db.execute_query("INSERT INTO users_partitioned SELECT * FROM users")
            
            console.print(f"[bold green]✅ Range partitioning setup completed![/bold green]")
            
        except Exception as e:
            console.print(f"[bold red]❌ Error: Range partitioning setup failed: {e}[/bold red]")
            raise
