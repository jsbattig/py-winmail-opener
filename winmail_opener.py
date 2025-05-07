import os  # Used for file system operations
import sys  # Used for accessing command line arguments
import argparse  # Used for parsing command-line arguments
import subprocess  # Used for opening the email body with the default text editor
import logging  # Used for logging debug information

# Version information - keep in sync with setup.py
__version__ = "1.0.4"

# Configure logging first before any imports that might use it
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.expanduser('~/winmail_opener_debug.log'),
    filemode='a'
)

# Try to import required libraries with fallback mechanisms
try:
    import tnefparse  # Used for parsing Winmail.dat files
    TNEFPARSE_AVAILABLE = True
    logging.debug("Successfully imported tnefparse")
except ImportError:
    TNEFPARSE_AVAILABLE = False
    logging.error("Failed to import tnefparse - will try alternative methods")
    print("Error: tnefparse module not found. Trying to install it now...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tnefparse"])
        import tnefparse
        TNEFPARSE_AVAILABLE = True
        logging.debug("Successfully installed and imported tnefparse")
    except Exception as e:
        logging.error(f"Could not auto-install tnefparse: {e}")
        print(f"Could not install tnefparse automatically: {e}")

try:
    import chardet  # Used for detecting character encoding of attachment names
    CHARDET_AVAILABLE = True
    logging.debug("Successfully imported chardet")
except ImportError:
    CHARDET_AVAILABLE = False
    logging.error("Failed to import chardet")
    print("Warning: chardet module not found. Character encoding detection may be limited.")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "chardet"])
        import chardet
        CHARDET_AVAILABLE = True
        logging.debug("Successfully installed and imported chardet")
    except Exception as e:
        logging.error(f"Could not auto-install chardet: {e}")

def extract_winmail_dat(winmail_dat_file):
    """
    Extracts attachments and email body from a Winmail.dat file.
    """
    logging.debug(f"Starting extraction for file: {winmail_dat_file}")
    
    try:
        # Make sure the file exists and is readable
        if not os.path.exists(winmail_dat_file):
            error_msg = f"File does not exist: {winmail_dat_file}"
            logging.error(error_msg)
            print(error_msg)
            return
            
        logging.debug(f"Opening file: {winmail_dat_file}")
        with open(winmail_dat_file, 'rb') as tnef_file:
            file_content = tnef_file.read()
            logging.debug(f"Read {len(file_content)} bytes from file")
            tnef = tnefparse.TNEF(file_content)  # Parse the Winmail.dat file using tnefparse

        # Extract attachments to ~/Downloads
        output_dir = os.path.expanduser("~/Downloads")
        logging.debug(f"Using output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist

        # Log attachment count
        logging.debug(f"Found {len(tnef.attachments)} attachments")
        
        for attachment in tnef.attachments:
            if isinstance(attachment.name, bytes):
                # Detect the character encoding of the attachment name
                encoding = chardet.detect(attachment.name)['encoding']
                try:
                    attachment_path = os.path.join(output_dir, attachment.name.decode(encoding))  # Decode the attachment name using the detected encoding
                    print(f"Extracted attachment: {attachment.name.decode(encoding)} to {output_dir}")
                except:
                    attachment_path = os.path.join(output_dir, attachment.name.decode('utf-8', 'ignore'))  # If decoding fails, use utf-8 with ignore
                    print(f"Extracted attachment: {attachment.name.decode('utf-8', 'ignore')} to {output_dir}")
            else:
                attachment_path = os.path.join(output_dir, attachment.name)  # If the attachment name is not bytes, use it directly
                print(f"Extracted attachment: {attachment.name} to {output_dir}")
            with open(attachment_path, 'wb') as f:
                f.write(attachment.data)  # Write the attachment data to the output file

        # Extract email body and open with TextEdit
        if tnef.body:
            email_body = tnef.body
            temp_file = "/tmp/email_body.txt"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(email_body)
            subprocess.call(["open", "-a", "TextEdit", temp_file])
            print(f"Extracted email body and opened with TextEdit.")
        else:
            print("No email body found.")

    except ValueError as e:
        # Handle ValueError which is what tnefparse raises for invalid TNEF files
        print(f"TNEF parsing error: {e}")
    except FileNotFoundError:
        print("Error: Winmail.dat file not found.")
    except OSError as e:
        print(f"OS error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

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
    
    parser = argparse.ArgumentParser(description="Extract attachments and email body from Winmail.dat files.")  # Create an argument parser
    parser.add_argument("winmail_dat_file", nargs='?', help="Path to the Winmail.dat file.")  # Add an argument for the Winmail.dat file path
    parser.add_argument("--file", help="Alternative way to specify the Winmail.dat file path (for use with Open With)")
    parser.add_argument("--version", action="version", version=f"winmail_opener {__version__}")
    
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
            possible_path = sys.argv[1].replace('\\', '')
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
        extract_winmail_dat(file_path)  # Call the extract_winmail_dat function with the file path
    except Exception as e:
        logging.exception(f"Unhandled exception in extract_winmail_dat: {e}")
        print(f"An unexpected error occurred. Please check the log at ~/winmail_opener_debug.log")

if __name__ == "__main__":
    main()  # Call the main function if the script is run directly
