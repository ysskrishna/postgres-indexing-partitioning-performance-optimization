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
        self.run_aggregation_performance()
        self.run_refresh_strategies()
        self.run_staleness_vs_performance()

    def run_aggregation_performance(self):
        console.print("\n[bold yellow]📊 Test: Aggregation Performance (MV vs live query)[/bold yellow]")
        
        # Query materialized view
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, "SELECT country, user_count, avg_age FROM user_country_stats ORDER BY user_count DESC LIMIT 10")
        console.print(f"[green]⚡ Materialized view query:[/green] [white]{time1:.4f}s[/white]")
        
        # Same query on live data
        time2, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT country, COUNT(*) as user_count, AVG(age) as avg_age FROM {self.TABLE_NAME} GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10")
        console.print(f"[red]⏱️  Live aggregation query:[/red] [white]{time2:.4f}s[/white]")
        
        console.print(f"[cyan]📊 Materialized view speedup: {time2/time1:.1f}x faster[/cyan]")
        
        # Test age distribution queries
        console.print("\n[blue]📊 Age Distribution Comparison:[/blue]")
        
        # MV query
        time3, _ = SimpleBenchmark.timed(self.db.execute_query, "SELECT age_group, user_count FROM user_age_distribution WHERE age_group BETWEEN 20 AND 60")
        console.print(f"[green]⚡ MV age distribution:[/green] [white]{time3:.4f}s[/white]")
        
        # Live query
        time4, _ = SimpleBenchmark.timed(self.db.execute_query, f"SELECT (age / 10) * 10 as age_group, COUNT(*) FROM {self.TABLE_NAME} WHERE age BETWEEN 20 AND 60 GROUP BY (age / 10) * 10")
        console.print(f"[red]⏱️  Live age distribution:[/red] [white]{time4:.4f}s[/white]")
        
        console.print(f"[cyan]📊 Age MV speedup: {time4/time3:.1f}x faster[/cyan]")

    def run_refresh_strategies(self):
        console.print("\n[bold yellow]📊 Test: Refresh Strategies (REFRESH vs CONCURRENTLY)[/bold yellow]")
        
        # Test regular REFRESH
        console.print("[blue]📊 Testing regular REFRESH (blocks access)...[/blue]")
        time1, _ = SimpleBenchmark.timed(self.db.execute_query, "REFRESH MATERIALIZED VIEW user_country_stats")
        console.print(f"[red]⏱️  Regular REFRESH:[/red] [white]{time1:.4f}s[/white] (blocks access)")
        
        # Test CONCURRENT REFRESH (requires unique index)
        console.print("[blue]📊 Testing REFRESH CONCURRENTLY (non-blocking)...[/blue]")
        
        # First create unique index required for concurrent refresh
        try:
            self.db.execute_query("CREATE UNIQUE INDEX idx_mv_country_unique ON user_country_stats(country)")
            
            time2, _ = SimpleBenchmark.timed(self.db.execute_query, "REFRESH MATERIALIZED VIEW CONCURRENTLY user_country_stats")
            console.print(f"[green]⚡ Concurrent REFRESH:[/green] [white]{time2:.4f}s[/white] (allows access)")
            
            if time2 > time1:
                console.print(f"[cyan]📊 Concurrent refresh is {time2/time1:.1f}x slower but non-blocking[/cyan]")
            
            self.db.execute_query("DROP INDEX idx_mv_country_unique")
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Concurrent refresh failed: {str(e)[:50]}...[/yellow]")
            console.print("[yellow]⚠️  Concurrent refresh requires unique index[/yellow]")
        
        # Show refresh impact on MV size
        mv_size = self.db.execute_query("SELECT pg_size_pretty(pg_total_relation_size('user_country_stats'))")
        console.print(f"[blue]📊 MV storage size:[/blue] [white]{mv_size[0][0]}[/white]")

    def run_staleness_vs_performance(self):
        console.print("\n[bold yellow]📊 Test: Staleness vs Performance Trade-offs[/bold yellow]")
        
        # Show current MV data timestamp
        mv_data = self.db.execute_query("SELECT COUNT(*), MAX(latest_user) FROM user_country_stats")
        mv_count, mv_latest = mv_data[0]
        console.print(f"[blue]📊 MV shows {mv_count} countries, latest user: {mv_latest}[/blue]")
        
        # Insert new test data to create staleness
        console.print("[blue]📊 Inserting new data to demonstrate staleness...[/blue]")
        
        try:
            # Insert test record
            self.db.execute_query(f"""
                INSERT INTO {self.TABLE_NAME} (username, email, first_name, last_name, age, city, country, created_at)
                VALUES ('test_mv_user', 'mv_test@example.com', 'MV', 'Test', 30, 'Test City', 'NewCountryMV', NOW())
            """)
            
            # Check if MV reflects new data (it shouldn't until refresh)
            mv_new_check = self.db.execute_query("SELECT user_count FROM user_country_stats WHERE country = 'NewCountryMV'")
            live_new_check = self.db.execute_query(f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE country = 'NewCountryMV'")
            
            console.print(f"[red]⏱️  MV shows new country:[/red] [bold]{len(mv_new_check)} records[/bold]")
            console.print(f"[green]⚡ Live query shows:[/green] [bold]{live_new_check[0][0]} records[/bold]")
            
            if len(mv_new_check) == 0 and live_new_check[0][0] > 0:
                console.print("[cyan]📊 MV is stale - shows old data for performance[/cyan]")
            
            # Refresh to bring MV up to date
            console.print("[blue]📊 Refreshing MV to update data...[/blue]")
            refresh_time, _ = SimpleBenchmark.timed(self.db.execute_query, "REFRESH MATERIALIZED VIEW user_country_stats")
            console.print(f"[yellow]⚙️  Refresh time:[/yellow] [white]{refresh_time:.4f}s[/white]")
            
            # Check again after refresh
            mv_after_refresh = self.db.execute_query("SELECT user_count FROM user_country_stats WHERE country = 'NewCountryMV'")
            if len(mv_after_refresh) > 0:
                console.print(f"[green]✅ After refresh, MV shows: {mv_after_refresh[0][0]} records[/green]")
            
            # Clean up test data
            self.db.execute_query(f"DELETE FROM {self.TABLE_NAME} WHERE username = 'test_mv_user'")
            self.db.execute_query("REFRESH MATERIALIZED VIEW user_country_stats")
            
        except Exception as e:
            console.print(f"[red]❌ Error testing staleness: {str(e)[:50]}...[/red]")
        
        # Performance vs freshness summary
        console.print("[cyan]📊 Trade-off: MVs provide fast queries but may show stale data[/cyan]")
        console.print("[cyan]📊 Refresh frequency determines data freshness vs system load[/cyan]")
    
    def cleanup(self):
        self.db.execute_query(f"DROP INDEX IF EXISTS idx_mv_country_unique")
        self.db.execute_query(f"DROP MATERIALIZED VIEW IF EXISTS user_country_stats")
        self.db.execute_query(f"DROP MATERIALIZED VIEW IF EXISTS user_age_distribution")
        self.db.execute_query(f"DROP TABLE IF EXISTS {self.TABLE_NAME}")
        