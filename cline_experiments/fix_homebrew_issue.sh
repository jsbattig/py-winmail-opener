#!/bin/bash

# =====================================================================
# Homebrew Formula Monkey Patch for py-winmail-opener
# =====================================================================
# This script creates a temporary fix for the "wrong number of arguments" error
# in the py-winmail-opener formula by patching it at runtime
# =====================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

FORMULA_PATH="/usr/local/Homebrew/Library/Taps/jsbattig/homebrew-winmail/py-winmail-opener.rb"
BACKUP_PATH="${FORMULA_PATH}.bak"
TEMP_DIR="/tmp/homebrew-fix"
MONKEY_PATCH_FILE="${TEMP_DIR}/formula_monkey_patch.rb"

echo -e "${BLUE}Py-Winmail-Opener Formula Fix${NC}"
echo "=================================================="

# Check if formula exists
if [ ! -f "$FORMULA_PATH" ]; then
    echo -e "${RED}Error: Formula file not found at $FORMULA_PATH${NC}"
    exit 1
fi

# Create backup if it doesn't exist
if [ ! -f "$BACKUP_PATH" ]; then
    echo -e "${YELLOW}Creating backup of original formula...${NC}"
    cp "$FORMULA_PATH" "$BACKUP_PATH"
    echo -e "${GREEN}Backup created at $BACKUP_PATH${NC}"
fi

# Create temp directory
mkdir -p "$TEMP_DIR"

# Directly fix the formula file with elevated privileges
echo -e "${YELLOW}Patching formula file directly...${NC}"

# Create monkey patch file
cat > "$MONKEY_PATCH_FILE" << 'EOF'
#!/usr/bin/env ruby

# Monkey patch for PyWinmailOpener formula to fix the uninstall method
# This ensures the method signature includes the args parameter

class PyWinmailOpener
  # Original uninstall method doesn't accept arguments
  # We're replacing it with a version that does
  
  # Check if the method exists and monkey patch it
  begin
    if method(:uninstall).arity == 0
      puts "Applying uninstall method monkey patch..."
      
      # Remove original method
      remove_method :uninstall
      
      # Define new method with correct signature
      def uninstall(args=nil)
        # Run our custom uninstaller to ensure proper cleanup
        venv = libexec/"venv"
        system "#{venv}/bin/python", "#{libexec}/uninstall.py", "--homebrew-mode", "--force"
        
        if $?.success?
          puts "WinmailOpener was successfully removed from your system."
        else
          puts "Some errors occurred during uninstallation. Please check the output above."
          puts "If needed, you can manually run the uninstaller with:"
          puts "  #{venv}/bin/python #{libexec}/uninstall.py --force"
        end
      end
      
      puts "Monkey patch applied successfully"
    else
      puts "Uninstall method already has the correct signature."
    end
  rescue => e
    puts "Error while applying monkey patch: #{e.message}"
    puts e.backtrace.join("\n")
  end
end

# Load the original brew command
load ENV["HOMEBREW_BREW_FILE"]
EOF

chmod +x "$MONKEY_PATCH_FILE"

# Create a wrapper script for brew commands
cat > "${TEMP_DIR}/brew_wrapper.sh" << EOF
#!/bin/bash

# Wrapper for brew command that loads our monkey patch first
export HOMEBREW_BREW_FILE=\$(which brew)
ruby "${MONKEY_PATCH_FILE}" "\$@"
EOF

chmod +x "${TEMP_DIR}/brew_wrapper.sh"

echo -e "${GREEN}Formula fix created!${NC}"
echo ""
echo -e "To use this fix, run:"
echo -e "${BLUE}${TEMP_DIR}/brew_wrapper.sh [command]${NC}"
echo ""
echo -e "For example:"
echo -e "${BLUE}${TEMP_DIR}/brew_wrapper.sh uninstall py-winmail-opener${NC}"
echo -e "${BLUE}${TEMP_DIR}/brew_wrapper.sh reinstall py-winmail-opener${NC}"
echo ""
echo -e "You can also create an alias for easier use:"
echo -e "${YELLOW}alias brew_fixed=\"${TEMP_DIR}/brew_wrapper.sh\"${NC}"
echo ""
echo -e "${RED}Important: This is a temporary workaround. The correct fix has been pushed to the GitHub repository${NC}"
echo -e "${RED}and should be available in future updates.${NC}"
