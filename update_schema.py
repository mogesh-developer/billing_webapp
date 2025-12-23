from config import Config
import mysql.connector

def update_schema():
    uri = Config.SQLALCHEMY_DATABASE_URI
    # Extract credentials
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
        password=password,
        database=dbname
    )
    cursor = conn.cursor()

    # Alter table commands
    commands = [
        "ALTER TABLE bills ADD COLUMN subtotal FLOAT NOT NULL DEFAULT 0.0;",
        "ALTER TABLE bills ADD COLUMN tax_amount FLOAT DEFAULT 0.0;",
        "ALTER TABLE bills ADD COLUMN discount_amount FLOAT DEFAULT 0.0;",
        "ALTER TABLE bills ADD COLUMN payment_mode VARCHAR(20) DEFAULT 'Cash';",
        "CREATE TABLE IF NOT EXISTS settings (id INT AUTO_INCREMENT PRIMARY KEY, shop_name VARCHAR(100) DEFAULT 'My Grocery Shop', address VARCHAR(200) DEFAULT '123 Market St', phone VARCHAR(20) DEFAULT '555-0123', currency_symbol VARCHAR(5) DEFAULT '$', default_tax_rate FLOAT DEFAULT 0.0);",
        # New Financials
        "ALTER TABLE products ADD COLUMN cost_price FLOAT DEFAULT 0.0;",
        "CREATE TABLE IF NOT EXISTS expenses (id INT AUTO_INCREMENT PRIMARY KEY, description VARCHAR(200) NOT NULL, amount FLOAT NOT NULL, category VARCHAR(50) DEFAULT 'Operational', date DATETIME DEFAULT CURRENT_TIMESTAMP);"
    ]

    for cmd in commands:
        try:
            cursor.execute(cmd)
            print(f"Executed: {cmd}")
        except mysql.connector.Error as err:
            if err.errno == 1060: # Duplicate column name
                print(f"Column already exists: {cmd}")
            else:
                print(f"Error executing {cmd}: {err}")

    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
