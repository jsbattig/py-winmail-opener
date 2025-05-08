# System Patterns

## Application Architecture

The application follows a simple, modular architecture:

1.  **Input:** The application takes a Winmail.dat file path as input, either from the command line or a GUI.
2.  **Processing:** The `tnefparse` library is used to parse the Winmail.dat file and extract attachments and the email body.
3.  **Output:** Attachments are saved to a specified output directory. The email body is displayed to the user.

## Key Components

*   `winmail_opener.py`: Contains the main application logic, including the `extract_winmail_dat` function and the `main` function.
*   `tnefparse`: A third-party library used to parse Winmail.dat files.
*   `chardet`: Used for character encoding detection.
*   `install.py`: Handles the installation process, including creating the AppleScript application bundle and setting file associations.
*   `uninstall.py`: Handles the uninstallation process, removing file associations and the application bundle.

## Design Patterns

*   **Command-line Interface:** The application provides a command-line interface for users who prefer to use the terminal.
*   **AppleScript Application Bundle:** For GUI integration, an AppleScript application bundle is created to handle file associations and provide a visual interface.
*   **Error Handling:** The application implements error handling to gracefully handle unexpected situations.

## Repository Structure

The repository has a specific structure that must be followed for development:

*   **Main Repository (`py-winmail-opener`)**: Contains the core application code and manages the Homebrew formula as a submodule.
*   **Homebrew Submodule (`homebrew/`)**: A Git submodule that contains the Homebrew formula (`py-winmail-opener.rb`) used for installation through Homebrew.

## Homebrew Integration Workflow

When making changes to the Homebrew formula, follow this specific workflow:

1. **Always make changes to the submodule first**: Edit `py-winmail-opener/homebrew/py-winmail-opener.rb`
2. **Commit changes to the submodule first**:
   ```
   cd py-winmail-opener/homebrew
   git add py-winmail-opener.rb
   git commit -m "Descriptive message about changes"
   git push
   ```
3. **Update the submodule pointer in the main repository**:
   ```
   cd py-winmail-opener
   git add homebrew
   git commit -m "Update homebrew submodule pointer"
   git push
   ```

⚠️ **IMPORTANT**: Never make changes directly to the homebrew-winmail tap repository. Always work through the submodule in the main repository. This ensures proper tracking of changes and maintains the correct relationship between repositories.
