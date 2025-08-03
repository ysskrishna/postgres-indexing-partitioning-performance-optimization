from core.database import DatabaseConnection
from core.benchmark import SimpleBenchmark
from core.base import BaseExecute
from core.logger import console
from datetime import datetime, timedelta

class Execute(BaseExecute):
    def __init__(self):
        self.db = DatabaseConnection()
        self.benchmark = SimpleBenchmark()
        self.TABLE_NAME = "users"
    
    def execute(self):
        self.run_partition_pruning()
        self.run_cross_partition_queries()
        self.run_partition_management()

    def run_partition_pruning(self):
        console.print("\n[bold yellow]📊 Test: Partition Pruning (single vs multiple partitions)[/bold yellow]")
        
        # Get date range for single partition
        single_partition_date = self.db.execute_query("SELECT MIN(created_at) FROM users_partitioned")[0][0]
        end_date = single_partition_date + timedelta(days=15)
        
        # Query single partition (should use partition pruning)
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, "SELECT COUNT(*) FROM users_partitioned WHERE created_at BETWEEN %s AND %s", (single_partition_date, end_date))
        console.print(f"[green]⚡ Single partition query:[/green] [bold]{time1:.4f}s[/bold]")
        
        # Query across multiple partitions
        multi_start = self.db.execute_query("SELECT MIN(created_at) FROM users_partitioned")[0][0]
        multi_end = self.db.execute_query("SELECT MAX(created_at) FROM users_partitioned")[0][0]
        
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, "SELECT COUNT(*) FROM users_partitioned WHERE created_at BETWEEN %s AND %s", (multi_start, multi_end))
        console.print(f"[red]⏱️  Multi-partition query:[/red] [bold]{time2:.4f}s[/bold]")
        
        # Compare with non-partitioned table
        time3, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE created_at BETWEEN %s AND %s", (single_partition_date, end_date))
        console.print(f"[blue]📊 Non-partitioned equivalent:[/blue] [bold]{time3:.4f}s[/bold]")
        
        if time1 < time3:
            console.print(f"[cyan]📊 Partitioning benefit: {time3/time1:.1f}x faster for targeted queries[/cyan]")

    def run_cross_partition_queries(self):
        console.print("\n[bold yellow]📊 Test: Cross-partition Performance[/bold yellow]")
        
        # Query that spans all partitions
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, "SELECT COUNT(*), AVG(age) FROM users_partitioned")
        console.print(f"[red]⏱️  Partitioned table (all partitions):[/red] [bold]{time1:.4f}s[/bold]")
        
        # Same query on original table
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*), AVG(age) FROM {self.TABLE_NAME}")
        console.print(f"[blue]📊 Original table:[/blue] [bold]{time2:.4f}s[/bold]")
        
        # Query with WHERE clause that can use pruning
        recent_date = datetime.now() - timedelta(days=90)
        time3, _ = SimpleBenchmark.timed(self.db.execute_query, "SELECT COUNT(*) FROM users_partitioned WHERE created_at > %s", (recent_date,))
        console.print(f"[green]⚡ Partitioned with pruning:[/green] [bold]{time3:.4f}s[/bold]")
        
        time4, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE created_at > %s", (recent_date,))
        console.print(f"[blue]📊 Original with same filter:[/blue] [bold]{time4:.4f}s[/bold]")
        
        console.print(f"[cyan]📊 Partition pruning advantage: {time4/time3:.1f}x faster[/cyan]")

    def run_partition_management(self):
        console.print("\n[bold yellow]📊 Test: Partition Management Operations[/bold yellow]")
        
        # Add a new partition
        console.print("[blue]📊 Adding new partition...[/blue]")
        future_date = datetime.now() + timedelta(days=365)
        future_end = future_date + timedelta(days=30)
        
        add_time, _ = SimpleBenchmark.timed(self.db.execute_query, f"""
            CREATE TABLE users_part_future PARTITION OF users_partitioned
            FOR VALUES FROM ('{future_date}') TO ('{future_end}')
        """)
        console.print(f"[green]⚡ Partition added:[/green] [bold]{add_time:.4f}s[/bold]")
        
        # List all partitions
        partitions = self.db.execute_query("""
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE tablename LIKE 'users_part_%' 
            ORDER BY tablename
        """)
        console.print(f"[blue]📊 Total partitions:[/blue] [bold]{len(partitions)}[/bold]")
        
        # Drop the future partition
        console.print("[blue]📊 Dropping partition...[/blue]")
        drop_time, _ = SimpleBenchmark.timed(self.db.execute_query, "DROP TABLE users_part_future")
        console.print(f"[green]⚡ Partition dropped:[/green] [bold]{drop_time:.4f}s[/bold]")
        
        console.print("[cyan]📊 Partition management operations are very fast[/cyan]")
    
    def cleanup(self):
        self.db.execute_query(f"DROP TABLE IF EXISTS {self.TABLE_NAME}")
        self.db.execute_query(f"DROP TABLE IF EXISTS users_partitioned")
        self.db.execute_query(f"DROP TABLE IF EXISTS users_part_future")
        