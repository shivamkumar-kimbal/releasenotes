import argparse
import os
import re
import subprocess
from datetime import datetime
from github import Github
from confluence_publisher import publish_to_confluence

def get_git_commits(from_tag=None, to_tag=None):
    """Get commits from local git repository."""
    try:
        if from_tag and to_tag:
            cmd = ['git', 'log', '--pretty=format:%s', f'{from_tag}..{to_tag}']
        else:
            # For single tag, limit to first occurrence
            cmd = ['git', 'log', '-n', '1', '--pretty=format:%H', to_tag]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                commit_hash = result.stdout.strip()
                cmd = ['git', 'log', '--pretty=format:%s', f'{commit_hash}^..{commit_hash}']

        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Git command: {' '.join(cmd)}")  # Debug output
        if result.returncode == 0:
            commits = [line for line in result.stdout.split('\n') if line]
            print(f"Raw commit output: {result.stdout}")  # Debug output
            # Remove duplicate commits
            return list(dict.fromkeys(commits))
        print(f"Git command failed with return code: {result.returncode}")  # Debug output
        return []
    except Exception as e:
        print(f"Error getting git commits: {str(e)}")
        return []

def parse_version(tag):
    """Parse version number from tag."""
    match = re.match(r'v(\d+)\.(\d+)\.(\d+)', tag)
    if not match:
        raise ValueError(f"Invalid tag format: {tag}")
    return [int(x) for x in match.groups()]

def determine_release_type(from_version, to_version):
    """Determine if release is major, minor, or patch."""
    if from_version[0] != to_version[0]:
        return "Major"
    elif from_version[1] != to_version[1]:
        return "Minor"
    return "Patch"

def extract_jira_tickets(commit_messages):
    """Extract JIRA ticket references from commit messages."""
    tickets = set()
    pattern = r'\[([A-Z]+-\d+)\]'
    ticket_details = {}

    for message in commit_messages:
        if message:  # Skip empty messages
            matches = re.findall(pattern, message)
            for ticket in matches:
                tickets.add(ticket)
                # Extract description after the ticket reference
                desc_match = re.search(rf'\[{ticket}\]\s*(.+?)(?=\[|$)', message)
                if desc_match:
                    ticket_details[ticket] = desc_match.group(1).strip()

    return sorted(list(tickets)), ticket_details

def categorize_changes(commit_messages):
    """Categorize changes based on commit messages."""
    categories = {
        'features': [],
        'bugs': [],
        'product_changes': [],
        'api_changes': [],
        'app_updates': [],
        'ux_enhancements': [],
        'security': []
    }

    seen_messages = set()  # Track unique messages
    for msg in commit_messages:
        if not msg or msg in seen_messages:  # Skip empty or duplicate messages
            continue
        seen_messages.add(msg)
        msg_lower = msg.lower()

        # Enhanced categorization based on prefixes and keywords
        if any(prefix in msg_lower for prefix in ['feat:', 'feature:', 'new:']):
            categories['features'].append(msg)
        elif any(prefix in msg_lower for prefix in ['fix:', 'bug:', 'patch:']):
            categories['bugs'].append(msg)
        elif any(prefix in msg_lower for prefix in ['api:', 'endpoint:', 'rest:']):
            categories['api_changes'].append(msg)
        elif any(prefix in msg_lower for prefix in ['security:', 'sec:', 'auth:']):
            categories['security'].append(msg)
        elif any(prefix in msg_lower for prefix in ['ui:', 'ux:', 'design:']):
            categories['ux_enhancements'].append(msg)
        elif any(prefix in msg_lower for prefix in ['app:', 'mobile:', 'web:']):
            categories['app_updates'].append(msg)
        elif any(prefix in msg_lower for prefix in ['prod:', 'product:']):
            categories['product_changes'].append(msg)

    return categories

def format_jira_link(ticket, description=''):
    """Format JIRA ticket link with description."""
    base_url = "https://sinhaludyog.atlassian.net/browse"
    if description:
        return f"[{ticket}] {description} - {base_url}/{ticket}"
    return f"[{ticket}] - {base_url}/{ticket}"

def generate_release_notes(from_tag, to_tag):
    """Generate release notes content."""
    # Get commits from local git repository
    commit_messages = get_git_commits(from_tag, to_tag)
    print(f"Found {len(commit_messages)} commits")
    print("Commit messages:", commit_messages)

    # Parse versions and determine release type
    to_version = parse_version(to_tag)
    release_type = "Minor"  # Default to Minor if no from_tag
    if from_tag:
        from_version = parse_version(from_tag)
        release_type = determine_release_type(from_version, to_version)
    print(f"Release type determined: {release_type}")

    # Categorize changes
    changes = categorize_changes(commit_messages)
    print("Categorized changes:")
    for category, items in changes.items():
        print(f"{category}: {len(items)} items")
        for item in items:
            print(f"  - {item}")

    # Extract JIRA tickets
    jira_tickets, ticket_details = extract_jira_tickets(commit_messages)
    print(f"Found JIRA tickets: {jira_tickets}")

    # Generate content with enhanced formatting
    content = f"Type of Release:\n\n{release_type}\n\n"
    content += f"Release version:\n\n{to_tag}\n\n"

    # Features section with JIRA links
    content += "New features\n\n"
    if changes['features']:
        for feature in changes['features']:
            ticket_match = re.search(r'\[([A-Z]+-\d+)\]', feature)
            if ticket_match:
                ticket = ticket_match.group(1)
                desc = ticket_details.get(ticket, '')
                content += f"{feature}\nTicket Link → {format_jira_link(ticket, desc)}\n\n"
            else:
                content += f"{feature}\n\n"
    else:
        content += "No new features\n\n"

    # Product changes section
    content += "Product changes:\n\n"
    if changes['product_changes']:
        for change in changes['product_changes']:
            content += f"{change}\n"
    else:
        content += "No\n"

    # Bug fixes section with JIRA links
    content += "\nBug fixes:\n\n"
    if changes['bugs']:
        for bug in changes['bugs']:
            ticket_match = re.search(r'\[([A-Z]+-\d+)\]', bug)
            if ticket_match:
                ticket = ticket_match.group(1)
                desc = ticket_details.get(ticket, '')
                content += f"{bug}\nTicket → {format_jira_link(ticket, desc)}\n\n"
            else:
                content += f"{bug}\n\n"
    else:
        content += "No\n"

    # Other sections
    sections = [
        ('App updates', changes['app_updates']),
        ('API changes', changes['api_changes']),
        ('User experience enhancements', changes['ux_enhancements']),
        ('Security updates', changes['security'])
    ]

    for section_name, items in sections:
        content += f"\n{section_name}:\n\n"
        if items:
            content += '\n'.join(f"{item}" for item in items) + '\n'
        else:
            content += "No\n"

    # Standard sections
    content += "\nBackward Compatible Version *:\n\nYes\n\n"
    content += "Upgrade Steps *:\n\nRun Github Action workflow of client\n\n"
    content += "Rollback Steps *:\n\nRun Github Action workflow of client with backward compatible version\n\n"
    content += "Rollback Steps for Major Release *:\n\n"
    content += "N/A - release type minor\n\n" if release_type.lower() != "major" else "* Detailed rollback steps for major version change\n\n"
    content += "External Dependencies:\n\nN/A\n\n"

    # JIRA tickets summary
    content += "Jira Tickets:\n\n"
    if jira_tickets:
        for ticket in jira_tickets:
            desc = ticket_details.get(ticket, '')
            content += f"{format_jira_link(ticket, desc)}\n\n"

    print("\nGenerated content preview:")
    print(content)
    return content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from-tag', help='Starting tag for range')
    parser.add_argument('--to-tag', help='Ending tag for range', required=True)
    args = parser.parse_args()

    content = generate_release_notes(args.from_tag, args.to_tag)

    # Publish to Confluence
    title = f"{args.to_tag} Release Notes"
    publish_to_confluence(title, content)

if __name__ == '__main__':
    main()
