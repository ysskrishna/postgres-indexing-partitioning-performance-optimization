import psycopg2
import io
from typing import List, Tuple, Optional, Dict, Any


class DatabaseConnection:    
    def __init__(self, host="localhost", port=5432, database="master_db", 
                 user="service_user", password="service_password"):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection_string = f"host={host} port={port} dbname={database} user={user} password={password}"
    
    def connect(self):
        """Create a database connection."""
        try:
            return psycopg2.connect(self.connection_string)
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("Make sure PostgreSQL is running with: docker-compose up -d")
            raise
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Tuple]:
        """Execute a query and return results."""
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                conn.commit()
                return []
    
    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute the same query with multiple parameter sets."""
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                conn.commit()
    
    def bulk_insert_copy(self, table_name: str, columns: Tuple[str], data: List[tuple]):
        with self.connect() as conn:
            with conn.cursor() as cursor:
                buffer = io.StringIO()
                for row in data:
                    buffer.write('\t'.join([str(x) if x is not None else '\\N' for x in row]) + '\n')
                buffer.seek(0)
                cursor.copy_from(buffer, table_name, sep='\t', columns=columns)
            conn.commit()
    
    def get_query_plan(self, query: str, params: Optional[tuple] = None) -> str:
        """Get the execution plan for a query."""
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {query}", params)
                plan = cursor.fetchall()
                return '\n'.join([row[0] for row in plan])
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        );
        """
        result = self.execute_query(query, (table_name,))
        return result[0][0] if result else False
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get basic information about a table."""
        if not self.table_exists(table_name):
            return {"error": f"Table {table_name} does not exist"}
        
        # Get row count
        count_query = f"SELECT COUNT(*) FROM {table_name}"
        row_count = self.execute_query(count_query)[0][0]
        
        # Get table size
        size_query = f"""
        SELECT 
            pg_size_pretty(pg_total_relation_size('{table_name}')) as total_size,
            pg_size_pretty(pg_relation_size('{table_name}')) as table_size
        """
        size_result = self.execute_query(size_query)[0]
        
        return {
            "table_name": table_name,
            "row_count": row_count,
            "total_size": size_result[0],
            "table_size": size_result[1]
        }
    
    def drop_table_if_exists(self, table_name: str) -> None:
        """Drop a table if it exists."""
        self.execute_query(f"DROP TABLE IF EXISTS {table_name} CASCADE")
    
    def analyze_table(self, table_name: str) -> None:
        """Update table statistics."""
        self.execute_query(f"ANALYZE {table_name}")