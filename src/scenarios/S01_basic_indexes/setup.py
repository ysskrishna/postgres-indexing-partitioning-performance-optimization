import time
from core.database import DatabaseConnection
from datasets.generator import DataGenerator


def setup_basic_index_scenario(users: int = 1_000_000):
    """Setup tables and data for basic index demonstrations with 1M users."""
    print("Setting up Basic Indexes Scenario...")
    print(f"Generating {users:,} users...")
    
    db = DatabaseConnection()
    generator = DataGenerator()
    TABLE_NAME = "users1"
    
    try:
        # Drop and recreate users table
        db.drop_table_if_exists(TABLE_NAME)
        
        # Create table
        print("Creating users table...")
        db.execute_query(generator.create_users_table(TABLE_NAME))
        
        # Generate and insert data in batches
        print("Generating and inserting sample data...")
        batch_size = 50000
        columns = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'country')

        total_generation_time = 0
        total_insertion_time = 0
        total_batches = 0

        for i in range(0, users, batch_size):
            batch_start = time.time()
            
            # Measure data generation time
            generation_start = time.time()
            users_data = generator.generate_users_data(batch_size, i)
            generation_time = time.time() - generation_start
            total_generation_time += generation_time
            
            # Measure bulk insertion time
            insertion_start = time.time()
            db.bulk_insert_copy(TABLE_NAME, columns, users_data)
            insertion_time = time.time() - insertion_start
            total_insertion_time += insertion_time
            
            total_batches += 1
            batch_time = time.time() - batch_start
            
            print(f"Progress: {i+batch_size:,}/{users:,} | "
                  f"Batch: {batch_time:.2f}s | "
                  f"Generation: {generation_time:.2f}s | "
                  f"Insertion: {insertion_time:.2f}s")
            
        # Update statistics
        print("\nUpdating table statistics...")
        db.analyze_table(TABLE_NAME)
        
        # Show table info
        print("\nTable Information:")
        info = db.get_table_info(TABLE_NAME)
        print(f"{TABLE_NAME}: {info['row_count']:,} rows, {info['total_size']}")
        
        # Show timing summary
        print("\nTiming Summary:")
        print(f"Total batches processed: {total_batches}")
        print(f"Total data generation time: {total_generation_time:.2f}s")
        print(f"Total bulk insertion time: {total_insertion_time:.2f}s")
        print(f"Average generation time per batch: {total_generation_time/total_batches:.2f}s")
        print(f"Average insertion time per batch: {total_insertion_time/total_batches:.2f}s")
        print(f"Average rows per second (generation): {users/total_generation_time:,.0f}")
        print(f"Average rows per second (insertion): {users/total_insertion_time:,.0f}")
        
        print("\nBasic Indexes Scenario setup completed!")
        
    except Exception as e:
        print(f"Error: Setup failed: {e}")
        raise
