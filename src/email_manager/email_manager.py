import sqlite3
from typing import List, Union
from gmail.gmail_manager import GmailManager
import logging

class EmailManager:
    def __init__(self, db_path: str = 'database/email.db'):
        self.db_path = db_path
        self.gmail = GmailManager()
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _update_local_db(self, email_ids: Union[str, List[str]], 
                        updates: dict) -> bool:
        """Update email records in local database"""
        if isinstance(email_ids, str):
            email_ids = [email_ids]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build the UPDATE query dynamically based on provided updates
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            placeholders = list(updates.values()) + email_ids
            
            cursor.execute(f"""
                UPDATE emails 
                SET {set_clause}
                WHERE id IN ({','.join(['?'] * len(email_ids))})
            """, placeholders)
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def mark_as_read(self, email_ids: Union[str, List[str]]) -> bool:
        """Mark emails as read in both Gmail and local database"""
        try:
            # Mark as read in Gmail
            success = self.gmail.modify_messages(
                message_ids=email_ids,
                add_labels=['UNREAD'],
                remove_labels=[]
            )
            
            if success:
                # Update local database
                return self._update_local_db(email_ids, {'is_read': 1})
            return False
            
        except Exception as e:
            self.logger.error(f"Error marking emails as read: {e}")
            return False

    def mark_as_unread(self, email_ids: Union[str, List[str]]) -> bool:
        """Mark emails as unread in both Gmail and local database"""
        try:
            # Mark as unread in Gmail
            success = self.gmail.modify_messages(
                message_ids=email_ids,
                add_labels=['UNREAD'],
                remove_labels=[]
            )
            
            if success:
                # Update local database
                return self._update_local_db(email_ids, {'is_read': 0})
            return False
            
        except Exception as e:
            self.logger.error(f"Error marking emails as unread: {e}")
            return False

    def move_to_label(self, email_ids: Union[str, List[str]], 
                     new_label: str, 
                     remove_current: bool = True) -> bool:
        """Move emails to a different label"""
        try:
            # Convert Gmail label format (e.g., "important" to "IMPORTANT")
            gmail_label = new_label.upper()
            
            # Prepare labels to remove if requested
            remove_labels = ['INBOX'] if remove_current else []
            
            # Move in Gmail
            success = self.gmail.modify_messages(
                message_ids=email_ids,
                add_labels=[gmail_label],
                remove_labels=remove_labels
            )
            
            if success:
                # Update local database
                return self._update_local_db(email_ids, {'label': new_label.lower()})
            return False
            
        except Exception as e:
            self.logger.error(f"Error moving emails to label {new_label}: {e}")
            return False

    def get_email_ids_by_query(self, query: str) -> List[str]:
        """Get email IDs from local database based on a query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id FROM emails 
                WHERE subject LIKE ? OR from_address LIKE ? OR message LIKE ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            
            return [str(row[0]) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return []
        finally:
            conn.close()
