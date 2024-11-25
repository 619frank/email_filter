import logging
from typing import List, Dict, Optional, Union
from auth.authenticator import GmailAuthenticator
from utils.email_parser import EmailParser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gmail_fetcher.log'),
        logging.StreamHandler()
    ]
)

class GmailManager:
    def __init__(self, config_path: str = 'configs/config.yaml'):
        self.logger = logging.getLogger(__name__)
        self.authenticator = GmailAuthenticator(config_path)
        self.user_id = 'me'
        self.email_parser = EmailParser()

    def get_messages(self, max_results: int = 10, query: str = '') -> List[Dict[str, str]]:
        """Fetches emails from Gmail based on the search query."""
        try:
            service = self.authenticator.authenticate()
            
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                parsed_email = self.email_parser.parse_message(msg)
                print(parsed_email['message_id'])
                emails.append(parsed_email)

            return emails

        except Exception as e:
            self.logger.error(f"Error fetching messages: {str(e)}")
            return []
        
    def _get_label_id(self, label_name: str) -> str:
        """
        Get Gmail label ID from label name
        Creates the label if it doesn't exist
        """
        try:
            # List all labels
            service = self.authenticator.authenticate()
            results = service.users().labels().list(userId=self.user_id).execute()
            labels = results.get('labels', [])

            # Search for existing label
            for label in labels:
                if label['name'].upper() == label_name.upper():
                    return label['id']

            # Create new label if it doesn't exist
            label_object = {
                'name': label_name.upper(),
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = self.service.users().labels().create(
                userId=self.user_id,
                body=label_object
            ).execute()
            
            return created_label['id']

        except Exception as e:
            self.logger.error(f"Error getting/creating label: {e}")
            raise  
    
    def modify_messages(self, 
                   message_ids: Union[str, List[str]], 
                   add_labels: List[str] = None,
                   remove_labels: List[str] = None) -> bool:
        """
        Modify Gmail messages one by one by adding or removing labels
        
        Args:
            message_ids: Single message ID or list of message IDs
            add_labels: List of label names to add
            remove_labels: List of label names to remove
            
        Returns:
            bool: True if all modifications were successful, False otherwise
        """
        if isinstance(message_ids, str):
            message_ids = [message_ids]
            
        if not add_labels:
            add_labels = []
        if not remove_labels:
            remove_labels = []

        try:
            # Convert label names to label IDs
            add_label_ids = [self._get_label_id(label) for label in add_labels]
            remove_label_ids = [self._get_label_id(label) for label in remove_labels]

            service = self.authenticator.authenticate()
            success_count = 0

            # Process each message individually
            for message_id in message_ids:
                try:
                    # Prepare modification body
                    modify_body = {
                        'addLabelIds': add_label_ids,
                        'removeLabelIds': remove_label_ids
                    }

                    # Modify message
                    service.users().messages().modify(
                        userId=self.user_id,
                        id=message_id,
                        body=modify_body
                    ).execute()

                    success_count += 1
                    self.logger.info(
                        f"Successfully modified message {message_id}: "
                        f"Added labels {add_labels}, Removed labels {remove_labels}"
                    )

                except HttpError as e:
                    self.logger.error(
                        f"Error modifying message {message_id}: {str(e)}"
                    )
                    continue
                except Exception as e:
                    self.logger.error(
                        f"Unexpected error modifying message {message_id}: {str(e)}"
                    )
                    continue

            return success_count == len(message_ids)

        except Exception as e:
            self.logger.error(f"Error in modify_messages: {str(e)}")
            return False
        
    # def modify_messages(self, 
    #                 message_ids: Union[str, List[str]], 
    #                 add_labels: List[str] = None,
    #                 remove_labels: List[str] = None) -> bool:
    #     """
    #     Modify Gmail messages one by one by adding or removing labels
        
    #     Args:
    #         message_ids: Single message ID or list of message IDs
    #         add_labels: List of label names to add
    #         remove_labels: List of label names to remove
            
    #     Returns:
    #         bool: True if all modifications were successful, False otherwise
    #     """
    #     if isinstance(message_ids, str):
    #         message_ids = [message_ids]
            
    #     if not add_labels:
    #         add_labels = []
    #     if not remove_labels:
    #         remove_labels = []

    #     try:
    #         # Convert label names to label IDs
    #         add_label_ids = [self._get_label_id(label) for label in add_labels]
    #         remove_label_ids = [self._get_label_id(label) for label in remove_labels]

    #         service = self.authenticator.authenticate()
    #         success_count = 0

    #         # Process each message individually
    #         for message_id in message_ids:
    #             try:
    #                 # First, get current labels
    #                 msg = service.users().messages().get(
    #                     userId=self.user_id,
    #                     id=message_id,
    #                     format='minimal'
    #                 ).execute()
                    
    #                 # Current labels
    #                 current_labels = msg.get('labelIds', [])
                    
    #                 # Remove specified labels
    #                 new_labels = [label for label in current_labels 
    #                             if label not in remove_label_ids]
                    
    #                 # Add new labels (avoid duplicates)
    #                 new_labels.extend(label for label in add_label_ids 
    #                                 if label not in new_labels)

    #                 # Modify message
    #                 service.users().messages().modify(
    #                     userId=self.user_id,
    #                     id=message_id,
    #                     body={'removeLabelIds': [], 'labelIds': new_labels}
    #                 ).execute()

    #                 success_count += 1
    #                 self.logger.info(
    #                     f"Successfully modified message {message_id}: "
    #                     f"Added labels {add_labels}, Removed labels {remove_labels}"
    #                 )

    #             except Exception as e:
    #                 self.logger.error(
    #                     f"Error modifying message {message_id}: {str(e)}"
    #                 )
    #                 continue
    #             except Exception as e:
    #                 self.logger.error(
    #                     f"Unexpected error modifying message {message_id}: {str(e)}"
    #                 )
    #                 continue

    #         return success_count == len(message_ids)

    #     except Exception as e:
    #         self.logger.error(f"Error in modify_messages: {str(e)}")
    #         return False      
        
