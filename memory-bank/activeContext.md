# Active Context

## Current Focus

We are currently working on ensuring the application correctly handles all email content types and runs properly in different execution environments:

1. HTML content, RTF content, and plain text content support
2. Sandboxed environment handling for file associations

## Recent Changes

### Sandboxed Environment Fix (May 7, 2025)

Added support for detecting and handling sandboxed execution environments when the application is launched via file association (double-click) rather than from the command line:

- Modified `winmail_opener.py` to detect when it's running in a sandboxed environment (working directory is root)
- Implemented a fallback to use a temporary directory for attachments when in sandboxed mode
- Maintained backward compatibility with command-line execution
- Updated version to 1.0.12

This enhancement ensures:
- Files with attachments work properly when opened via file association
- Permission errors are avoided in sandboxed environments
- The application handles the different security contexts of various launch methods

### HTML Content Support (May 7, 2025)

Added support for displaying HTML content from winmail.dat files. Previously, the application only checked for RTF and plain text content, but some winmail.dat files only contain HTML content in the `htmlbody` attribute.

Changes included:
- Modified `winmail_opener.py` to prioritize HTML content over RTF and plain text
- Added a new `sanitize_html_content()` function to properly extract and clean HTML content
- Maintained backward compatibility with existing RTF and plain text handling

This enhancement ensures:
- Email content is properly displayed regardless of format (HTML, RTF, or plain text)
- Rich formatting in HTML emails is preserved
- The application handles a wider range of winmail.dat files

## Next Steps

1. Add more thorough testing with various winmail.dat file formats
2. Consider improving RTF-to-HTML conversion for better fidelity
3. Add support for file attachments with international characters
4. Update documentation to reflect the new content handling capabilities

## Active Decisions and Considerations

- Maintaining code structure that prioritizes different content types in descending order: HTML → RTF → plain text
- Preserving style information from the original HTML when possible
- Ensuring sanitization of HTML content for security
- Keeping the interface clean and consistent across different content types
- Handling different execution contexts (command line vs. file association)
- Maintaining compatibility with macOS security models and sandboxing

## Important Patterns and Preferences

1. Content type prioritization:
   - HTML content (if available)
   - RTF content (if available and no HTML)
   - Plain text (if no HTML or RTF is available)

2. File processing workflow:
   - Parse the TNEF file
   - Extract metadata
   - Extract and display the appropriate body content
   - Extract and provide links to attachments

3. Environment detection:
   - Check working directory to detect sandboxed execution
   - Use appropriate output directories based on execution context
   - Adapt permissions requirements to the context

## Learnings and Project Insights

1. TNEF files can contain content in multiple formats simultaneously or in only one format
2. The HTML content in TNEF files is often structured as complete HTML documents with metadata and styling information
3. Different email clients may generate winmail.dat files with different content formats
4. macOS security model applies different restrictions to applications depending on how they're launched
5. When an application is launched via file association, it runs with more restricted permissions than from the command line
