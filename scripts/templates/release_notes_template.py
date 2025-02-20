RELEASE_TEMPLATE = """
<h1>{version} Release Notes</h1>

<p>Owned by {owner}</p>
<p>Last updated: {last_updated}</p>

<h2>Type of Release:</h2>
<p>{release_type}</p>

<h2>Release version:</h2>
<p>{version}</p>

<h2>New features</h2>
{new_features}

<h2>Product changes</h2>
{product_changes}

<h2>Bug fixes</h2>
{bug_fixes}

<h2>App updates</h2>
{app_updates}

<h2>API changes</h2>
{api_changes}

<h2>User experience enhancements</h2>
{ux_changes}

<h2>Security updates</h2>
{security_updates}

<h2>Backward Compatible Version</h2>
<p>{backward_compatible}</p>

<h2>Upgrade Steps</h2>
{upgrade_steps}

<h2>Rollback Steps</h2>
{rollback_steps}

<h2>Rollback Steps for Major Release</h2>
{major_rollback_steps}

<h2>External Dependencies</h2>
{dependencies}

<h2>Jira Tickets</h2>
{jira_tickets}
"""

def format_ticket_list(tickets):
    """Format a list of JIRA tickets with proper links."""
    if not tickets:
        return "<p>None</p>"
    ticket_links = []
    for ticket in tickets:
        link = f'<a href="https://sinhaludyog.atlassian.net/browse/{ticket}">{ticket}</a>'
        ticket_links.append(link)
    return "<ul>" + "".join([f"<li>{link}</li>" for link in ticket_links]) + "</ul>"

def format_section(items):
    """Format a section with bullet points if it has items."""
    if not items:
        return "<p>No</p>"
    return "<ul>" + "".join([f"<li>{item}</li>" for item in items]) + "</ul>"

def format_feature_with_ticket(feature, ticket):
    """Format a feature description with its JIRA ticket link."""
    if not ticket:
        return feature
    ticket_link = f'<a href="https://sinhaludyog.atlassian.net/browse/{ticket}">{ticket}</a>'
    return f"{feature}<br/>Ticket Link → {ticket_link}"
