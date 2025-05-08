# Progress

## What Works

- Base functionality to extract and display TNEF (Winmail.dat) file contents
- File type association to handle double-clicking Winmail.dat files
- HTML viewer for email content
- Attachment extraction and linking
- Support for all content types (HTML, RTF, plain text)
- Homebrew formula for easy installation
- Auto-update capability via GitHub Actions
- Uninstallation script
- Sandboxed environment handling for file associations

## What's Left

- Improved error handling for corrupted or non-standard TNEF files
- Better handling of international character attachments
- Implementing file drag and drop support
- Adding support for viewing raw MAPI properties for debugging
- Email address parsing and formatting improvements
- Support macOS dark mode in the HTML viewer

## Current Status

### May 7, 2025: Sandboxed Environment Support Added

Implemented support for detecting and handling sandboxed execution environments when the application is launched via file association (double-click). Previously, files containing attachments would fail when opened via double-click due to macOS permission restrictions.

The fix includes:
1. Detection of sandboxed environment (working directory is root)
2. Alternative attachment storage location for sandboxed mode
3. Improved error handling for permission-related issues

This ensures all winmail.dat files open properly regardless of how they're launched and what content they contain.

### May 7, 2025: HTML Content Support Added

Implemented support for displaying HTML content from winmail.dat files. The application now properly prioritizes content in the following order:
1. HTML content (if available)
2. RTF content (if no HTML is available)
3. Plain text (if no HTML or RTF is available)

Testing confirmed the application now correctly renders HTML content that was previously not being displayed. The HTML content is properly sanitized and styled, preserving the original formatting as much as possible.

### May 8, 2025: Repository Reset to Formula-Based Approach

Reset the repository back to the formula-based Homebrew approach by returning to the "last-formula" tag:
1. Reverted the master branch to the v1.1.0 commit
2. Reset the homebrew submodule to its corresponding pre-cask state
3. Removed cask-related files and directories 
4. Ensured proper Homebrew formula installation method

This reset was necessary because the cask-based approach was causing installation issues and didn't work as expected. The formula-based approach provides a simpler, more reliable installation method with standard Homebrew commands.

### April 29, 2025: Fixed Homebrew Formula and Installation

Corrected an issue with the Homebrew formula that was causing installation problems on some systems. Updated the installation documentation to reflect the changes. The app now installs properly via `brew install jsbattig/winmail/py-winmail-opener`.

### April 27, 2025: Integrated File Association Fixes

Implemented multiple approaches to resolve the file association issues on different macOS versions:
- Added LaunchAgent-based solution
- Implemented duti-based fix
- Added AppleScript fallback option
- Created a comprehensive fix script that tries multiple approaches

### April 25, 2025: Added Error Handling and Logging

Improved error handling throughout the application to gracefully handle malformed winmail.dat files and provide more user-friendly error messages. Added comprehensive logging to assist with troubleshooting.

## Known Issues

- Some attachment names with special characters may not display correctly
- Opening multiple files in rapid succession can cause display issues
- RTF to HTML conversion is basic and may not preserve complex formatting
- Some email metadata fields may not be properly extracted from all winmail.dat files

## Decisions

- Decided to use a browser-based HTML viewer rather than a native UI for simplicity and cross-platform compatibility
- Chose to maintain Python 3.6+ compatibility to ensure broad system support
- Prioritized extraction of body content in all available formats to maximize compatibility
- Implemented environment detection to handle different macOS security contexts

## Changes to Initial Plan

- Added Homebrew formula support for easier distribution
- Implemented multiple file association fixes instead of a single approach
- Added HTML content support to handle a wider range of winmail.dat files
- Added sandboxed environment handling for better compatibility with macOS security
