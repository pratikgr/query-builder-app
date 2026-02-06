"""
Database initialization script
Run this to create tables and populate with sample data
"""
from app.db.database import engine, SessionLocal
from app.db.models import Base, User, Product, Order, OrderItem
from datetime import datetime, timedelta
import random


def init_db():
    """Initialize database with tables and sample data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already contains data. Skipping initialization.")
            return
        
        print("Adding sample users...")
        users = [
            User(first_name="John", last_name="Doe", email="john.doe@example.com", age=30, city="New York", country="USA", is_active=True),
            User(first_name="Jane", last_name="Smith", email="jane.smith@example.com", age=25, city="Los Angeles", country="USA", is_active=True),
            User(first_name="Bob", last_name="Johnson", email="bob.johnson@example.com", age=35, city="Chicago", country="USA", is_active=False),
            User(first_name="Alice", last_name="Williams", email="alice.williams@example.com", age=28, city="San Francisco", country="USA", is_active=True),
            User(first_name="Charlie", last_name="Brown", email="charlie.brown@example.com", age=42, city="Seattle", country="USA", is_active=True),
            User(first_name="Emma", last_name="Davis", email="emma.davis@example.com", age=31, city="Boston", country="USA", is_active=True),
            User(first_name="Michael", last_name="Miller", email="michael.miller@example.com", age=29, city="Austin", country="USA", is_active=False),
            User(first_name="Sarah", last_name="Wilson", email="sarah.wilson@example.com", age=33, city="Denver", country="USA", is_active=True),
            User(first_name="David", last_name="Moore", email="david.moore@example.com", age=27, city="Portland", country="USA", is_active=True),
            User(first_name="Lisa", last_name="Taylor", email="lisa.taylor@example.com", age=36, city="Miami", country="USA", is_active=True),
        ]
        db.add_all(users)
        db.commit()
        
        print("Adding sample products...")
        products = [
            Product(name="Laptop", category="Electronics", price=999.99, stock_quantity=50, is_available=True, description="High-performance laptop"),
            Product(name="Smartphone", category="Electronics", price=699.99, stock_quantity=100, is_available=True, description="Latest model smartphone"),
            Product(name="Headphones", category="Electronics", price=149.99, stock_quantity=200, is_available=True, description="Noise-cancelling headphones"),
            Product(name="Desk Chair", category="Furniture", price=299.99, stock_quantity=30, is_available=True, description="Ergonomic office chair"),
            Product(name="Standing Desk", category="Furniture", price=599.99, stock_quantity=20, is_available=True, description="Adjustable standing desk"),
            Product(name="Monitor", category="Electronics", price=399.99, stock_quantity=75, is_available=True, description="27-inch 4K monitor"),
            Product(name="Keyboard", category="Electronics", price=89.99, stock_quantity=150, is_available=True, description="Mechanical keyboard"),
            Product(name="Mouse", category="Electronics", price=49.99, stock_quantity=180, is_available=True, description="Wireless mouse"),
            Product(name="Bookshelf", category="Furniture", price=199.99, stock_quantity=40, is_available=False, description="Wooden bookshelf"),
            Product(name="Lamp", category="Furniture", price=79.99, stock_quantity=90, is_available=True, description="LED desk lamp"),
        ]
        db.add_all(products)
        db.commit()
        
        print("Adding sample orders...")
        # Create some orders
        for i in range(20):
            user = random.choice(users)
            order = Order(
                user_id=user.id,
                order_date=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                status=random.choice(["pending", "completed", "shipped", "cancelled"]),
                total_amount=0  # Will be calculated
            )
            db.add(order)
            db.flush()
            
            # Add order items
            num_items = random.randint(1, 4)
            total = 0
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                price = product.price
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=price
                )
                db.add(order_item)
                total += price * quantity
            
            order.total_amount = round(total, 2)
        
        db.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
