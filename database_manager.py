import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        
    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            return self.conn
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise
    
    def create_tables(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS emails (
            id SERIAL PRIMARY KEY,
            message_id VARCHAR(255) UNIQUE NOT NULL,
            thread_id VARCHAR(255),
            from_email VARCHAR(255),
            to_email TEXT,
            subject TEXT,
            message_body TEXT,
            received_date TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            labels TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_message_id ON emails(message_id);
        CREATE INDEX IF NOT EXISTS idx_from_email ON emails(from_email);
        CREATE INDEX IF NOT EXISTS idx_received_date ON emails(received_date);
        """
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_query)
            self.conn.commit()
            cursor.close()
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise
    
    def insert_email(self, email_data):
        insert_query = """
        INSERT INTO emails (message_id, thread_id, from_email, to_email, 
                          subject, message_body, received_date, is_read, labels)
        VALUES (%(message_id)s, %(thread_id)s, %(from_email)s, %(to_email)s,
                %(subject)s, %(message_body)s, %(received_date)s, %(is_read)s, %(labels)s)
        ON CONFLICT (message_id) DO UPDATE SET
            is_read = EXCLUDED.is_read,
            labels = EXCLUDED.labels;
        """
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(insert_query, email_data)
            self.conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error inserting email: {e}")
            self.conn.rollback()
    
    def get_all_emails(self):
        query = "SELECT * FROM emails ORDER BY received_date DESC"
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def update_email_status(self, message_id, is_read):
        query = "UPDATE emails SET is_read = %s WHERE message_id = %s"
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (is_read, message_id))
            self.conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error updating email status: {e}")
            self.conn.rollback()
    
    def close(self):
        if self.conn:
            self.conn.close()