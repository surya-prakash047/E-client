import unittest
from unittest.mock import patch
import sys
from main import main

class TestMainArguments(unittest.TestCase):
    @patch('main.gmailApi')
    @patch('main.EmailDatabase')
    @patch('main.RuleEngine')
    def test_count_argument(self, mock_rule_engine, mock_db, mock_gmail):
        # Test default count
        with patch('sys.argv', ['main.py']):
            main()
            mock_gmail.return_value.fetch_emails.assert_called_with(count=10)

        # Test custom count
        with patch('sys.argv', ['main.py', '-c', '5']):
            main()
            mock_gmail.return_value.fetch_emails.assert_called_with(count=5)

        # Test long form argument
        with patch('sys.argv', ['main.py', '--count', '15']):
            main()
            mock_gmail.return_value.fetch_emails.assert_called_with(count=15)

    @patch('main.gmailApi')
    @patch('main.EmailDatabase')
    @patch('main.RuleEngine')
    def test_refresh_argument(self, mock_rule_engine, mock_db, mock_gmail):
        mock_gmail.return_value.fetch_emails.return_value = [
            {'subject': 'Test Email', 'id': '123'}
        ]

        with patch('sys.argv', ['main.py', '--refresh']):
            main()
            mock_gmail.return_value.fetch_emails.assert_called_once()
            mock_db.return_value.store_email.assert_called_once()

    @patch('main.gmailApi')
    @patch('main.EmailDatabase')
    @patch('main.RuleEngine')
    def test_rules_argument(self, mock_rule_engine, mock_db, mock_gmail):
        with patch('sys.argv', ['main.py', '--rules']):
            main()
            mock_rule_engine.return_value.process_emails.assert_called_once()

    @patch('main.gmailApi')
    @patch('main.EmailDatabase')
    @patch('main.RuleEngine')
    @patch('main.display_email')
    def test_display_argument(self, mock_display, mock_rule_engine, mock_db, mock_gmail):
        mock_gmail.return_value.fetch_emails.return_value = [
            {'subject': 'Test Email', 'id': '123'}
        ]

        with patch('sys.argv', ['main.py', '--display']):
            main()
            mock_display.assert_called_once()
            mock_gmail.return_value.fetch_emails.assert_called_once()

    @patch('main.gmailApi')
    @patch('main.EmailDatabase')
    @patch('main.RuleEngine')
    def test_mark_read_argument(self, mock_rule_engine, mock_db, mock_gmail):
        mock_gmail.return_value.fetch_emails.return_value = [
            {'subject': 'Test Email', 'id': '123'}
        ]

        with patch('sys.argv', ['main.py', '--mark-read']):
            main()
            mock_gmail.return_value.mark_as_read.assert_called_once_with('123')

    @patch('main.gmailApi')
    @patch('main.EmailDatabase')
    @patch('main.RuleEngine')
    def test_mark_unread_argument(self, mock_rule_engine, mock_db, mock_gmail):
        mock_gmail.return_value.fetch_emails.return_value = [
            {'subject': 'Test Email', 'id': '123'}
        ]

        with patch('sys.argv', ['main.py', '--mark-unread']):
            main()
            mock_gmail.return_value.mark_as_unread.assert_called_once_with('123')

    @patch('main.gmailApi')
    @patch('main.EmailDatabase')
    @patch('main.RuleEngine')
    def test_multiple_arguments(self, mock_rule_engine, mock_db, mock_gmail):
        mock_gmail.return_value.fetch_emails.return_value = [
            {'subject': 'Test Email', 'id': '123'}
        ]

        with patch('sys.argv', ['main.py', '--refresh', '--rules', '-c', '5']):
            main()
            mock_gmail.return_value.fetch_emails.assert_called_with(count=5)
            mock_db.return_value.store_email.assert_called_once()
            mock_rule_engine.return_value.process_emails.assert_called_once()

    @patch('main.gmailApi')
    @patch('main.EmailDatabase')
    @patch('main.RuleEngine')
    def test_no_emails_found(self, mock_rule_engine, mock_db, mock_gmail):
        mock_gmail.return_value.fetch_emails.return_value = []

        with patch('sys.argv', ['main.py', '--refresh']):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_any_call("No emails found")
                mock_db.return_value.store_email.assert_not_called()

if __name__ == '__main__':
    unittest.main()