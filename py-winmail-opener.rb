class PyWinmailOpener < Formula
  desc "Extract attachments and email body from Winmail.dat files"
  homepage "https://github.com/jsbattig/py-winmail-opener"
  url "https://github.com/jsbattig/py-winmail-opener/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "1fbd0ef6e6dd9672a7dac2939670c409079ebd4c3c9acfdd5f4ae382fafccabe"
  license "MIT"

  depends_on "python@3.10"
  depends_on "duti" => :recommended

  def install
    # Install Python files to libexec to avoid conflicts
    libexec.install Dir["*"]
    
    # Create bin directory if it doesn't exist
    bin.mkpath
    
    # Create a wrapper script in bin
    (bin/"winmail-opener").write <<~EOS
      #!/bin/bash
      "#{Formula["python@3.10"].opt_bin}/python3" "#{libexec}/winmail_opener.py" "$@"
    EOS
    
    # Make the wrapper executable
    chmod 0755, bin/"winmail-opener"
  end

  def post_install
    # Run the install.py script with the correct paths in homebrew mode
    system Formula["python@3.10"].opt_bin/"python3", "#{libexec}/install.py", "--homebrew-mode"
  end

  test do
    # Test the version output
    assert_match "winmail_opener 1.0.0", shell_output("#{bin}/winmail-opener --version")
  end
end
