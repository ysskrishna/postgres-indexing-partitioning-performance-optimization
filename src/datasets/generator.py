from faker import Faker
from typing import List, Tuple
import random
from datetime import datetime, timedelta

class DataGenerator:
    """Generate sample data for performance testing."""
    
    def __init__(self, seed=42):
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
    
    def create_users_table(self, table_name: str) -> str:
        """Create users table SQL."""
        return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            email VARCHAR UNIQUE NOT NULL,
            first_name VARCHAR,
            last_name VARCHAR,
            age INTEGER,
            city VARCHAR,
            country VARCHAR,
            created_at TIMESTAMP
        );
        """
    
    def random_datetime(self, start: datetime, end: datetime) -> datetime:
        """
        Generate a random datetime between `start` and `end`.
        """
        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)
    
    def generate_users_data(self, count: int, start_index: int = 0) -> List[Tuple]:
        """Generate optimized user data using firstname+lastname+index for uniqueness."""
        # Pre-generate pools per batch
        first_names = [self.fake.first_name() for _ in range(500)]
        last_names = [self.fake.last_name() for _ in range(500)]
        cities = [self.fake.city() for _ in range(200)]
        countries = [self.fake.country() for _ in range(100)]
        
        created_at_start = datetime.now() - timedelta(days=365)
        created_at_end = datetime.now()

        users = []
        for i in range(start_index, start_index + count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            username = f"{first.lower()}.{last.lower()}{i}"
            email = f"{username}@example.com"
            users.append(
                (
                    username,          # unique username
                    email,             # unique email
                    first,             # first name
                    last,              # last name
                    random.randint(18, 80),  # age
                    random.choice(cities),
                    random.choice(countries),
                    self.random_datetime(created_at_start, created_at_end)
                )
            )
        return users