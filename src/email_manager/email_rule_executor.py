import sqlite3
from typing import List, Dict
import json
from email_manager.email_manager import EmailManager
from datetime import datetime, timedelta
import logging

class EmailRuleExecutor:
    def __init__(self, db_path: str = 'database/email.db', rules_path: str = 'rules.json'):
        self.db_path = db_path
        self.manager = EmailManager()
        self.rules = self._load_rules(rules_path)
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _load_rules(self, rules_path: str) -> Dict:
        """Load rules from JSON file"""
        try:
            with open(rules_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading rules: {e}")
            return {"rules": []}

    def get_recent_emails(self, limit: int = 5) -> List[Dict]:
        """Get the most recent emails from SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    id,
                    message_id,
                    from_address,
                    to_address,
                    subject,
                    message,
                    received_at,
                    is_read,
                    label
                FROM emails 
                ORDER BY id DESC 
                LIMIT ?
            """, (limit,))
            
            columns = ['id', 'message_id', 'from_address', 'to_address', 'subject', 
                      'message', 'received_at', 'is_read', 'label']
            emails = []
            
            for row in cursor.fetchall():
                email_dict = dict(zip(columns, row))
                emails.append(email_dict)
                
            return emails
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def _evaluate_condition(self, email: Dict, condition: Dict) -> bool:
        """Evaluate a single condition against an email"""
        field_value = {
            'from': email['from_address'],
            'to': email['to_address'],
            'subject': email['subject'],
            'message': email['message'],
            'received': email['received_at']
        }.get(condition['field'])
        print(field_value)
        if not field_value:
            return False

        if condition['field'] == 'received':
            email_date = datetime.strptime(field_value, '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()
            
            value_parts = condition['value'].split('_')
            number = int(value_parts[0])
            unit = value_parts[1]
            
            if unit == 'day':
                delta = timedelta(days=number)
            elif unit == 'month':
                delta = timedelta(days=number * 30)
            
            if condition['predicate'] == 'less_than':
                return (current_time - email_date) < delta
            elif condition['predicate'] == 'greater_than':
                return (current_time - email_date) > delta
        else:
            if condition['predicate'] == 'contains':
                return condition['value'].lower() in field_value.lower()
            elif condition['predicate'] == 'does_not_contain':
                return condition['value'].lower() not in field_value.lower()
            elif condition['predicate'] == 'equals':
                return condition['value'].lower() == field_value.lower()
            elif condition['predicate'] == 'does_not_equal':
                return condition['value'].lower() != field_value.lower()

        return False

    def _evaluate_rule(self, email: Dict, rule: Dict) -> bool:
        """Evaluate all conditions in a rule against an email"""
        results = [
            self._evaluate_condition(email, condition)
            for condition in rule['conditions']
        ]
        
        if rule['match_type'] == 'all':
            return all(results)
        return any(results)

    def _apply_actions(self, email_id: str, actions: List[Dict]) -> None:
        """Apply all actions for a matching rule"""
        for action in actions:
            try:
                if action['type'] == 'move':
                    success = self.manager.move_to_label(email_id, action['value'])
                    self.logger.info(
                        f"Moved email {email_id} to {action['value']}: "
                        f"{'Success' if success else 'Failed'}"
                    )
                    
                elif action['type'] == 'mark_as':
                    if action['value'] == 'read':
                        success = self.manager.mark_as_read(email_id)
                        self.logger.info(
                            f"Marked email {email_id} as read: "
                            f"{'Success' if success else 'Failed'}"
                        )
                    elif action['value'] == 'unread':
                        success = self.manager.mark_as_unread(email_id)
                        self.logger.info(
                            f"Marked email {email_id} as unread: "
                            f"{'Success' if success else 'Failed'}"
                        )
                        
            except Exception as e:
                self.logger.error(f"Error applying action {action}: {e}")

    def process_emails(self, limit: int = 5) -> None:
        """Process recent emails against all rules"""
        emails = self.get_recent_emails(limit)
        
        self.logger.info(f"Processing {len(emails)} recent emails")
        
        for email in emails:
            for rule in self.rules['rules']:
                try:
                    if self._evaluate_rule(email, rule):
                        self.logger.info(
                            f"Rule '{rule['name']}' matched for email: "
                            f"{email['subject']}"
                        )
                        self._apply_actions(email['message_id'], rule['actions'])
                except Exception as e:
                    self.logger.error(
                        f"Error processing rule '{rule['name']}' "
                        f"for email {email['message_id']}: {e}"
                    )

