import os
from atlassian import Confluence

def publish_to_confluence(title, content):
    """Publish content to Confluence page."""
    base_url = os.getenv('CONFLUENCE_BASE_URL')
    api_user = os.getenv('CONFLUENCE_API_USER')
    api_token = os.getenv('CONFLUENCE_API_TOKEN')

    # Validate required environment variables
    if not all([base_url, api_user, api_token]):
        missing = []
        if not base_url: missing.append('CONFLUENCE_BASE_URL')
        if not api_user: missing.append('CONFLUENCE_API_USER')
        if not api_token: missing.append('CONFLUENCE_API_TOKEN')
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    try:
        confluence = Confluence(
            url=base_url,
            username=api_user,
            password=api_token,
            cloud=True
        )

        space_key = os.getenv('SPACE_KEY')
        ancestor_id = os.getenv('ANCESTOR_ID')

        if not all([space_key, ancestor_id]):
            missing = []
            if not space_key: missing.append('SPACE_KEY')
            if not ancestor_id: missing.append('ANCESTOR_ID')
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        try:
            # Test connection and permissions
            confluence.get_space(space_key)
        except Exception as e:
            print(f"Error connecting to Confluence or accessing space: {str(e)}")
            print("Please verify your API token and permissions.")
            raise

        try:
            # Check if page exists
            existing_page = confluence.get_page_by_title(
                space=space_key,
                title=title
            )

            if existing_page:
                # Update existing page
                confluence.update_page(
                    page_id=existing_page['id'],
                    title=title,
                    body=content,
                    parent_id=ancestor_id,
                    type='page',
                    representation='wiki'
                )
                print(f"Updated existing page: {title}")
            else:
                # Create new page
                confluence.create_page(
                    space=space_key,
                    title=title,
                    body=content,
                    parent_id=ancestor_id,
                    type='page',
                    representation='wiki'
                )
                print(f"Created new page: {title}")

        except Exception as e:
            print(f"Error managing Confluence page: {str(e)}")
            print("Please verify page permissions and parent page existence.")
            raise

    except Exception as e:
        print(f"Error publishing to Confluence: {str(e)}")
        print("Please verify your Confluence configuration and try again.")
        raise
