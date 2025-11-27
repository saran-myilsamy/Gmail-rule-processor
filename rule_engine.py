from datetime import datetime, timedelta
import re

class RuleEngine:
    def __init__(self, db_manager, gmail_service):
        self.db = db_manager
        self.service = gmail_service
    
    def evaluate_condition(self, email, condition):
        field = condition.get('field')
        predicate = condition.get('predicate')
        value = condition.get('value')
        
        if field == 'from':
            email_value = email.get('from_email', '').lower()
        elif field == 'subject':
            email_value = email.get('subject', '').lower()
        elif field == 'message':
            email_value = email.get('message_body', '').lower()
        elif field == 'received':
            return self.evaluate_date_condition(email, predicate, value)
        else:
            return False
        
        value_lower = str(value).lower()
        
        if predicate == 'contains':
            return value_lower in email_value
        elif predicate == 'does_not_contain':
            return value_lower not in email_value
        elif predicate == 'equals':
            return email_value == value_lower
        elif predicate == 'does_not_equal':
            return email_value != value_lower
        
        return False
    
    def evaluate_date_condition(self, email, predicate, value):
        received_date = email.get('received_date')
        if not received_date:
            return False
        
        # Handle timezone-aware datetime
        if received_date.tzinfo is not None:
            now = datetime.now(received_date.tzinfo)
        else:
            now = datetime.now()
            if hasattr(received_date, 'replace'):
                received_date = received_date.replace(tzinfo=None)
        
        try:
            amount = int(value.get('amount', 0))
            unit = value.get('unit', 'days')
            
            if unit == 'days':
                delta = timedelta(days=amount)
            elif unit == 'months':
                delta = timedelta(days=amount * 30)
            else:
                return False
            
            threshold_date = now - delta
            
            if predicate == 'less_than':
                return received_date > threshold_date
            elif predicate == 'greater_than':
                return received_date < threshold_date
            
        except Exception as e:
            print(f"Date evaluation error: {e}")
            return False
        
        return False
    
    def check_rule(self, email, rule):
        conditions = rule.get('conditions', [])
        predicate_type = rule.get('predicate', 'all').lower()
        
        if not conditions:
            return False
        
        results = [self.evaluate_condition(email, cond) for cond in conditions]
        
        if predicate_type == 'all':
            return all(results)
        elif predicate_type == 'any':
            return any(results)
        
        return False
    
    def execute_actions(self, email, actions):
        message_id = email.get('message_id')
        
        for action in actions:
            action_type = action.get('type')
            
            try:
                if action_type == 'mark_as_read':
                    self.mark_as_read(message_id)
                    self.db.update_email_status(message_id, True)
                    print(f"Marked email {message_id[:10]}... as read")
                    
                elif action_type == 'mark_as_unread':
                    self.mark_as_unread(message_id)
                    self.db.update_email_status(message_id, False)
                    print(f"Marked email {message_id[:10]}... as unread")
                    
                elif action_type == 'move':
                    label = action.get('destination')
                    self.move_message(message_id, label)
                    print(f"Moved email {message_id[:10]}... to {label}")
                    
            except Exception as e:
                print(f"Error executing action {action_type}: {e}")
    
    def mark_as_read(self, message_id):
        self.service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
    
    def mark_as_unread(self, message_id):
        self.service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': ['UNREAD']}
        ).execute()
    
    def move_message(self, message_id, destination_label):
        # Get or create label
        label_id = self.get_or_create_label(destination_label)
        
        if label_id:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'addLabelIds': [label_id],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
    
    def get_or_create_label(self, label_name):
        try:
            # List existing labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']
            
            # Create new label if not found
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            return created_label['id']
            
        except Exception as e:
            print(f"Error with label {label_name}: {e}")
            return None