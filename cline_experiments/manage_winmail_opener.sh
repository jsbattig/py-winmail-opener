#!/bin/bash

# =====================================================================
# Py-Winmail-Opener Package Manager
# =====================================================================
# This script safely manages the py-winmail-opener package, working around
# the "wrong number of arguments" error in the Homebrew formula.
# =====================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
INSTALLED_PATH="/usr/local/Cellar/py-winmail-opener/1.0.9"
ORIGINAL_BIN="/usr/local/bin/winmail-opener"
TAP_PATH="/usr/local/Homebrew/Library/Taps/jsbattig/homebrew-winmail"
FORMULA_PATH="$TAP_PATH/py-winmail-opener.rb"
VENV_PATH="$INSTALLED_PATH/libexec/venv"
LOCAL_BIN_DIR="$HOME/bin"
LOCAL_WRAPPER="$LOCAL_BIN_DIR/winmail-opener-local"

function print_header() {
    echo "======================================================================================"
    echo -e "${BLUE}PY-WINMAIL-OPENER MANAGER${NC}"
    echo "======================================================================================"
    echo ""
}

function check_installation() {
    if [ -f "$ORIGINAL_BIN" ]; then
        echo -e "${GREEN}✓ Py-winmail-opener is installed${NC}"
        return 0
    else
        echo -e "${RED}✗ Py-winmail-opener is not installed${NC}"
        return 1
    fi
}

function create_wrapper() {
    echo -e "${BLUE}Creating local wrapper script...${NC}"
    
    # Create local bin directory if it doesn't exist
    mkdir -p "$LOCAL_BIN_DIR"
    
    # Create wrapper script
    cat > "$LOCAL_WRAPPER" << EOL
#!/bin/bash
# This is a wrapper for winmail-opener that bypasses Homebrew
# Created by manage_winmail_opener.sh

if [ -f "$INSTALLED_PATH/libexec/bin/winmail-opener" ]; then
    exec "$INSTALLED_PATH/libexec/bin/winmail-opener" "\$@"
else
    echo "Error: winmail-opener binary not found at $INSTALLED_PATH"
    echo "The application may need to be reinstalled."
    exit 1
fi
EOL
    
    # Make executable
    chmod +x "$LOCAL_WRAPPER"
    
    echo -e "${GREEN}✓ Created wrapper script at $LOCAL_WRAPPER${NC}"
    
    # Add to path if needed
    if [[ ":$PATH:" != *":$LOCAL_BIN_DIR:"* ]]; then
        echo -e "${YELLOW}ℹ Adding $LOCAL_BIN_DIR to your PATH${NC}"
        echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.bash_profile"
        echo -e "${YELLOW}ℹ For immediate effect, run: source ~/.bash_profile${NC}"
    fi
}

function show_workaround() {
    echo -e "${BLUE}WORKAROUND FOR HOMEBREW ERRORS${NC}"
    echo ""
    echo -e "You can use the local wrapper script to run winmail-opener:"
    echo ""
    echo -e "   ${GREEN}$LOCAL_WRAPPER${NC}"
    echo ""
    echo -e "This completely bypasses Homebrew's formula issue."
    echo ""
}

function try_run_uninstaller() {
    echo -e "${BLUE}Attempting to run the uninstaller script directly...${NC}"
    
    if [ -f "$VENV_PATH/bin/python" ] && [ -f "$INSTALLED_PATH/uninstall.py" ]; then
        echo -e "${YELLOW}ℹ Running uninstaller script${NC}"
        "$VENV_PATH/bin/python" "$INSTALLED_PATH/uninstall.py" --force
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Uninstaller completed successfully${NC}"
        else
            echo -e "${RED}✗ Uninstaller reported errors, but may have partially worked${NC}"
        fi
    else
        echo -e "${RED}✗ Could not find Python or uninstaller script${NC}"
    fi
}

function show_version() {
    if [ -f "$LOCAL_WRAPPER" ]; then
        echo -e "${BLUE}Checking installed version...${NC}"
        VERSION_OUTPUT=$("$LOCAL_WRAPPER" --version 2>&1)
        echo -e "${GREEN}Version: $VERSION_OUTPUT${NC}"
    else
        echo -e "${RED}✗ Wrapper script not found. Run 'create-wrapper' first.${NC}"
    fi
}

function show_help() {
    print_header
    echo -e "${BLUE}AVAILABLE COMMANDS:${NC}"
    echo ""
    echo -e "  ${GREEN}status${NC}          - Check if py-winmail-opener is installed"
    echo -e "  ${GREEN}create-wrapper${NC}  - Create a local wrapper script (bypasses Homebrew)"
    echo -e "  ${GREEN}run${NC} [args]      - Run winmail-opener with arguments"
    echo -e "  ${GREEN}version${NC}         - Show installed version"
    echo -e "  ${GREEN}uninstall${NC}       - Try to run uninstaller directly (may help with cleanup)"
    echo ""
    echo -e "${YELLOW}BACKGROUND:${NC}"
    echo -e "The Homebrew formula for py-winmail-opener has a method signature issue"
    echo -e "that prevents normal upgrade and uninstall operations. This script provides"
    echo -e "workarounds for these issues."
    echo ""
}

# Main command handling
case "$1" in
    status)
        print_header
        check_installation
        ;;
    create-wrapper)
        print_header
        create_wrapper
        show_workaround
        ;;
    run)
        shift
        if [ -f "$LOCAL_WRAPPER" ]; then
            "$LOCAL_WRAPPER" "$@"
        else
            print_header
            echo -e "${RED}✗ Wrapper script not found. Run 'create-wrapper' first.${NC}"
            exit 1
        fi
        ;;
    version)
        print_header
        show_version
        ;;
    uninstall)
        print_header
        try_run_uninstaller
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        print_header
        echo -e "${RED}Unknown command: $1${NC}"
        echo -e "Run '${GREEN}$0 help${NC}' for usage information."
        exit 1
        ;;
esac
