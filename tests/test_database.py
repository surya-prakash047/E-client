import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.database.models import EmailDatabase, Email, Attachment

class TestEmailDatabase(unittest.TestCase):
    def setUp(self):
        self.db = EmailDatabase()
        self.test_email_data = {
            'id': 'test123',
            'subject': 'Test Subject',
            'snippet': 'Test snippet',
            'from': 'sender@test.com',
            'to': 'recipient@test.com',
            'date': 'Thu, 1 Jan 2024 10:00:00 +0000',
            'body': 'Test email body',
            'has_attachment': True,
            'attachment_types': ['application/pdf', 'image/jpeg'],
            'is_read': False,
            'folder_name': 'INBOX'
        }

    def tearDown(self):
        self.db.session.query(Email).delete()
        self.db.session.query(Attachment).delete()
        self.db.session.commit()
        self.db.close()

    def test_store_email(self):
        # Test storing email with attachments
        result = self.db.store_email(self.test_email_data)
        self.assertTrue(result)
        
        # Verify email was stored
        stored_email = self.db.session.query(Email).filter_by(id='test123').first()
        self.assertIsNotNone(stored_email)
        self.assertEqual(stored_email.subject, 'Test Subject')
        self.assertEqual(len(stored_email.attachments), 2)

    def test_store_email_without_attachment(self):
        email_data = self.test_email_data.copy()
        email_data['has_attachment'] = False
        del email_data['attachment_types']
        
        result = self.db.store_email(email_data)
        self.assertTrue(result)
        
        stored_email = self.db.session.query(Email).filter_by(id='test123').first()
        self.assertIsNotNone(stored_email)
        self.assertEqual(len(stored_email.attachments), 0)

    def test_get_all_emails(self):
        # Store multiple test emails
        email_data1 = self.test_email_data.copy()
        email_data2 = self.test_email_data.copy()
        email_data2['id'] = 'test456'
        email_data2['date'] = 'Thu, 2 Jan 2024 10:00:00 +0000'
        
        self.db.store_email(email_data1)
        self.db.store_email(email_data2)
        
        emails = self.db.get_all_emails()
        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0].id, 'test456')  # Should be newest first

    def test_update_email_status(self):
        self.db.store_email(self.test_email_data)
        
        # Test marking as read
        result = self.db.update_email_status('test123', is_read=True)
        self.assertTrue(result)
        
        updated_email = self.db.session.query(Email).filter_by(id='test123').first()
        self.assertTrue(updated_email.is_read)
        
        # Test moving to different folder
        result = self.db.update_email_status('test123', folder_name='ARCHIVE')
        self.assertTrue(result)
        
        updated_email = self.db.session.query(Email).filter_by(id='test123').first()
        self.assertEqual(updated_email.folder_name, 'ARCHIVE')

    def test_get_attachment_stats(self):
        self.db.store_email(self.test_email_data)
        
        stats = self.db.get_attachment_stats()
        self.assertEqual(len(stats), 2)
        
        mime_types = [stat[0] for stat in stats]
        self.assertIn('application/pdf', mime_types)
        self.assertIn('image/jpeg', mime_types)

    def test_get_folder_stats(self):
        # Store emails in different folders
        email_data1 = self.test_email_data.copy()
        email_data2 = self.test_email_data.copy()
        email_data2['id'] = 'test456'
        email_data2['folder_name'] = 'ARCHIVE'
        
        self.db.store_email(email_data1)
        self.db.store_email(email_data2)
        
        # Test with count limit
        stats = self.db.get_folder_stats(count=2)
        self.assertEqual(len(stats), 2)
        
        # Test without count limit
        all_stats = self.db.get_folder_stats()
        self.assertEqual(len(all_stats), 2)

    def test_get_email_timing(self):
        self.db.store_email(self.test_email_data)
        
        timing = self.db.get_email_timing()
        self.assertEqual(len(timing), 1)
        self.assertEqual(timing[0][0], self.test_email_data['date'])

    def test_error_handling(self):
        # Test with invalid email data
        invalid_email = {'id': 'invalid'}
        result = self.db.store_email(invalid_email)
        self.assertFalse(result)
        
        # Test updating non-existent email
        result = self.db.update_email_status('nonexistent', is_read=True)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()