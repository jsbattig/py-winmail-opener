#!/usr/bin/env python3
"""
Verify Uninstallation of Winmail.dat Opener

This script verifies that all components of the Winmail.dat Opener
application have been properly removed from the system, even if
Homebrew's uninstallation process had errors.

Usage:
  python verify_uninstall.py

Output:
  A report of any remaining components that need cleanup.
"""

import os
import glob
import subprocess
import sys

def check_color(text, success=True):
    """Add color to terminal output."""
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'
    
    if success:
        return f"{green}✓ {text}{end}"
    else:
        return f"{red}✗ {text}{end}"

def check_app_bundles():
    """Check if any WinmailOpener.app bundles remain."""
    app_paths = [
        os.path.expanduser("~/Applications/WinmailOpener.app"),
        "/Applications/WinmailOpener.app"
    ]
    
    found = False
    for path in app_paths:
        if os.path.exists(path):
            found = True
            print(check_color(f"App bundle found: {path}", False))
    
    if not found:
        print(check_color("No application bundles found"))
    
    return not found

def check_homebrew_files():
    """Check if any Homebrew files remain."""
    cellar_paths = [
        "/usr/local/Cellar/py-winmail-opener",
        "/opt/homebrew/Cellar/py-winmail-opener"
    ]
    
    bin_paths = [
        "/usr/local/bin/winmail-opener",
        "/opt/homebrew/bin/winmail-opener"
    ]
    
    success = True
    
    # Check Cellar directories
    for path in cellar_paths:
        if os.path.exists(path):
            success = False
            print(check_color(f"Homebrew Cellar directory found: {path}", False))
            # List any version directories
            versions = glob.glob(os.path.join(path, "*"))
            for version in versions:
                if os.path.isdir(version):
                    print(f"  - Version directory: {version}")
    
    # Check binary wrappers
    for path in bin_paths:
        if os.path.exists(path):
            success = False
            print(check_color(f"Homebrew binary wrapper found: {path}", False))
    
    if success:
        print(check_color("No Homebrew files found"))
    
    return success

def check_file_associations():
    """Check if .dat file associations still point to WinmailOpener."""
    try:
        # Try using duti to check file associations
        result = subprocess.run(
            ["duti", "-x", ".dat"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if "WinmailOpener" in result.stdout:
            print(check_color("File association for .dat files still points to WinmailOpener", False))
            return False
        else:
            print(check_color("No WinmailOpener file associations found"))
            return True
    except:
        # If duti isn't available, we can't easily check
        print("Cannot check file associations (duti not available)")
        return True

def check_log_files():
    """Check if any log files remain."""
    log_paths = [
        os.path.expanduser("~/WinmailOpener_log.txt"),
        os.path.expanduser("~/winmail_opener_debug.log")
    ]
    
    found = False
    for path in log_paths:
        if os.path.exists(path):
            found = True
            print(check_color(f"Log file found: {path}", False))
    
    if not found:
        print(check_color("No log files found"))
    
    return not found

def suggest_cleanup(all_clean):
    """Suggest cleanup commands if needed."""
    if all_clean:
        print("\n====================================================")
        print("✅ All components appear to be properly removed!")
        print("====================================================")
        return
    
    print("\n====================================================")
    print("⚠️  Some components remain on your system")
    print("====================================================")
    print("\nTo completely remove all components, run:")
    print("\npython py-winmail-opener/uninstall.py --force --homebrew-mode\n")
    print("This will:")
    print("- Remove application bundles from ~/Applications and /Applications")
    print("- Remove Homebrew files from Cellar and bin directories")
    print("- Reset file associations for .dat files")
    print("- Remove log files and any other components")

def main():
    """Main function to check for remaining components."""
    print("\n====================================================")
    print("🔍 Checking for Winmail.dat Opener components...")
    print("====================================================\n")
    
    app_clean = check_app_bundles()
    print("")
    
    brew_clean = check_homebrew_files()
    print("")
    
    assoc_clean = check_file_associations()
    print("")
    
    log_clean = check_log_files()
    
    all_clean = app_clean and brew_clean and assoc_clean and log_clean
    
    suggest_cleanup(all_clean)

if __name__ == "__main__":
    main()
