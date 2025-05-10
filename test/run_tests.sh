#!/bin/bash

# Script to run the automated tests for py-winmail-opener

# Check if mpack is installed
if ! command -v mpack &> /dev/null; then
    echo "Error: mpack is not installed. Please install it with 'brew install mpack' on macOS."
    exit 1
fi

# Check if beautifulsoup4 is installed
python -c "import bs4" 2>/dev/null || {
    echo "Error: beautifulsoup4 is not installed. Please install it with 'pip install beautifulsoup4'."
    exit 1
}

# Run all tests
echo "Running all tests..."
python -m unittest discover -s test

# Run specific tests (uncomment to use)
# echo "Running body-only extraction test..."
# python -m unittest test.test_winmail_opener.WinmailOpenerTests.test_body_only_extraction
# 
# echo "Running metadata extraction test..."
# python -m unittest test.test_winmail_opener.WinmailOpenerTests.test_metadata_extraction
# 
# echo "Running attachments extraction test..."
# python -m unittest test.test_winmail_opener.WinmailOpenerTests.test_attachments_extraction
# 
# echo "Running command-line interface test..."
# python -m unittest test.test_winmail_opener.WinmailOpenerTests.test_command_line_interface