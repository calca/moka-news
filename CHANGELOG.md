# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PyPI packaging infrastructure with `pyproject.toml` configuration
- CI/CD pipeline with GitHub Actions for testing and building
- Automated PyPI publishing workflow on release creation
- DISTRIBUTION.md guide for building, testing, and distributing the package
- RELEASE.md checklist for maintainers to release new versions
- CHANGELOG.md to track all notable changes
- Virtual environment usage throughout build process to avoid system pollution
- Multi-version Python testing (3.8-3.12) in CI
- Package validation with twine in CI pipeline
- Trusted publishing (OIDC) for secure PyPI deployment

### Changed
- Updated `pyproject.toml` with comprehensive PyPI metadata (keywords, classifiers, URLs)
- Migrated license format to modern SPDX standard (`license = "MIT"`)
- Enhanced README.md with PyPI installation instructions and distribution documentation links
- CI workflow now uses `continue-on-error` for linting/formatting checks (non-blocking)

### Security
- Added explicit permissions to GitHub Actions workflows
- Limited GITHUB_TOKEN scope to minimum required permissions

## [0.1.0] - YYYY-MM-DD

### Added
- Initial release of MoKa News
- TUI RSS news aggregator with AI-powered editorial generation
- Support for multiple AI providers:
  - API-based: OpenAI, Anthropic, Google Gemini, Mistral AI
  - CLI-based: GitHub Copilot CLI, Gemini CLI, Mistral CLI
- Smart first-run setup wizard
- Keyword-focused editorial generation
- Smart date filtering (fetch only new articles)
- Editorial archive with markdown format
- Past editorial browsing through TUI
- OPML feed management
- Scheduled refreshes (8 AM and 8 PM)
- Theme support (rose-pine dark and light themes)
- Configuration file support (YAML)
- Command-line interface with multiple options
- Comprehensive test suite

[Unreleased]: https://github.com/calca/moka-news/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/calca/moka-news/releases/tag/v0.1.0
