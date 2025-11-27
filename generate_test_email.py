import random
from datetime import datetime, timedelta
from database_manager import DatabaseManager
import config

class TestEmailGenerator:
    def __init__(self, db_manager):
        self.db = db_manager
        
    def generate_test_emails(self, count=20):
        """Generate realistic test emails for rule testing"""
        
        # Sample data pools
        from_emails = [
            'marketing@company.com',
            'newsletter@deals.com',
            'boss@workplace.com',
            'client@important.com',
            'support@service.com',
            'noreply@automated.com',
            'friend@personal.com',
            'sales@promotion.com',
            'hr@company.com',
            'updates@news.com'
        ]
        
        subjects = [
            'Weekly Newsletter - Special Offers Inside',
            'Important: Project Deadline Tomorrow',
            'Your monthly statement is ready',
            'RE: Meeting notes from yesterday',
            'Unsubscribe anytime - New products',
            'Urgent: Client needs response',
            'Team lunch this Friday?',
            'Marketing campaign results',
            'Your order has been shipped',
            'Quarterly review meeting invite',
            'Special discount just for you',
            'Important document attached',
            'Newsletter: This week in tech',
            'Automated report generated',
            'Follow up on our conversation'
        ]
        
        bodies = [
            'This is an automated marketing email with special offers.',
            'Hi, just following up on the project we discussed.',
            'Please review the attached document and provide feedback.',
            'Our weekly newsletter with the latest updates.',
            'This is an important client request that needs attention.',
            'Automated system notification - no reply needed.',
            'Hey! Want to grab lunch this week?',
            'Here are the results from last quarter.',
            'Your subscription renewal is coming up.',
            'Thanks for your purchase! Track your order here.',
            'Important security update for your account.',
            'Meeting reminder: Tomorrow at 2 PM',
            'Check out our new product line!',
            'Unsubscribe link at the bottom of this email.',
            'Your report has been generated successfully.'
        ]
        
        print(f"Generating {count} test emails...")
        
        for i in range(count):
            # Random date within last 6 months
            days_ago = random.randint(1, 180)
            received_date = datetime.now() - timedelta(days=days_ago)
            
            email_data = {
                'message_id': f'test_{i}_{random.randint(1000, 9999)}',
                'thread_id': f'thread_{random.randint(100, 999)}',
                'from_email': random.choice(from_emails),
                'to_email': 'test05121977@gmail.com',
                'subject': random.choice(subjects),
                'message_body': random.choice(bodies),
                'received_date': received_date,
                'is_read': random.choice([True, False]),
                'labels': ['INBOX']
            }
            
            self.db.insert_email(email_data)
            
            if (i + 1) % 5 == 0:
                print(f"Generated {i + 1}/{count} emails...")
        
        print(f"\n✅ Successfully generated {count} test emails!")
        print("\nSample distribution:")
        print(f"  - Marketing emails: ~{count // 4}")
        print(f"  - Old emails (>90 days): ~{count // 3}")
        print(f"  - Recent emails (<7 days): ~{count // 5}")
        print(f"  - Client emails: ~{count // 10}")
        
    def generate_specific_test_cases(self):
        """Generate specific emails to test each rule"""
        
        test_cases = [
            {
                'name': 'Marketing email with newsletter',
                'message_id': 'test_marketing_1',
                'thread_id': 'thread_m1',
                'from_email': 'marketing@shop.com',
                'to_email': 'me@myemail.com',
                'subject': 'Newsletter: Best deals this week',
                'message_body': 'Check out our amazing offers. Unsubscribe anytime.',
                'received_date': datetime.now() - timedelta(days=5),
                'is_read': False,
                'labels': ['INBOX']
            },
            {
                'name': 'Important client email (recent)',
                'message_id': 'test_client_1',
                'thread_id': 'thread_c1',
                'from_email': 'client@business.com',
                'to_email': 'me@myemail.com',
                'subject': 'Project update needed',
                'message_body': 'Can you provide an update on the project status?',
                'received_date': datetime.now() - timedelta(days=3),
                'is_read': True,
                'labels': ['INBOX']
            },
            {
                'name': 'Old email (4 months)',
                'message_id': 'test_old_1',
                'thread_id': 'thread_o1',
                'from_email': 'notifications@service.com',
                'to_email': 'me@myemail.com',
                'subject': 'Your monthly summary',
                'message_body': 'Here is your activity summary for the month.',
                'received_date': datetime.now() - timedelta(days=120),
                'is_read': False,
                'labels': ['INBOX']
            },
            {
                'name': 'Marketing from field contains marketing',
                'message_id': 'test_marketing_2',
                'thread_id': 'thread_m2',
                'from_email': 'noreply@marketing-team.com',
                'to_email': 'me@myemail.com',
                'subject': 'Special offer for you',
                'message_body': 'Limited time offer! Click here to unsubscribe.',
                'received_date': datetime.now() - timedelta(days=10),
                'is_read': False,
                'labels': ['INBOX']
            },
            {
                'name': 'Old important email (should not be archived)',
                'message_id': 'test_important_old',
                'thread_id': 'thread_io1',
                'from_email': 'boss@company.com',
                'to_email': 'me@myemail.com',
                'subject': 'Important: Annual review documents',
                'message_body': 'Please keep this for your records.',
                'received_date': datetime.now() - timedelta(days=100),
                'is_read': False,
                'labels': ['INBOX']
            },
            {
                'name': 'Recent automated email',
                'message_id': 'test_automated_1',
                'thread_id': 'thread_a1',
                'from_email': 'noreply@automated.com',
                'to_email': 'me@myemail.com',
                'subject': 'Automated report generated',
                'message_body': 'Your weekly automated report is ready.',
                'received_date': datetime.now() - timedelta(days=2),
                'is_read': False,
                'labels': ['INBOX']
            }
        ]
        
        print("\nGenerating specific test cases...\n")
        
        for test_case in test_cases:
            name = test_case.pop('name')
            self.db.insert_email(test_case)
            print(f"✓ Created: {name}")
        
        print(f"\n✅ Generated {len(test_cases)} specific test case emails!")
        print("\nThese emails are designed to test:")
        print("  1. Marketing email filtering (newsletter/unsubscribe)")
        print("  2. Important client emails (recent, non-automated)")
        print("  3. Old email cleanup (>3 months, not important)")
        print("  4. Edge cases and combinations")

def main():
    print("=" * 60)
    print("TEST EMAIL GENERATOR")
    print("=" * 60)
    
    db = DatabaseManager(config.DB_CONFIG)
    db.connect()
    db.create_tables()
    
    generator = TestEmailGenerator(db)
    
    print("\nChoose an option:")
    print("1. Generate 20 random test emails")
    print("2. Generate specific test case emails only")
    print("3. Generate both (recommended)")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == '1':
        generator.generate_test_emails(20)
    elif choice == '2':
        generator.generate_specific_test_cases()
    elif choice == '3':
        generator.generate_test_emails(20)
        generator.generate_specific_test_cases()
    else:
        print("Invalid choice. Exiting.")
    
    db.close()
    print("\n" + "=" * 60)
    print("Done! You can now run: python process_rules.py")
    print("=" * 60)

if __name__ == '__main__':
    main()