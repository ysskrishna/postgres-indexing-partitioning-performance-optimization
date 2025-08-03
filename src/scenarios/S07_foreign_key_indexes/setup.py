from core.database import DatabaseConnection
from datasets.generator import DataGenerator
from core.benchmark import SimpleBenchmark
from core.logger import console
from core.base import BaseSetup

class Setup(BaseSetup):
    def __init__(self):
        self.db = DatabaseConnection()
        self.generator = DataGenerator()
        self.TABLE_USERS = "users"
        self.TABLE_ORDERS = "orders"
    
    def setup(self, users: int = 500_000, orders: int = 2_500_000):
        """Setup tables and data for foreign key index demonstrations with 1M users and 5M orders."""
        try:
            self.db.drop_table_if_exists(self.TABLE_USERS)
            self.db.drop_table_if_exists(self.TABLE_ORDERS)
            
            # Create users table and populate
            console.print(f"[bold]📋 Creating {self.TABLE_USERS} table...[/bold]")
            self.db.execute_query(self.generator.create_users_table(self.TABLE_USERS))
            batch_size = 50000
            columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country', 'created_at')

            for i in range(0, users, batch_size):
                generation_time, users_data = SimpleBenchmark.timed(self.generator.generate_users_data, batch_size, i)
                insertion_time, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, self.TABLE_USERS, columns, users_data)
                
                console.print(
                    f"📊 Progress: {i+batch_size:,}/{users:,} | "
                    f"⚙️  Generation: [white]{generation_time:.2f}s[/white] | "
                    f"💾 Insertion: [white]{insertion_time:.2f}s[/white]"
                )
            
            # Create orders table and populate
            console.print(f"[bold]📋 Creating {self.TABLE_ORDERS} table...[/bold]")
            self.db.execute_query(self.generator.create_orders_table(self.TABLE_ORDERS))
            orders_columns = ('user_id', 'order_date', 'total_amount')
            
            for i in range(0, orders, batch_size):
                generation_time, orders_data = SimpleBenchmark.timed(self.generator.generate_orders_data, batch_size, users, i)
                insertion_time, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, self.TABLE_ORDERS, orders_columns, orders_data)
                
                console.print(
                    f"📊 Orders Progress: {i+batch_size:,}/{orders:,} | "
                    f"⚙️  Generation: [white]{generation_time:.2f}s[/white] | "
                    f"💾 Insertion: [white]{insertion_time:.2f}s[/white]"
                )
            
        except Exception as e:
            console.print(f"[bold red]❌ Error: Setup failed: {e}[/bold red]")
            raise
