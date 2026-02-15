# Release Checklist

Quick reference for releasing a new version of MoKa News.

## Pre-Release

1. **Update Version Numbers**
   - [ ] Update version in `pyproject.toml`
   - [ ] Update `__version__` in `moka_news/__init__.py`
   - [ ] Ensure both versions match

2. **Run Quality Checks**
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

3. **Test Build**
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

4. **Test Installation**
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

1. **Commit Version Changes**
   ```bash
   git add pyproject.toml moka_news/__init__.py
   git commit -m "Bump version to X.Y.Z"
   git push
   ```

2. **Create Git Tag**
   ```bash
   git tag vX.Y.Z
   git push --tags
   ```

3. **Create GitHub Release**
   - Go to https://github.com/calca/moka-news/releases/new
   - Select the tag you just created
   - Set release title: `vX.Y.Z`
   - Add release notes describing changes
   - Click "Publish release"
   
   The GitHub Actions workflow will automatically:
   - Build the package
   - Run checks
   - Publish to PyPI

### Manual (If Needed)

If automatic publishing fails:

```bash
# Ensure you have PyPI credentials configured
# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

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

3. **Update Documentation**
   - [ ] Update README if needed
   - [ ] Update DISTRIBUTION.md if release process changed
   - [ ] Close related issues on GitHub

## Version Numbering

Follow Semantic Versioning (SemVer):
- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality, backward compatible
- **PATCH** version (0.0.X): Bug fixes, backward compatible

Examples:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.1` → `0.2.0`: New feature
- `0.9.0` → `1.0.0`: First stable release

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
- Verify PyPI credentials
- Check package version doesn't already exist
- Ensure twine check passes
- For trusted publishing: verify GitHub Actions permissions

### Installation Fails
- Check PyPI package page for issues
- Verify version number
- Try installing in clean environment
- Check dependency conflicts

## GitHub Actions Workflows

### CI Workflow
- **Trigger**: Push or PR to main/develop branches
- **Actions**: Test, lint, build, upload artifacts
- **View**: https://github.com/calca/moka-news/actions/workflows/ci.yml

### Publish Workflow
- **Trigger**: GitHub release created
- **Actions**: Build and publish to PyPI
- **View**: https://github.com/calca/moka-news/actions/workflows/publish.yml

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [PyPI Help](https://pypi.org/help/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
