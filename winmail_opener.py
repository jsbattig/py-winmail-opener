import argparse  # Used for parsing command-line arguments
import datetime  # Used for formatting dates
import logging  # Used for logging debug information
import os  # Used for file system operations
import re  # Used for RTF conversion
import subprocess  # Used for opening the email body with the default text editor
import sys  # Used for accessing command line arguments

# Version information - keep in sync with setup.py
__version__ = "2.0.21"

# Configure logging first before any imports that might use it
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=os.path.expanduser("~/winmail_opener_debug.log"),
    filemode="a",
)

# Try to import required libraries with improved error messages
try:
    import tnefparse  # Used for parsing Winmail.dat files

    TNEFPARSE_AVAILABLE = True
    logging.debug("Successfully imported tnefparse")
except ImportError:
    TNEFPARSE_AVAILABLE = False
    logging.error("Failed to import tnefparse")
    print(
        """
Error: Required dependency 'tnefparse' is not available.
This usually means the application was not installed correctly.

If you installed via Homebrew:
  brew reinstall py-winmail-opener

For manual installation:
  pip install tnefparse
"""
    )

try:
    import chardet  # Used for detecting character encoding of attachment names

    CHARDET_AVAILABLE = True
    logging.debug("Successfully imported chardet")
except ImportError:
    CHARDET_AVAILABLE = False
    logging.error("Failed to import chardet")
    print(
        """
Warning: Optional dependency 'chardet' is not available.
Character encoding detection will be limited.

If you installed via Homebrew:
  brew reinstall py-winmail-opener

For manual installation:
  pip install chardet
"""
    )


def extract_winmail_dat(winmail_dat_file):
    """
    Extracts attachments and email body from a Winmail.dat file.
    Displays content as HTML with metadata and attachment links.
    """
    logging.debug(f"Starting extraction for file: {winmail_dat_file}")

    try:
        # Validate file
        if not os.path.exists(winmail_dat_file):
            error_msg = f"File does not exist: {winmail_dat_file}"
            logging.error(error_msg)
            print(error_msg)
            return

        # Parse the winmail.dat file
        logging.debug(f"Opening file: {winmail_dat_file}")
        with open(winmail_dat_file, "rb") as tnef_file:
            file_content = tnef_file.read()
            logging.debug(f"Read {len(file_content)} bytes from file")

            # Check if file is empty
            if len(file_content) == 0:
                error_msg = f"Error: The file {winmail_dat_file} is empty"
                logging.error(error_msg)
                print(error_msg)
                return

            try:
                tnef = tnefparse.TNEF(file_content)
            except Exception as e:
                error_msg = (
                    f"Error: {winmail_dat_file} is not a valid TNEF (Winmail.dat) file"
                )
                logging.error(f"{error_msg}: {str(e)}")
                print(f"{error_msg}: {str(e)}")
                return

        # Determine the output directory
        # When launched via file association, the working directory is often / (root)
        # In this case, we need to use a more accessible directory due to sandboxing
        working_dir = os.getcwd()
        is_sandboxed = working_dir == "/"
        logging.debug(f"Is running in sandboxed environment: {is_sandboxed}")

        if is_sandboxed:
            # When sandboxed, use a temporary directory which is usually accessible
            import tempfile

            output_dir = os.path.join(tempfile.gettempdir(), "winmail_attachments")
            logging.debug(f"Using sandboxed-safe output directory: {output_dir}")
        else:
            # Standard case - use Downloads folder
            output_dir = os.path.expanduser("~/Downloads")
            logging.debug(f"Using standard output directory: {output_dir}")

        os.makedirs(output_dir, exist_ok=True)

        # Track extracted attachments for link generation
        extracted_attachments = []
        logging.debug(f"Found {len(tnef.attachments)} attachments")

        for attachment in tnef.attachments:
            attachment_name = ""
            if isinstance(attachment.name, bytes):
                # Detect encoding and decode attachment name
                encoding = chardet.detect(attachment.name)["encoding"] or "utf-8"
                try:
                    attachment_name = attachment.name.decode(encoding)
                except:
                    attachment_name = attachment.name.decode("utf-8", "ignore")
            else:
                attachment_name = attachment.name

            attachment_path = os.path.join(output_dir, attachment_name)
            extracted_attachments.append(
                {
                    "name": attachment_name,
                    "path": attachment_path,
                    "size": len(attachment.data),
                    "url": f"file://{attachment_path}",
                }
            )

            print(f"Extracted attachment: {attachment_name} to {output_dir}")
            with open(attachment_path, "wb") as f:
                f.write(attachment.data)

        # Create HTML content
        html_content = create_html_view(tnef, extracted_attachments)

        # Save HTML to temporary file
        temp_html_file = "/tmp/winmail_view.html"
        with open(temp_html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Open with default browser
        subprocess.call(["open", temp_html_file])
        print(f"Opened winmail.dat content in browser")

    except ValueError as e:
        # Handle ValueError which is what tnefparse raises for invalid TNEF files
        print(f"TNEF parsing error: {e}")
    except FileNotFoundError:
        print("Error: Winmail.dat file not found.")
    except OSError as e:
        print(f"OS error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.exception("Error in extract_winmail_dat")


def create_html_view(tnef, attachments):
    """
    Creates an HTML representation of winmail.dat content including:
    - Metadata (From, To, Subject, Date, etc.)
    - Email body (converted from RTF if available)
    - Attachment links
    """
    # CSS styling for a clean, modern look
    css = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .metadata-item {
            margin-bottom: 8px;
        }
        .metadata-label {
            font-weight: bold;
            color: #555;
            width: 100px;
            display: inline-block;
        }
        .body-container {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e1e4e8;
        }
        .attachments {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .attachment-list {
            list-style-type: none;
            padding-left: 0;
        }
        .attachment-item {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .attachment-item:last-child {
            border-bottom: none;
        }
        .attachment-link {
            text-decoration: none;
            color: #0366d6;
        }
        .attachment-link:hover {
            text-decoration: underline;
        }
        .attachment-size {
            color: #666;
            font-size: 0.9em;
        }
        h1 {
            color: #24292e;
            font-size: 24px;
            font-weight: 600;
            margin-top: 0;
        }
        h2 {
            color: #24292e;
            font-size: 20px;
            font-weight: 600;
            margin-top: 0;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 8px;
        }
    </style>
    """

    # Start building HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Winmail.dat Content</title>
    {css}
</head>
<body>
    <div class="header">
        <h1>Email Content</h1>
    """

    # Extract and display metadata
    metadata = extract_metadata(tnef)
    for key, value in metadata.items():
        if value:  # Only display non-empty metadata
            html += f'<div class="metadata-item"><span class="metadata-label">{key}:</span> {value}</div>\n'

    html += "</div>"  # Close header

    # Email body content
    html += '<div class="body-container">'

    # Try to get HTML body first, then RTF, then plain text
    if hasattr(tnef, "htmlbody") and tnef.htmlbody:
        # Use the HTML body content
        html_content = sanitize_html_content(tnef.htmlbody)
        html += f"<div>{html_content}</div>"
    elif hasattr(tnef, "rtfbody") and tnef.rtfbody:
        # Convert RTF to HTML
        body_html = convert_rtf_to_html(tnef.rtfbody)
        html += f"<div>{body_html}</div>"
    elif hasattr(tnef, "body") and tnef.body:
        # If no RTF, use plain text with simple formatting
        if isinstance(tnef.body, bytes):
            body_text = tnef.body.decode("utf-8", "ignore")
        else:
            body_text = tnef.body

        # Format plain text for HTML display (preserve line breaks)
        body_html = (
            body_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        body_html = body_html.replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;")
        html += f"<div>{body_html}</div>"
    else:
        html += "<div><em>No email body content found</em></div>"

    html += "</div>"  # Close body container

    # Attachments section
    html += """
    <div class="attachments">
        <h2>Attachments</h2>
    """

    if attachments:
        html += '<ul class="attachment-list">'
        for attachment in attachments:
            size_str = format_file_size(attachment["size"])
            html += f"""
            <li class="attachment-item">
                <a href="{attachment['url']}" class="attachment-link">{attachment['name']}</a>
                <span class="attachment-size"> ({size_str})</span>
            </li>
            """
        html += "</ul>"
    else:
        html += "<p>No attachments found</p>"

    html += "</div>"  # Close attachments

    # Close HTML document
    html += """
</body>
</html>
    """

    return html


def extract_metadata(tnef):
    """Extract all available metadata from TNEF object"""
    metadata = {}

    # Map TNEF attributes to human-readable labels
    attribute_map = {
        "subject": "Subject",
        "from": "From",
        "sender_name": "Sender",
        "message_id": "Message ID",
        "date_sent": "Date Sent",
        "date_received": "Date Received",
        "message_class": "Message Class",
        "priority": "Priority",
        "conversation_id": "Conversation",
    }

    # Try to extract common metadata values
    if hasattr(tnef, "subject"):
        metadata["Subject"] = get_tnef_value(tnef.subject)

    # 'from' is a Python reserved keyword, need to use getattr
    if hasattr(tnef, "from"):
        metadata["From"] = get_tnef_value(getattr(tnef, "from"))

    if hasattr(tnef, "date_sent"):
        sent_date = get_tnef_value(tnef.date_sent)
        if sent_date:
            # Format date if it's a datetime object
            if isinstance(sent_date, (datetime.datetime, datetime.date)):
                sent_date = sent_date.strftime("%Y-%m-%d %H:%M:%S")
            metadata["Date Sent"] = sent_date

    if hasattr(tnef, "date_received"):
        recv_date = get_tnef_value(tnef.date_received)
        if recv_date and isinstance(recv_date, (datetime.datetime, datetime.date)):
            metadata["Date Received"] = recv_date.strftime("%Y-%m-%d %H:%M:%S")

    # Add any other available metadata from TNEF attributes
    for attr in dir(tnef):
        if attr.startswith("__") or attr in (
            "attachments",
            "body",
            "rtfbody",
            "has_body",
        ):
            continue

        if attr in attribute_map and not attribute_map[attr] in metadata:
            value = get_tnef_value(getattr(tnef, attr))
            if value:
                metadata[attribute_map[attr]] = value

    return metadata


def get_tnef_value(value):
    """Safely extract and decode TNEF attribute values"""
    if value is None:
        return None

    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", "ignore")
        except:
            return str(value)

    return str(value)


def sanitize_html_content(html_content):
    """
    Clean up and sanitize HTML content from winmail.dat files
    to make it safe for display and properly formatted.
    """
    if isinstance(html_content, bytes):
        html_content = html_content.decode("utf-8", "ignore")

    # Extract just the body content if possible
    body_start = html_content.find("<body")
    if body_start >= 0:
        body_end = html_content.find("</body>", body_start)
        if body_end >= 0:
            # Include the body tag itself
            body_content = html_content[body_start : body_end + 7]

            # Attempt to preserve styles
            head_start = html_content.find("<head")
            head_end = html_content.find("</head>")
            if head_start >= 0 and head_end >= 0:
                style_start = html_content.find("<style", head_start)
                style_end = html_content.find("</style>", style_start)
                if style_start >= 0 and style_end >= 0:
                    style_content = html_content[style_start : style_end + 8]
                    return f"{style_content}{body_content}"

            return body_content

    # If we couldn't extract the body, return the full content
    return html_content


def convert_rtf_to_html(rtf_data):
    """Convert RTF content to HTML"""
    # For initial implementation, we'll use a simple approach
    # In a future version, we could integrate a more robust RTF-to-HTML converter
    if isinstance(rtf_data, bytes):
        try:
            rtf_text = rtf_data.decode("utf-8", "ignore")
        except:
            return "<pre>RTF content available but could not be converted</pre>"
    else:
        rtf_text = str(rtf_data)

    # Very basic RTF cleanup - remove RTF control sequences
    # This is a minimal implementation - a more robust parser would be better
    try:
        # Strip RTF control sequences
        cleaned_text = re.sub(r"\\[a-z]+[-]?[0-9]*", " ", rtf_text)
        cleaned_text = re.sub(r"[{}]", "", cleaned_text)
        cleaned_text = re.sub(r"\\\'[0-9a-f]{2}", "", cleaned_text)

        # Replace line breaks
        cleaned_text = cleaned_text.replace("\\par", "<br>")

        # Handle HTML entities
        cleaned_text = (
            cleaned_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

        return cleaned_text
    except:
        # If conversion fails, return the raw RTF in a pre tag
        safe_rtf = (
            rtf_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        return f"<pre>{safe_rtf}</pre>"


def format_file_size(size_bytes):
    """Format file size in a human-readable way"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/(1024*1024):.1f} MB"


def main():
    """
    Main function to parse command-line arguments and call the extract_winmail_dat function.
    """
    # Log startup information
    logging.debug("==========================================")
    logging.debug(f"Starting winmail_opener.py")
    logging.debug(f"Working directory: {os.getcwd()}")
    logging.debug(f"Command line args: {sys.argv}")
    logging.debug(f"Python version: {sys.version}")

    parser = argparse.ArgumentParser(
        description="Extract attachments and email body from Winmail.dat files."
    )  # Create an argument parser
    parser.add_argument(
        "winmail_dat_file", nargs="?", help="Path to the Winmail.dat file."
    )  # Add an argument for the Winmail.dat file path
    parser.add_argument(
        "--file",
        help="Alternative way to specify the Winmail.dat file path (for use with Open With)",
    )
    parser.add_argument(
        "--version", action="version", version=f"winmail_opener {__version__}"
    )

    # Try to parse args, but don't exit on error
    try:
        args, unknown = parser.parse_known_args()
        logging.debug(f"Parsed args: {args}")
        if unknown:
            logging.debug(f"Unknown args: {unknown}")
    except Exception as e:
        logging.error(f"Error parsing arguments: {e}")
        args = None

    # Determine which file path to use with extensive logging
    file_path = None

    # Try different ways to get the file path
    if args and args.winmail_dat_file:
        file_path = args.winmail_dat_file
        logging.debug(f"Using file path from positional argument: {file_path}")
    elif args and args.file:
        file_path = args.file
        logging.debug(f"Using file path from --file option: {file_path}")
    elif len(sys.argv) > 1:
        # This is a fallback in case argparse doesn't work
        file_path = sys.argv[1]
        logging.debug(f"Using file path from raw sys.argv[1]: {file_path}")
    else:
        logging.error("No file path specified in arguments")

    # Try to interpret macOS-specific paths if nothing else worked
    if not file_path and len(sys.argv) > 1:
        # macOS might pass file paths with special characters
        try:
            possible_path = sys.argv[1].replace("\\", "")
            if os.path.exists(possible_path):
                file_path = possible_path
                logging.debug(f"Found file after path cleanup: {file_path}")
        except Exception as e:
            logging.error(f"Error processing possible path: {e}")

    # Final validation
    if not file_path:
        error_msg = "Error: No Winmail.dat file specified."
        logging.error(error_msg)
        print(error_msg)
        parser.print_help()
        return

    # Normalize and verify the file path
    try:
        file_path = os.path.abspath(os.path.expanduser(file_path))
        logging.debug(f"Normalized file path: {file_path}")
    except Exception as e:
        logging.error(f"Error normalizing path: {e}")

    # Make sure file exists
    if not os.path.isfile(file_path):
        error_msg = f"Error: File not found: {file_path}"
        logging.error(error_msg)
        print(error_msg)
        return

    # Log file info
    try:
        file_size = os.path.getsize(file_path)
        logging.debug(f"File exists, size: {file_size} bytes")
    except Exception as e:
        logging.error(f"Error getting file info: {e}")

    # Process the file
    try:
        extract_winmail_dat(
            file_path
        )  # Call the extract_winmail_dat function with the file path
    except Exception as e:
        logging.exception(f"Unhandled exception in extract_winmail_dat: {e}")
        print(
            f"An unexpected error occurred. Please check the log at ~/winmail_opener_debug.log"
        )


if __name__ == "__main__":
    main()  # Call the main function if the script is run directly
