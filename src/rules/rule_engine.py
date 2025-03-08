import json
from datetime import datetime, timedelta
from src.database import EmailDatabase
from src.api import gmailApi

class RuleEngine:
    FIELD_PREDICATES = {
        'from': ['contains', 'does_not_contain', 'equals', 'does_not_equal'],
        'subject': ['contains', 'does_not_contain', 'equals', 'does_not_equal'],
        'message': ['contains', 'does_not_contain', 'equals', 'does_not_equal'],
        'date_received': ['less_than', 'greater_than']
    }

    def __init__(self, rules_file='config/rules.json'):
        self.rules = self._load_rules(rules_file)
        self.gmail = gmailApi()
        self.db = EmailDatabase()

    def _load_rules(self, rules_file):
        with open(rules_file, 'r') as f:
            return json.load(f)['rules']

    def check_condition(self, condition, email):
        field = condition['field']
        predicate = condition['predicate']
        value = condition['value']

        if field == 'date_received':
            email_date = datetime.strptime(email['date'], '%a, %d %b %Y %H:%M:%S %z')
            days = int(value)
            threshold = datetime.now(email_date.tzinfo) - timedelta(days=days)
            print(days,email_date,threshold)
            
            if predicate == 'less_than':
                return email_date > threshold
            elif predicate == 'greater_than':
                return email_date < threshold
        else:
            email_value = str(email.get(field, '')).lower()
            value = str(value).lower()

            if predicate == 'contains':
                return value in email_value
            elif predicate == 'does_not_contain':
                return value not in email_value
            elif predicate == 'equals':
                return value == email_value
            elif predicate == 'does_not_equal':
                return value != email_value

        return False

    def evaluate_rule(self, rule, email):
        predicate_type = rule['predicate_type']
        conditions = rule['conditions']
        
        results = [self.check_condition(condition, email) for condition in conditions]
        
        if predicate_type == 'all':
            return all(results)
        elif predicate_type == 'any':
            return any(results)
        return False

    def execute_actions(self, actions, email):
        for action in actions:
            action_type = action['type']
            
            if action_type == 'mark_as_read':
                if self.gmail.mark_as_read(email['id']):
                    self.db.update_email_status(email['id'], is_read=True)
                    
            elif action_type == 'mark_as_unread':
                if self.gmail.mark_as_unread(email['id']):
                    self.db.update_email_status(email['id'], is_read=False)
                    
            elif action_type == 'move_message':
                if self.gmail.move_message(email['id'], action['folder']):
                    self.db.update_email_status(email['id'], folder_name=action['folder'])
                self.gmail.move_message(email['id'], action['folder'])

    def process_emails(self, count=None):
        emails = self.db.get_all_emails()
        if count:
            emails = emails[:count]
        
        for email in emails:
            email_dict = {
                'id': email.id,
                'from': email.sender,
                'subject': email.subject,
                'message': email.body,
                'date': email.date,
                'is_read': email.is_read,
                'folder_name': email.folder_name
            }
            
            for rule in self.rules:
                if self.evaluate_rule(rule, email_dict):
                    print(f"Rule '{rule['name']}' matched for email: {email.subject}")
                    self.execute_actions(rule['actions'], email_dict)
        
    def close(self):
        self.db.close()