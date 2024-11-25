import sqlite3
from datetime import datetime
from typing import List, Dict
import logging

class EmailDatabase:
    def __init__(self, db_path: str = 'database/email.db'):
        self.db_path = db_path

    def insert_emails(self, emails: List[Dict]) -> int:
        """
        Insert emails into the database
        Returns the number of emails successfully inserted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        inserted_count = 0

        try:
            for email in emails:
                # Convert the email format from Gmail to our database schema
                email_data = {
                    'message_id': email['message_id'],
                    'from_address': email['sender'],
                    'to_address': email.get('recipient', ''),  # Add default in case recipient is missing
                    'subject': email['subject'],
                    'message': email['body'],
                    'received_at': email['date'],
                    'is_read': 0,  # Since query specified unread emails
                    'label': 'inbox'
                }

                cursor.execute('''
                INSERT INTO emails (
                    message_id, from_address, to_address, subject, message, 
                    received_at, is_read, label
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    email_data['message_id'],
                    email_data['from_address'],
                    email_data['to_address'],
                    email_data['subject'],
                    email_data['message'],
                    email_data['received_at'],
                    email_data['is_read'],
                    email_data['label']
                ))
                inserted_count += 1

            conn.commit()
            return inserted_count

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            conn.rollback()
            raise
        except Exception as e:
            logging.error(f"Error inserting emails: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
