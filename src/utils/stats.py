from src.database import EmailDatabase

class EmailStats:
    def __init__(self):
        self.reset_stats()
        self.db = EmailDatabase()

    def reset_stats(self):
        self.total_count = 0
        self.read_count = 0
        self.unread_count = 0
        self.attachment_count = 0
        self.folder_distribution = {}

    def update_from_emails(self, emails):
        self.total_count = len(emails)
        self.read_count = sum(1 for email in emails if email['is_read'])
        self.unread_count = self.total_count - self.read_count
        self.attachment_count = sum(1 for email in emails if email['has_attachment'])
        
        # Update folder distribution
        self.folder_distribution.clear()
        for email in emails:
            for label in email['labels']:
                self.folder_distribution[label] = self.folder_distribution.get(label, 0) + 1

    def mark_all_read(self, count):
        self.read_count = count
        self.unread_count = 0

    def mark_all_unread(self, count):
        self.read_count = 0
        self.unread_count = count


    def get_basic_stats(self):
        return {
            'total': self.total_count,
            'read': self.read_count,
            'attachments': self.attachment_count
        }

    def __del__(self):
        self.db.close()