import subprocess
import requests
import json
import os
import sys
import re
from datetime import datetime

def get_git_log(start_tag, end_tag):
    try:
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
        sys.exit(1)

def should_include_commit(commit_info, exclude_authors=None, jira_pattern=None):
    commit_hash, author, subject, body = commit_info

    # Check if author should be excluded
    if exclude_authors and author in exclude_authors:
        return False

    # Check for JIRA ticket pattern if specified
    if jira_pattern:
        # Look for JIRA pattern in subject or body
        full_text = f"{subject}\n{body}"
        if not re.search(jira_pattern, full_text):
            return False

    return True

def format_release_notes(git_log, start_tag, end_tag, exclude_authors=None, jira_pattern=None):
    # Process exclude_authors from comma-separated string
    excluded_authors = set(a.strip() for a in exclude_authors.split(',')) if exclude_authors else set()

    # Convert default JIRA pattern [A-Z]-[1-9] to regex if no custom pattern provided
    if jira_pattern == '[A-Z]-[1-9]' or not jira_pattern:
        jira_pattern = r'[A-Z]+-[1-9][0-9]*'

    # Start with header
    confluence_content = f"""
    <h1>Release Notes: {start_tag} to {end_tag}</h1>
    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """

    if excluded_authors:
        confluence_content += f"<p>Excluding commits from authors: {', '.join(excluded_authors)}</p>"
    if jira_pattern:
        confluence_content += f"<p>Filtering commits by JIRA pattern: {jira_pattern}</p>"

    confluence_content += """
    <h2>Changes</h2>
    <table>
        <tr>
            <th>Commit</th>
            <th>Author</th>
            <th>Description</th>
            <th>JIRA Ticket</th>
        </tr>
    """

    # Process each commit
    included_commits = 0
    for line in git_log.split('\n'):
        if not line.strip():
            continue

        try:
            commit_info = line.split('|', 3)
            if len(commit_info) != 4:
                continue

            if not should_include_commit(commit_info, excluded_authors, jira_pattern):
                continue

            commit_hash, author, subject, body = commit_info

            # Create link to commit
            commit_link = f"<a href='https://github.com/{os.getenv('GITHUB_REPOSITORY')}/commit/{commit_hash}'>{commit_hash[:7]}</a>"

            # Extract JIRA ticket if present
            jira_ticket = ''
            if jira_pattern:
                match = re.search(jira_pattern, f"{subject}\n{body}")
                if match:
                    jira_ticket = match.group(0)

            # Escape HTML special characters
            author = author.replace('<', '&lt;').replace('>', '&gt;')
            subject = subject.replace('<', '&lt;').replace('>', '&gt;')

            # Add row to table
            confluence_content += f"""
            <tr>
                <td>{commit_link}</td>
                <td>{author}</td>
                <td>{subject}</td>
                <td>{jira_ticket}</td>
            </tr>
            """
            included_commits += 1

        except ValueError:
            continue

    confluence_content += "</table>"

    if included_commits == 0:
        print("⚠️ Warning: No commits matched the specified filters")
        confluence_content += "<p>No commits matched the specified filters.</p>"
    else:
        confluence_content += f"<p>Total commits included: {included_commits}</p>"

    return confluence_content

def create_confluence_page(content):
    base_url = os.getenv('CONFLUENCE_BASE_URL')
    api_user = os.getenv('CONFLUENCE_API_USER')
    api_token = os.getenv('CONFLUENCE_API_TOKEN')
    space_key = os.getenv('SPACE_KEY')
    page_title = os.getenv('PAGE_TITLE')

    # Validate required environment variables
    if not all([base_url, api_user, api_token, space_key, page_title]):
        print("❌ Missing required environment variables")
        return False

    url = f"{base_url}/rest/api/content"

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "type": "page",
        "title": page_title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage",
            }
        },
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            auth=(api_user, api_token),  # Now we know these are not None
            data=json.dumps(data),
        )

        response.raise_for_status()

        page_url = f"{base_url}{response.json().get('_links', {}).get('webui')}"
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
    exclude_authors = os.getenv('EXCLUDE_AUTHORS', '')
    jira_pattern = os.getenv('JIRA_PATTERN', '[A-Z]-[1-9]')  # Default pattern

    if not all([start_tag, end_tag]):
        print("❌ Missing required tags")
        sys.exit(1)

    print(f"🔍 Generating release notes from {start_tag} to {end_tag}")
    if exclude_authors:
        print(f"👤 Excluding authors: {exclude_authors}")
    if jira_pattern:
        print(f"🎫 Using JIRA pattern: {jira_pattern}")

    # Get git log
    git_log = get_git_log(start_tag, end_tag)

    if not git_log:
        print("❌ No changes found between tags")
        sys.exit(1)

    # Format content for Confluence
    confluence_content = format_release_notes(git_log, start_tag, end_tag, exclude_authors, jira_pattern)

    # Create Confluence page
    if not create_confluence_page(confluence_content):
        sys.exit(1)

if __name__ == "__main__":
    main()