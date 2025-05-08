on open theFiles
	set filePaths to ""
	repeat with aFile in theFiles
		set filePaths to filePaths & quoted form of POSIX path of aFile & " "
	end repeat
	
	set appPath to path to me
	set appContents to appPath & "Contents:"
	set resourcesPath to appContents & "Resources:"
	set pythonPath to resourcesPath & "python:bin:python3"
	set scriptPath to resourcesPath & "winmail_opener.py"
	
	-- Log the event
	set logFile to (path to home folder as text) & "WinmailOpener_log.txt"
	do shell script "echo '========================================' >> " & quoted form of POSIX path of logFile
	do shell script "echo 'WinmailOpener AppleScript handler launched at $(date)' >> " & quoted form of POSIX path of logFile
	do shell script "echo 'Files received: " & filePaths & "' >> " & quoted form of POSIX path of logFile
	
	-- Run the Python script with the files
	do shell script quoted form of POSIX path of pythonPath & " " & quoted form of POSIX path of scriptPath & " " & filePaths & " 2>&1 | tee -a " & quoted form of POSIX path of logFile
	
	-- Notify the user
	display notification "Winmail.dat file processed. See your Downloads folder for extracted attachments." with title "WinmailOpener"
end open

on run
	-- This handles when the application is launched directly without files
	display dialog "Please double-click a winmail.dat file instead of launching this app directly." buttons {"OK"} default button "OK" with title "WinmailOpener"
end run
