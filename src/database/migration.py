import sqlite3
from datetime import datetime

def create_email_schema():
    """
    Creates the email messages table in SQLite database
    """
    # Connect to SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect('email.db')
    cursor = conn.cursor()

    # Create the emails table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id TEXT NOT NULL,
        from_address TEXT NOT NULL,
        to_address TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read BOOLEAN DEFAULT 0,
        label TEXT DEFAULT 'inbox'
    )
    ''')

    # Create indexes for common query patterns
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_from_address ON emails(from_address)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_id ON emails(message_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_to_address ON emails(to_address)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_label ON emails(label)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_received_at ON emails(received_at)')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_email_schema()