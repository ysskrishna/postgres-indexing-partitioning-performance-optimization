from core.database import DatabaseConnection
from datasets.generator import DataGenerator
from core.benchmark import SimpleBenchmark
from core.logger import console
from core.base import BaseSetup

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
            
            # Create materialized views for common aggregations
            console.print(f"[bold]📋 Creating materialized views...[/bold]")
            
            self.db.execute_query("DROP MATERIALIZED VIEW IF EXISTS user_country_stats")
            self.db.execute_query("DROP MATERIALIZED VIEW IF EXISTS user_age_distribution")

            self.db.execute_query("""
                CREATE MATERIALIZED VIEW user_country_stats AS
                SELECT 
                    country, 
                    COUNT(*) as user_count, 
                    AVG(age) as avg_age,
                    MIN(created_at) as first_user,
                    MAX(created_at) as latest_user
                FROM users 
                GROUP BY country
            """)

            self.db.execute_query("""
                CREATE MATERIALIZED VIEW user_age_distribution AS
                SELECT 
                    (age / 10) * 10 as age_group,
                    COUNT(*) as user_count,
                    AVG(EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400) as avg_days_old
                FROM users 
                GROUP BY (age / 10) * 10
                ORDER BY age_group
            """)

            # Create indexes on materialized views
            self.db.execute_query("CREATE INDEX idx_mv_country ON user_country_stats(country)")
            self.db.execute_query("CREATE INDEX idx_mv_age_group ON user_age_distribution(age_group)")
            
            console.print(f"[bold green]✅ Materialized views created successfully![/bold green]")
            
        except Exception as e:
            console.print(f"[bold red]❌ Error: Setup failed: {e}[/bold red]")
            raise
