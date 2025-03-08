import argparse
from src.api.gmail_api import gmailApi
from src.database import EmailDatabase
from src.rules import RuleEngine

def display_email(email):
    print("\nEmail Details:")
    print(f"From: {email['from']}")
    print(f"To: {email['to']}")
    print(f"Subject: {email['subject']}")
    print(f"Date: {email['date']}")
    print(f"Labels: {email['labels']}")
    print(f"Is Read: {email['is_read']}")
    print(f"Snippet: {email['snippet']}")
    if email['has_attachment']:
        print(f"Attachment Types: {', '.join(email['attachment_types'])}")
    print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description='Email Client CLI')
    parser.add_argument('-c', '--count', type=int, default=10,
                      help='Number of emails to fetch (default: 10)')
    parser.add_argument('--refresh', action='store_true',
                      help='Refresh database with new emails')
    parser.add_argument('--display', action='store_true',
                      help='Display fetched emails')
    parser.add_argument('--mark-read', action='store_true',
                      help='Mark all fetched emails as read')
    parser.add_argument('--mark-unread', action='store_true',
                      help='Mark all fetched emails as unread')
    
    args = parser.parse_args()

    gmail = gmailApi()
    db = EmailDatabase()
    rule_engine = RuleEngine()

    try:
        if args.display:
            emails = gmail.fetch_emails(count=args.count)
            if emails:
                for email in emails:
                    display_email(email)
            return

        if args.mark_read or args.mark_unread:
            emails = gmail.fetch_emails(count=args.count)
            if emails:
                for email in emails:
                    if args.mark_read:
                        gmail.mark_as_read(email['id'])
                        print(f"Marked as read: {email['subject'][:50]}...")
                    if args.mark_unread:
                        gmail.mark_as_unread(email['id'])
                        print(f"Marked as unread: {email['subject'][:50]}...")
            return

        # Original functionality
        if args.refresh:
            print(f"Fetching {args.count} emails...")
            emails = gmail.fetch_emails(count=args.count)
            if not emails:
                print("No emails found")
                return

            print("\nStoring emails in database...")
            for email in emails:
                success = db.store_email(email)
                if success:
                    print(f"Stored/Updated email: {email['subject'][:50]}...")
                else:
                    print(f"Failed to store email: {email['subject'][:50]}...")


        if not args.refresh and not args.rules:
            emails = gmail.fetch_emails(count=args.count)
            if emails:
                for email in emails:
                    db.store_email(email)
                rule_engine.process_emails()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        db.close()
        rule_engine.close()

if __name__ == "__main__":
    main()