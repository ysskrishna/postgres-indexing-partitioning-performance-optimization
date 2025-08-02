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
                generation_time, users_data = SimpleBenchmark.timed(self.generator.generate_users_data_list_partitioning_country, batch_size, i)
                insertion_time, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, self.TABLE_NAME, columns, users_data)
                
                console.print(
                    f"📊 Progress: {i+batch_size:,}/{users:,} | "
                    f"⚙️  Generation: [white]{generation_time:.2f}s[/white] | "
                    f"💾 Insertion: [white]{insertion_time:.2f}s[/white]"
                )
            
            # Setup list partitioning
            console.print(f"[bold]🔧 Setting up list partitioning...[/bold]")
            self._setup_list_partitioning()
                
        except Exception as e:
            console.print(f"[bold red]❌ Error: Setup failed: {e}[/bold red]")
            raise

    def _setup_list_partitioning(self):
        """Create partitioned table by country with list partitioning."""
        try:
            # Drop existing partitioned table if it exists
            self.db.execute_query("DROP TABLE IF EXISTS users_by_country CASCADE")
            
            # Create partitioned table
            self.db.execute_query("""
                CREATE TABLE users_by_country (
                    user_id INT,
                    username VARCHAR,
                    email VARCHAR,
                    first_name VARCHAR,
                    last_name VARCHAR,
                    age INTEGER,
                    city VARCHAR,
                    country VARCHAR,
                    created_at TIMESTAMP
                ) PARTITION BY LIST (country)
            """)

            # Get top countries from existing data
            console.print(f"[bold]🌍 Analyzing country distribution...[/bold]")
            top_countries = self.db.execute_query("""
                SELECT country, COUNT(*) 
                FROM users 
                GROUP BY country 
                ORDER BY COUNT(*) DESC 
                LIMIT 10
            """)

            # Create partitions for top countries
            partition_count = 0
            for country_row in top_countries:
                country = country_row[0]
                count = country_row[1]
                safe_name = country.replace(' ', '_').replace('-', '_').replace('.', '').lower()[:20]
                
                self.db.execute_query(f"""
                    CREATE TABLE users_country_{safe_name} PARTITION OF users_by_country
                    FOR VALUES IN ('{country}')
                """)
                partition_count += 1
                console.print(f"📊 Created partition for {country}: {count:,} users")

            # Create default partition for other countries
            self.db.execute_query("""
                CREATE TABLE users_country_default PARTITION OF users_by_country DEFAULT
            """)
            partition_count += 1

            console.print(f"[bold]📊 Created {partition_count} partitions (10 country-specific + 1 default)[/bold]")

            # Insert data into partitioned table
            console.print(f"[bold]📥 Copying data to partitioned table...[/bold]")
            self.db.execute_query("INSERT INTO users_by_country SELECT * FROM users")
            
            console.print(f"[bold green]✅ List partitioning setup completed![/bold green]")
            
        except Exception as e:
            console.print(f"[bold red]❌ Error: List partitioning setup failed: {e}[/bold red]")
            raise
