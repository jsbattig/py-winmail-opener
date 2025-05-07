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
    # Install Python files to libexec to avoid conflicts
    libexec.install Dir["*"]

    # Create bin directory
    bin.mkpath

    # Create a wrapper script directly in bin (avoiding libexec/bin)
    (bin/"winmail-opener").write <<~EOS
      #!/bin/bash
      "#{Formula["python@3.10"].opt_bin}/python3.10" "#{libexec}/winmail_opener.py" "$@"
    EOS

    # Make the wrapper executable
    chmod 0755, bin/"winmail-opener"
  end

  def post_install
    # Try to run the installer automatically with homebrew mode
    system "#{Formula["python@3.10"].opt_bin}/python3.10", "#{libexec}/install.py", "--homebrew-mode"

    if $?.success?
      puts "WinmailOpener.app was successfully created and installed!"
      puts "You can now open .dat files with WinmailOpener."
    else
      puts "Automatic app creation failed. This might be due to permission restrictions."
      puts "To create the app manually, run the following command:"
      puts "  #{Formula["python@3.10"].opt_bin}/python3.10 #{libexec}/install.py"
    end
  end

  test do
    # Test the version output
    assert_match "winmail_opener 1.0.9", shell_output("#{bin}/winmail-opener --version")
  end
end
