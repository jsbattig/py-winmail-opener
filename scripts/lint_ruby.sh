#!/bin/bash
# lint_ruby.sh - Run Ruby linters and syntax checkers

set -e  # Exit on error

echo "Running Ruby linters and syntax checkers..."

# Check if Ruby is installed
if ! command -v ruby &> /dev/null; then
    echo "Warning: Ruby is not installed. Ruby linting will be skipped."
    echo "To install Ruby:"
    echo "  - On macOS: brew install ruby"
    echo "  - On Linux: Use your package manager (apt, yum, etc.)"
    exit 0
fi

# Find Ruby files
RUBY_FILES=$(find . -name "*.rb" -not -path "*/\.*")

if [ -z "$RUBY_FILES" ]; then
    echo "No Ruby files found."
    exit 0
fi

# Initialize error flag
ERRORS=0

# Check if RuboCop is installed
if ! command -v rubocop &> /dev/null; then
    echo "Warning: RuboCop is not installed. Install with: gem install rubocop"
    echo "Performing basic Ruby syntax check instead..."
    
    # Perform basic syntax check
    for file in $RUBY_FILES; do
        echo "Checking syntax in $file..."
        ruby -c "$file" || ERRORS=$((ERRORS+1))
    done
else
    # Run RuboCop
    echo "Running RuboCop..."
    rubocop $RUBY_FILES || ERRORS=$((ERRORS+1))
fi

# Check if Homebrew is installed (for brew audit)
if command -v brew &> /dev/null; then
    echo "Running brew audit..."
    if [ -f "homebrew/py-winmail-opener.rb" ]; then
        # Use the formula name instead of path
        brew audit --strict py-winmail-opener || ERRORS=$((ERRORS+1))
    else
        echo "Homebrew formula not found at homebrew/py-winmail-opener.rb"
    fi
else
    echo "Homebrew not installed. Skipping brew audit."
fi

# Report results
if [ $ERRORS -gt 0 ]; then
    echo "Ruby linting found $ERRORS issues."
    exit 1
else
    echo "All Ruby checks passed!"
    exit 0
fi