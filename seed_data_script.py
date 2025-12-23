from app import app, db, Product, Bill, BillItem, Expense
from datetime import datetime, timedelta
import random

def seed_data():
    with app.app_context():
        print("Seeding data...")
        
        # Check if products exist, if not create some
        if Product.query.count() == 0:
            products = [
                Product(name="Milk", barcode="1001", price=3.50, cost_price=2.00, stock_quantity=50, category="Dairy"),
                Product(name="Bread", barcode="1002", price=2.50, cost_price=1.20, stock_quantity=40, category="Bakery"),
                Product(name="Eggs (Dozen)", barcode="1003", price=4.00, cost_price=2.80, stock_quantity=30, category="Dairy"),
                Product(name="Apple", barcode="1004", price=0.80, cost_price=0.40, stock_quantity=100, category="Fruits"),
                Product(name="Rice (1kg)", barcode="1005", price=5.00, cost_price=3.50, stock_quantity=20, category="Grains")
            ]
            db.session.add_all(products)
            db.session.commit()
            print("Added Products.")
        
        products = Product.query.all()
        
        # Generate Sales for last 7 days
        for i in range(7):
            day = datetime.now() - timedelta(days=i)
            # Create 3-8 bills per day
            for _ in range(random.randint(3, 8)):
                bill = Bill(customer_name="Walk-in Customer", total_amount=0, date=day)
                db.session.add(bill)
                db.session.flush() # get ID
                
                total = 0
                # Add 1-5 items
                for _ in range(random.randint(1, 5)):
                    p = random.choice(products)
                    qty = random.randint(1, 3)
                    item = BillItem(bill_id=bill.id, product_id=p.id, product_name=p.name, 
                                    quantity=qty, price=p.price, total=p.price*qty)
                    total += item.total
                    db.session.add(item)
                
                bill.total_amount = total
            
            # Add Expenses
            if random.choice([True, False]):
                exp = Expense(description="Daily Maintenance", amount=random.uniform(10, 50), category="Operational", date=day)
                db.session.add(exp)
        
        db.session.commit()
        print("Seeding Complete! Dashboard should now show data.")

if __name__ == "__main__":
    seed_data()
