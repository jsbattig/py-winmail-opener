#!/usr/bin/env python3
import argparse
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile


def create_virtual_environment():
    """
    Creates a virtual environment and installs dependencies in it.
    Returns the path to the virtual environment's Python interpreter.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(current_dir, "venv")

    # Get the best available Python interpreter
    python_cmd = sys.executable if sys.executable else "python3"

    # First check if venv already exists
    if os.path.exists(venv_dir):
        print(f"Using existing virtual environment at {venv_dir}")
    else:
        print(f"Creating a virtual environment at {venv_dir}")
        try:
            # Create the virtual environment
            subprocess.check_call([python_cmd, "-m", "venv", venv_dir])
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            print("You may need to install venv:")
            print("  brew install python-venv")
            return None

    # Determine path to python in the virtual environment
    if sys.platform.startswith("win"):
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    if not os.path.exists(venv_python):
        print(
            f"Error: Could not find Python in the virtual environment at {venv_python}"
        )
        return None

    # Install dependencies in the virtual environment
    try:
        # Install dependencies with pip
        print(f"Installing dependencies in the virtual environment...")
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call(
            [venv_python, "-m", "pip", "install", "tnefparse", "chardet"]
        )

        # Verify installations
        try:
            verify_cmd = f"{venv_python} -c 'import tnefparse, chardet; print(\"Modules successfully imported.\")'"
            result = subprocess.call(verify_cmd, shell=True)

            if result == 0:
                print(
                    "Dependencies installed and verified successfully in the virtual environment."
                )
                return venv_python
            else:
                print(
                    "Warning: Dependencies may not be correctly installed in the virtual environment."
                )
                return None
        except Exception as e:
            print(f"Error verifying dependencies: {e}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies in the virtual environment: {e}")
        return None


def create_applescript_handler(venv_python=None, homebrew_mode=False):
    """
    Creates a simple AppleScript-based file handler without using Launch Agents.
    This is a security-friendly approach that doesn't trigger antivirus warnings.

    Args:
        venv_python: Path to the Python interpreter to use
        homebrew_mode: Whether running in Homebrew installation mode
    """
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if not venv_python:
        # Try to find a virtual environment Python
        if sys.platform.startswith("win"):
            venv_python = os.path.join(script_dir, "venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join(script_dir, "venv", "bin", "python")

        if not os.path.exists(venv_python):
            print(f"Warning: Virtual environment Python not found at {venv_python}")
            print("Using system Python instead")
            venv_python = sys.executable if sys.executable else "python3"

    winmail_script = os.path.join(script_dir, "winmail_opener.py")
    handler_script_path = os.path.join(script_dir, "winmail_handler.sh")

    # Create handler script - this will be called by the AppleScript app
    print(f"Creating handler script at {handler_script_path}")
    with open(handler_script_path, "w") as f:
        f.write(
            """#!/bin/bash

# Log file for debugging
LOG_FILE=~/WinmailOpener_log.txt

# Log this execution
echo "========================================" >> "$LOG_FILE"
echo "Handler script executed at $(date)" >> "$LOG_FILE"
echo "Arguments received: $@" >> "$LOG_FILE"

# If no arguments, show a dialog
if [ $# -eq 0 ]; then
    echo "No arguments provided - showing dialog" >> "$LOG_FILE"
    osascript -e 'display dialog "Please double-click a winmail.dat file instead of launching the app directly." buttons {"OK"} default button "OK" with title "WinmailOpener"'
    exit 0
fi

# Process the file
FILEPATH="$1"
echo "Processing file: $FILEPATH" >> "$LOG_FILE"

# Try to find the winmail_opener.py script and Python interpreter
# First try the Homebrew opt (version-independent) directory
WINMAIL_SCRIPT="/usr/local/opt/py-winmail-opener/libexec/winmail_opener.py"
VENV_PYTHON=""

# Check for Python in various locations
if [ -f "/usr/local/opt/py-winmail-opener/libexec/venv/bin/python" ]; then
    # First try the venv in the opt directory
    VENV_PYTHON="/usr/local/opt/py-winmail-opener/libexec/venv/bin/python"
elif [ -f "/usr/local/opt/python@3.10/bin/python3.10" ]; then
    # Try Homebrew's Python 3.10
    VENV_PYTHON="/usr/local/opt/python@3.10/bin/python3.10"
else
    # Fallback to system Python
    VENV_PYTHON=$(which python3)
fi

# If the script doesn't exist at the expected location, try to find it
if [ ! -f "$WINMAIL_SCRIPT" ]; then
    # Try the original install location first
    ORIGINAL_SCRIPT="{winmail_script}"
    if [ -f "$ORIGINAL_SCRIPT" ]; then
        WINMAIL_SCRIPT="$ORIGINAL_SCRIPT"
    else
        # Find the newest version in the Cellar
        FOUND_SCRIPT=$(find /usr/local/Cellar/py-winmail-opener -name 'winmail_opener.py' | head -1)
        if [ ! -z "$FOUND_SCRIPT" ]; then
            WINMAIL_SCRIPT="$FOUND_SCRIPT"
        fi
    fi
fi

echo "Using Python: $VENV_PYTHON" >> "$LOG_FILE"
echo "Using script: $WINMAIL_SCRIPT" >> "$LOG_FILE"

# Execute the Python script with the file
"$VENV_PYTHON" "$WINMAIL_SCRIPT" "$FILEPATH" 2>&1 | tee -a "$LOG_FILE"

# Notify the user
osascript -e 'display notification "Winmail.dat file processed. See your Downloads folder for extracted attachments." with title "WinmailOpener"'

exit 0
"""
        )

    # Make the handler script executable
    os.chmod(handler_script_path, 0o755)

    # Ensure Homebrew can clean it up later
    try:
        # Make the file writable by the group
        os.chmod(handler_script_path, 0o775)
        # If we're in Homebrew mode, ensure the file is owned by the Homebrew group
        if homebrew_mode:
            # Try to get Homebrew's group
            brew_group = subprocess.check_output(
                ["stat", "-f", "%Sg", "/usr/local/bin/brew"], text=True
            ).strip()
            subprocess.run(["chgrp", brew_group, handler_script_path], check=False)
    except Exception as e:
        print(f"Note: Could not update file permissions for cleanup: {e}")
        print(
            "This may cause warnings during future upgrades but won't affect functionality."
        )

    # Create the AppleScript app
    print("Creating AppleScript application...")
    if homebrew_mode:
        # In Homebrew mode, install to a location managed by Homebrew
        try:
            # Try to get Homebrew prefix
            brew_prefix = subprocess.check_output(
                ["brew", "--prefix"], text=True
            ).strip()

            # Create the opt directory structure if it doesn't exist
            opt_dir = os.path.join(brew_prefix, "opt/py-winmail-opener/libexec")
            os.makedirs(opt_dir, exist_ok=True)

            # Copy handler_script to opt directory for version independence
            opt_handler_path = os.path.join(opt_dir, "winmail_handler.sh")
            shutil.copy2(handler_script_path, opt_handler_path)
            os.chmod(opt_handler_path, 0o775)  # More permissive for cleanup

            # Ensure Homebrew can clean it up later
            try:
                # Try to get Homebrew's group
                brew_group = subprocess.check_output(
                    ["stat", "-f", "%Sg", "/usr/local/bin/brew"], text=True
                ).strip()
                subprocess.run(["chgrp", brew_group, opt_handler_path], check=False)
            except Exception as e:
                print(f"Note: Could not update file permissions for cleanup: {e}")

            # Copy winmail_opener.py to opt directory for version independence
            opt_script_path = os.path.join(opt_dir, "winmail_opener.py")
            shutil.copy2(winmail_script, opt_script_path)

            # Set the regular app path
            app_path = os.path.join(
                brew_prefix, "opt/py-winmail-opener/share/WinmailOpener.app"
            )
            # Ensure the directory exists
            os.makedirs(os.path.dirname(app_path), exist_ok=True)
            print(f"Using Homebrew app location: {app_path}")
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"Error determining Homebrew prefix: {e}")
            # Fallback to a location that should be writable
            app_path = os.path.join(script_dir, "WinmailOpener.app")
            print(f"Using fallback app location: {app_path}")
    else:
        # Standard installation to user's Applications folder
        app_path = os.path.expanduser("~/Applications/WinmailOpener.app")

    # Create temp AppleScript file
    applescript_path = os.path.join(script_dir, "winmail_opener.applescript")

    # Define the AppleScript template
    applescript_template = """
-- Simple Winmail.dat file handler
-- This script handles opening .dat files without any launch agents

on open theFiles
    set filePath to POSIX path of (item 1 of theFiles)
    
    -- First, try to find the handler script in the Homebrew opt directory (version-independent)
    set homebrewHandler to "/usr/local/opt/py-winmail-opener/libexec/winmail_handler.sh"
    
    -- Use a do shell script that first checks if the file exists
    set handlerExists to do shell script "[ -f '" & homebrewHandler & "' ] && echo 'yes' || echo 'no'"
    
    if handlerExists is "yes" then
        do shell script "'" & homebrewHandler & "' '" & filePath & "'"
    else
        -- Fallback to original handler script path if it exists
        set originalHandler to "$HANDLER_SCRIPT_PATH$"
        set originalExists to do shell script "[ -f '" & originalHandler & "' ] && echo 'yes' || echo 'no'"
        
        if originalExists is "yes" then
            do shell script "'" & originalHandler & "' '" & filePath & "'"
        else
            -- Fallback to discover the handler script dynamically
            -- Find all possible winmail_handler.sh files in Homebrew Cellar
            set possibleHandlers to paragraphs of (do shell script "find /usr/local/Cellar/py-winmail-opener -name 'winmail_handler.sh' 2>/dev/null || echo ''")
            
            if (count of possibleHandlers) > 0 and item 1 of possibleHandlers is not "" then
                -- Use the first available handler script
                do shell script "'" & (item 1 of possibleHandlers) & "' '" & filePath & "'"
            else
                -- Ultimate fallback if no handler script is found
                display dialog "Error: Could not find the winmail_handler.sh script." buttons {"OK"} default button "OK" with title "WinmailOpener Error"
            end if
        end if
    end if
end open

on run
    display dialog "Please double-click a winmail.dat file instead of launching this app directly." buttons {"OK"} default button "OK" with title "WinmailOpener"
end run
"""

    # Replace the placeholder with the actual handler script path
    applescript_content = applescript_template.replace(
        "$HANDLER_SCRIPT_PATH$", handler_script_path
    )

    # Write the AppleScript with the substituted path
    with open(applescript_path, "w") as f:
        f.write(applescript_content)

    # Compile the AppleScript to a temporary app
    temp_app_path = os.path.join(tempfile.mkdtemp(), "TempWinmailOpener.app")
    subprocess.run(["osacompile", "-o", temp_app_path, applescript_path], check=True)

    # Update the Info.plist with proper file associations
    info_plist_path = os.path.join(temp_app_path, "Contents", "Info.plist")
    with open(info_plist_path, "rb") as f:
        info_plist = plistlib.load(f)

    # Set file associations
    info_plist["CFBundleDocumentTypes"] = [
        {
            "CFBundleTypeExtensions": ["dat"],
            "CFBundleTypeName": "Winmail.dat File",
            "CFBundleTypeRole": "Editor",
            "LSHandlerRank": "Owner",
            "LSTypeIsPackage": False,
        }
    ]
    info_plist["CFBundleIdentifier"] = "com.winmailopener.app"
    info_plist["LSHandlerRank"] = "Owner"

    # Add necessary keys for Apple Events but keep it minimal
    info_plist["NSAppleEventsUsageDescription"] = (
        "WinmailOpener needs to process winmail.dat files."
    )

    # Write updated Info.plist
    with open(info_plist_path, "wb") as f:
        plistlib.dump(info_plist, f)

    # Remove old app if it exists
    if os.path.exists(app_path):
        print(f"Removing existing app: {app_path}")
        shutil.rmtree(app_path)

    # Move the new app to Applications folder
    print(f"Installing app to {app_path}")
    shutil.copytree(temp_app_path, app_path)

    # Clean up temporary files
    os.unlink(applescript_path)
    shutil.rmtree(os.path.dirname(temp_app_path))

    # Register file associations with duti if available
    try:
        subprocess.run(["which", "duti"], check=True, stdout=subprocess.DEVNULL)
        print("Setting file associations with duti...")
        subprocess.run(
            ["duti", "-s", "com.winmailopener.app", ".dat", "all"], check=True
        )
    except:
        print("duti not available, using macOS native file association...")
        try:
            # Use the macOS native way to set file associations
            subprocess.run(
                [
                    "defaults",
                    "write",
                    "com.apple.LaunchServices/com.apple.launchservices.secure",
                    "LSHandlers",
                    "-array-add",
                    '{"LSHandlerContentType":"public.data","LSHandlerRoleAll":"com.winmailopener.app"}',
                ],
                check=True,
            )
            subprocess.run(
                [
                    "defaults",
                    "write",
                    "com.apple.LaunchServices/com.apple.launchservices.secure",
                    "LSHandlers",
                    "-array-add",
                    '{"LSHandlerExtension":"dat","LSHandlerRoleAll":"com.winmailopener.app"}',
                ],
                check=True,
            )
        except:
            print("Warning: Could not set file associations using defaults.")
            print("You'll need to manually set the file association.")

    # Update the Launch Services database
    try:
        subprocess.run(["touch", app_path], check=True)
        print("Updating Launch Services database...")
        subprocess.run(
            [
                "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister",
                "-f",
                app_path,
            ],
            check=True,
        )
    except:
        print(
            "Warning: Could not update Launch Services database. This is not critical."
        )

    # Create test file if it doesn't exist and not in Homebrew mode
    if not homebrew_mode:
        try:
            test_path = os.path.expanduser("~/Desktop/test_winmail.dat")
            if not os.path.exists(test_path):
                with open(test_path, "w") as f:
                    f.write(
                        "This is a test winmail.dat file for testing file associations."
                    )
        except Exception as e:
            print(f"Note: Could not create test file (this is not critical): {e}")

    return True


def test_app_bundle():
    """
    Test the application bundle by running it directly with a sample file.
    """
    print("\nTesting WinmailOpener.app...")
    app_path = os.path.expanduser("~/Applications/WinmailOpener.app")

    # Check if the app exists
    if not os.path.exists(app_path):
        print(f"Error: Application bundle not found at {app_path}")
        return

    # Check if we have a sample file
    sample_path = None
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Look for test file
    possible_samples = [os.path.join(os.path.dirname(current_dir), "test_winmail.dat")]

    for path in possible_samples:
        if os.path.exists(path):
            sample_path = path
            break

    if not sample_path:
        print("No sample winmail.dat file found for testing. Skipping test.")
        return

    # Find the handler script
    handler_script = os.path.join(current_dir, "winmail_handler.sh")
    if not os.path.exists(handler_script):
        print(f"Error: Handler script not found at {handler_script}")
        return

    # Run the test
    try:
        print(f"Testing with sample file: {sample_path}")
        # Execute the handler script with the sample file
        subprocess.run([handler_script, sample_path], check=True)
        print("Test completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running test: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during testing: {e}")


def main():
    """
    Main function to install dependencies and create the application.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Install WinmailOpener")
    parser.add_argument(
        "--homebrew-mode",
        action="store_true",
        help="Run in Homebrew mode with modified paths",
    )
    args = parser.parse_args()

    homebrew_mode = args.homebrew_mode

    print("=== WinmailOpener Installation ===")
    # Version 2.0.26 with version-independent paths
    # Version 2.0.25 with version-independent paths
    # Version 2.0.24 with version-independent paths
    # Version 2.0.23 with version-independent paths
    # Version 2.0.22 with version-independent paths
    # Version 2.0.21 with version-independent paths
    # Version 2.0.20 with version-independent paths
    # Version 2.0.19 with version-independent paths
    # Version 2.0.18 with version-independent paths
    # Version 2.0.17 with version-independent paths
    # Version 2.0.16 with version-independent paths
    # Version 2.0.15 with version-independent paths
    # Version 2.0.14 with version-independent paths
    # Version 2.0.13 with version-independent paths
    # Version 2.0.12 with version-independent paths
    # Version 2.0.11 with version-independent paths
    # Version 2.0.10 with version-independent paths
    # Version 2.0.9 with version-independent paths
    # Version 2.0.8 with version-independent paths
    # Version 2.0.7 with version-independent paths
    # Version 2.0.6 with version-independent paths
    # Version 2.0.5 with version-independent paths
    # Version 2.0.4 with version-independent paths
    # Version 2.0.3 with version-independent paths
    # Version 2.0.2 with version-independent paths
    # Version 2.0.1 with version-independent paths
    print("This script will:")
    print("1. Create a virtual environment and install dependencies")
    print(
        "2. Create a security-friendly AppleScript application for handling winmail.dat files"
    )
    print("3. Register the application as the default handler for .dat files")
    print()

    if homebrew_mode:
        print("Running in Homebrew mode")
        # In Homebrew mode, we use the system Python that Homebrew installed
        venv_python = sys.executable
    else:
        # Create a virtual environment and install dependencies
        venv_python = create_virtual_environment()
        if not venv_python:
            print(
                "Failed to create a virtual environment. The application may not work correctly."
            )
            if not homebrew_mode:
                response = input(
                    "Do you want to continue with the installation? (y/n): "
                )
                if response.lower() != "y":
                    print("Installation aborted.")
                    return
            else:
                # In Homebrew mode, continue without asking
                print("Continuing with system Python...")
                venv_python = sys.executable

    # Create the AppleScript handler application
    print("\nCreating AppleScript handler application...")
    if create_applescript_handler(venv_python, homebrew_mode):
        print("\nAppleScript handler application created successfully!")
    else:
        print("\nFailed to create AppleScript handler application.")
        return

    # Test the app bundle if not in Homebrew mode (avoid during package build)
    if not homebrew_mode:
        test_app_bundle()

    print("\nInstallation complete!")
    print("To finalize setup, please right-click on a winmail.dat file,")
    print("select 'Open With' > 'Other...', navigate to ~/Applications,")
    print("select WinmailOpener.app, and check 'Always Open With'.")


if __name__ == "__main__":
    main()
