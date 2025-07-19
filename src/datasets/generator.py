"""
Simple data generator for PostgreSQL performance demos.
"""

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
            id SERIAL PRIMARY KEY,
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
    
    def create_orders_table(self) -> str:
        """Create orders table SQL."""
        return """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            order_date DATE NOT NULL,
            total_amount DECIMAL(10,2),
            status VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    def generate_users_data(self, count: int = 1000) -> List[Tuple]:
        """Generate sample user data."""
        users = []
        for i in range(count):
            user = (
                i + 1,  # id
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
    
    def generate_orders_data(self, count: int = 5000, user_count: int = 1000) -> List[Tuple]:
        """Generate sample order data."""
        orders = []
        statuses = ['pending', 'completed', 'cancelled', 'shipped']
        
        for i in range(count):
            order = (
                i + 1,  # id
                random.randint(1, user_count),  # user_id
                self.fake.date_between(start_date='-1y', end_date='today'),  # order_date
                round(random.uniform(10.0, 1000.0), 2),  # total_amount
                random.choice(statuses),  # status
            )
            orders.append(order)
        return orders