# Automated Tests for py-winmail-opener

This directory contains automated tests for the py-winmail-opener utility. The tests verify the functionality of extracting content from winmail.dat files.

## Test Structure

- `test_winmail_opener.py`: Main test file containing test cases
- `tnef_generator.py`: Utility to programmatically generate winmail.dat files for testing
- `fixtures/`: Contains expected HTML output files for comparison
- `resources/`: Contains resources for creating test files

## Prerequisites

Before running the tests, you need to install the required dependencies:

```bash
pip install beautifulsoup4
brew install mpack  # On macOS, required for generating winmail.dat files
```

## Running the Tests

To run all tests:

```bash
cd /path/to/py-winmail-opener
python -m unittest discover -s test
```

To run a specific test:

```bash
python -m unittest test.test_winmail_opener.WinmailOpenerTests.test_body_only_extraction
```

## Test Cases

1. **Body-only Extraction**: Tests extraction of a winmail.dat file with just a body and no metadata or attachments.
2. **Metadata Extraction**: Tests extraction of a winmail.dat file with body and rich metadata.
3. **Attachments Extraction**: Tests extraction of a winmail.dat file with body, metadata, and attachments.
4. **Command-line Interface**: Tests the command-line interface of the utility.

## Adding New Tests

To add a new test case:

1. Add a new test method to the `WinmailOpenerTests` class in `test_winmail_opener.py`
2. If needed, add a new method to `TNEFGenerator` to create a specific type of winmail.dat file
3. Create expected HTML output in the `fixtures/` directory

## Note About Sample Files

The sample files in the `resources/` directory are placeholders. In a real implementation, you should replace them with actual binary files:

- Replace `sample_image.txt` with a real JPG image
- Replace `sample_document.txt` with a real PDF document

After replacing these files, update the file extensions in:
- `tnef_generator.py`
- `test_winmail_opener.py`
- `fixtures/expected_with_attachments.html`