#!/bin/bash

# =============================================================================
# Manual Installation Script for py-winmail-opener
# =============================================================================
# This script completely bypasses Homebrew and manually installs
# py-winmail-opener directly on your system
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation paths
INSTALL_BASE="$HOME/.py-winmail-opener"
APP_PATH="$HOME/Applications/WinmailOpener.app"
BIN_PATH="/usr/local/bin/winmail-opener"

echo "======================================================================="
echo -e "${BLUE}PY-WINMAIL-OPENER MANUAL INSTALLER${NC}"
echo "======================================================================="
echo ""
echo -e "${YELLOW}This script will install py-winmail-opener directly without using Homebrew.${NC}"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required but not found. Please install Python 3 first.${NC}"
    exit 1
fi

# Create installation directory
echo -e "${BLUE}Creating installation directory...${NC}"
mkdir -p "$INSTALL_BASE"
mkdir -p "$INSTALL_BASE/bin"

# Copy files to installation directory
echo -e "${BLUE}Copying files...${NC}"
# Copy all Python files and other resources from the current directory
cp -R py-winmail-opener/*.py "$INSTALL_BASE/"
cp -R py-winmail-opener/LICENSE "$INSTALL_BASE/"
cp -R py-winmail-opener/README.md "$INSTALL_BASE/"

# Create a virtual environment
echo -e "${BLUE}Creating Python virtual environment...${NC}"
python3 -m venv "$INSTALL_BASE/venv"

# Activate the virtual environment and install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
"$INSTALL_BASE/venv/bin/pip" install --upgrade pip
"$INSTALL_BASE/venv/bin/pip" install tnefparse chardet

# Create the wrapper script
echo -e "${BLUE}Creating wrapper script...${NC}"
cat > "$INSTALL_BASE/bin/winmail-opener" << EOF
#!/bin/bash
exec "$INSTALL_BASE/venv/bin/python" "$INSTALL_BASE/winmail_opener.py" "\$@"
EOF

# Make the wrapper executable
chmod 0755 "$INSTALL_BASE/bin/winmail-opener"

# Create symlink in /usr/local/bin if it doesn't exist
echo -e "${BLUE}Creating symlink in /usr/local/bin...${NC}"
if [ -f "$BIN_PATH" ]; then
    echo -e "${YELLOW}Removing existing symlink...${NC}"
    sudo rm -f "$BIN_PATH"
fi
sudo ln -sf "$INSTALL_BASE/bin/winmail-opener" "$BIN_PATH"

# Run the installer script to create the application bundle
echo -e "${BLUE}Creating application bundle...${NC}"
"$INSTALL_BASE/venv/bin/python" "$INSTALL_BASE/install.py" --force

# Verify installation
echo -e "${BLUE}Verifying installation...${NC}"

if [ -d "$APP_PATH" ]; then
    echo -e "${GREEN}✓ Application bundle created successfully${NC}"
else
    echo -e "${YELLOW}⚠ Application bundle was not created at the expected location${NC}"
    echo "  You may need to run the installer manually with:"
    echo "  $INSTALL_BASE/venv/bin/python $INSTALL_BASE/install.py --force"
fi

if [ -f "$BIN_PATH" ] && [ -x "$BIN_PATH" ]; then
    echo -e "${GREEN}✓ Command-line tool installed successfully${NC}"
    
    # Test the command-line tool
    VERSION_OUTPUT=$("$BIN_PATH" --version 2>&1)
    if [[ "$VERSION_OUTPUT" == *"winmail_opener"* ]]; then
        echo -e "${GREEN}✓ Command-line tool is working correctly${NC}"
    else
        echo -e "${YELLOW}⚠ Command-line tool may not be working correctly${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Command-line tool was not installed properly${NC}"
fi

# Print final instructions
echo ""
echo "======================================================================="
echo -e "${GREEN}INSTALLATION COMPLETE!${NC}"
echo "======================================================================="
echo ""
echo "You can now use py-winmail-opener in the following ways:"
echo ""
echo "1. Double-click on Winmail.dat files to open them with the WinmailOpener app"
echo "2. Use the command-line tool: winmail-opener [path-to-dat-file]"
echo ""
echo -e "${YELLOW}If you encounter any issues with file associations, you can run:${NC}"
echo "$INSTALL_BASE/venv/bin/python $INSTALL_BASE/install.py --force"
echo ""
echo -e "${YELLOW}To uninstall, run:${NC}"
echo "$INSTALL_BASE/venv/bin/python $INSTALL_BASE/uninstall.py --force"
echo ""
