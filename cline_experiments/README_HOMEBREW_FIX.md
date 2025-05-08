# Homebrew Formula Fix for py-winmail-opener

This document provides solutions for the "wrong number of arguments" error that occurs when trying to install, uninstall, or upgrade py-winmail-opener using Homebrew.

## The Issue

When running Homebrew commands like:

```
brew install jsbattig/winmail/py-winmail-opener
brew uninstall py-winmail-opener
```

You see an error:
```
Error: jsbattig/winmail/py-winmail-opener: wrong number of arguments (given 1, expected 0)
```

This error occurs because of a compatibility issue between the formula's `uninstall` method signature and Homebrew's expectations. The error persists even though the formula file looks correct.

## Solutions

We've created multiple solutions to address this issue, from least to most invasive:

### 1. Complete Cleaner (`complete_cleaner.sh`)

This script completely removes all traces of py-winmail-opener from your system, allowing for a fresh installation:

```bash
./complete_cleaner.sh
```

What it does:
- Untaps the formula repository to release any locks
- Removes Homebrew caches and formula files from Cellar
- Removes application bundles from both /Applications and ~/Applications
- Cleans preference files and saved states
- Removes any symlinks in /usr/local/bin
- Re-taps the repository to get the latest version from GitHub

### 2. Direct Formula Patch (`direct_patch.sh`)

This script directly replaces the formula file with a known-good version:

```bash
./direct_patch.sh
```

What it does:
- Creates a backup of the original formula file
- Replaces the formula with a known-good version that has the correct signature
- Ensures all method signatures are compatible with your version of Homebrew

### 3. Homebrew-Bypass Helper (`direct_homebrew_commands.rb`)

This script performs critical operations (uninstall, reinstall) directly without going through Homebrew:

```bash
ruby direct_homebrew_commands.rb uninstall
ruby direct_homebrew_commands.rb reinstall
```

What it does:
- Finds installed files without using Homebrew
- Removes them directly using Ruby's FileUtils
- Bypasses the problematic Homebrew CLI layer

### 4. Manual Installation (`manual_install.sh`)

This script completely bypasses Homebrew and installs py-winmail-opener directly:

```bash
./manual_install.sh
```

What it does:
- Creates a custom installation in ~/.py-winmail-opener
- Sets up a Python virtual environment with all dependencies
- Creates application bundles and symlinks
- Provides full functionality without using Homebrew

## Recommended Approach

1. Try the `complete_cleaner.sh` first, as it's the least invasive and might solve the issue immediately.
2. If you still encounter issues, try the `direct_patch.sh` to fix the formula file.
3. If formula patching doesn't work, try `manual_install.sh` to bypass Homebrew entirely.

## Technical Details

The core issue is with the `uninstall` method in the formula:

```ruby
def uninstall(args=nil)
  # Method implementation
end
```

Homebrew expects different method signatures in different versions. The fix makes this method compatible with all recent Homebrew versions.

## Long-term Solution

The issue has been reported upstream and will be fixed in future versions of the formula. These scripts provide immediate relief while waiting for the updates to propagate.

If you've successfully installed the formula with any of these methods, you can continue using it normally, and future updates should work without issues.
