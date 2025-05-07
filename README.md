# py-winmail-opener

A utility to extract attachments and email body from Winmail.dat files on macOS.

## Features

* Automatically extracts attachments to `~/Downloads`
* Opens email body with TextEdit.app
* Uses a simple, security-friendly AppleScript approach for file associations

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
3. Set up file associations if possible

### Installation

```
# Install dependencies and create application bundle
python py-winmail-opener/install.py
```

The installer will:
1. Create a dedicated virtual environment for dependencies
2. Install required packages (tnefparse, chardet)
3. Create a security-friendly AppleScript application in your ~/Applications folder
4. Set up the file association with .dat files if possible

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

Uninstaller options:
```
# Keep the virtual environment (useful for development)
python py-winmail-opener/uninstall.py --keep-venv

# Keep log files for troubleshooting
python py-winmail-opener/uninstall.py --keep-logs
```

### Setting Up File Associations

After installation, you'll need to associate .dat files with the app **once**:
1. Right-click on a winmail.dat file
2. Select "Open With" > "Other..."
3. Navigate to ~/Applications, select WinmailOpener.app
4. Check "Always Open With" to make this the default for all .dat files

After this one-time setup, you can double-click any winmail.dat file to automatically extract its contents.

### How It Works

The application uses a simple AppleScript handler to receive file open events from macOS, which then calls a Python script to process the winmail.dat file. This approach:

1. Avoids triggering security warnings from antivirus software
2. Works reliably with double-clicked files
3. Provides desktop notifications when files are processed
4. Logs all activity to ~/WinmailOpener_log.txt for troubleshooting

### Manual File Association

If the automatic file association doesn't work, you can manually set it:
1. Right-click on a .dat file
2. Select "Get Info"
3. Under "Open with:", select WinmailOpener.app
4. Click "Change All..." to apply to all .dat files

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
2. If an email body is present, it will open in TextEdit.app

## Dependencies

* tnefparse
* chardet

## Running Tests

```
python py-winmail-opener/test_winmail_opener.py
```

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

To set up these workflows:

1. Create a Personal Access Token with `repo` scope
2. Add it as a repository secret named `HOMEBREW_TAP_TOKEN` in your GitHub repository settings
3. Ensure the token has write access to the homebrew-winmail repository

Once configured, the entire release process will be automated.

### Creating a Manual Release

While the automated system handles most release scenarios, you can still create a release manually if needed:

1. Update the version in `setup.py` and `winmail_opener.py`
2. Create a tagged release on GitHub:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```
3. Create a release on GitHub through the web interface

### Updating the Homebrew Formula

The Homebrew formula is located in `py-winmail-opener.rb`. When updating:

1. Make sure `url` points to the latest release
2. Update the `sha256` with the correct checksum
3. Update the version in the test assertion if version number changed
4. If dependencies changed, update the `depends_on` section

### Creating the Homebrew Tap Repository

To make your formula available via Homebrew:

1. Create a new GitHub repository named `homebrew-winmail`
2. Add the `py-winmail-opener.rb` formula file to this repository
3. Users can then install with:
   ```bash
   brew tap jsbattig/winmail
   brew install py-winmail-opener
   ```

For more information, see [Homebrew's documentation on taps](https://docs.brew.sh/Taps).
