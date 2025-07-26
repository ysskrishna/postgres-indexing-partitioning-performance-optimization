from core.database import DatabaseConnection
from core.benchmark import SimpleBenchmark
from datasets.generator import DataGenerator
from datetime import datetime, timedelta
from core.logger import console

def run_basic_index_executor():
    """Run the basic indexes demonstration."""
    TABLE_NAME = "users"
    
    db = DatabaseConnection()
    benchmark = SimpleBenchmark()
    
    # Get a random existing user_id for testing
    existing_user = db.execute_query(f"SELECT user_id FROM {TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
    if not existing_user:
        console.print("No users found in database. Please ensure data is loaded first.")
        return
    
    # Test 1: Range Query - Created At
    console.print("\nTest 1: Range Query (WHERE created_at BETWEEN X AND Y):")
    
    # First without index
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    result2, time2 = benchmark.time_query(
        db,
        f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE created_at BETWEEN %s AND %s",
        (start_date, end_date),
        "Date range without index"
    )
    console.print(f"Time without index: {time2:.4f} seconds")
    
    # Create index on created_at
    console.print("\nCreating index on created_at...")
    db.execute_query(f"CREATE INDEX IF NOT EXISTS idx_users_created_at ON {TABLE_NAME}(created_at)")
    
    # Test with index
    result3, time3 = benchmark.time_query(
        db,
        f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE created_at BETWEEN %s AND %s",
        (start_date, end_date),
        "Date range with index"
    )
    console.print(f"Time with index: {time3:.4f} seconds")
    
    # Test 3: ORDER BY Operations
    console.print("\nTest 3: ORDER BY Operations:")
    
    # Without index
    result4, time4 = benchmark.time_query(
        db,
        f"SELECT * FROM {TABLE_NAME} ORDER BY username LIMIT 100",
        None,
        "ORDER BY without index"
    )
    console.print(f"Time without index: {time4:.4f} seconds")
    
    # Create index for ORDER BY
    console.print("\nCreating index on username...")
    db.execute_query(f"CREATE INDEX IF NOT EXISTS idx_users_username ON {TABLE_NAME}(username)")
    
    # Test with index
    result5, time5 = benchmark.time_query(
        db,
        f"SELECT * FROM {TABLE_NAME} ORDER BY username LIMIT 100",
        None,
        "ORDER BY with index"
    )
    console.print(f"Time with index: {time5:.4f} seconds")