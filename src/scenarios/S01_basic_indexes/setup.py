from core.database import DatabaseConnection
from datasets.generator import DataGenerator


def setup_basic_index_scenario(users: int = 1_000_000):
    """Setup tables and data for basic index demonstrations with 1M users."""
    print("Setting up Basic Indexes Scenario...")
    print(f"Generating {users:,} users...")
    
    db = DatabaseConnection()
    generator = DataGenerator()
    
    try:
        # Drop and recreate users table
        db.drop_table_if_exists("users")
        
        # Create table
        print("Creating users table...")
        db.execute_query(generator.create_users_table())
        
        # Generate and insert data in batches
        print("Generating and inserting sample data...")
        batch_size = 10000
        
        # Users data
        total_users_inserted = 0
        for i in range(0, users, batch_size):
            batch_count = min(batch_size, users - i)
            users_data = generator.generate_users_data(batch_count)
            db.execute_many(
                "INSERT INTO users (username, email, first_name, last_name, age, city, country) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                users_data
            )
            total_users_inserted += len(users_data)
            print(f"Progress: {total_users_inserted:,}/{users:,} users inserted")
        
        # Update statistics
        print("\nUpdating table statistics...")
        db.analyze_table("users")
        
        # Show table info
        print("\nTable Information:")
        info = db.get_table_info("users")
        print(f"users: {info['row_count']:,} rows, {info['total_size']}")
        
        print("\nBasic Indexes Scenario setup completed!")
        
    except Exception as e:
        print(f"Error: Setup failed: {e}")
        raise
