from faker import Faker
from typing import List, Tuple
import random

class DataGenerator:
    """Generate sample data for performance testing."""
    
    def __init__(self, seed=42):
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
    
    def create_users_table(self) -> str:
        """Create users table SQL."""
        return """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            email VARCHAR UNIQUE NOT NULL,
            first_name VARCHAR,
            last_name VARCHAR,
            age INTEGER,
            city VARCHAR,
            country VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    def generate_users_data(self, count: int = 1000) -> List[Tuple]:
        """Generate sample user data."""
        users = []
        for i in range(count):
            user = (
                self.fake.unique.user_name(),  # username
                self.fake.unique.email(),  # email
                self.fake.first_name(),  # first_name
                self.fake.last_name(),  # last_name
                random.randint(18, 80),  # age
                self.fake.city(),  # city
                self.fake.country(),  # country
            )
            users.append(user)
        return users