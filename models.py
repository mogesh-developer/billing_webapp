from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    # Storing price as float for simplicity, consider Decimal for high precision financial apps
    price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, default=0.0)
    stock_quantity = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))

    @property
    def cost_price_total(self):
        return self.cost_price * self.stock_quantity

    @property
    def sell_price_total(self):
        return self.price * self.stock_quantity

    @property
    def profit(self):
        return self.price - self.cost_price

    @property
    def margin(self):
        if self.cost_price > 0:
            return (self.profit / self.cost_price) * 100
        return 100 if self.price > 0 else 0

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'barcode': self.barcode,
            'price': self.price,
            'cost_price': self.cost_price,
            'stock_quantity': self.stock_quantity,
            'category': self.category
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), default='Operational')
    date = db.Column(db.DateTime, default=datetime.now)

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(100), default="My Grocery Shop")
    address = db.Column(db.String(200), default="123 Market St")
    phone = db.Column(db.String(20), default="555-0123")
    currency_symbol = db.Column(db.String(5), default="$")
    default_tax_rate = db.Column(db.Float, default=0.0)

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    customer_name = db.Column(db.String(100), nullable=True)
    
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_mode = db.Column(db.String(20), default="Cash")
    
    items = db.relationship('BillItem', backref='bill', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'bill_number': self.bill_number,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'customer_name': self.customer_name,
            'subtotal': self.subtotal,
            'tax': self.tax_amount,
            'discount': self.discount_amount,
            'total_amount': self.total_amount,
            'payment_mode': self.payment_mode,
            'items': [item.to_dict() for item in self.items]
        }

class BillItem(db.Model):
    __tablename__ = 'bill_items'
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_sale = db.Column(db.Float, nullable=False) # Price at the time of purchase
    subtotal = db.Column(db.Float, nullable=False)

    product = db.relationship('Product', backref='bill_items')

    def to_dict(self):
        return {
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price': self.price_at_sale,
            'subtotal': self.subtotal
        }
