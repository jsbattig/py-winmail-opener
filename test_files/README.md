# Test Files

This directory contains test files for the winmail.dat opener application.

## Current Test Files

- `dummy.dat`: A simple text file that's used for basic testing of file association and path handling. This is not an actual TNEF-encoded file and will produce an expected "Wrong TNEF signature" error when processed.

## Testing with Real Winmail.dat Files

For proper testing of attachment extraction, you'll need a real winmail.dat file from an email. These files have specific binary structures that can't be easily created manually.

### How to Get Real Test Files:

1. Check your email for messages with winmail.dat attachments (common from Microsoft Outlook users)
2. Ask colleagues using Outlook to send you test emails with attachments
3. Search online for sample winmail.dat files used for testing

When you have a real winmail.dat file, you can:

1. Place it in this directory for testing
2. Run the application against it to verify full extraction capabilities

### Privacy Note:

Real winmail.dat files can contain sensitive information from emails, so:

- Don't commit real winmail.dat files to the repository
- Be cautious with how you share and store test files
- Consider creating test files with non-sensitive content for testing
