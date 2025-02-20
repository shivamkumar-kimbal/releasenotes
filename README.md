# GitHub Action Release Notes Generator

Automatically generate and publish release notes to Confluence when new tags are created. This action helps maintain consistent and well-structured release documentation by extracting information from git commits and publishing it to your Confluence space.

## Features

- 🔄 Automatic release notes generation on new tag creation
- 📅 Support for generating notes between specific tag ranges
- 🏷️ Smart detection of release type (Major/Minor/Patch)
- 🎯 Categorization of changes (Features, Bugs, API changes, etc.)
- 📋 JIRA ticket extraction and linking
- ☁️ Direct publishing to Confluence

## Setup

1. Add the workflow file to your repository:
   ```bash
   mkdir -p .github/workflows
   cp release-notes.yml .github/workflows/
   ```

2. Configure required secrets in your GitHub repository:
   - `CONFLUENCE_API_TOKEN`: Your Confluence API token
   - `JIRA_API_TOKEN`: (Optional) If you want to fetch JIRA ticket details

3. Update the following environment variables in the workflow file:
   ```yaml
   CONFLUENCE_BASE_URL: "https://your-instance.atlassian.net/wiki"
   CONFLUENCE_API_USER: "your.email@domain.com"
   SPACE_KEY: "YOUR_SPACE"
   ANCESTOR_ID: "YOUR_PAGE_ID"
   ```

## Usage

### Automatic Generation
The action automatically runs when you create a new tag:
```bash
git tag v1.2.3
git push origin v1.2.3
```

### Manual Generation
You can also manually generate release notes for a specific tag range:
1. Go to your repository's Actions tab
2. Select "Generate Release Notes" workflow
3. Click "Run workflow"
4. Enter the tag range (e.g., from: v1.0.0, to: v1.1.0)

## Release Notes Format

The generated release notes include:
- Release type (Major/Minor/Patch)
- Version number
- New features
- Bug fixes
- Product changes
- API changes
- Security updates
- Backward compatibility status
- Upgrade and rollback steps
- External dependencies
- Related JIRA tickets

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Technical Documentation

For detailed information about the implementation and logic, see [LOGIC.md](LOGIC.md).
