# Email Processing Application

A Python application that downloads Gmail messages and applies filters both locally and in Gmail. The application consists of two main scripts for fetching and processing emails using the Gmail API.

## Project Structure

```
src/
├── fetch_emails.py     # Downloads latest 5 messages to SQLite
├── process_emails.py   # Applies filters to local DB and Gmail
└── database/
    └── migration.py    # Sets up SQLite database schema
```

## Prerequisites

- Python 3.x
- SQLite
- Windows OS (tested environment)

## Required Libraries

- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Set up Python virtual environment:
   ```bash
   python -m pip install --user virtualenv
   python -m virtualenv .
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source Scripts/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Create and set up the database:
   ```bash
   cd src/database
   python migration.py
   ```

2. Fetch recent emails:
   ```bash
   cd src
   python fetch_emails.py
   ```

3. Apply email filters:
   ```bash
   python process_emails.py
   ```

## Script Details

### fetch_emails.py
- Downloads the latest 5 messages from Gmail
- Stores the messages in SQLite database
- Requires Gmail API authentication

### process_emails.py
- Applies filtering rules to emails stored in local SQLite database
- Synchronizes filters with Gmail
- Processes emails according to defined criteria

## Database

The application uses SQLite for local storage:
- Located in the project directory
- Schema created through migration script
- Stores email metadata and content

## Notes

- The application has been tested on Windows environments
- Make sure to configure Gmail API credentials before running
- The virtual environment must be activated before running any scripts