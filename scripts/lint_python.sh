#!/bin/bash
# lint_python.sh - Run Python linters and syntax checkers

set -e  # Exit on error

echo "Running Python linters and syntax checkers..."

# Check Python files
PYTHON_FILES=$(find . -name "*.py" -not -path "*/\.*" -not -path "*/venv/*")

# Check if SSL is available in Python
if ! python3 -c "import ssl" &> /dev/null; then
    echo "Warning: SSL module is not available in Python. This may prevent installing linting tools."
    echo "Running basic syntax check only..."
    
    # Run basic syntax check
    for file in $PYTHON_FILES; do
        echo "Checking syntax in $file..."
        if ! python3 -m py_compile "$file"; then
            echo "Syntax error in $file"
            exit 1
        fi
    done
    
    echo "Basic syntax check passed. For more thorough linting, install Python with SSL support."
    exit 0
fi

# Initialize error flag
ERRORS=0

# Run flake8
echo "Running flake8..."
if command -v flake8 &> /dev/null; then
    flake8 $PYTHON_FILES || ERRORS=$((ERRORS+1))
else
    echo "flake8 not found. Install with: pip install flake8"
    echo "Skipping flake8 checks."
fi

# Run pylint
echo "Running pylint..."
if command -v pylint &> /dev/null; then
    pylint --disable=all --enable=syntax-error,undefined-variable,unused-import,unused-variable $PYTHON_FILES || ERRORS=$((ERRORS+1))
else
    echo "pylint not found. Install with: pip install pylint"
    echo "Skipping pylint checks."
fi

# Run black
echo "Running black..."
if command -v black &> /dev/null; then
    black --check $PYTHON_FILES || ERRORS=$((ERRORS+1))
else
    echo "black not found. Install with: pip install black"
    echo "Skipping black checks."
fi

# Run isort
echo "Running isort..."
if command -v isort &> /dev/null; then
    isort --check $PYTHON_FILES || ERRORS=$((ERRORS+1))
else
    echo "isort not found. Install with: pip install isort"
    echo "Skipping isort checks."
fi

# Run mypy
echo "Running mypy..."
if command -v mypy &> /dev/null; then
    mypy --ignore-missing-imports $PYTHON_FILES || ERRORS=$((ERRORS+1))
else
    echo "mypy not found. Install with: pip install mypy"
    echo "Skipping mypy checks."
fi

# Report results
if [ $ERRORS -gt 0 ]; then
    echo "Linting found $ERRORS issues."
    exit 1
fi

echo "All Python checks passed!"