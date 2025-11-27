import os

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'gmail_automation'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'root@123'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}