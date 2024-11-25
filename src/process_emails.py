from email_manager.email_rule_executor import EmailRuleExecutor

def main():
    # Initialize the executor
    executor = EmailRuleExecutor()
    
    # Process the 5 most recent emails
    executor.process_emails(limit=5)


if __name__ == "__main__":
    main()