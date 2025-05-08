#!/bin/bash

# This script fixes the Homebrew formula by copying the corrected version to the tap location
# It needs to be run with sudo permissions

# Path to the fixed formula in the repo
FIXED_FORMULA="$PWD/py-winmail-opener/homebrew/py-winmail-opener.rb"

# Path to the tap formula
TAP_FORMULA="/usr/local/Homebrew/Library/Taps/jsbattig/homebrew-winmail/py-winmail-opener.rb"

echo "Fixing Homebrew formula..."
echo "  Source: $FIXED_FORMULA"
echo "  Target: $TAP_FORMULA"

# Copy the fixed formula to the tap location
cp -f "$FIXED_FORMULA" "$TAP_FORMULA"

if [ $? -eq 0 ]; then
    echo "Formula successfully updated!"
    echo "Running brew cleanup to refresh cache..."
    brew cleanup
    echo "Done!"
else
    echo "Failed to update formula. You might need to run this script with sudo."
    echo "Try: sudo $0"
fi
