#!/usr/bin/env python3
"""
Build script for creating WinmailOpener.app bundle and DMG for Homebrew Cask distribution.

This script:
1. Creates a standalone app bundle with all dependencies included
2. Optionally packages the app into a DMG for distribution
3. Calculates SHA256 hash for the DMG (for Homebrew Cask formula)

Usage:
  python build_app.py [--dmg] [--dev] [--version VERSION]
"""

import os
import sys
import subprocess
import shutil
import plistlib
import tempfile
import argparse
import re
import glob
import time

def get_version():
    """Extract version from setup.py"""
    with open("setup.py", "r") as f:
        content = f.read()
    
    match = re.search(r"version=['\"]([^'\"]+)['\"]", content)
    if match:
        return match.group(1)
    return "1.0.0"  # Default version

def compile_applescript(source_path, target_path):
    """
    Compile an AppleScript file into a binary executable
    
    Args:
        source_path: Path to the source .applescript file
        target_path: Path where the compiled script should be saved
    
    Returns:
        True if compilation succeeded, False otherwise
    """
    try:
        print(f"Compiling AppleScript from {source_path} to {target_path}")
        compile_cmd = [
            "osacompile",
            "-o", target_path,
            source_path
        ]
        subprocess.run(compile_cmd, check=True)
        print(f"AppleScript compilation successful")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error compiling AppleScript: {e}")
        return False

def build_app_bundle(version, dev_mode=False):
    """
    Build a standalone app bundle that includes all dependencies
    
    Args:
        version: Version string for the app
        dev_mode: If True, create a development build with '-dev' suffix
    
    Returns:
        Path to the created app bundle
    """
    # Get source directory
    src_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Determine app name
    if dev_mode:
        app_name = f"WinmailOpener-dev.app"
    else:
        app_name = f"WinmailOpener-{version}.app"
    
    print(f"Building {app_name}...")
    
    # Create directory structure
    app_dir = os.path.join(src_dir, app_name)
    contents_dir = os.path.join(app_dir, "Contents")
    macos_dir = os.path.join(contents_dir, "MacOS")
    resources_dir = os.path.join(contents_dir, "Resources")
    frameworks_dir = os.path.join(contents_dir, "Frameworks")
    python_dir = os.path.join(resources_dir, "python")
    
    # Remove existing app if it exists
    if os.path.exists(app_dir):
        print(f"Removing existing app bundle at {app_dir}")
        shutil.rmtree(app_dir)
    
    # Create directories
    for dir_path in [contents_dir, macos_dir, resources_dir, frameworks_dir, python_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Create Info.plist with proper file associations
    info_plist = {
        'CFBundleDisplayName': 'WinmailOpener',
        'CFBundleExecutable': 'document_handler',  # Use our AppleScript handler as the main executable
        'CFBundleIdentifier': 'com.github.jsbattig.winmailopener',
        'CFBundleName': 'WinmailOpener',
        'CFBundleVersion': version,
        'CFBundleShortVersionString': version,
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.14',
        'NSHumanReadableCopyright': '© 2025 jsbattig',
        'NSPrincipalClass': 'NSApplication',
        'NSAppleEventsUsageDescription': 'WinmailOpener uses AppleEvents to process files and display results.',
        'NSAppleScriptEnabled': True,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeExtensions': ['dat'],
                'CFBundleTypeName': 'Winmail.dat File',
                'CFBundleTypeRole': 'Editor',
                'LSHandlerRank': 'Owner',
                'LSTypeIsPackage': False,
                'CFBundleTypeIconFile': 'AppIcon.icns', 
                'LSItemContentTypes': ['com.microsoft.winmail.dat']
            }
        ],
        'UTExportedTypeDeclarations': [
            {
                'UTTypeIdentifier': 'com.microsoft.winmail.dat',
                'UTTypeDescription': 'Microsoft Outlook Winmail.dat File',
                'UTTypeConformsTo': ['public.data'],
                'UTTypeTagSpecification': {
                    'public.filename-extension': ['dat']
                }
            }
        ]
    }
    
    with open(os.path.join(contents_dir, 'Info.plist'), 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # Create icon
    print("Creating app icon (placeholder for now)...")
    # In a real app, you would include a proper icon
    icon_path = os.path.join(resources_dir, 'AppIcon.icns')
    # This is a placeholder - in a real implementation, you would copy an actual icon file
    # shutil.copy(os.path.join(src_dir, 'assets', 'icon.icns'), icon_path)
    
    # Copy Python script files to Resources
    print("Copying Python scripts...")
    for script in ['winmail_opener.py', 'extract_tnef.py']:
        if os.path.exists(os.path.join(src_dir, script)):
            shutil.copy(os.path.join(src_dir, script), os.path.join(resources_dir, script))
    
    # We'll still create the launcher script as a backup
    print("Creating launcher script...")
    with open(os.path.join(macos_dir, 'WinmailOpener'), 'w') as f:
        f.write('''#!/bin/bash
# Get the directory containing this script
DIR="$( cd "$( dirname "'''+r'${BASH_SOURCE[0]}'+'''" )" && pwd )"
RESOURCES="$DIR/../Resources"
PYTHON="$RESOURCES/python/bin/python3"

# Log file for debugging
LOG_FILE=~/WinmailOpener_log.txt

# Log this execution
echo "========================================" >> "$LOG_FILE"
echo "WinmailOpener launcher script executed at $(date)" >> "$LOG_FILE"
echo "Arguments received: $@" >> "$LOG_FILE"

# If this script is called with a file path, process it
if [ $# -gt 0 ]; then
    # Process the file
    "$PYTHON" "$RESOURCES/winmail_opener.py" "$@" 2>&1 | tee -a "$LOG_FILE"
    
    # Notify the user
    osascript -e 'display notification "Winmail.dat file processed. See your Downloads folder for extracted attachments." with title "WinmailOpener"'
else
    # Show a dialog if launched without arguments
    osascript -e 'display dialog "Please double-click a winmail.dat file instead of launching this app directly." buttons {"OK"} default button "OK" with title "WinmailOpener"'
fi
''')
    
    # Make launcher executable
    os.chmod(os.path.join(macos_dir, 'WinmailOpener'), 0o755)
    
    # Compile and add the AppleScript handler
    print("Adding AppleScript document handler...")
    src_dir = os.path.dirname(os.path.abspath(__file__))
    applescript_source = os.path.join(src_dir, "document_handler.applescript")
    applescript_target = os.path.join(macos_dir, "document_handler")
    
    if not compile_applescript(applescript_source, applescript_target):
        print("Warning: Could not compile AppleScript. Using fallback method.")
        # Copy the raw script as a fallback
        shutil.copy(applescript_source, os.path.join(resources_dir, "document_handler.applescript"))
    
    # Create launcher symlink
    print("Creating command-line symlink...")
    cli_path = os.path.join(macos_dir, 'winmail-opener')
    with open(cli_path, 'w') as f:
        f.write(f'''#!/bin/bash
# This is a CLI wrapper for the WinmailOpener application
DIR="$( cd "$( dirname "'''+r'${BASH_SOURCE[0]}'+'''" )" && pwd )"
"$DIR/WinmailOpener" "$@"
''')
    os.chmod(cli_path, 0o755)
    
    # Create Python virtual environment
    print("Creating embedded Python environment...")
    try:
        # First create a temporary venv
        temp_venv = os.path.join(tempfile.mkdtemp(), "venv")
        subprocess.run([sys.executable, "-m", "venv", temp_venv], check=True)
        
        # Install dependencies into venv
        venv_pip = os.path.join(temp_venv, "bin", "pip")
        subprocess.run([venv_pip, "install", "tnefparse", "chardet"], check=True)
        
        # Copy Python executable and libraries
        venv_python = os.path.join(temp_venv, "bin", "python3")
        shutil.copy(venv_python, os.path.join(python_dir, "bin", "python3"))
        
        # Copy Python libraries
        venv_site_packages = glob.glob(os.path.join(temp_venv, "lib", "python*", "site-packages"))[0]
        dest_site_packages = os.path.join(python_dir, "lib", "site-packages")
        os.makedirs(os.path.dirname(dest_site_packages), exist_ok=True)
        shutil.copytree(venv_site_packages, dest_site_packages)
        
        # Clean up temp venv
        shutil.rmtree(os.path.dirname(temp_venv))
    except Exception as e:
        print(f"Error creating embedded Python environment: {e}")
        print("Creating a minimal embedded Python environment instead...")
        
        # Create directories
        os.makedirs(os.path.join(python_dir, "bin"), exist_ok=True)
        os.makedirs(os.path.join(python_dir, "lib"), exist_ok=True)
        
        # Create a simple wrapper that uses system Python
        with open(os.path.join(python_dir, "bin", "python3"), 'w') as f:
            f.write('''#!/bin/bash
# Fallback to system Python
/usr/bin/env python3 "$@"
''')
        os.chmod(os.path.join(python_dir, "bin", "python3"), 0o755)
    
    print(f"App bundle created at: {app_dir}")
    return app_dir

def create_dmg(app_dir, version):
    """
    Package the app into a DMG
    
    Args:
        app_dir: Path to the app bundle
        version: Version string for the app
        
    Returns:
        Path to the created DMG
    """
    print("Creating DMG...")
    src_dir = os.path.dirname(os.path.abspath(__file__))
    dmg_path = os.path.join(src_dir, f"WinmailOpener-{version}.dmg")
    
    # Remove existing DMG if it exists
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
    
    # Create DMG using hdiutil
    try:
        subprocess.run([
            "hdiutil", "create",
            "-volname", "WinmailOpener",
            "-srcfolder", app_dir,
            "-ov", "-format", "UDZO",
            dmg_path
        ], check=True)
        
        print(f"DMG created at: {dmg_path}")
        return dmg_path
    except subprocess.CalledProcessError as e:
        print(f"Error creating DMG: {e}")
        return None
    except FileNotFoundError:
        print("Error: hdiutil command not found. This script requires macOS to create DMGs.")
        return None

def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file"""
    try:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return None
        
        # Use shasum command if available
        try:
            result = subprocess.run(
                ["shasum", "-a", "256", file_path],
                capture_output=True, text=True, check=True
            )
            return result.stdout.split()[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back to Python's hashlib
            import hashlib
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
    except Exception as e:
        print(f"Error calculating SHA256: {e}")
        return None

def generate_cask_formula(version, sha256):
    """Generate a cask formula template"""
    # We need to use double braces to escape Ruby template variables in Python f-strings
    cask_formula = f'''cask "py-winmail-opener" do
  version "{version}"
  sha256 "{sha256}"
  
  url "https://github.com/jsbattig/py-winmail-opener/releases/download/v#{{version}}/WinmailOpener-#{{version}}.dmg"
  name "WinmailOpener"
  desc "Extract attachments and email body from Winmail.dat files"
  homepage "https://github.com/jsbattig/py-winmail-opener"
  
  app "WinmailOpener-#{{version}}.app"
  
  # Use explicit path to application directory instead of appdir variable
  binary "/Applications/WinmailOpener-#{{version}}.app/Contents/MacOS/winmail-opener", target: "winmail-opener"
  
  uninstall delete: "/usr/local/bin/winmail-opener"
  
  zap trash: [
    "~/Library/Logs/WinmailOpener_log.txt",
    "~/Library/Preferences/com.github.jsbattig.winmailopener.plist"
  ]
end
'''
    return cask_formula

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Build WinmailOpener app bundle and DMG")
    parser.add_argument("--dmg", action="store_true", help="Create DMG after building app bundle")
    parser.add_argument("--dev", action="store_true", help="Create development build")
    parser.add_argument("--version", help="Specify version number (defaults to value from setup.py)")
    args = parser.parse_args()
    
    # Get version
    version = args.version if args.version else get_version()
    
    # Build app bundle
    app_dir = build_app_bundle(version, dev_mode=args.dev)
    
    # Create DMG if requested
    if args.dmg and app_dir:
        dmg_path = create_dmg(app_dir, version)
        
        if dmg_path:
            # Calculate SHA256
            sha256 = calculate_sha256(dmg_path)
            
            if sha256:
                print(f"SHA256: {sha256}")
                
                # Generate cask formula
                cask_formula = generate_cask_formula(version, sha256)
                print("\nCask Formula Template:")
                print("----------------------")
                print(cask_formula)
                
                # Write cask formula to file
                cask_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "py-winmail-opener-cask.rb")
                with open(cask_path, "w") as f:
                    f.write(cask_formula)
                print(f"\nCask formula written to: {cask_path}")
                
                # Instructions for testing locally
                print("\nTo test locally:")
                print(f"  brew install --cask {os.path.abspath(dmg_path)}")

if __name__ == "__main__":
    main()
