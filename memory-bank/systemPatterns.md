# System Patterns

**Architecture:**

The application follows a simple, modular architecture:

1.  **Input:** The application takes a Winmail.dat file path as input, either from the command line or a GUI.
2.  **Processing:** The `extract_msg` library is used to parse the Winmail.dat file and extract attachments and the email body.
3.  **Output:** Attachments are saved to a specified output directory. The email body is displayed to the user.

**Key Components:**

*   `winmail_opener.py`: Contains the main application logic, including the `extract_winmail_dat` function and the `main` function.
*   `extract_msg`: A third-party library used to parse Winmail.dat files.
*   `tkinter`: A Python GUI library used to create the user interface (optional).

**Design Patterns:**

*   **Command-line Interface:** The application provides a command-line interface for users who prefer to use the terminal.
*   **Graphical User Interface:** The application provides a graphical user interface for users who prefer a visual interface.
*   **Error Handling:** The application implements error handling to gracefully handle unexpected situations.
