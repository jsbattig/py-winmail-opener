# py-winmail-opener

[![CI Status](https://github.com/jsbattig/py-winmail-opener/actions/workflows/ci.yml/badge.svg)](https://github.com/jsbattig/py-winmail-opener/actions/workflows/ci.yml)
[![Python Linting](https://github.com/jsbattig/py-winmail-opener/actions/workflows/ci.yml/badge.svg?job=python-lint)](https://github.com/jsbattig/py-winmail-opener/actions/workflows/ci.yml)
[![Ruby Linting](https://github.com/jsbattig/py-winmail-opener/actions/workflows/ci.yml/badge.svg?job=ruby-lint)](https://github.com/jsbattig/py-winmail-opener/actions/workflows/ci.yml)
[![Tests](https://github.com/jsbattig/py-winmail-opener/actions/workflows/ci.yml/badge.svg?job=test)](https://github.com/jsbattig/py-winmail-opener/actions/workflows/ci.yml)
[![Release Status](https://github.com/jsbattig/py-winmail-opener/actions/workflows/auto-release.yml/badge.svg)](https://github.com/jsbattig/py-winmail-opener/actions/workflows/auto-release.yml)
[![Homebrew Update](https://github.com/jsbattig/py-winmail-opener/actions/workflows/update-homebrew.yml/badge.svg)](https://github.com/jsbattig/py-winmail-opener/actions/workflows/update-homebrew.yml)
[![Submodule Update](https://github.com/jsbattig/py-winmail-opener/actions/workflows/update-homebrew.yml/badge.svg?job=update-submodule)](https://github.com/jsbattig/py-winmail-opener/actions/workflows/update-homebrew.yml)

A utility to extract attachments and email body from Winmail.dat files on macOS.

## Understanding Winmail.dat Files

### What are Winmail.dat files?

Winmail.dat files are containers that use Microsoft's proprietary **Transport Neutral Encapsulation Format (TNEF)** to bundle email content. When you receive an email with a Winmail.dat attachment, it typically means:

- The sender used Microsoft Outlook or Exchange
- The email contains rich formatting, attachments, or Microsoft-specific features
- Your email client can't natively process this proprietary format

### Why Microsoft Outlook/Exchange Uses TNEF Format

Microsoft Exchange and Outlook generate Winmail.dat attachments for several reasons:

1. **Rich Formatting Support**: TNEF preserves Microsoft-specific rich text formatting, including custom fonts, tables, and embedded objects.

2. **Exchange Server Default Behavior**: Particularly in older Exchange environments, messages are automatically encoded in TNEF format for internal communications.

3. **RTF Format Selection**: When users select Rich Text Format (RTF) instead of HTML or plain text, Outlook automatically uses TNEF.

4. **Proprietary Features**: TNEF supports Outlook-specific features like voting buttons and meeting requests.

Instead of sending standard MIME attachments that all email clients can read, Outlook bundles everything into a single Winmail.dat file that only Microsoft products can natively interpret.

If you're using an email client and receive Winmail.dat attachments, you'll need a tool like py-winmail-opener to extract the actual content.

## Features

* Automatically extracts attachments to `~/Downloads`
* Converts email body to HTML and opens it in your default web browser
* Displays convenient links to all extracted attachments at the bottom of the HTML page
* Uses a simple AppleScript approach for file associations

## Installation and Uninstallation

### Homebrew Installation (Recommended)

The easiest way to install py-winmail-opener is using Homebrew:

```bash
# Add the tap
brew tap jsbattig/winmail

# Install the package
brew install py-winmail-opener
```

This will automatically:
1. Install all dependencies
2. Create the AppleScript application for handling winmail.dat files
3. Set up file associations

### Manual Installation

```
# Install dependencies and create application bundle
python py-winmail-opener/install.py
```

The installer will:
1. Create a dedicated virtual environment for dependencies
2. Install required packages (tnefparse, chardet)
3. Create a security-friendly AppleScript application in your ~/Applications folder
4. Set up the file association with .dat files

Note: If you receive antivirus warnings during installation or usage, use your antivirus software's trust function to allow the application.

### Uninstallation

#### Homebrew Uninstallation

If you installed using Homebrew, uninstallation is simple:

```bash
brew uninstall py-winmail-opener
```

You can also remove the tap if you no longer need it:

```bash
brew untap jsbattig/winmail
```

If you encounter errors during Homebrew uninstallation, you can verify and fix any remaining components:

```bash
# Check for any remaining components
python py-winmail-opener/verify_uninstall.py

# Force complete removal if needed
python py-winmail-opener/uninstall.py --force --homebrew-mode
```

#### Manual Uninstallation

If you installed manually, you can remove the application completely:

```
# Remove the application and all associated components
python py-winmail-opener/uninstall.py
```

The uninstaller will:
1. Remove the application from ~/Applications
2. Reset file associations for .dat files
3. Clean up handler scripts and log files
4. Remove the virtual environment
5. Remove Homebrew-specific files if detected

Uninstaller options:
```
# Keep the virtual environment (useful for development)
python py-winmail-opener/uninstall.py --keep-venv

# Keep log files for troubleshooting
python py-winmail-opener/uninstall.py --keep-logs

# Force removal even if components are not found
python py-winmail-opener/uninstall.py --force

# Clean up Homebrew-specific files
python py-winmail-opener/uninstall.py --homebrew-mode
```

### How It Works

The application uses a simple AppleScript handler to receive file open events from macOS, which then calls a Python script to process the winmail.dat file. This approach:

1. Works reliably with double-clicked files
2. Provides desktop notifications when files are processed
3. Logs all activity to ~/WinmailOpener_log.txt for troubleshooting

## Usage

After installation, you can use the tool in two ways:

### From the command line

#### If installed with Homebrew:

```bash
# Use the provided command
winmail-opener <winmail_dat_file>
```

#### If installed manually:

```bash
python py-winmail-opener/winmail_opener.py <winmail_dat_file>
```

* `<winmail_dat_file>`: Path to the Winmail.dat file.

### By double-clicking a .dat file

Once you've set WinmailOpener.app as the default handler for .dat files, you can simply double-click any .dat file and:
1. All attachments will be extracted to `~/Downloads`
2. If an email body is present, it will be converted to HTML and opened in your default web browser
3. The HTML view includes clickable links to all extracted attachments at the bottom of the page

## Dependencies

* tnefparse
* chardet

## For Developers

### Automated Release Process

This project features a fully automated release system that creates new releases and updates the Homebrew formula automatically when changes are pushed to the master branch.

#### How It Works

1. When you push commits to the master branch, a GitHub Actions workflow is triggered
2. The workflow analyzes the commit message to determine the version bump type
3. Version numbers are automatically updated in all relevant files
4. A new Git tag is created with the new version number
5. A GitHub release is published with automatically generated release notes
6. The Homebrew formula is updated with the new version and SHA256 hash

#### Controlling Version Bumps with Commit Messages

You can control how the version number is incremented by including special prefixes in your commit messages:

| Prefix | Description | Example | Result |
|--------|-------------|---------|--------|
| `[patch]` or no prefix | Bump patch version | `Fix bug in extraction [patch]` or `Fix bug in extraction` | 1.0.0 → 1.0.1 |
| `[minor]` | Bump minor version | `Add new feature [minor]` | 1.0.0 → 1.1.0 |
| `[major]` | Bump major version | `Breaking API change [major]` | 1.0.0 → 2.0.0 |
| `[skip-release]` | Don't create a release | `Update documentation [skip-release]` | No version change |

#### Examples

```bash
# This will create a patch release (e.g., 1.0.0 -> 1.0.1)
git commit -m "Fix extraction bug for large attachments"

# This will create a minor release (e.g., 1.0.0 -> 1.1.0)
git commit -m "Add support for new attachment types [minor]"

# This will create a major release (e.g., 1.0.0 -> 2.0.0)
git commit -m "Restructure API for better performance [major]"

# This will not create a release
git commit -m "Update README documentation [skip-release]"
```

#### Manual Release Triggering

You can also manually trigger a release by:

1. Going to the "Actions" tab in GitHub
2. Selecting the "Automatic Release" workflow
3. Clicking "Run workflow"
4. Selecting the desired version bump type and other options

#### GitHub Actions Setup

This project includes two GitHub Actions workflows:

1. **auto-release.yml**: Creates new releases based on commit messages
2. **update-homebrew.yml**: Updates the Homebrew formula when releases are published
3. **ci.yml**: Runs syntax checks and tests on every push and pull request

For more information, see [Homebrew's documentation on taps](https://docs.brew.sh/Taps).

### Development Tools

This project includes several tools to help maintain code quality:

1. **Linting and Testing Scripts**:
   - `scripts/lint_python.sh`: Checks Python code for syntax and style issues
   - `scripts/lint_ruby.sh`: Checks Ruby code for syntax and style issues
   - `scripts/run_tests.sh`: Runs the test suite
   - `scripts/pre-commit.sh`: Runs all checks before committing

2. **Setting Up the Development Environment**:

```bash
# Install all dependencies and set up linters
./scripts/setup_dev_environment.sh
```

3. **Pre-commit Checks**:

Before committing, you can run all checks with:

```bash
./scripts/pre-commit.sh
```

This will ensure your code meets the project's quality standards.
