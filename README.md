# Gmail Rule-Based Email Automation

This project is a standalone Python application that integrates with Gmail API to perform rule-based operations on emails. It fetches emails from your inbox, stores them in a PostgreSQL database, and processes them according to custom rules defined in a JSON file.

## Features

- **OAuth Authentication**: Secure authentication using Google's official Python client
- **Email Fetching**: Retrieves emails from Gmail inbox using REST API (not IMAP)
- **Database Storage**: Stores emails in PostgreSQL with proper indexing
- **Rule-Based Processing**: Flexible rule engine supporting multiple conditions and actions
- **Supported Conditions**:
  - String fields (From, Subject, Message): Contains, Does not Contain, Equals, Does not equal
  - Date field (Received): Less than / Greater than (days/months)
- **Supported Actions**:
  - Mark as read/unread
  - Move message to labels
- **Predicate Logic**: Support for "All" (AND) and "Any" (OR) rule predicates

## Project Structure
## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/saran-myilsamy/Gmail-rule-processor.git
cd Gmail-rule-processor
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

Create a new database:

```bash
psql -U postgres
CREATE DATABASE gmail_automation;
\q
```

### 5. Configure Environment Variables

Copy the example environment file and update it:

Edit `.env` with your database credentials:

```
DB_NAME=gmail_automation
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 6. Set Up Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as the application type
   - Download the credentials JSON file
5. Save the downloaded file as `credentials.json` in the project root directory

## Usage

### Step 1: Fetch Emails from Gmail

Run the fetch script to download emails and store them in the database:

```bash
python fetch_emails.py
```

This will:
- Authenticate with Gmail (opens browser for first-time authorization)
- Fetch up to 50 emails from your inbox
- Parse and store them in PostgreSQL
- Create necessary database tables automatically

### Step 2: Configure Rules

Edit `rules.json` to define your email processing rules. Here's an example:

```json
{
  "rules": [
    {
      "name": "Marketing Emails Auto-Archive",
      "predicate": "any",
      "conditions": [
        {
          "field": "from",
          "predicate": "contains",
          "value": "marketing"
        },
        {
          "field": "subject",
          "predicate": "contains",
          "value": "newsletter"
        }
      ],
      "actions": [
        {
          "type": "mark_as_read"
        },
        {
          "type": "move",
          "destination": "Marketing"
        }
      ]
    }
  ]
}
```

**Rule Structure:**

- `name`: Descriptive name for the rule
- `predicate`: "all" (AND logic) or "any" (OR logic)
- `conditions`: Array of conditions to match
  - `field`: "from", "subject", "message", or "received"
  - `predicate`: String predicates (contains, does_not_contain, equals, does_not_equal) or date predicates (less_than, greater_than)
  - `value`: String value or date object `{"amount": 7, "unit": "days"}`
- `actions`: Array of actions to execute
  - `type`: "mark_as_read", "mark_as_unread", or "move"
  - `destination`: Label name (for move action)

### Step 3: Process Emails with Rules

Run the processing script to apply rules to your emails:

```bash
python process_rules.py
```

This will:
- Load rules from `rules.json`
- Fetch all emails from the database
- Evaluate each email against each rule
- Execute actions for matching emails
- Update Gmail via API

## Running Tests

using unittest:

```bash
python -m unittest test_rule_engine.py
```

The test suite includes:
- Unit tests for condition evaluation
- Rule matching logic tests
- Date condition testing
- Mock API interaction tests
- Database integration tests

## Examples

### Example 1: Archive Old Promotional Emails

```json
{
  "name": "Old Promos Cleanup",
  "predicate": "all",
  "conditions": [
    {
      "field": "subject",
      "predicate": "contains",
      "value": "sale"
    },
    {
      "field": "received",
      "predicate": "greater_than",
      "value": {"amount": 1, "unit": "months"}
    }
  ],
  "actions": [
    {
      "type": "mark_as_read"
    },
    {
      "type": "move",
      "destination": "Archive"
    }
  ]
}
```

### Example 2: Flag Important Recent Emails

```json
{
  "name": "Recent Important",
  "predicate": "all",
  "conditions": [
    {
      "field": "from",
      "predicate": "contains",
      "value": "boss@company.com"
    },
    {
      "field": "received",
      "predicate": "less_than",
      "value": {"amount": 3, "unit": "days"}
    }
  ],
  "actions": [
    {
      "type": "mark_as_unread"
    }
  ]
}
```

## Database Schema

The application creates the following table structure:

```sql
CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    thread_id VARCHAR(255),
    from_email VARCHAR(255),
    to_email TEXT,
    subject TEXT,
    message_body TEXT,
    received_date TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    labels TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
