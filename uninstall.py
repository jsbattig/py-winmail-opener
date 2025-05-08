#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import argparse
import glob

def uninstall_app(force=False):
    """
    Remove the WinmailOpener application bundle from ~/Applications.
    """
    app_paths = [
        os.path.expanduser("~/Applications/WinmailOpener.app"),
        "/Applications/WinmailOpener.app"  # Check system Applications directory too
    ]
    
    success = True
    app_found = False
    
    for app_path in app_paths:
        if os.path.exists(app_path):
            app_found = True
            print(f"Removing application: {app_path}")
            try:
                shutil.rmtree(app_path)
                print(f"Application removed successfully from {app_path}.")
            except Exception as e:
                print(f"Error removing application from {app_path}: {e}")
                success = False
    
    if not app_found and not force:
        print("Application not found in Applications folders. It may have been removed already.")
    
    return success

def remove_file_associations():
    """
    Remove file associations for .dat files.
    """
    print("Removing file associations...")
    
    try:
        # Try using duti first
        subprocess.run(["which", "duti"], check=True, stdout=subprocess.DEVNULL)
        print("Using duti to remove file associations...")
        
        # This will reset the association to the system default
        subprocess.run(["duti", "-s", "com.apple.finder", ".dat", "all"], check=False)
        print("File associations removed using duti.")
    except:
        print("duti not available, using macOS native methods...")
        try:
            # This command removes the specific handler entries
            subprocess.run([
                "defaults", "delete", "com.apple.LaunchServices/com.apple.launchservices.secure", 
                "LSHandlers"
            ], check=False)
            print("Attempted to remove file associations with defaults command.")
        except Exception as e:
            print(f"Warning: Could not fully remove file associations: {e}")
            print("You may need to manually reassign .dat files in Finder if needed.")
    
    # Reset Launch Services database
    try:
        subprocess.run([
            "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister",
            "-kill", "-r", "-domain", "local", "-domain", "user"
        ], check=False)
        print("Launch Services database has been reset.")
    except Exception as e:
        print(f"Warning: Could not reset Launch Services database: {e}")
    
    return True

def clean_handler_script():
    """
    Remove the handler script.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    handler_script = os.path.join(script_dir, "winmail_handler.sh")
    
    if os.path.exists(handler_script):
        print(f"Removing handler script: {handler_script}")
        try:
            os.remove(handler_script)
            print("Handler script removed successfully.")
        except Exception as e:
            print(f"Error removing handler script: {e}")
            return False
    else:
        print("Handler script not found. It may have been removed already.")
    
    return True

def remove_test_files():
    """
    Remove any test files created by the installer.
    """
    test_file = os.path.expanduser("~/Desktop/test_winmail.dat")
    if os.path.exists(test_file):
        print(f"Removing test file: {test_file}")
        try:
            os.remove(test_file)
            print("Test file removed successfully.")
        except Exception as e:
            print(f"Error removing test file: {e}")
            return False
    else:
        print("Test file not found on Desktop. It may have been removed already.")
    
    return True

def remove_virtual_environment():
    """
    Remove the virtual environment.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, "venv")
    
    if os.path.exists(venv_dir):
        print(f"Removing virtual environment: {venv_dir}")
        try:
            shutil.rmtree(venv_dir)
            print("Virtual environment removed successfully.")
        except Exception as e:
            print(f"Error removing virtual environment: {e}")
            return False
    else:
        print("Virtual environment not found. It may have been removed already.")
    
    return True

def remove_log_files():
    """
    Remove log files created by the application.
    """
    log_file = os.path.expanduser("~/WinmailOpener_log.txt")
    debug_log = os.path.expanduser("~/winmail_opener_debug.log")
    
    for file_path in [log_file, debug_log]:
        if os.path.exists(file_path):
            print(f"Removing log file: {file_path}")
            try:
                os.remove(file_path)
                print(f"Log file {os.path.basename(file_path)} removed successfully.")
            except Exception as e:
                print(f"Error removing log file {file_path}: {e}")
    
    return True

def remove_homebrew_files(force=False):
    """
    Remove Homebrew-specific files for py-winmail-opener.
    """
    # Potential Homebrew Cellar directories
    cellar_paths = [
        "/usr/local/Cellar/py-winmail-opener",
        "/opt/homebrew/Cellar/py-winmail-opener"
    ]
    
    # Potential binary wrapper paths
    bin_paths = [
        "/usr/local/bin/winmail-opener",
        "/opt/homebrew/bin/winmail-opener"
    ]
    
    success = True
    
    # Clean up Cellar directories
    found_cellar = False
    for cellar_path in cellar_paths:
        if os.path.exists(cellar_path):
            found_cellar = True
            print(f"Removing Homebrew Cellar directory: {cellar_path}")
            try:
                # Find all version directories
                version_dirs = glob.glob(os.path.join(cellar_path, "*"))
                for version_dir in version_dirs:
                    if os.path.isdir(version_dir):
                        print(f"Removing version directory: {version_dir}")
                        shutil.rmtree(version_dir)
                
                # Try to remove the main directory if empty
                if not os.listdir(cellar_path):
                    os.rmdir(cellar_path)
                
                print(f"Homebrew Cellar directory removed successfully.")
            except Exception as e:
                print(f"Error removing Homebrew Cellar directory: {e}")
                success = False
    
    if not found_cellar and not force:
        print("No Homebrew Cellar directory found for py-winmail-opener.")
    
    # Clean up binary wrappers
    found_bin = False
    for bin_path in bin_paths:
        if os.path.exists(bin_path):
            found_bin = True
            print(f"Removing Homebrew binary wrapper: {bin_path}")
            try:
                os.remove(bin_path)
                print(f"Homebrew binary wrapper removed successfully.")
            except Exception as e:
                print(f"Error removing Homebrew binary wrapper: {e}")
                success = False
    
    if not found_bin and not force:
        print("No Homebrew binary wrapper found for winmail-opener.")
    
    return success

def main():
    """
    Main function to handle the uninstallation process.
    """
    parser = argparse.ArgumentParser(description="Uninstall Winmail.dat Opener")
    parser.add_argument("--keep-venv", action="store_true", help="Keep the virtual environment")
    parser.add_argument("--keep-logs", action="store_true", help="Keep log files")
    parser.add_argument("--homebrew-mode", action="store_true", help="Run in Homebrew uninstallation mode")
    parser.add_argument("--force", action="store_true", help="Force removal even if components are not found")
    args = parser.parse_args()
    
    print("=== Winmail.dat Opener Uninstaller ===")
    print("This script will remove Winmail.dat Opener components from your system.")
    
    success = True
    
    # Step 1: Remove the application bundle
    if not uninstall_app(args.force):
        success = False
        
    # Step 1b: Remove Homebrew files if in homebrew mode or if explicitly requested
    if args.homebrew_mode or args.force:
        print("\nDetected Homebrew installation mode. Cleaning up Homebrew files...")
        if not remove_homebrew_files(args.force):
            success = False
    
    # Step 2: Remove file associations
    if not remove_file_associations():
        success = False
    
    # Step 3: Clean up handler script
    if not clean_handler_script():
        success = False
    
    # Step 4: Remove test files
    if not remove_test_files():
        success = False
    
    # Step 5: Remove virtual environment (unless --keep-venv is specified)
    if not args.keep_venv:
        if not remove_virtual_environment():
            success = False
    else:
        print("Keeping virtual environment as requested.")
    
    # Step 6: Remove log files (unless --keep-logs is specified)
    if not args.keep_logs:
        if not remove_log_files():
            success = False
    else:
        print("Keeping log files as requested.")
    
    if success:
        print("\nUninstallation completed successfully!")
    else:
        print("\nUninstallation completed with some errors. Please check the messages above.")
    
    print("\nNote: If you want to reinstall the application, simply run install.py again.")

if __name__ == "__main__":
    main()
