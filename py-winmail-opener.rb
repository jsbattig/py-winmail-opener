class PyWinmailOpener < Formula
  desc "Extract attachments and email body from Winmail.dat files"
  homepage "https://github.com/jsbattig/py-winmail-opener"
  url "https://github.com/jsbattig/py-winmail-opener/archive/refs/tags/v1.0.9.tar.gz"
  sha256 "d9125ddfdd57897422d70edf42543c7f6bde21c14526b52121f99fc494665aad"
  license "MIT"

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
    
    # Install our files to libexec
    libexec.install Dir["*"]
    
    # Create bin directory
    bin.mkpath
    
    # Create a wrapper script that uses the virtualenv python
    (bin/"winmail-opener").write <<~EOS
      #!/bin/bash
      "#{venv}/bin/python" "#{libexec}/winmail_opener.py" "$@"
    EOS
    
    # Make the wrapper executable
    chmod 0755, bin/"winmail-opener"
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
  
  def uninstall
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
    assert_match "winmail_opener", shell_output("#{bin}/winmail-opener --version")
  end
end
