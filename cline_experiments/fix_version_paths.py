#!/usr/bin/env python3
"""
One-time fix script for the version path mismatch issue.

This script creates symbolic links from the old version paths to the current version,
and also sets up the version-independent paths in the opt directory for future updates.
"""

import os
import shutil
import subprocess
import sys


def main():
    print("=== WinmailOpener Version Path Fix ===")
    print("This script will fix path issues when upgrading between versions.")
    print()

    # 1. Determine paths
    try:
        # Get Homebrew prefix
        brew_prefix = subprocess.check_output(["brew", "--prefix"], text=True).strip()

        # Old version directory (1.0.9) where the app is looking for files
        old_cellar_dir = os.path.join(brew_prefix, "Cellar/py-winmail-opener/1.0.9")
        old_libexec_dir = os.path.join(old_cellar_dir, "libexec")

        # Current version directory (2.0.0 or whatever is currently installed)
        # Find the newest version in the Cellar
        cellar_dir = os.path.join(brew_prefix, "Cellar/py-winmail-opener")
        if not os.path.exists(cellar_dir):
            print(
                f"Error: py-winmail-opener is not installed in Homebrew Cellar ({cellar_dir})"
            )
            return False

        # Get all version directories
        version_dirs = [
            d
            for d in os.listdir(cellar_dir)
            if os.path.isdir(os.path.join(cellar_dir, d))
        ]
        if not version_dirs:
            print("Error: No version directories found in Cellar")
            return False

        # Sort versions to find the newest
        version_dirs.sort(
            key=lambda v: [int(x) if x.isdigit() else x for x in v.split(".")]
        )
        current_version = version_dirs[-1]
        current_cellar_dir = os.path.join(cellar_dir, current_version)
        current_libexec_dir = os.path.join(current_cellar_dir, "libexec")

        print(f"Old version directory: {old_cellar_dir}")
        print(f"Current version directory: {current_cellar_dir}")

        # Version-independent opt directory
        opt_dir = os.path.join(brew_prefix, "opt/py-winmail-opener/libexec")

        # Ensure the opt directory exists
        os.makedirs(opt_dir, exist_ok=True)

        # 2. Fix immediate issue: Create old version directory structure if needed
        if not os.path.exists(old_libexec_dir):
            print(f"Creating directory: {old_libexec_dir}")
            os.makedirs(old_libexec_dir, exist_ok=True)

        # 3. Find source files
        winmail_script = os.path.join(current_libexec_dir, "winmail_opener.py")
        if not os.path.exists(winmail_script):
            winmail_script = os.path.join(
                current_cellar_dir, "libexec/winmail_opener.py"
            )
            if not os.path.exists(winmail_script):
                # Try to find it elsewhere
                try:
                    found_scripts = (
                        subprocess.check_output(
                            ["find", current_cellar_dir, "-name", "winmail_opener.py"],
                            text=True,
                        )
                        .strip()
                        .split("\n")
                    )
                    if found_scripts and found_scripts[0]:
                        winmail_script = found_scripts[0]
                    else:
                        print("Error: Could not find winmail_opener.py script")
                        return False
                except:
                    print("Error: Could not find winmail_opener.py script")
                    return False

        # 4. Create the handler script in the old location
        old_handler_script = os.path.join(old_libexec_dir, "winmail_handler.sh")
        print(f"Creating handler script at {old_handler_script}")
        with open(old_handler_script, "w") as f:
            f.write(
                f"""#!/bin/bash

# Log file for debugging
LOG_FILE=~/WinmailOpener_log.txt

# Log this execution
echo "========================================" >> "$LOG_FILE"
echo "Handler script executed at $(date)" >> "$LOG_FILE"
echo "Arguments received: $@" >> "$LOG_FILE"
echo "This is a compatibility script for version 1.0.9 -> {current_version}" >> "$LOG_FILE"

# If no arguments, show a dialog
if [ $# -eq 0 ]; then
    echo "No arguments provided - showing dialog" >> "$LOG_FILE"
    osascript -e 'display dialog "Please double-click a winmail.dat file instead of launching the app directly." buttons {{"OK"}} default button "OK" with title "WinmailOpener"'
    exit 0
fi

# Process the file
FILEPATH="$1"
echo "Processing file: $FILEPATH" >> "$LOG_FILE"

# Try to find the Python interpreter and script
if [ -f "{current_libexec_dir}/winmail_opener.py" ]; then
    echo "Using current version script" >> "$LOG_FILE"
    SCRIPT="{current_libexec_dir}/winmail_opener.py"
else
    echo "Using opt directory script" >> "$LOG_FILE"
    SCRIPT="/usr/local/opt/py-winmail-opener/libexec/winmail_opener.py"
fi

if [ -f "/usr/local/opt/python@3.10/bin/python3.10" ]; then
    PYTHON="/usr/local/opt/python@3.10/bin/python3.10"
else
    PYTHON="$(which python3)"
fi

echo "Using Python: $PYTHON" >> "$LOG_FILE"
echo "Using script: $SCRIPT" >> "$LOG_FILE"

# Execute the Python script with the file
"$PYTHON" "$SCRIPT" "$FILEPATH" 2>&1 | tee -a "$LOG_FILE"

# Notify the user
osascript -e 'display notification "Winmail.dat file processed. See your Downloads folder for extracted attachments." with title "WinmailOpener"'

exit 0
"""
            )

        # Make the script executable
        os.chmod(old_handler_script, 0o755)

        # 5. Copy/link files to the version-independent opt directory
        # Copy the winmail_opener.py script
        opt_script = os.path.join(opt_dir, "winmail_opener.py")
        print(f"Copying {winmail_script} -> {opt_script}")
        shutil.copy2(winmail_script, opt_script)

        # Copy the handler script
        opt_handler = os.path.join(opt_dir, "winmail_handler.sh")
        print(f"Copying handler script -> {opt_handler}")
        shutil.copy2(old_handler_script, opt_handler)
        os.chmod(opt_handler, 0o755)

        print("\nFix completed successfully!")
        print(f"Created compatibility scripts in {old_libexec_dir}")
        print(f"Set up version-independent scripts in {opt_dir}")

        # Show message about rebuilding the app
        print("\nRecommendation:")
        print("If you continue to have issues, consider reinstalling the application:")
        print("  brew reinstall py-winmail-opener")
        print(
            "This will use the updated installation script with version-independent paths."
        )

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
