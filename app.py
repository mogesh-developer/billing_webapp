from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import Config
from models import db, Product, Bill, BillItem, Settings, Expense
from datetime import datetime, timedelta
import uuid
import mysql.connector

# --- Database Auto-Creation Logic ---
def create_db_if_not_exists():
    # Extract credentials from Config.SQLALCHEMY_DATABASE_URI
    # URI format: mysql+mysqlconnector://user:password@host/dbname
    uri = Config.SQLALCHEMY_DATABASE_URI
    try:
        # Simple extraction (assumes standard format)
        part1 = uri.split('://')[1]
        creds, server_db = part1.split('@')
        user_pass = creds.split(':')
        host_db = server_db.split('/')
        
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        host = host_db[0]
        dbname = host_db[1]

        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname}")
        conn.close()
        print(f"Database '{dbname}' checked/created successfully.")
    except Exception as e:
        print(f"Warning: Could not auto-create database. Ensure it exists. Error: {e}")

create_db_if_not_exists()
# ------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Helper to ensure DB tables exist
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    # Real Stats
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.stock_quantity < 5).count()
    
    # Calculate today's sales
    today = datetime.now().date()
    current_month_start = today.replace(day=1)
    
    # 1. Today's Stats
    today_bills = Bill.query.filter(db.func.date(Bill.date) == today).all()
    today_sales = sum(bill.total_amount for bill in today_bills)
    
    # 2. Monthly Stats
    month_bills = Bill.query.filter(Bill.date >= current_month_start).all()
    month_sales = sum(bill.total_amount for bill in month_bills)
    
    # Calculate Profits (Daily & Monthly)
    def calculate_profit(bills_list):
        cogs = 0
        for bill in bills_list:
            for item in bill.items:
                if item.product:
                    cogs += item.product.cost_price * item.quantity
        return cogs

    today_cogs = calculate_profit(today_bills)
    month_cogs = calculate_profit(month_bills)
    
    today_expenses = db.session.query(db.func.sum(Expense.amount)).filter(db.func.date(Expense.date) == today).scalar() or 0
    month_expenses = db.session.query(db.func.sum(Expense.amount)).filter(Expense.date >= current_month_start).scalar() or 0
    
    today_profit = today_sales - today_cogs - today_expenses
    month_profit = month_sales - month_cogs - month_expenses
    
    recent_bills = Bill.query.order_by(Bill.date.desc()).limit(5).all()

    # Chart Data (Last 7 Days)
    dates = []
    sales_data = []
    profit_data = []
    expense_data = []
    
    for i in range(6, -1, -1):
        d = datetime.now().date() - timedelta(days=i)
        dates.append(d.strftime('%b %d'))
        
        # Sales
        day_sales = db.session.query(db.func.sum(Bill.total_amount)).filter(db.func.date(Bill.date) == d).scalar() or 0
        sales_data.append(day_sales)
        
        # Expenses
        day_exp = db.session.query(db.func.sum(Expense.amount)).filter(db.func.date(Expense.date) == d).scalar() or 0
        expense_data.append(day_exp)

        # COGS (Complex query, simplest is to iterate bills of day)
        day_bills = Bill.query.filter(db.func.date(Bill.date) == d).all()
        day_cogs = 0
        for b in day_bills:
            for it in b.items:
                if it.product:
                    day_cogs += it.product.cost_price * it.quantity
        
        profit_data.append(day_sales - day_cogs - day_exp)

    return render_template('dashboard.html', 
                           total_products=total_products, 
                           low_stock=low_stock, 
                           today_sales=today_sales,
                           today_profit=today_profit,
                           today_expenses=today_expenses,
                           month_sales=month_sales,
                           month_profit=month_profit,
                           recent_bills=recent_bills,
                           chart_labels=dates,
                           chart_data=sales_data,
                           chart_profit=profit_data,
                           chart_expenses=expense_data)

@app.route('/inventory')
def inventory():
    products = Product.query.all()
    # Pre-check low stock for alert
    low_stock_items = [p.name for p in products if p.stock_quantity < 5]
    return render_template('inventory.html', products=products, low_stock_alert=low_stock_items)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        desc = request.form['description']
        amt = float(request.form['amount'])
        cat = request.form['category']
        
        new_exp = Expense(description=desc, amount=amt, category=cat)
        db.session.add(new_exp)
        db.session.commit()
        return redirect(url_for('expenses'))
        
    all_expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('expenses.html', expenses=all_expenses)

@app.route('/billing')
def billing():
    return render_template('billing.html')

@app.route('/receipt/<int:bill_id>')
def receipt(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    settings = Settings.query.first()
    return render_template('receipt.html', bill=bill, settings=settings)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        settings.shop_name = request.form['shop_name']
        settings.address = request.form['address']
        settings.phone = request.form['phone']
        settings.currency_symbol = request.form['currency_symbol']
        settings.default_tax_rate = float(request.form['default_tax_rate'])
        db.session.commit()
        return redirect(url_for('settings'))
        
    return render_template('settings.html', settings=settings)

@app.route('/history')
def history():
    bills = Bill.query.order_by(Bill.date.desc()).all()
    return render_template('history.html', bills=bills)

# API Routes
@app.route('/api/settings', methods=['GET'])
def get_settings():
    settings = Settings.query.first()
    if not settings:
        return jsonify({'shop_name': 'My Shop', 'currency_symbol': '$', 'default_tax_rate': 0})
    return jsonify({
        'shop_name': settings.shop_name,
        'address': settings.address,
        'phone': settings.phone,
        'currency_symbol': settings.currency_symbol,
        'default_tax_rate': settings.default_tax_rate
    })
@app.route('/api/products', methods=['GET'])
def get_products():
    query = request.args.get('q', '')
    if query:
        # Search by name or barcode
        products = Product.query.filter((Product.name.ilike(f'%{query}%')) | (Product.barcode.ilike(f'%{query}%'))).all()
    else:
        products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/product/<barcode>', methods=['GET'])
def get_product_by_barcode(barcode):
    # Strip any whitespace
    barcode = barcode.strip()
    product = Product.query.filter_by(barcode=barcode).first()
    if product:
        return jsonify(product.to_dict())
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.json
    try:
        new_bill = Bill(
            bill_number=str(uuid.uuid4()).split('-')[0].upper(),
            customer_name=data.get('customer_name', 'Walk-in'),
            subtotal=data.get('subtotal', 0),
            tax_amount=data.get('tax_amount', 0),
            discount_amount=data.get('discount_amount', 0),
            total_amount=data.get('total_amount'),
            payment_mode=data.get('payment_mode', 'Cash'),
            date=datetime.now()
        )
        db.session.add(new_bill)
        
        for item in data.get('items', []):
            product = Product.query.get(item['product_id'])
            if product:
                if product.stock_quantity < item['quantity']:
                    return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
                
                product.stock_quantity -= item['quantity']
                
                bill_item = BillItem(
                    bill=new_bill,
                    product_id=product.id,
                    quantity=item['quantity'],
                    price_at_sale=item['price'],
                    subtotal=item['subtotal']
                )
                db.session.add(bill_item)
        
        db.session.commit()
        return jsonify({'message': 'Bill saved successfully', 'bill_id': new_bill.id, 'bill_number': new_bill.bill_number, 'date': new_bill.date.strftime('%Y-%m-%d %H:%M')})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    try:
        # Check duplicate
        if Product.query.filter_by(barcode=data['barcode']).first():
             return jsonify({'error': 'Barcode already exists'}), 400

        new_product = Product(
            name=data['name'],
            barcode=data['barcode'],
            price=float(data['price']),
            cost_price=float(data.get('cost_price', 0)),
            stock_quantity=int(data['stock_quantity']),
            category=data.get('category', 'General')
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully', 'product': new_product.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/product/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    try:
        product.name = data.get('name', product.name)
        product.barcode = data.get('barcode', product.barcode)
        product.price = float(data.get('price', product.price))
        if 'cost_price' in data:
            product.cost_price = float(data['cost_price'])
        product.stock_quantity = int(data.get('stock_quantity', product.stock_quantity))
        product.category = data.get('category', product.category)
        
        db.session.commit()
        return jsonify({'message': 'Product updated', 'product': product.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Cannot delete product (likely used in bills)'}), 400



if __name__ == '__main__':
    app.run(debug=True)
