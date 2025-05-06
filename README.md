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

### GitHub Actions Automation

This project includes a GitHub Actions workflow that automatically updates the Homebrew formula when you create a new release. The workflow:

1. Triggers when a new release is published on GitHub
2. Downloads the release tarball
3. Calculates the SHA256 checksum
4. Updates the formula in the homebrew-winmail repository
5. Commits and pushes the changes

To set this up:

1. Create a Personal Access Token with `repo` scope
2. Add it as a repository secret named `HOMEBREW_TAP_TOKEN` in your GitHub repository settings
3. Ensure the token has write access to the homebrew-winmail repository

Once configured, the Homebrew formula will be automatically updated whenever you create a new release.

### Creating a Release

To create a new release for use with Homebrew:

1. Update the version in `setup.py` and `winmail_opener.py`
2. Create a tagged release on GitHub:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```
3. Create a release on GitHub through the web interface
4. Download the release tarball and calculate the SHA256 checksum:
   ```bash
   curl -L https://github.com/jsbattig/py-winmail-opener/archive/refs/tags/v1.0.0.tar.gz -o v1.0.0.tar.gz
   shasum -a 256 v1.0.0.tar.gz
   ```
5. Update the SHA256 in the Homebrew formula with the new checksum

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
