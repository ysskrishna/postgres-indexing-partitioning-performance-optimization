from core.database import DatabaseConnection
from core.benchmark import SimpleBenchmark
from core.base import BaseExecute
from core.logger import console

class Execute(BaseExecute):
    def __init__(self):
        self.db = DatabaseConnection()
        self.benchmark = SimpleBenchmark()
        self.TABLE_USERS = "users"
        self.TABLE_ORDERS = "orders"
    
    def execute(self):
        self.run_join_performance()
        self.run_referential_integrity()
        self.run_fk_index_impact()

    def run_join_performance(self):
        console.print("\n[bold yellow]📊 Test: Join Performance (users with orders)[/bold yellow]")
        
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT u.username, COUNT(o.order_id) FROM {self.TABLE_USERS} u LEFT JOIN {self.TABLE_ORDERS} o ON u.user_id = o.user_id GROUP BY u.user_id, u.username LIMIT 1000")
        console.print(f"[red]⏱️  Without FK index:[/red] [bold]{time1:.4f}s[/bold]")
        
        self.db.execute_query(f"CREATE INDEX idx_user_orders_user_id ON {self.TABLE_ORDERS}(user_id)")
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT u.username, COUNT(o.order_id) FROM {self.TABLE_USERS} u LEFT JOIN {self.TABLE_ORDERS} o ON u.user_id = o.user_id GROUP BY u.user_id, u.username LIMIT 1000")
        console.print(f"[green]⚡ With FK index:[/green] [bold]{time2:.4f}s[/bold] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.execute_query("DROP INDEX idx_user_orders_user_id")

    def run_referential_integrity(self):
        console.print("\n[bold yellow]📊 Test: Referential Integrity (FK constraint)[/bold yellow]")
        
        console.print("[blue]📊 Testing invalid user_id insertion...[/blue]")
        try:
            self.db.execute_query(f"INSERT INTO {self.TABLE_ORDERS} (user_id, amount) VALUES (99999999, 100.00)")
            console.print("[red]❌ Invalid FK allowed (unexpected)[/red]")
        except Exception as e:
            console.print("[green]✅ Invalid FK prevented by constraint[/green]")

    def run_fk_index_impact(self):
        console.print("\n[bold yellow]📊 Test: FK Index Impact (user orders lookup)[/bold yellow]")
        
        # Get random user with orders
        user_result = self.db.execute_query(f"SELECT DISTINCT ON (user_id) user_id FROM {self.TABLE_ORDERS} ORDER BY user_id, RANDOM() LIMIT 1")

        if user_result:
            test_user_id = user_result[0][0]
            
            time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_ORDERS} WHERE user_id = %s", (test_user_id,))
            console.print(f"[red]⏱️  Without FK index:[/red] [bold]{time1:.4f}s[/bold]")
            
            self.db.execute_query(f"CREATE INDEX idx_orders_userid_fk ON {self.TABLE_ORDERS}(user_id)")
            
            time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_ORDERS} WHERE user_id = %s", (test_user_id,))
            console.print(f"[green]⚡ With FK index:[/green] [bold]{time2:.4f}s[/bold] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
            
            self.db.execute_query("DROP INDEX idx_orders_userid_fk")
        else:
            console.print("[yellow]⚠️  No orders found for testing[/yellow]")