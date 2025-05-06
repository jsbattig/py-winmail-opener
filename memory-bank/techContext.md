# Tech Context

**Technologies Used:**

*   Python 3.x
*   `extract_msg` library: Used for parsing Winmail.dat files.
*   `tkinter` library: Used for creating the graphical user interface (optional).
*   `argparse` library: Used for parsing command-line arguments.
*   `os` library: Used for interacting with the operating system (e.g., creating directories, joining file paths).
*   `subprocess` library: Used for opening the email body with the default text editor.

**Development Setup:**

*   The application can be run from the command line using the `python winmail_opener.py` command.
*   The `extract_msg` library can be installed using pip: `pip install extract_msg`.
*   The `tkinter` library is included with most Python installations.

**Technical Constraints:**

*   The `extract_msg` library may not support all Winmail.dat file formats.
*   The `tkinter` library is not available on all platforms.
