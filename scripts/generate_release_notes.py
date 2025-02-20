import subprocess
import requests
import json
import os
import sys
import re
from datetime import datetime
from templates.release_notes_template import (
    RELEASE_TEMPLATE, 
    format_ticket_list, 
    format_section,
    format_feature_with_ticket
)

COMMIT_CATEGORIES = {
    'feat': 'new_features',
    'fix': 'bug_fixes',
    'api': 'api_changes',
    'sec': 'security_updates',
    'prod': 'product_changes',
    'app': 'app_updates',
    'ux': 'ux_changes'
}

def parse_commit_message(message):
    """Parse commit message to extract category, description, and JIRA ticket."""
    category = 'other'
    jira_ticket = None
    description = message

    # Extract JIRA ticket
    jira_match = re.search(r'([A-Z]+-\d+)', message)
    if jira_match:
        jira_ticket = jira_match.group(1)
        # Clean up the description by removing the ticket reference
        description = re.sub(r'\[?'+jira_ticket+r'\]?\s*[|-]?\s*', '', description).strip()

    # Determine category from common prefixes and keywords
    lower_msg = message.lower()
    for key, value in COMMIT_CATEGORIES.items():
        if key in lower_msg or value.replace('_', ' ') in lower_msg:
            category = key
            break

    return category, description, jira_ticket

def get_git_log(start_tag, end_tag):
    try:
        # First check if tags exist
        check_tag_cmd = ['git', 'tag', '-l']
        result = subprocess.run(check_tag_cmd, capture_output=True, text=True, check=True)
        existing_tags = set(result.stdout.strip().split('\n'))

        if start_tag not in existing_tags:
            print(f"❌ Start tag '{start_tag}' not found in repository")
            print("Available tags:", ', '.join(sorted(existing_tags)))
            sys.exit(1)
        if end_tag not in existing_tags:
            print(f"❌ End tag '{end_tag}' not found in repository")
            print("Available tags:", ', '.join(sorted(existing_tags)))
            sys.exit(1)

        # Get git log between tags with pretty formatting
        cmd = [
            'git', 'log', 
            f'{start_tag}..{end_tag}',
            '--pretty=format:%h|%an|%s|%b'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting git log: {e}")
        print(f"Error output: {e.stderr}")
        if "fatal: not a git repository" in e.stderr:
            print("❌ Current directory is not a git repository")
        sys.exit(1)

def categorize_commits(git_log):
    """Categorize commits and collect JIRA tickets."""
    categories = {
        'new_features': [],
        'bug_fixes': [],
        'api_changes': [],
        'security_updates': [],
        'product_changes': [],
        'app_updates': [],
        'ux_changes': [],
        'other': []
    }
    jira_tickets = set()

    for line in git_log.split('\n'):
        if not line.strip():
            continue

        try:
            commit_hash, author, subject, body = line.split('|', 3)
            category, description, ticket = parse_commit_message(f"{subject}\n{body}")

            if ticket:
                jira_tickets.add(ticket)

            feature_text = format_feature_with_ticket(description, ticket)
            if category in COMMIT_CATEGORIES:
                categories[COMMIT_CATEGORIES[category]].append(feature_text)
            else:
                categories['other'].append(feature_text)

        except ValueError:
            continue

    return categories, jira_tickets

def determine_release_type(categories):
    """Determine if release is major, minor, or patch."""
    if categories['api_changes'] or categories['security_updates']:
        return "Major"
    if categories['new_features']:
        return "Minor"
    return "Patch"

def format_release_notes(git_log, version):
    categories, jira_tickets = categorize_commits(git_log)
    release_type = determine_release_type(categories)

    content = RELEASE_TEMPLATE.format(
        version=version,
        owner=os.getenv('RELEASE_OWNER', 'Release Team'),
        last_updated=datetime.now().strftime('%b %d, %Y'),
        release_type=release_type,
        new_features=format_section(categories['new_features']),
        product_changes=format_section(categories['product_changes']),
        bug_fixes=format_section(categories['bug_fixes']),
        app_updates=format_section(categories['app_updates']),
        api_changes=format_section(categories['api_changes']),
        ux_changes=format_section(categories['ux_changes']),
        security_updates=format_section(categories['security_updates']),
        backward_compatible="Yes" if release_type != "Major" else "No",
        upgrade_steps="<p>Run Github Action workflow of client</p>",
        rollback_steps="<p>Run Github Action workflow of client with backward compatible version</p>",
        major_rollback_steps="<p>N/A - " + ("release type " + release_type.lower() if release_type != "Major" else "See rollback steps above") + "</p>",
        dependencies="<p>N/A</p>",
        jira_tickets=format_ticket_list(sorted(jira_tickets))
    )

    return content

def create_confluence_page(content):
    base_url = os.getenv('CONFLUENCE_BASE_URL')
    api_user = os.getenv('CONFLUENCE_API_USER')
    api_token = os.getenv('CONFLUENCE_API_TOKEN')
    space_key = os.getenv('SPACE_KEY')
    page_title = os.getenv('PAGE_TITLE')
    ancestor = os.getenv('ANCESTOR_ID')

    # Validate all required environment variables are present and not None
    if not all([base_url, api_user, api_token, space_key, page_title, ancestor]):
        print("❌ Missing required environment variables")
        if not base_url:
            print("Missing CONFLUENCE_BASE_URL")
        if not api_user:
            print("Missing CONFLUENCE_API_USER")
        if not api_token:
            print("Missing CONFLUENCE_API_TOKEN")
        if not space_key:
            print("Missing SPACE_KEY")
        if not page_title:
            print("Missing PAGE_TITLE")
        if not ancestor:
            print("Missing ANCESTOR_ID")
        return False

    url = f"{base_url}/rest/api/content"

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "type": "page",
        "title": page_title,
        "space": {"key": space_key},
        "ancestors": [{"id": ancestor}],
        "body": {
            "storage": {
                "value": content,
                "representation": "storage",
            }
        },
    }

    try:
        # Only proceed with the request if we have valid credentials
        if not (isinstance(api_user, str) and isinstance(api_token, str)):
            print("❌ Invalid API credentials format")
            return False

        response = requests.post(
            url,
            headers=headers,
            auth=(api_user, api_token),  # Now we know these are strings
            data=json.dumps(data),
        )

        response.raise_for_status()

        page_url = f"{base_url}{response.json().get('_links', {}).get('webui', '')}"
        print("✅ Page created successfully!")
        print(f"📄 Page URL: {page_url}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create Confluence page: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def main():
    start_tag = os.getenv('START_TAG')
    end_tag = os.getenv('END_TAG')

    if not all([start_tag, end_tag]):
        print("❌ Missing required tags")
        sys.exit(1)

    print(f"🔍 Generating release notes from {start_tag} to {end_tag}")

    # Get git log
    git_log = get_git_log(start_tag, end_tag)

    if not git_log:
        print("❌ No changes found between tags")
        sys.exit(1)

    # Format content for Confluence
    confluence_content = format_release_notes(git_log, end_tag)

    # Create Confluence page
    if not create_confluence_page(confluence_content):
        sys.exit(1)

if __name__ == "__main__":
    main()
