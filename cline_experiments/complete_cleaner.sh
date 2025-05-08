#!/bin/bash

# =====================================================================
# Complete Cleaner for py-winmail-opener
# =====================================================================
# This script completely removes all traces of py-winmail-opener from
# your local environment so you can reinstall fresh from GitHub
# =====================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Package information
FORMULA_NAME="py-winmail-opener"
HOMEBREW_PREFIX="/usr/local"
USER_HOME="$HOME"
APP_NAME="WinmailOpener"

# Function to display header
function print_header() {
  echo "====================================================================="
  echo -e "${BLUE}COMPLETE CLEANER FOR PY-WINMAIL-OPENER${NC}"
  echo "====================================================================="
  echo ""
}

# Function to get user confirmation
function confirm() {
  read -p "Continue? (y/n) " response
  case "$response" in
    [yY][eE][sS]|[yY]) 
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Function to remove files with sudo if needed
function remove_with_permission() {
  local path="$1"
  
  if [ -e "$path" ]; then
    if [ -w "$(dirname "$path")" ]; then
      echo -e "Removing ${path}..."
      rm -rf "$path"
      echo -e "${GREEN}✓ Removed${NC}"
    else
      echo -e "${YELLOW}Need elevated permissions to remove ${path}${NC}"
      sudo rm -rf "$path"
      echo -e "${GREEN}✓ Removed with sudo${NC}"
    fi
  fi
}

# Main cleanup function
function cleanup() {
  echo -e "${BLUE}Starting thorough cleanup...${NC}"
  
  # 1. Untap the formula first to ensure no locks
  echo -e "\n${YELLOW}Untapping any existing taps...${NC}"
  brew untap jsbattig/winmail 2>/dev/null || true
  
  # 2. Remove Homebrew caches
  echo -e "\n${YELLOW}Removing Homebrew caches...${NC}"
  remove_with_permission "${HOMEBREW_PREFIX}/var/homebrew/locks/${FORMULA_NAME}.formula.lock"
  remove_with_permission "${HOMEBREW_PREFIX}/Caskroom/${FORMULA_NAME}*"
  remove_with_permission "${HOMEBREW_PREFIX}/Cellar/${FORMULA_NAME}"
  
  # 3. Remove app bundle
  echo -e "\n${YELLOW}Removing application bundles...${NC}"
  remove_with_permission "/Applications/${APP_NAME}.app"
  remove_with_permission "${USER_HOME}/Applications/${APP_NAME}.app"
  
  # 4. Remove preference files
  echo -e "\n${YELLOW}Removing preference files...${NC}"
  remove_with_permission "${USER_HOME}/Library/Preferences/com.jsbattig.${FORMULA_NAME}.plist"
  remove_with_permission "${USER_HOME}/Library/Saved Application State/com.jsbattig.${FORMULA_NAME}.savedState"
  
  # 5. Remove symlinks
  echo -e "\n${YELLOW}Removing symlinks...${NC}"
  remove_with_permission "${HOMEBREW_PREFIX}/bin/winmail-opener"
  
  # 6. Clean remaining files
  echo -e "\n${YELLOW}Searching for any remaining traces...${NC}"
  
  # Find any remaining formula files
  remaining_files=$(find ${HOMEBREW_PREFIX} -name "*${FORMULA_NAME}*" 2>/dev/null | grep -v "/Taps/" || true)
  
  if [ ! -z "$remaining_files" ]; then
    echo "Found remaining files:"
    echo "$remaining_files"
    echo ""
    echo -e "${YELLOW}Removing remaining files...${NC}"
    while IFS= read -r file; do
      remove_with_permission "$file"
    done <<< "$remaining_files"
  else
    echo -e "${GREEN}No additional formula files found${NC}"
  fi
  
  # 7. Re-tap to get the latest version
  echo -e "\n${YELLOW}Re-tapping homebrew formula...${NC}"
  brew tap jsbattig/winmail
  
  echo -e "\n${GREEN}CLEANUP COMPLETE!${NC}"
  echo "You can now reinstall the formula with:"
  echo -e "${BLUE}brew install jsbattig/winmail/${FORMULA_NAME}${NC}"
  echo ""
}

# Main script execution
print_header

echo -e "${RED}WARNING: This script will completely remove all traces of ${FORMULA_NAME}${NC}"
echo -e "${RED}including installed formula, app bundle, and preferences.${NC}"
echo -e "${YELLOW}Make sure you want to completely reset this package before continuing.${NC}"
echo ""

if confirm; then
  cleanup
else
  echo -e "\n${RED}Cleanup cancelled${NC}"
fi
