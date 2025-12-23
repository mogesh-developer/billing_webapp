# Setup Guide for Grocery Billing App

## Prerequisites
1. **Python**: Ensure Python is installed.
2. **MySQL Server**: You need a running MySQL server.

## Installation Steps

1. **Install Dependencies**
   Open a terminal in this folder and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database**
   - Open your MySQL client (Workbench, Command Line, etc.).
   - Create a new database:
     ```sql
     CREATE DATABASE grocery_billing_db;
     ```
   - Open `config.py` in this folder.
   - Update the `SQLALCHEMY_DATABASE_URI` line with your MySQL username and password.
     ```python
     # Format: mysql+mysqlconnector://<username>:<password>@<host>/<database_name>
     SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost/grocery_billing_db'
     ```

3. **Run the Application**
   Run the following command:
   ```bash
   python app.py
   ```
   The application will start on `http://127.0.0.1:5000`.

## Features
- **Dashboard**: View sales overview.
- **Inventory**: Add and manage products (Name, Barcode, Price, Stock).
- **Billing**: Search/Scan products, add to bill, calculate total, and checkout.
