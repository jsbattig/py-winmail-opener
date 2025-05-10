import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class TNEFGenerator:
    """Utility class to generate winmail.dat files for testing"""

    def __init__(self, resources_dir):
        """Initialize the generator with path to resource files"""
        self.resources_dir = resources_dir
        # Ensure mpack is available
        try:
            # Just check if mpack exists, don't try to get version
            subprocess.run(
                ["which", "mpack"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError(
                "mpack utility is required. Install with 'brew install mpack' on macOS"
            )

    def create_winmail_dat(
        self,
        output_path,
        body_text,
        subject=None,
        sender=None,
        recipient=None,
        date=None,
        attachments=None,
        html_body=False,
    ):
        """
        Create a winmail.dat file with specified content

        Args:
            output_path: Where to save the winmail.dat file
            body_text: Email body text
            subject: Email subject
            sender: Sender email
            recipient: Recipient email
            date: Email date
            attachments: List of file paths to attach
            html_body: Whether body is HTML

        Returns:
            Path to the generated winmail.dat file
        """
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        try:
            # Create a multipart message
            msg = MIMEMultipart()
            msg["Subject"] = subject or "Test Email"
            msg["From"] = sender or "sender@example.com"
            msg["To"] = recipient or "recipient@example.com"
            msg["Date"] = date or datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

            # Add body text
            if html_body:
                msg.attach(MIMEText(body_text, "html"))
            else:
                msg.attach(MIMEText(body_text))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    with open(os.path.join(self.resources_dir, file_path), "rb") as f:
                        attachment = MIMEApplication(f.read())
                        attachment.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=os.path.basename(file_path),
                        )
                        msg.attach(attachment)

            # Write the email to a file
            eml_path = os.path.join(temp_dir, "test_email.eml")
            with open(eml_path, "w") as f:
                f.write(msg.as_string())

            # Use mpack to convert to winmail.dat
            winmail_path = os.path.join(temp_dir, "winmail.dat")
            print(f"Running mpack command: mpack -o {winmail_path} {eml_path}")

            try:
                # Add a timeout to prevent hanging
                result = subprocess.run(
                    ["mpack", "-o", winmail_path, eml_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    timeout=5,
                )  # 5 second timeout

                print(f"mpack stdout: {result.stdout.decode('utf-8', 'ignore')}")
                print(f"mpack stderr: {result.stderr.decode('utf-8', 'ignore')}")

                # Check if the file was created
                if os.path.exists(winmail_path):
                    print(
                        f"winmail.dat file created: {os.path.getsize(winmail_path)} bytes"
                    )
                else:
                    print(f"Error: winmail.dat file was not created")

            except subprocess.TimeoutExpired:
                print("Error: mpack command timed out after 5 seconds")
                raise RuntimeError("mpack command timed out")
            except Exception as e:
                print(f"Error running mpack: {str(e)}")
                raise

            # Copy to the output location
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy(winmail_path, output_path)

            return output_path

        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)

    def create_body_only_winmail(self, output_path):
        """Create a winmail.dat file with just a body and no metadata"""
        body_text = "This is a simple test email body with no special formatting or attachments."
        return self.create_winmail_dat(
            output_path=output_path,
            body_text=body_text,
            subject=None,
            sender=None,
            recipient=None,
            date=None,
            attachments=None,
        )

    def create_metadata_winmail(self, output_path):
        """Create a winmail.dat file with body and rich metadata"""
        body_text = (
            "This email contains metadata like sender, recipient, subject, and date."
        )
        return self.create_winmail_dat(
            output_path=output_path,
            body_text=body_text,
            subject="Test Email with Metadata",
            sender="test.sender@example.com",
            recipient="test.recipient@example.com",
            date="Mon, 01 Jan 2025 12:00:00 +0000",
            attachments=None,
        )

    def create_attachments_winmail(self, output_path):
        """Create a winmail.dat file with body, metadata, and attachments"""
        body_text = """
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
        """
        return self.create_winmail_dat(
            output_path=output_path,
            body_text=body_text,
            subject="Test Email with Attachments",
            sender="test.sender@example.com",
            recipient="test.recipient@example.com",
            date="Mon, 01 Jan 2025 12:00:00 +0000",
            attachments=["sample_image.txt", "sample_document.txt"],
            html_body=True,
        )
