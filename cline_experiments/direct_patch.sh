#!/bin/bash

# Direct patch script for py-winmail-opener Homebrew formula
# This directly modifies the formula file to ensure it has the correct uninstall method signature

FORMULA_PATH="/usr/local/Homebrew/Library/Taps/jsbattig/homebrew-winmail/py-winmail-opener.rb"
BACKUP_PATH="${FORMULA_PATH}.direct_backup"

echo "Creating backup..."
cp "$FORMULA_PATH" "$BACKUP_PATH"

echo "Directly patching formula..."

# Create a temporary file
TMP_FILE=$(mktemp)

# Create the fixed file - completely replacing it
cat > "$TMP_FILE" << 'EOF'
class PyWinmailOpener < Formula
  desc "Extract attachments and email body from Winmail.dat files"
  homepage "https://github.com/jsbattig/py-winmail-opener"
  url "https://github.com/jsbattig/py-winmail-opener/archive/refs/tags/v2.0.7.tar.gz"
  sha256 "f8ed0daac6da06547babb0c84b999466612260a33868d1ecc3771833d9f71b1a"
  license "MIT"
  revision 2
  
  # Explicitly disable bottle - not a compiled binary
  bottle :unneeded

  # Skip binary validation for all our files
  skip_clean :all

  depends_on "python@3.10"
  depends_on "duti" => :recommended

  def install
    # Create a virtualenv with proper SSL support
    venv = libexec/"venv"
    system Formula["python@3.10"].opt_bin/"python3.10", "-m", "venv", venv

    # Upgrade pip and install dependencies directly
    system "#{venv}/bin/pip", "install", "--upgrade", "pip"
    system "#{venv}/bin/pip", "install", "tnefparse", "chardet"

    # Skip cleanup of script files to avoid permission warnings during upgrade
    inreplace "install.py", "os.chmod(handler_script_path, 0o755)", "os.chmod(handler_script_path, 0o775)"
    
    # Install our files to libexec
    libexec.install Dir["*"]

    # Create bin directory inside libexec
    (libexec/"bin").mkpath

    # Create the wrapper script inside libexec/bin
    (libexec/"bin/winmail-opener").write <<~EOS
      #!/bin/bash
      exec "#{venv}/bin/python" "#{libexec}/winmail_opener.py" "$@"
    EOS

    # Make the wrapper executable
    chmod 0755, libexec/"bin/winmail-opener"
    
    # Create symlinks from the actual bin directory
    bin.install_symlink libexec/"bin/winmail-opener"
  end

  def post_install
    # Try to run the installer automatically with homebrew mode
    venv = libexec/"venv"
    system "#{venv}/bin/python", "#{libexec}/install.py", "--homebrew-mode"

    if $?.success?
      puts "WinmailOpener.app was successfully created and installed!"
      puts "You can now open .dat files with WinmailOpener."
    else
      puts "Automatic app creation failed. This might be due to permission restrictions."
      puts "To create the app manually, run the following command:"
      puts "  #{venv}/bin/python #{libexec}/install.py"
    end
  end
  
  def pre_uninstall
    # Fix permissions on files that might cause apply2files errors during cleanup
    begin
      # Execute permission fix in uninstall.py
      venv = libexec/"venv"
      system "#{venv}/bin/python", "#{libexec}/uninstall.py", "--homebrew-mode", "--force", "--keep-logs", "--keep-venv"
    rescue
      # Don't fail if this doesn't work - the main uninstall will still run
      opoo "Pre-uninstall cleanup encountered errors but will continue with uninstallation"
    end
  end
  
  def uninstall(args=nil)
    # Run our custom uninstaller to ensure proper cleanup
    venv = libexec/"venv"
    system "#{venv}/bin/python", "#{libexec}/uninstall.py", "--homebrew-mode", "--force"
    
    if $?.success?
      puts "WinmailOpener was successfully removed from your system."
    else
      puts "Some errors occurred during uninstallation. Please check the output above."
      puts "If needed, you can manually run the uninstaller with:"
      puts "  #{venv}/bin/python #{libexec}/uninstall.py --force"
    end
  end

  test do
    # Test the version output
    assert_match "winmail_opener 2.0.7", shell_output("#{bin}/winmail-opener --version")
  end
end
EOF

# Use sudo to copy the temporary file to the formula location
sudo cp "$TMP_FILE" "$FORMULA_PATH"
rm "$TMP_FILE"

echo "Formula has been directly patched. Try installing now."
echo "brew install jsbattig/winmail/py-winmail-opener"
