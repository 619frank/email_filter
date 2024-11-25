import base64
import email
from typing import Dict, Any

class EmailParser:
    @staticmethod
    def parse_message(msg: Dict[str, Any]) -> Dict[str, str]:
        """Parse Gmail API message into a structured format."""
        # print(msg.keys())
        # print(msg['id'])
        # print(msg['threadId'])
        # print(msg['labelIds'])
        message_id = msg['id']
        headers = msg['payload']['headers']
        subject = next(h['value'] for h in headers if h['name'].lower() == 'subject')
        sender = next(h['value'] for h in headers if h['name'].lower() == 'from')
        date = next(h['value'] for h in headers if h['name'].lower() == 'date')

        # Get email body
        if 'parts' in msg['payload']:
            parts = msg['payload']['parts']
            data = parts[0]['body'].get('data', '')
        else:
            data = msg['payload']['body'].get('data', '')

        body = base64.urlsafe_b64decode(data).decode('utf-8') if data else "No content"

        return {
            'message_id': message_id,
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body
        }