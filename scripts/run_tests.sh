#!/bin/bash
# run_tests.sh - Run the test suite

set -e  # Exit on error

echo "Running py-winmail-opener test suite..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if mpack is installed
if ! command -v mpack &> /dev/null; then
    echo "Error: mpack is required but not installed."
    echo "Install with: brew install mpack (on macOS)"
    exit 1
fi

# Check if required Python packages are installed
python3 -c "import tnefparse" 2>/dev/null || {
    echo "Error: tnefparse package is not installed."
    echo "Install with: pip install tnefparse"
    exit 1
}

python3 -c "import chardet" 2>/dev/null || {
    echo "Error: chardet package is not installed."
    echo "Install with: pip install chardet"
    exit 1
}

python3 -c "import bs4" 2>/dev/null || {
    echo "Error: beautifulsoup4 package is not installed."
    echo "Install with: pip install beautifulsoup4"
    exit 1
}

# Run the tests
python3 -m unittest discover -s test

echo "All tests passed!"