import os

class Config:
    # Database Configuration
    # Replace 'root', 'password', 'localhost', 'grocery_billing_db' with your actual credentials
    # For now, we assume a standard local MySQL setup: user='root', password='', db='grocery_billing_db'
    # NOTE: You must create the database `grocery_billing_db` in MySQL manually before running the app.
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/grocery_billing_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
