import json
from gmail_authenticator import GmailAuthenticator
from database_manager import DatabaseManager
from rule_engine import RuleEngine
import config

def load_rules(rules_file='rules.json'):
    try:
        with open(rules_file, 'r') as f:
            rules_data = json.load(f)
        return rules_data.get('rules', [])
    except FileNotFoundError:
        print(f"Rules file {rules_file} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing rules file: {e}")
        return []

def process_emails_with_rules(rules_file='rules.json'):
    # Setup Gmail service
    authenticator = GmailAuthenticator()
    service = authenticator.get_service()
    
    # Setup database
    db = DatabaseManager(config.DB_CONFIG)
    db.connect()
    
    # Load rules
    rules = load_rules(rules_file)
    if not rules:
        print("No rules to process")
        db.close()
        return
    
    print(f"Loaded {len(rules)} rule(s)")
    
    # Get emails from database
    emails = db.get_all_emails()
    print(f"Processing {len(emails)} emails against rules...")
    
    # Initialize rule engine
    engine = RuleEngine(db, service)
    
    matched_count = 0
    
    # Process each email against each rule
    for email in emails:
        for rule_idx, rule in enumerate(rules, 1):
            rule_name = rule.get('name', f'Rule {rule_idx}')
            
            if engine.check_rule(email, rule):
                print(f"\nEmail '{email.get('subject', '')[:50]}...' matched {rule_name}")
                actions = rule.get('actions', [])
                engine.execute_actions(email, actions)
                matched_count += 1
    
    print(f"\n{'='*50}")
    print(f"Processing complete!")
    print(f"Total emails processed: {len(emails)}")
    print(f"Rules matched: {matched_count}")
    print(f"{'='*50}")
    
    db.close()

def main():
    print("Starting rule-based email processing...")
    process_emails_with_rules()

if __name__ == '__main__':
    main()