# Contributing to Release Notes Generator

Thank you for your interest in contributing to the Release Notes Generator! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/release-notes-generator.git
   cd release-notes-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   export CONFLUENCE_BASE_URL="your-confluence-url"
   export CONFLUENCE_API_USER="your-email"
   export SPACE_KEY="your-space"
   export ANCESTOR_ID="your-page-id"
   ```

## Code Style Guidelines

1. Follow PEP 8 style guide for Python code
2. Use meaningful variable and function names
3. Add docstrings for functions and classes
4. Include type hints where appropriate
5. Keep functions focused and modular

## Pull Request Process

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit using conventional commit messages:
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation changes
   - style: Code style changes
   - refactor: Code refactoring
   - test: Adding tests
   - chore: Maintenance tasks

3. Update documentation as needed

4. Run tests and ensure they pass:
   ```bash
   python -m pytest
   ```

5. Push your changes and create a pull request

## Issue Reporting

When creating an issue, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Relevant logs or error messages

## Testing

- Write unit tests for new features
- Update existing tests when modifying functionality
- Run the test suite locally before submitting PR
- Include both positive and negative test cases

## Documentation

When adding or modifying features:
1. Update relevant documentation
2. Include docstrings for new functions/classes
3. Update README.md if needed
4. Add examples for new functionality

## Review Process

1. All PRs require at least one review
2. Address review comments promptly
3. Keep PR scope focused and manageable
4. Ensure CI checks pass

## Git Workflow

1. Keep commits atomic and focused
2. Write clear commit messages
3. Rebase feature branches on main
4. Squash commits before merging

## Need Help?

- Check existing issues and documentation
- Join our community discussions
- Ask questions in pull requests
- Contact maintainers

Thank you for contributing!
