cask "py-winmail-opener" do
  version "1.1.5"
  sha256 "25660497ce9247b15a1020b29818f9c3e72be99d397b1a39cc4d0cdc4c24f34e"
  
  url "https://github.com/jsbattig/py-winmail-opener/releases/download/v#{version}/WinmailOpener-#{version}.dmg"
  name "WinmailOpener"
  desc "Extract attachments and email body from Winmail.dat files"
  homepage "https://github.com/jsbattig/py-winmail-opener"
  
  app "WinmailOpener-#{version}.app"
  
  # Use explicit path to application directory instead of appdir variable
  binary "/Applications/WinmailOpener-#{version}.app/Contents/MacOS/winmail-opener", target: "winmail-opener"
  
  uninstall delete: "/usr/local/bin/winmail-opener"
  
  zap trash: [
    "~/Library/Logs/WinmailOpener_log.txt",
    "~/Library/Preferences/com.github.jsbattig.winmailopener.plist"
  ]
end
