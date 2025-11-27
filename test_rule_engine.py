import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from rule_engine import RuleEngine

class TestRuleEngine(unittest.TestCase):
    
    def setUp(self):
        self.mock_db = Mock()
        self.mock_service = Mock()
        self.engine = RuleEngine(self.mock_db, self.mock_service)
        
        self.sample_email = {
            'message_id': 'test123',
            'from_email': 'sender@example.com',
            'subject': 'Test Subject',
            'message_body': 'This is a test email body',
            'received_date': datetime.now()
        }
    
    def test_evaluate_condition_contains(self):
        condition = {
            'field': 'subject',
            'predicate': 'contains',
            'value': 'Test'
        }
        result = self.engine.evaluate_condition(self.sample_email, condition)
        self.assertTrue(result)
    
    def test_evaluate_condition_does_not_contain(self):
        condition = {
            'field': 'subject',
            'predicate': 'does_not_contain',
            'value': 'Random'
        }
        result = self.engine.evaluate_condition(self.sample_email, condition)
        self.assertTrue(result)
    
    def test_evaluate_condition_equals(self):
        condition = {
            'field': 'from',
            'predicate': 'equals',
            'value': 'sender@example.com'
        }
        result = self.engine.evaluate_condition(self.sample_email, condition)
        self.assertTrue(result)
    
    def test_evaluate_condition_does_not_equal(self):
        condition = {
            'field': 'from',
            'predicate': 'does_not_equal',
            'value': 'other@example.com'
        }
        result = self.engine.evaluate_condition(self.sample_email, condition)
        self.assertTrue(result)
    
    def test_evaluate_date_less_than(self):
        email = self.sample_email.copy()
        email['received_date'] = datetime.now() - timedelta(days=3)
        
        condition = {
            'field': 'received',
            'predicate': 'less_than',
            'value': {'amount': 7, 'unit': 'days'}
        }
        result = self.engine.evaluate_condition(email, condition)
        self.assertTrue(result)
    
    def test_evaluate_date_greater_than(self):
        email = self.sample_email.copy()
        email['received_date'] = datetime.now() - timedelta(days=100)
        
        condition = {
            'field': 'received',
            'predicate': 'greater_than',
            'value': {'amount': 2, 'unit': 'months'}
        }
        result = self.engine.evaluate_condition(email, condition)
        self.assertTrue(result)
    
    def test_check_rule_all_predicate_true(self):
        rule = {
            'predicate': 'all',
            'conditions': [
                {'field': 'subject', 'predicate': 'contains', 'value': 'Test'},
                {'field': 'from', 'predicate': 'contains', 'value': 'sender'}
            ]
        }
        result = self.engine.check_rule(self.sample_email, rule)
        self.assertTrue(result)
    
    def test_check_rule_all_predicate_false(self):
        rule = {
            'predicate': 'all',
            'conditions': [
                {'field': 'subject', 'predicate': 'contains', 'value': 'Test'},
                {'field': 'from', 'predicate': 'contains', 'value': 'wrong'}
            ]
        }
        result = self.engine.check_rule(self.sample_email, rule)
        self.assertFalse(result)
    
    def test_check_rule_any_predicate_true(self):
        rule = {
            'predicate': 'any',
            'conditions': [
                {'field': 'subject', 'predicate': 'contains', 'value': 'Test'},
                {'field': 'from', 'predicate': 'contains', 'value': 'wrong'}
            ]
        }
        result = self.engine.check_rule(self.sample_email, rule)
        self.assertTrue(result)
    
    def test_check_rule_any_predicate_false(self):
        rule = {
            'predicate': 'any',
            'conditions': [
                {'field': 'subject', 'predicate': 'contains', 'value': 'wrong1'},
                {'field': 'from', 'predicate': 'contains', 'value': 'wrong2'}
            ]
        }
        result = self.engine.check_rule(self.sample_email, rule)
        self.assertFalse(result)
    
    def test_mark_as_read_calls_api(self):
        mock_modify = MagicMock()
        self.mock_service.users().messages().modify = mock_modify
        
        self.engine.mark_as_read('test_message_id')
        
        mock_modify.assert_called_once()
        call_args = mock_modify.call_args
        self.assertEqual(call_args[1]['id'], 'test_message_id')
        self.assertIn('UNREAD', call_args[1]['body']['removeLabelIds'])
    
    def test_mark_as_unread_calls_api(self):
        mock_modify = MagicMock()
        self.mock_service.users().messages().modify = mock_modify
        
        self.engine.mark_as_unread('test_message_id')
        
        mock_modify.assert_called_once()
        call_args = mock_modify.call_args
        self.assertEqual(call_args[1]['id'], 'test_message_id')
        self.assertIn('UNREAD', call_args[1]['body']['addLabelIds'])
    
    def test_execute_actions_mark_as_read(self):
        actions = [{'type': 'mark_as_read'}]
        
        mock_modify = MagicMock()
        self.mock_service.users().messages().modify = mock_modify
        
        self.engine.execute_actions(self.sample_email, actions)
        
        mock_modify.assert_called_once()
        self.mock_db.update_email_status.assert_called_with('test123', True)
    
    def test_case_insensitive_matching(self):
        condition = {
            'field': 'subject',
            'predicate': 'contains',
            'value': 'TEST'
        }
        result = self.engine.evaluate_condition(self.sample_email, condition)
        self.assertTrue(result)

class TestDatabaseIntegration(unittest.TestCase):
    
    @patch('database_manager.psycopg2.connect')
    def test_database_connection(self, mock_connect):
        from database_manager import DatabaseManager
        
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        db_config = {
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass',
            'host': 'localhost',
            'port': '5432'
        }
        
        db = DatabaseManager(db_config)
        db.connect()
        
        mock_connect.assert_called_once_with(**db_config)
    
    @patch('database_manager.psycopg2.connect')
    def test_insert_email(self, mock_connect):
        from database_manager import DatabaseManager
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        db = DatabaseManager({})
        db.conn = mock_conn
        
        email_data = {
            'message_id': 'test123',
            'thread_id': 'thread123',
            'from_email': 'test@example.com',
            'to_email': 'recipient@example.com',
            'subject': 'Test',
            'message_body': 'Body',
            'received_date': datetime.now(),
            'is_read': False,
            'labels': ['INBOX']
        }
        
        db.insert_email(email_data)
        
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()