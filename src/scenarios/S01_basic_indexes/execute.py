from core.database import DatabaseConnection
from core.benchmark import SimpleBenchmark
from datasets.generator import DataGenerator
from datetime import datetime, timedelta


def run_basic_index_executor():
    """Run the basic indexes demonstration."""
    print("Basic Indexes Demo")
    print("=" * 50)
    print("This demo shows how indexes dramatically improve query performance.")
    print()
    
    TABLE_NAME = "users1"
    
    db = DatabaseConnection()
    benchmark = SimpleBenchmark()
    generator = DataGenerator()
    
    # Get sample data for testing
    print("\nRunning test queries on user records:")
    print("-" * 50)
    
    # Test 1: Point Query - ID lookup
    print("\nTest 1: Point Query (WHERE user_id = X):")
    
    # Get a random existing user_id for testing
    existing_user = db.execute_query(f"SELECT user_id FROM {TABLE_NAME} ORDER BY RANDOM() LIMIT 1")
    if not existing_user:
        print("No users found in database. Please ensure data is loaded first.")
        return
    
    test_id = existing_user[0][0]
    print(f"Testing with user_id: {test_id}")
    
    # Without index (though PK has automatic index)
    result1, time1 = benchmark.time_query(
        db,
        f"SELECT * FROM {TABLE_NAME} WHERE user_id = %s",
        (test_id,),
        "ID lookup (with PK index)"
    )
    print(f"Time: {time1:.4f} seconds")
    print(f"Rows: {len(result1)}")
    print("\nQuery Plan:")
    plan1 = db.get_query_plan(f"SELECT * FROM {TABLE_NAME} WHERE user_id = %s", (test_id,))
    print(plan1)
    
    # Test 2: Range Query - Created At
    print("\nTest 2: Range Query (WHERE created_at BETWEEN X AND Y):")
    
    # First without index
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    result2, time2 = benchmark.time_query(
        db,
        f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE created_at BETWEEN %s AND %s",
        (start_date, end_date),
        "Date range without index"
    )
    print(f"Time without index: {time2:.4f} seconds")
    print("\nQuery Plan (without index):")
    plan2 = db.get_query_plan(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE created_at BETWEEN %s AND %s", (start_date, end_date))
    print(plan2)
    
    # Create index on created_at
    print("\nCreating index on created_at...")
    db.execute_query(f"CREATE INDEX IF NOT EXISTS idx_users_created_at ON {TABLE_NAME}(created_at)")
    
    # Test with index
    result3, time3 = benchmark.time_query(
        db,
        f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE created_at BETWEEN %s AND %s",
        (start_date, end_date),
        "Date range with index"
    )
    print(f"Time with index: {time3:.4f} seconds")
    print("\nQuery Plan (with index):")
    plan3 = db.get_query_plan(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE created_at BETWEEN %s AND %s", (start_date, end_date))
    print(plan3)
    
    # Test 3: ORDER BY Operations
    print("\nTest 3: ORDER BY Operations:")
    
    # Without index
    result4, time4 = benchmark.time_query(
        db,
        f"SELECT * FROM {TABLE_NAME} ORDER BY username LIMIT 100",
        None,
        "ORDER BY without index"
    )
    print(f"Time without index: {time4:.4f} seconds")
    print("\nQuery Plan (without index):")
    plan4 = db.get_query_plan(f"SELECT * FROM {TABLE_NAME} ORDER BY username LIMIT 100")
    print(plan4)
    
    # Create index for ORDER BY
    print("\nCreating index on username...")
    db.execute_query(f"CREATE INDEX IF NOT EXISTS idx_users_username ON {TABLE_NAME}(username)")
    
    # Test with index
    result5, time5 = benchmark.time_query(
        db,
        f"SELECT * FROM {TABLE_NAME} ORDER BY username LIMIT 100",
        None,
        "ORDER BY with index"
    )
    print(f"Time with index: {time5:.4f} seconds")
    print("\nQuery Plan (with index):")
    plan5 = db.get_query_plan(f"SELECT * FROM {TABLE_NAME} ORDER BY username LIMIT 100")
    print(plan5)
    
    # Compare all results
    print("\nPerformance Summary:")
    benchmark.compare_results()
    
    # Show I/O Stats for each index
    print("\nIndex Statistics:")
    for index_name in ["users_pkey", "idx_users_created_at", "idx_users_username"]:
        stats = db.execute_query(f"""
            SELECT 
                pg_size_pretty(pg_relation_size(i.indexrelid)) as index_size,
                idx_scan as number_of_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched
            FROM pg_stat_user_indexes ui
            JOIN pg_index i ON ui.indexrelid = i.indexrelid
            WHERE ui.indexrelname = '{index_name}'
        """)
        if stats:
            print(f"\n{index_name}:")
            print(f"    Size: {stats[0][0]}")
            print(f"    Scans: {stats[0][1]}")
            print(f"    Tuples read: {stats[0][2]}")
            print(f"    Tuples fetched: {stats[0][3]}")
    
    print("\nBasic Indexes Demo completed!")