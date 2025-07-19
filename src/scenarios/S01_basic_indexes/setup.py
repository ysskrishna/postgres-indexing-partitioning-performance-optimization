from core.database import DatabaseConnection
from datasets.generator import DataGenerator


def setup_basic_index_scenario(users: int = 1000, orders: int = 5000):
    """Setup tables and data for basic index demonstrations."""
    print("🚀 Setting up Basic Indexes Scenario...")
    
    db = DatabaseConnection()
    generator = DataGenerator()
    
    try:
        db.drop_table_if_exists("orders")
        db.drop_table_if_exists("users")
        
        # Create tables
        print("📋 Creating tables...")
        db.execute_query(generator.create_users_table())
        db.execute_query(generator.create_orders_table())
        
        # Generate and insert data
        print("📊 Generating sample data...")
        
        # Users data
        users_data = generator.generate_users_data(users)
        db.execute_many(
            "INSERT INTO users (id, username, email, first_name, last_name, age, city, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            users_data
        )
        print(f"✅ Inserted {len(users_data)} users")
        
        # Orders data
        orders_data = generator.generate_orders_data(orders, users)
        db.execute_many(
            "INSERT INTO orders (id, user_id, order_date, total_amount, status) VALUES (%s, %s, %s, %s, %s)",
            orders_data
        )
        print(f"✅ Inserted {len(orders_data)} orders")
        
        # Update statistics
        print("📈 Updating table statistics...")
        db.analyze_table("users")
        db.analyze_table("orders")
        
        # Show table info
        print("\n📊 Table Information:")
        for table in ["users", "orders"]:
            info = db.get_table_info(table)
            print(f"  {table}: {info['row_count']} rows, {info['total_size']}")
        
        print("\n✅ Basic Indexes Scenario setup completed!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        raise
