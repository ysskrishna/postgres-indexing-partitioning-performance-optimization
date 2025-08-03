from core.database import DatabaseConnection
from core.benchmark import SimpleBenchmark
from core.base import BaseExecute
from core.logger import console
from datasets.generator import DataGenerator

class Execute(BaseExecute):
    def __init__(self):
        self.db = DatabaseConnection()
        self.benchmark = SimpleBenchmark()
        self.generator = DataGenerator()
        self.TABLE_NAME = "users"
    
    def execute(self):
        self.run_copy_vs_insert()
        self.run_index_timing()
        self.run_batch_size_optimization()
        

    def _bulk_insert_method(self, table_name, columns, data):
        """Helper method to test regular INSERT with executemany."""
        placeholders = ','.join(['%s'] * len(columns))
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        self.db.execute_many(query, data)

    def run_copy_vs_insert(self):
        console.print("\n[bold yellow]📊 Test: COPY vs INSERT (20k records)[/bold yellow]")
        
        INSERT_TABLE = f"{self.TABLE_NAME}_insert"
        COPY_TABLE = f"{self.TABLE_NAME}_copy"
        
        self.db.drop_table_if_exists(INSERT_TABLE)
        self.db.drop_table_if_exists(COPY_TABLE)
        
        # Create test tables using the generator
        self.db.execute_query(self.generator.create_users_table(INSERT_TABLE))
        self.db.execute_query(self.generator.create_users_table(COPY_TABLE))
        
        test_data = self.generator.generate_users_data(20000, 2000000)
        columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country', 'created_at')
        
        # Test INSERT method
        time1, _ = SimpleBenchmark.timed(self._bulk_insert_method, INSERT_TABLE, columns, test_data)
        console.print(f"[red]⏱️  INSERT method:[/red] [white]{time1:.4f}s[/white]")
        
        # Test COPY method
        time2, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, COPY_TABLE, columns, test_data)
        console.print(f"[green]⚡ COPY method:[/green] [white]{time2:.4f}s[/white] | [cyan]Speedup: {time1/time2:.1f}x[/cyan]")
        
        self.db.drop_table_if_exists(INSERT_TABLE)
        self.db.drop_table_if_exists(COPY_TABLE)

    def run_index_timing(self):
        console.print("\n[bold yellow]📊 Test: Index Timing 500k records (index first vs data first)[/bold yellow]")
        
        test_data = self.generator.generate_users_data(500000, 3000000)
        columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country', 'created_at')
        
        DATA_FIRST_TABLE = f"{self.TABLE_NAME}_data_first"
        INDEX_FIRST_TABLE = f"{self.TABLE_NAME}_index_first"
        
        self.db.drop_table_if_exists(DATA_FIRST_TABLE)
        self.db.drop_table_if_exists(INDEX_FIRST_TABLE)
        
        # Strategy 1: Data first, then index
        self.db.execute_query(self.generator.create_users_table(DATA_FIRST_TABLE))
        time1, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, DATA_FIRST_TABLE, columns, test_data)
        time1_idx, _ = SimpleBenchmark.timed(self.db.execute_query, f"CREATE INDEX idx_{DATA_FIRST_TABLE}_age ON {DATA_FIRST_TABLE}(age)")
        total_time1 = time1 + time1_idx
        console.print(f"[red]⏱️  Data first, then index:[/red] [white]{total_time1:.4f}s[/white] (data: {time1:.2f}s + index: {time1_idx:.2f}s)")
        
        # Strategy 2: Index first, then data
        self.db.execute_query(self.generator.create_users_table(INDEX_FIRST_TABLE))
        time2_idx, _ = SimpleBenchmark.timed(self.db.execute_query, f"CREATE INDEX idx_{INDEX_FIRST_TABLE}_age ON {INDEX_FIRST_TABLE}(age)")
        time2, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, INDEX_FIRST_TABLE, columns, test_data)
        total_time2 = time2 + time2_idx
        console.print(f"[green]⚡ Index first, then data:[/green] [white]{total_time2:.4f}s[/white] (index: {time2_idx:.2f}s + data: {time2:.2f}s)")
        
        if total_time1 < total_time2:
            console.print(f"[cyan]📊 Data-first is {total_time2/total_time1:.1f}x faster[/cyan]")
        else:
            console.print(f"[cyan]📊 Index-first is {total_time1/total_time2:.1f}x faster[/cyan]")
        
        self.db.drop_table_if_exists(DATA_FIRST_TABLE)
        self.db.drop_table_if_exists(INDEX_FIRST_TABLE)

    def run_batch_size_optimization(self):
        console.print("\n[bold yellow]📊 Test: Batch Size Optimization (1k, 10k, 50k records)[/bold yellow]")
        
        batch_sizes = [1000, 10000, 50000, 200000]
        
        for batch_size in batch_sizes:
            table_name = f"test_batch_{batch_size}"
            self.db.execute_query(self.generator.create_users_table(table_name))
            test_data = self.generator.generate_users_data(batch_size, 4000000 + batch_size)
            columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country', 'created_at')
            
            time_taken, _ = SimpleBenchmark.timed(self.db.bulk_insert_copy, table_name, columns, test_data)
            rate = batch_size / time_taken
            console.print(f"[blue]📊 Batch {batch_size:,}:[/blue] [white]{time_taken:.4f}s[/white] ([cyan]{rate:.0f} records/sec[/cyan])")
            
            self.db.drop_table_if_exists(table_name)
        
    def cleanup(self):
        self.db.execute_query(f"DROP TABLE IF EXISTS {self.TABLE_NAME}")
        self.db.execute_query(f"DROP TABLE IF EXISTS {self.TABLE_NAME}_insert")
        self.db.execute_query(f"DROP TABLE IF EXISTS {self.TABLE_NAME}_copy")
        self.db.execute_query(f"DROP TABLE IF EXISTS {self.TABLE_NAME}_data_first")
        self.db.execute_query(f"DROP TABLE IF EXISTS {self.TABLE_NAME}_index_first")
        self.db.execute_query(f"DROP TABLE IF EXISTS test_batch_1000")
        self.db.execute_query(f"DROP TABLE IF EXISTS test_batch_10000")
        self.db.execute_query(f"DROP TABLE IF EXISTS test_batch_50000")
        self.db.execute_query(f"DROP TABLE IF EXISTS test_batch_200000")