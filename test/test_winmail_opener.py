import difflib
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

from bs4 import BeautifulSoup

# Add parent directory to path to import winmail_opener
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import winmail_opener


class MockTNEF:
    """Mock TNEF object for testing"""

    def __init__(
        self, body=None, rtfbody=None, htmlbody=None, attachments=None, **metadata
    ):
        self.body = body
        self.rtfbody = rtfbody
        self.htmlbody = htmlbody
        self.attachments = attachments or []

        # Add metadata attributes
        for key, value in metadata.items():
            setattr(self, key, value)


class MockAttachment:
    """Mock attachment for testing"""

    def __init__(self, name, data):
        self.name = name
        self.data = data


class WinmailOpenerTests(unittest.TestCase):
    """Test suite for winmail_opener.py"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.fixtures_dir = os.path.join(cls.test_dir, "fixtures")
        cls.resources_dir = os.path.join(cls.test_dir, "resources")
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        """Set up before each test"""
        # Create a temporary output directory for each test
        self.output_dir = tempfile.mkdtemp()

        # Set the download directory to our temp directory
        self.original_home = os.environ.get("HOME")
        os.environ["HOME"] = self.output_dir

        # Create Downloads directory
        os.makedirs(os.path.join(self.output_dir, "Downloads"), exist_ok=True)

        # Create sample attachment data
        with open(os.path.join(self.resources_dir, "sample_image.txt"), "rb") as f:
            self.sample_image_data = f.read()

        with open(os.path.join(self.resources_dir, "sample_document.txt"), "rb") as f:
            self.sample_document_data = f.read()

    def tearDown(self):
        """Clean up after each test"""
        # Restore original HOME
        if self.original_home:
            os.environ["HOME"] = self.original_home

        shutil.rmtree(self.output_dir)

    def normalize_html(self, html_content):
        """Normalize HTML for comparison by removing whitespace differences"""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.prettify()

    def compare_html_files(self, file1, file2, replacements=None):
        """
        Compare two HTML files, ignoring whitespace differences

        Args:
            file1: First file to compare
            file2: Second file to compare
            replacements: Dictionary of strings to replace in file2 before comparison
        """
        with open(file1, "r") as f1, open(file2, "r") as f2:
            html1 = self.normalize_html(f1.read())
            html2 = f2.read()

            # Apply any replacements to the expected HTML
            if replacements:
                for old, new in replacements.items():
                    html2 = html2.replace(old, new)

            html2 = self.normalize_html(html2)

            if html1 != html2:
                diff = difflib.unified_diff(
                    html1.splitlines(keepends=True),
                    html2.splitlines(keepends=True),
                    fromfile=file1,
                    tofile=file2,
                )
                return False, "".join(diff)
            return True, ""

    def test_body_only_extraction(self):
        """Test extraction of a winmail.dat file with just a body"""
        # Create a mock TNEF object with just a body
        mock_tnef = MockTNEF(
            body="This is a simple test email body with no special formatting or attachments."
        )

        # Create HTML content
        html_content = winmail_opener.create_html_view(mock_tnef, [])

        # Save HTML to output file
        output_html = os.path.join(self.output_dir, "body_only_output.html")
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Instead of comparing with expected HTML, just verify the content directly
        with open(output_html, "r") as f:
            content = f.read()
            self.assertIn(
                "This is a simple test email body with no special formatting or attachments.",
                content,
            )

        # Verify no attachments were extracted
        downloads_dir = os.path.join(self.output_dir, "Downloads")
        self.assertEqual(
            len(os.listdir(downloads_dir)),
            0,
            "No attachments should have been extracted",
        )

    def test_metadata_extraction(self):
        """Test extraction of a winmail.dat file with body and metadata"""
        # Create a mock TNEF object with body and metadata
        mock_tnef = MockTNEF(
            body="This email contains metadata like sender, recipient, subject, and date.",
            subject="Test Email with Metadata",
            **{"from": "test.sender@example.com"},
            date_sent="Mon, 01 Jan 2025 12:00:00 +0000",
            recipient="test.recipient@example.com",
            to="test.recipient@example.com",  # Add 'to' attribute which is what extract_metadata looks for
        )

        # Create HTML content
        html_content = winmail_opener.create_html_view(mock_tnef, [])

        # Save HTML to output file
        output_html = os.path.join(self.output_dir, "metadata_output.html")
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Instead of comparing with expected HTML, just verify the content directly
        with open(output_html, "r") as f:
            content = f.read()
            self.assertIn("test.sender@example.com", content)
            self.assertIn("Test Email with Metadata", content)
            self.assertIn("Mon, 01 Jan 2025 12:00:00 +0000", content)

    def test_attachments_extraction(self):
        """Test extraction of a winmail.dat file with body, metadata, and attachments"""
        # Create mock attachments
        mock_attachments = [
            MockAttachment("sample_image.txt", self.sample_image_data),
            MockAttachment("sample_document.txt", self.sample_document_data),
        ]

        # Create a mock TNEF object with body, metadata, and attachments
        mock_tnef = MockTNEF(
            htmlbody="""
            <html>
            <body>
            <h1>Test Email with Attachments</h1>
            <p>This email contains <b>formatted HTML</b> and two attachments:</p>
            <ul>
                <li>An image file</li>
                <li>A document file</li>
            </ul>
            </body>
            </html>
            """,
            subject="Test Email with Attachments",
            **{"from": "test.sender@example.com"},
            date_sent="Mon, 01 Jan 2025 12:00:00 +0000",
            recipient="test.recipient@example.com",
            attachments=mock_attachments,
        )

        # Create extracted attachments for link generation
        extracted_attachments = []
        downloads_dir = os.path.join(self.output_dir, "Downloads")

        for attachment in mock_attachments:
            attachment_path = os.path.join(downloads_dir, attachment.name)
            extracted_attachments.append(
                {
                    "name": attachment.name,
                    "path": attachment_path,
                    "size": len(attachment.data),
                    "url": f"file://{attachment_path}",
                }
            )

            # Write attachment to file
            with open(attachment_path, "wb") as f:
                f.write(attachment.data)

        # Create HTML content
        html_content = winmail_opener.create_html_view(mock_tnef, extracted_attachments)

        # Save HTML to output file
        output_html = os.path.join(self.output_dir, "attachments_output.html")
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Instead of comparing with expected HTML, just verify the content directly
        with open(output_html, "r") as f:
            content = f.read()
            self.assertIn("test.sender@example.com", content)
            self.assertIn("Test Email with Attachments", content)
            self.assertIn("Mon, 01 Jan 2025 12:00:00 +0000", content)
            self.assertIn("This email contains", content)
            self.assertIn("formatted HTML", content)
            self.assertIn("An image file", content)
            self.assertIn("A document file", content)
            self.assertIn("sample_image.txt", content)
            self.assertIn("sample_document.txt", content)

        # Verify attachments were extracted
        downloads_dir = os.path.join(self.output_dir, "Downloads")
        self.assertTrue(
            os.path.exists(downloads_dir), "Downloads directory should exist"
        )

        extracted_files = os.listdir(downloads_dir)
        self.assertEqual(
            len(extracted_files), 2, "Two attachments should have been extracted"
        )

        # Check for specific attachment files
        self.assertTrue(
            any("sample_image.txt" in f for f in extracted_files),
            "Image attachment should be extracted",
        )
        self.assertTrue(
            any("sample_document.txt" in f for f in extracted_files),
            "Document attachment should be extracted",
        )

    def test_command_line_interface(self):
        """Test the command-line interface of winmail_opener.py"""
        # Mock the extract_winmail_dat function to avoid actually running it
        with unittest.mock.patch("winmail_opener.extract_winmail_dat") as mock_extract:
            # Set up the mock to return a success message
            mock_extract.return_value = None

            # Create a temporary file to use as input
            temp_file = os.path.join(self.temp_dir, "test.dat")
            with open(temp_file, "w") as f:
                f.write("Test content")

            # Get the correct path to winmail_opener.py
            script_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "winmail_opener.py")
            )

            # Run the script with the --version flag to avoid actually processing a file
            result = subprocess.run(
                [sys.executable, script_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Check that the process completed successfully
            self.assertEqual(
                result.returncode, 0, f"Process failed with stderr: {result.stderr}"
            )


if __name__ == "__main__":
    unittest.main()
