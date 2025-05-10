#!/bin/bash
# pre-commit.sh - Run before git commit

set -e  # Exit on error

echo "Running pre-commit checks..."

# Store exit codes
PYTHON_EXIT=0
RUBY_EXIT=0
TESTS_EXIT=0
SKIPPED_CHECKS=0

# Run Python linters
echo "Running Python linters..."
if [ -f "./scripts/lint_python.sh" ]; then
    ./scripts/lint_python.sh || PYTHON_EXIT=$?
    
    # Check if only basic syntax check was performed due to missing tools
    if grep -q "basic syntax check" <(./scripts/lint_python.sh 2>&1); then
        echo "Note: Only basic Python syntax check was performed due to missing linting tools."
        SKIPPED_CHECKS=1
    fi
else
    echo "Python linter script not found."
    PYTHON_EXIT=1
fi

# Run Ruby linters
echo "Running Ruby linters..."
if [ -f "./scripts/lint_ruby.sh" ]; then
    if command -v ruby &> /dev/null; then
        ./scripts/lint_ruby.sh || RUBY_EXIT=$?
    else
        echo "Ruby is not installed. Skipping Ruby linting."
        SKIPPED_CHECKS=1
    fi
else
    echo "Ruby linter script not found."
    RUBY_EXIT=1
fi

# Run tests
echo "Running tests..."
if [ -f "./test/run_tests.sh" ]; then
    ./test/run_tests.sh || TESTS_EXIT=$?
else
    echo "Test script not found."
    TESTS_EXIT=1
fi

# Check if any checks failed
if [ $PYTHON_EXIT -ne 0 ] || [ $RUBY_EXIT -ne 0 ] || [ $TESTS_EXIT -ne 0 ]; then
    echo "Pre-commit checks failed!"
    echo "Python linters: $([ $PYTHON_EXIT -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
    echo "Ruby linters: $([ $RUBY_EXIT -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
    echo "Tests: $([ $TESTS_EXIT -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
    
    # Return non-zero exit code to prevent commit
    exit 1
elif [ $SKIPPED_CHECKS -ne 0 ]; then
    echo "All available checks passed, but some checks were skipped due to missing tools."
    echo "Consider installing the missing tools for more thorough checking."
    exit 0
else
    echo "All pre-commit checks passed!"
    exit 0
fi