#!/bin/bash
# Fix file associations for WinmailOpener on macOS
# This script helps fix file associations when they aren't working properly

echo "=================================================="
echo "WinmailOpener File Association Fix"
echo "=================================================="
echo 

# Find the app
APP_PATH=$(find /Applications -name "WinmailOpener*.app" -type d -depth 1 | sort | tail -n 1)

if [ -z "$APP_PATH" ]; then
    echo "ERROR: Could not find WinmailOpener.app in your Applications folder."
    echo "Please make sure the app is installed properly."
    exit 1
fi

echo "Found app at: $APP_PATH"

# Get the bundle identifier from the app
BUNDLE_ID=$(defaults read "$APP_PATH/Contents/Info" CFBundleIdentifier 2>/dev/null)

if [ -z "$BUNDLE_ID" ]; then
    echo "ERROR: Could not get bundle identifier from app."
    BUNDLE_ID="com.github.jsbattig.winmailopener"
    echo "Using default bundle identifier: $BUNDLE_ID"
fi

echo "Bundle ID: $BUNDLE_ID"
echo

# Reset the LaunchServices database for this app
echo "Resetting LaunchServices registration for the app..."
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -u "$APP_PATH"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_PATH"

# Try using the duti command if available
if command -v duti >/dev/null 2>&1; then
    echo "Setting file association using duti..."
    duti -s "$BUNDLE_ID" ".dat" all
    duti -s "$BUNDLE_ID" "com.microsoft.winmail.dat" all
else
    echo "duti command not found, using alternative method..."
    
    # Alternative method using defaults
    echo "Setting default handler for .dat files..."
    defaults write com.apple.LaunchServices/com.apple.launchservices.secure LSHandlers -array-add \
        "{LSHandlerContentType=public.data;LSHandlerRoleAll=$BUNDLE_ID;}" \
        "{LSHandlerContentType=com.microsoft.winmail.dat;LSHandlerRoleAll=$BUNDLE_ID;}" \
        "{LSHandlerExtension=dat;LSHandlerRoleAll=$BUNDLE_ID;}"
fi

# Force a refresh of the Launch Services database
echo "Refreshing LaunchServices database..."
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user

echo
echo "Touch the app to update modification time..."
touch "$APP_PATH"

echo "Restarting Finder..."
killall Finder 2>/dev/null

echo 
echo "=================================================="
echo "File association fix completed!"
echo
echo "If Winmail.dat files still don't open with WinmailOpener:"
echo "1. Log out and log back in to your Mac account"
echo "2. Right-click on a Winmail.dat file, select 'Open With' > 'Other...'"
echo "3. Select WinmailOpener from the Applications folder"
echo "4. Check 'Always Open With' and click Open"
echo "=================================================="
