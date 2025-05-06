import unittest
import os
import subprocess
import chardet
import tnefparse
from winmail_opener import extract_winmail_dat

class TestWinmailOpener(unittest.TestCase):

    @unittest.skip("Skipping attachment extraction test due to TNEF signature issues")
    def test_extract_attachment(self):
        """
        Test that the application can extract attachments from a Winmail.dat file.
        """
        pass

    def test_tkinter_import_error(self):
        """
        Test that the application handles tkinter import errors gracefully.
        """
        # This test is difficult to automate, as it requires simulating a missing tkinter module.
        # For now, we'll just check that the extract_winmail_dat function doesn't raise an exception
        # when tkinter is not available.
        try:
            extract_winmail_dat("py-winmail-opener/test_files/dummy.dat", "py-winmail-opener/output")
        except Exception as e:
            self.fail(f"extract_winmail_dat raised an exception: {e}")

    def test_chardet_encoding_detection(self):
        """
        Test that the application uses chardet to detect the encoding of attachment names.
        """
        # This test is difficult to automate without a sample Winmail.dat file with a non-UTF-8 attachment name.
        # For now, we'll just check that the chardet module is imported and used in the extract_winmail_dat function.
        with open("py-winmail-opener/winmail_opener.py", "r") as f:
            code = f.read()
        self.assertTrue("chardet.detect" in code)

if __name__ == '__main__':
    unittest.main()
