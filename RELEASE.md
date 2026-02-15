# Release Checklist

Quick reference for releasing a new version of MoKa News.

## Pre-Release

1. **Determine Version Number**
   
   Follow [Semantic Versioning 2.0.0](https://semver.org/):
   
   Given a version number MAJOR.MINOR.PATCH, increment the:
   - **MAJOR** version when you make incompatible API changes
   - **MINOR** version when you add functionality in a backward compatible manner
   - **PATCH** version when you make backward compatible bug fixes
   
   Examples:
   - Bug fix: `0.1.0` → `0.1.1`
   - New feature: `0.1.1` → `0.2.0`
   - Breaking change: `0.9.0` → `1.0.0`

2. **Update CHANGELOG**
   - [ ] Move items from `[Unreleased]` section to new version section
   - [ ] Add release date in format `[X.Y.Z] - YYYY-MM-DD`
   - [ ] Update comparison links at bottom of CHANGELOG.md
   - [ ] Ensure all changes are categorized: Added, Changed, Deprecated, Removed, Fixed, Security

3. **Update Version Numbers**
   - [ ] Update version in `pyproject.toml`
   - [ ] Update `__version__` in `moka_news/__init__.py`
   - [ ] Ensure both versions match the version in CHANGELOG

4. **Run Quality Checks**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install dev dependencies
   pip install -e ".[dev]"
   
   # Run tests
   pytest
   
   # Check linting (optional)
   ruff check moka_news/
   
   # Check formatting (optional)
   black --check moka_news/
   ```

5. **Test Build**
   ```bash
   # Install build tools
   pip install build twine
   
   # Clean previous builds
   rm -rf dist/ build/ *.egg-info/
   
   # Build package
   python -m build
   
   # Check package
   twine check dist/*
   ```

6. **Test Installation**
   ```bash
   # Create test environment
   python -m venv test_env
   source test_env/bin/activate
   
   # Install from wheel
   pip install dist/moka_news-*.whl
   
   # Test command
   moka-news --help
   ```

## Release Process

### Automated (Recommended)

1. **Commit Version and CHANGELOG Changes**
   ```bash
   git add CHANGELOG.md pyproject.toml moka_news/__init__.py
   git commit -m "Release version X.Y.Z"
   git push
   ```

2. **Create Git Tag**
   ```bash
   git tag vX.Y.Z -a -m "Release version X.Y.Z"
   git push --tags
   ```

3. **Create GitHub Release**
   - Go to https://github.com/calca/moka-news/releases/new
   - Select the tag you just created
   - Set release title: `vX.Y.Z`
   - Copy the relevant section from CHANGELOG.md as release notes
   - Click "Publish release"
   
   The GitHub Actions workflow will automatically:
   - Build the package
   - Run checks
   - Publish to PyPI

### Manual (If Needed)

If automatic publishing fails, you can publish manually:

```bash
# Build the package in a virtual environment
python -m venv venv
source venv/bin/activate
pip install build twine

# Build
python -m build

# Upload to PyPI
# Option 1: Using API token stored in environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-pypi-api-token
twine upload dist/*

# Option 2: Using .pypirc configuration file
twine upload dist/*
```

**Important**: 
- Never commit PyPI API tokens to the repository
- Store tokens as **GitHub secrets** (e.g., `PYPI_API_TOKEN`) if using in workflows
- For local publishing, use environment variables or `~/.pypirc` file
- Create API tokens from PyPI account settings: https://pypi.org/help/#apitoken

## Post-Release

1. **Verify PyPI Upload**
   - Check https://pypi.org/project/moka-news/
   - Verify correct version is displayed
   - Test installation: `pip install moka-news==X.Y.Z`

2. **Test Installation**
   ```bash
   # In a new environment
   python -m venv fresh_env
   source fresh_env/bin/activate
   pip install moka-news
   moka-news --help
   ```

3. **Update Documentation and Prepare for Next Version**
   - [ ] Update README if needed
   - [ ] Update DISTRIBUTION.md if release process changed
   - [ ] Close related issues on GitHub
   - [ ] Add new `[Unreleased]` section to CHANGELOG.md for next version
   - [ ] Update comparison link in CHANGELOG.md to track unreleased changes

4. **Announce Release** (optional)
   - Share release notes with users
   - Update project documentation sites if applicable

## Semantic Versioning Guidelines

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR** version (X.0.0): Incompatible API changes
  - Breaking changes to command-line interface
  - Removal of features or configuration options
  - Changes that require user action to upgrade
  
- **MINOR** version (0.X.0): New functionality, backward compatible
  - New features or commands
  - New configuration options
  - New AI provider support
  - Performance improvements
  
- **PATCH** version (0.0.X): Bug fixes, backward compatible
  - Bug fixes
  - Security patches
  - Documentation updates
  - Internal refactoring

### Pre-release Versions

For pre-release versions, use suffixes:
- `X.Y.Z-alpha.N`: Alpha releases (early testing)
- `X.Y.Z-beta.N`: Beta releases (feature complete, testing)
- `X.Y.Z-rc.N`: Release candidates (ready for release)

### Version 0.x.x

While in major version zero (0.y.z):
- MINOR version changes MAY include breaking changes
- PATCH version changes are for backward compatible fixes
- Consider anything as potentially unstable

### Version 1.0.0

Version 1.0.0 defines the first stable public API. After this:
- Strictly follow semver rules
- Breaking changes require MAJOR version increment

### Examples

- `0.1.0` → `0.1.1`: Bug fix (README typo, test fix)
- `0.1.1` → `0.2.0`: New feature (add new AI provider)
- `0.9.0` → `1.0.0`: First stable release with stable API
- `1.0.0` → `2.0.0`: Breaking change (remove deprecated option)
- `1.0.0` → `1.1.0`: New feature (add export command)
- `1.1.0` → `1.1.1`: Bug fix (fix crash on empty feed)

## Troubleshooting

### Build Fails
- Check Python version (3.8+)
- Ensure pyproject.toml is valid
- Clean old build artifacts: `rm -rf dist/ build/ *.egg-info/`

### Tests Fail
- Run in clean virtual environment
- Check for missing dependencies
- Review test output for specific failures

### Upload Fails
- **For automated publishing (GitHub Actions)**:
  - Verify OIDC trusted publishing is configured in PyPI project settings
  - Check GitHub Actions permissions (should have `id-token: write`)
  - Ensure workflow is triggered from a release event
- **For manual publishing**:
  - Verify PyPI API token is valid
  - Ensure token is stored as GitHub secret if using in workflows
  - Never commit tokens to repository
  - Check package version doesn't already exist on PyPI
  - Ensure `twine check dist/*` passes before uploading

### Installation Fails
- Check PyPI package page for issues
- Verify version number
- Try installing in clean environment
- Check dependency conflicts

## GitHub Actions Workflows

### CI Workflow
- **Trigger**: Pull requests to main/develop branches, or manual trigger (workflow_dispatch)
- **Actions**: Test, lint, build, upload artifacts
- **Note**: Does not run automatically on push to main/develop
- **View**: https://github.com/calca/moka-news/actions/workflows/ci.yml

### Publish Workflow
- **Trigger**: GitHub release created, or manual trigger
- **Actions**: Build and publish to PyPI using OIDC trusted publishing
- **Authentication**: No API tokens required (uses OIDC)
- **View**: https://github.com/calca/moka-news/actions/workflows/publish.yml

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [PyPI Help](https://pypi.org/help/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
