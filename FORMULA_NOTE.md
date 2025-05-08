# Homebrew Formula Structure

## Single Source of Truth

As of May 8, 2025, we've established the following structure for managing the Homebrew formula:

1. The **single source of truth** for the formula is located in the `homebrew` submodule, which points to the official tap repository (jsbattig/homebrew-winmail).

2. The file `homebrew-formula-template.rb` serves as a template for formula generation but is not used directly for installations.

3. There is **no duplicate formula** in the root directory. The `py-winmail-opener.rb` file in the root has been removed to avoid duplication and potential inconsistencies.

## Formula Update Process

When a new version is released:

1. The `auto-release.yml` workflow creates a new tag and release on GitHub.
2. This triggers the `update-homebrew.yml` workflow, which updates the formula in the homebrew tap.
3. The workflow now preserves important method signatures, including the `uninstall(args=nil)` method that accepts an optional argument.

## Formula Fix (May 8, 2025)

We fixed an issue with the Homebrew formula where the `uninstall` method was not accepting arguments. The fix:

- Modified the formula to change `def uninstall` to `def uninstall(args=nil)`
- Updated the workflow to ensure this signature is preserved during updates
- Removed the duplicate formula from the root to maintain a single source of truth

This fix ensures that Homebrew commands like `brew upgrade` and `brew uninstall` work correctly with our formula.
