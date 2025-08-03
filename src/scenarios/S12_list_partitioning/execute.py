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
        self.run_country_specific_queries()
        self.run_multi_country_queries()
        self.run_default_partition()

    def run_country_specific_queries(self):
        console.print("\n[bold yellow]📊 Test: Country-specific Queries (partition pruning)[/bold yellow]")
        
        # Get a country that has its own partition
        top_country = self.db.execute_query("""
            SELECT country FROM users_by_country 
            WHERE country IN (
                SELECT country FROM users 
                GROUP BY country 
                ORDER BY COUNT(*) DESC 
                LIMIT 1
            ) LIMIT 1
        """)[0][0]
        
        # Query partitioned table (should use single partition)
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, "SELECT COUNT(*), AVG(age) FROM users_by_country WHERE country = %s", (top_country,))
        console.print(f"[green]⚡ Partitioned table query:[/green] [white]{time1:.4f}s[/white]")
        
        # Query original table for comparison
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT COUNT(*), AVG(age) FROM {self.TABLE_NAME} WHERE country = %s", (top_country,))
        console.print(f"[blue]📊 Original table query:[/blue] [white]{time2:.4f}s[/white]")
        
        # Show partition pruning benefit
        if time2 > time1:
            console.print(f"[cyan]📊 List partitioning benefit: {time2/time1:.1f}x faster[/cyan]")
        else:
            console.print(f"[cyan]📊 Performance similar (small dataset or good indexing)[/cyan]")

    def run_multi_country_queries(self):
        console.print("\n[bold yellow]📊 Test: Multi-country Queries (cross-partition)[/bold yellow]")
        
        # Get top 3 countries
        top_countries = self.db.execute_query("""
            SELECT country FROM users 
            GROUP BY country 
            ORDER BY COUNT(*) DESC 
            LIMIT 3
        """)
        country_list = [row[0] for row in top_countries]
        
        # Query across multiple partitions
        placeholders = ', '.join(['%s'] * len(country_list))
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT country, COUNT(*) FROM users_by_country WHERE country IN ({placeholders}) GROUP BY country", country_list)
        console.print(f"[red]⏱️  Partitioned (multiple partitions):[/red] [white]{time1:.4f}s[/white]")
        
        # Same query on original table
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT country, COUNT(*) FROM {self.TABLE_NAME} WHERE country IN ({placeholders}) GROUP BY country", country_list)
        console.print(f"[blue]📊 Original table:[/blue] [white]{time2:.4f}s[/white]")
        
        # Query all countries (hits all partitions)
        time3, _ = SimpleBenchmark.timed(self.db.execute_query, "SELECT COUNT(DISTINCT country) FROM users_by_country")
        console.print(f"[yellow]⚙️  All partitions query:[/yellow] [white]{time3:.4f}s[/white]")

    def run_default_partition(self):
        console.print("\n[bold yellow]📊 Test: Default Partition Behavior[/bold yellow]")
        
        # Insert a record with a new country (should go to default partition)
        console.print("[blue]📊 Testing default partition with new country...[/blue]")
        
        try:
            # Insert test record with new country
            self.db.execute_query("""
                INSERT INTO users_by_country (username, email, first_name, last_name, age, city, country, created_at)
                VALUES ('test_user_unique_country', 'test@newcountry.com', 'Test', 'User', 25, 'Test City', 'TestCountryUnique', NOW())
            """)
            
            # Query the default partition to see if it contains our record
            default_count = self.db.execute_query("SELECT COUNT(*) FROM users_country_default WHERE country = 'TestCountryUnique'")
            
            if default_count[0][0] > 0:
                console.print("[green]✅ New country routed to default partition[/green]")
            else:
                console.print("[yellow]⚠️  Record may be in named partition[/yellow]")
            
            # Show countries in default partition
            default_countries = self.db.execute_query("SELECT DISTINCT country FROM users_country_default LIMIT 5")
            country_names = [row[0] for row in default_countries]
            console.print(f"[blue]📊 Sample countries in default:[/blue] {', '.join(country_names[:3])}...")
            
            # Clean up test record
            self.db.execute_query("DELETE FROM users_by_country WHERE username = 'test_user_unique_country'")
            
        except Exception as e:
            console.print(f"[red]❌ Error testing default partition: {str(e)[:50]}...[/red]")
        
        # Show total records in default vs named partitions
        default_total = self.db.execute_query("SELECT COUNT(*) FROM users_country_default")[0][0]
        total_records = self.db.execute_query("SELECT COUNT(*) FROM users_by_country")[0][0]
        
        console.print(f"[cyan]📊 Default partition: {default_total:,} records ({(default_total/total_records)*100:.1f}%)[/cyan]")
    
    def cleanup(self):
        self.db.execute_query(f"DROP TABLE IF EXISTS {self.TABLE_NAME}")
        self.db.execute_query(f"DROP TABLE IF EXISTS users_by_country")
        self.db.execute_query(f"DROP TABLE IF EXISTS users_country_default")