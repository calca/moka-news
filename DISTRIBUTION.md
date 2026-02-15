# Distribution Guide

This document explains how to build and distribute MoKa News as a Python package.

## Prerequisites

- Python 3.8 or higher
- Virtual environment support (`python -m venv`)
- Git

## Building the Package

The project uses a modern `pyproject.toml` configuration and follows Python packaging best practices.

### 1. Set Up a Virtual Environment

**Important**: Always use a virtual environment to avoid system pollution when building packages.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Build Dependencies

```bash
pip install --upgrade pip
pip install build twine
```

### 3. Build the Package

```bash
python -m build
```

This creates two distribution files in the `dist/` directory:
- `moka_news-X.Y.Z-py3-none-any.whl` - Wheel distribution (recommended for installation)
- `moka_news-X.Y.Z.tar.gz` - Source distribution

### 4. Verify the Package

Check that the package meets PyPI requirements:

```bash
twine check dist/*
```

## Testing the Package Locally

Before publishing, test the package in a clean environment:

```bash
# Create a new test environment
python -m venv test_env
source test_env/bin/activate

# Install the package from the wheel file
pip install dist/moka_news-*.whl

# Test the installation
moka-news --help
```

## Publishing to PyPI

### Automated Publishing (Recommended)

The project includes a GitHub Actions workflow that automatically publishes to PyPI when a release is created:

1. Update the version in `pyproject.toml` and `moka_news/__init__.py`
2. Commit and push the changes
3. Create a new release on GitHub with a version tag (e.g., `v0.1.0`)
4. The workflow will automatically build and publish to PyPI

**Authentication**: The workflow uses **OIDC trusted publishing** (OpenID Connect), which doesn't require API tokens or secrets. This is the recommended and most secure method for publishing to PyPI from GitHub Actions.

**One-time setup**: Configure trusted publishing in your PyPI project settings to authorize this GitHub repository.

### Manual Publishing

If you need to publish manually (e.g., from your local machine):

```bash
# Activate your virtual environment
source venv/bin/activate

# Build the package
python -m build

# Publish to Test PyPI first (optional but recommended)
twine upload --repository testpypi dist/*

# After testing, publish to PyPI
twine upload dist/*
```

**Authentication for manual publishing**: 
- Create a PyPI API token from your PyPI account settings
- Store the token as a **GitHub secret** named `PYPI_API_TOKEN` if using in workflows
- For local manual publishing, configure the token in `~/.pypirc` or use the `TWINE_USERNAME` and `TWINE_PASSWORD` environment variables
- Never commit API tokens to the repository

See [PyPI's documentation](https://pypi.org/help/#apitoken) for creating and managing API tokens.

## GitHub Actions Workflows

The project includes two workflows:

### CI Workflow (`.github/workflows/ci.yml`)

Runs on pull requests to `main` and `develop` branches, or manually via workflow_dispatch:
- Tests on Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Lints with `ruff`
- Checks formatting with `black`
- Runs the test suite
- Builds the package and uploads artifacts

**Note**: CI does not run automatically on push to main/develop branches. Use pull requests or trigger manually when needed.

### Publish Workflow (`.github/workflows/publish.yml`)

Runs when a GitHub release is published:
- Builds the package in a clean virtual environment
- Verifies the package with `twine check`
- Publishes to PyPI using **OIDC trusted publishing** (no API tokens required)

Can also be manually triggered to publish to Test PyPI for testing.

## Development Workflow

### Installing for Development

```bash
# Clone the repository
git clone https://github.com/calca/moka-news.git
cd moka-news

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black moka_news/

# Lint code
ruff check moka_news/

# Auto-fix linting issues
ruff check --fix moka_news/
```

## Version Management

This project follows [Semantic Versioning 2.0.0](https://semver.org/).

The version is defined in three places and should be kept in sync:
- `pyproject.toml` - The `version` field under `[project]`
- `moka_news/__init__.py` - The `__version__` variable
- `CHANGELOG.md` - The version sections tracking changes

### Releasing a New Version

1. Determine the version number following semver rules (see RELEASE.md)
2. Update CHANGELOG.md:
   - Move items from `[Unreleased]` to new version section
   - Add release date
   - Update comparison links
3. Update version in `pyproject.toml` and `moka_news/__init__.py`
4. Commit changes: `git commit -m "Release version X.Y.Z"`
5. Create annotated tag: `git tag vX.Y.Z -a -m "Release version X.Y.Z"`
6. Push with tags: `git push --tags`
7. Create a GitHub release (triggers automatic PyPI publishing)

See [RELEASE.md](RELEASE.md) for detailed release checklist.

## Package Configuration

The package configuration in `pyproject.toml` includes:
- Project metadata (name, description, authors)
- Dependencies
- Optional dependencies (dev tools, AI providers)
- Entry points (command-line scripts)
- Build system configuration
- Tool configurations (black, ruff)

## PyPI Project URLs

The package includes the following project URLs:
- Homepage: https://github.com/calca/moka-news
- Repository: https://github.com/calca/moka-news
- Issues: https://github.com/calca/moka-news/issues

## License

The package is distributed under the MIT License.
