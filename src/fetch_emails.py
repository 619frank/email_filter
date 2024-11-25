from database.email_repository import EmailDatabase
from gmail.gmail_manager import GmailManager

def main():
    gmail = GmailManager()
    db = EmailDatabase()

    emails = gmail.get_messages(
        max_results=5,
        query='after:2024/11/24'
    )
    
    # Insert emails into database
    inserted_count = db.insert_emails(emails)
    print(f"Successfully inserted {inserted_count} emails into the database.")
    
    print(emails[0].keys())

if __name__ == "__main__":
    main()