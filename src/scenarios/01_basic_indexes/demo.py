import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.database import DatabaseConnection
from core.benchmark import SimpleBenchmark
from datasets.generator import DataGenerator


def run_basic_index_demo():
    """Run the basic indexes demonstration."""
    print("🔍 Basic Indexes Demo")
    print("=" * 50)
    print("This demo shows how indexes dramatically improve query performance.")
    print()
    
    db = DatabaseConnection()
    benchmark = SimpleBenchmark()
    generator = DataGenerator()
    
    # Get sample data for testing
    users_data = generator.generate_users_data(100)
    test_email = users_data[0][2]  # Get first user's email
    test_city = users_data[0][6]   # Get first user's city
    
    print("📊 Testing Query Performance:")
    print("-" * 30)
    
    # Test 1: Query without indexes
    print("\n1️⃣ Query WITHOUT indexes:")
    print(f"   Finding user with email: {test_email}")
    
    result1, time1 = benchmark.time_query(
        db, 
        "SELECT * FROM users WHERE email = %s", 
        (test_email,),
        "Query without index"
    )
    
    print(f"   ⏱️  Time: {time1:.4f} seconds")
    print(f"   📄 Rows returned: {len(result1)}")
    
    # Show query plan
    print("\n   🔍 Query Plan (without index):")
    plan1 = db.get_query_plan("SELECT * FROM users WHERE email = %s", (test_email,))
    print("   " + plan1.replace('\n', '\n   '))
    
    # Create index
    print("\n2️⃣ Creating index on email column...")
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    print("   ✅ Index created!")
    
    # Test 2: Query with index
    print("\n3️⃣ Query WITH index:")
    print(f"   Finding user with email: {test_email}")
    
    result2, time2 = benchmark.time_query(
        db, 
        "SELECT * FROM users WHERE email = %s", 
        (test_email,),
        "Query with index"
    )
    
    print(f"   ⏱️  Time: {time2:.4f} seconds")
    print(f"   📄 Rows returned: {len(result2)}")
    
    # Show query plan
    print("\n   🔍 Query Plan (with index):")
    plan2 = db.get_query_plan("SELECT * FROM users WHERE email = %s", (test_email,))
    print("   " + plan2.replace('\n', '\n   '))
    
    # Compare results
    benchmark.compare_results()
    
    # Test city query
    print("\n" + "=" * 50)
    print("🏙️  Testing another query - Find users by city:")
    print(f"   Finding users in city: {test_city}")
    
    benchmark.clear_results()
    
    # Without index
    result3, time3 = benchmark.time_query(
        db,
        "SELECT * FROM users WHERE city = %s",
        (test_city,),
        "City query without index"
    )
    print(f"   ⏱️  Time without index: {time3:.4f} seconds")
    
    # Create index on city
    db.execute_query("CREATE INDEX IF NOT EXISTS idx_users_city ON users(city)")
    
    # With index
    result4, time4 = benchmark.time_query(
        db,
        "SELECT * FROM users WHERE city = %s",
        (test_city,),
        "City query with index"
    )
    print(f"   ⏱️  Time with index: {time4:.4f} seconds")
    
    benchmark.compare_results()
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    run_basic_index_demo() 