#!/usr/bin/env python3
"""
Script to fix the file association for Winmail.dat files on macOS.

This script:
1. Creates a LaunchServices database entry for the app
2. Associates the .dat extension with the app
3. Refreshes the LaunchServices database
"""

import os
import subprocess
import sys
import plistlib

def print_step(message):
    """Print a step message with some formatting."""
    print("\n" + "="*80)
    print(f"  {message}")
    print("="*80)

def run_command(command, description=None):
    """Run a shell command and print its output."""
    if description:
        print(f"\n> {description}")
    
    print(f"$ {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(f"ERROR: {result.stderr}")
    
    return result.returncode == 0

def is_app_installed(app_path):
    """Check if the app is installed at the specified path."""
    return os.path.exists(app_path) and os.path.isdir(app_path)

def get_current_app_path():
    """Get the path to the currently installed app."""
    # Find all WinmailOpener apps in the Applications folder
    result = subprocess.run(
        ["find", "/Applications", "-name", "WinmailOpener*.app", "-type", "d"],
        capture_output=True, text=True
    )
    
    apps = result.stdout.strip().split("\n")
    apps = [app for app in apps if app]  # Remove empty entries
    
    if not apps:
        return None
    
    # Return the most recent version (assuming the highest version number)
    return sorted(apps)[-1]

def check_app_info(app_path):
    """Check the Info.plist of the app for proper settings."""
    info_plist_path = os.path.join(app_path, "Contents", "Info.plist")
    
    if not os.path.exists(info_plist_path):
        print(f"ERROR: Info.plist not found at {info_plist_path}")
        return False
    
    try:
        with open(info_plist_path, 'rb') as f:
            info = plistlib.load(f)
        
        # Check for document type registration
        if not info.get('CFBundleDocumentTypes'):
            print("ERROR: No document types registered in Info.plist")
            return False
        
        # Check for .dat extension registration
        for doc_type in info.get('CFBundleDocumentTypes', []):
            extensions = doc_type.get('CFBundleTypeExtensions', [])
            if 'dat' in extensions:
                print("✓ Found .dat extension registration in Info.plist")
                return True
        
        print("ERROR: No .dat extension found in document types")
        return False
        
    except Exception as e:
        print(f"ERROR: Failed to read Info.plist: {e}")
        return False

def fix_file_association():
    """Fix the file association for Winmail.dat files."""
    print_step("Checking for installed WinmailOpener app")
    
    app_path = get_current_app_path()
    if not app_path:
        print("ERROR: WinmailOpener app not found in /Applications")
        return False
    
    print(f"Found app at: {app_path}")
    
    print_step("Checking app bundle structure")
    if not check_app_info(app_path):
        print("ERROR: App bundle has issues with its Info.plist")
        return False
    
    print_step("Setting up file association using lsregister")
    
    # Reset the LaunchServices database for the app
    run_command([
        "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister",
        "-u", app_path
    ], "Unregistering app from LaunchServices")
    
    # Register the app with LaunchServices
    run_command([
        "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister",
        "-f", app_path
    ], "Registering app with LaunchServices")
    
    print_step("Setting up file type association for .dat files")
    
    # Associate .dat extension specifically
    bundle_id = f"com.github.jsbattig.winmailopener"
    
    # Use duti for file association (if available)
    duti_success = run_command([
        "duti", "-s", bundle_id, "com.microsoft.winmail.dat", "all"
    ], "Setting file association using duti")
    
    if not duti_success:
        print("WARNING: duti command failed, trying alternative method")
        
        # Alternative: Use defaults command
        run_command([
            "defaults", "write", "com.apple.LaunchServices/com.apple.launchservices.secure",
            "LSHandlers", "-array-add",
            f'{{"LSHandlerContentType":"com.microsoft.winmail.dat","LSHandlerRoleAll":"{bundle_id}"}}'
        ], "Setting file association using defaults")
    
    print_step("Refreshing LaunchServices database")
    
    # Force LaunchServices to update
    run_command([
        "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister",
        "-kill", "-r", "-domain", "local", "-domain", "system", "-domain", "user"
    ], "Refreshing LaunchServices database")
    
    # Touch the application to update its modification time
    run_command(["touch", app_path], "Updating app modification time")
    
    print_step("File association setup complete")
    print(f"\nWinmail.dat files should now open with: {app_path}")
    print("\nIf this doesn't work immediately, you may need to:")
    print("1. Log out and back in")
    print("2. Clear the application cache: killall Finder; killall Dock")
    print("3. Reset the LaunchServices database: /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user")
    
    return True

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script should be run with sudo to ensure proper file association")
        print("Please run: sudo python3 fix_file_association.py")
        sys.exit(1)
    
    success = fix_file_association()
    sys.exit(0 if success else 1)
