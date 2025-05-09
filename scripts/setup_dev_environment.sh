#!/bin/bash
# setup_dev_environment.sh - Install all development dependencies

set -e  # Exit on error

echo "Setting up development environment for py-winmail-opener..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

# Check if Ruby is installed (for Homebrew formula linting)
if ! command -v ruby &> /dev/null; then
    echo "Warning: Ruby is not installed. Homebrew formula linting will not be available."
fi

# Check if Homebrew is installed (for macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        echo "Warning: Homebrew is not installed. Some dependencies may not be installable."
    else
        echo "Installing mpack via Homebrew..."
        brew install mpack
    fi
fi

echo "Installing Python dependencies..."

# Check for SSL support in Python
if ! python3 -c "import ssl" &> /dev/null; then
    echo "Warning: SSL module is not available in Python. This will prevent pip from installing packages."
    echo "This is likely due to Python being compiled without SSL support."
    echo ""
    echo "Possible solutions:"
    echo "1. Reinstall Python with SSL support (recommended)"
    echo "   - On macOS: 'brew install openssl && brew reinstall python'"
    echo "   - On Linux: Install the appropriate SSL development packages and reinstall Python"
    echo ""
    echo "2. Use an alternative Python installation that has SSL support"
    echo ""
    echo "Skipping pip installations. You'll need to manually install the following packages:"
    echo "- tnefparse chardet beautifulsoup4 (runtime dependencies)"
    echo "- flake8 pylint black isort mypy pre-commit (development dependencies)"
    echo ""
    echo "Checking if runtime dependencies are already installed..."
    
    MISSING_DEPS=0
    
    # Check for runtime dependencies
    for pkg in tnefparse chardet bs4; do
        if ! python3 -c "import $pkg" &> /dev/null; then
            echo "- $pkg is missing"
            MISSING_DEPS=1
        else
            echo "- $pkg is installed"
        fi
    done
    
    if [ $MISSING_DEPS -eq 1 ]; then
        echo "Some runtime dependencies are missing. The application may not work correctly."
    else
        echo "All runtime dependencies are installed."
    fi
else
    # SSL is available, proceed with pip installations
    pip3 install --upgrade pip
    pip3 install tnefparse chardet beautifulsoup4  # Runtime dependencies
    pip3 install flake8 pylint black isort mypy pre-commit  # Development dependencies
fi

# Install Ruby dependencies if Ruby is available
if command -v gem &> /dev/null; then
    echo "Installing Ruby dependencies..."
    # Try to install with user flag first to avoid permission issues
    gem install --user-install rubocop || {
        echo "Failed to install with --user-install flag."
        echo "Trying with sudo (may require password)..."
        sudo gem install rubocop || {
            echo "Warning: Failed to install RuboCop."
            echo "You may need to install it manually with one of these commands:"
            echo "  gem install --user-install rubocop"
            echo "  sudo gem install rubocop"
            echo "  brew install rubocop (if using Homebrew)"
        }
    }
fi

# Set up pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "Setting up pre-commit hooks..."
    # Create pre-commit config if it doesn't exist
    if [ ! -f .pre-commit-config.yaml ]; then
        cat > .pre-commit-config.yaml << 'EOF'
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        additional_dependencies: [types-requests]
EOF
    fi
    
    # Install the hooks
    pre-commit install
fi

# Create linter configuration files
echo "Creating linter configuration files..."

# Flake8 config
cat > .flake8 << 'EOF'
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist,*.egg-info
EOF

# Pylint config
cat > .pylintrc << 'EOF'
[MASTER]
disable=C0111,C0103,C0303,W0621,C0330,C0326
ignore=CVS
ignore-patterns=
persistent=yes

[FORMAT]
max-line-length=100
EOF

# Black and isort config
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 100
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 100
EOF

# Mypy config
cat > mypy.ini << 'EOF'
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
disallow_incomplete_defs = False
EOF

# RuboCop config for Ruby
cat > .rubocop.yml << 'EOF'
AllCops:
  TargetRubyVersion: 2.6
  NewCops: enable
  
Metrics/LineLength:
  Max: 100
  
Style/StringLiterals:
  EnforcedStyle: double_quotes
EOF

echo "Development environment setup complete!"
echo "You can now run './scripts/lint_python.sh' to check Python code"
echo "You can now run './scripts/lint_ruby.sh' to check Ruby code"
echo "You can now run './scripts/run_tests.sh' to run the test suite"
echo "Pre-commit hooks are installed and will run automatically on commit"