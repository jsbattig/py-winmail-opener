# py-winmail-opener

A utility to extract attachments and email body from Winmail.dat files on macOS.

## Features

* Automatically extracts attachments to `~/Downloads`
* Opens email body with TextEdit.app
* Uses a simple, security-friendly AppleScript approach for file associations

## Installation

```
# Install dependencies and create application bundle
python py-winmail-opener/install.py
```

The installer will:
1. Create a dedicated virtual environment for dependencies
2. Install required packages (tnefparse, chardet)
3. Create a security-friendly AppleScript application in your ~/Applications folder
4. Set up the file association with .dat files if possible

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

```
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
