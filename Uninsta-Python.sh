#Uninstalls Python 2.7x versions from macOS
sudo rm -rf /Library/Frameworks/Python.framework/Versions/2.7
sudo rm -f /usr/local/bin/python2.7
sudo rm -f /usr/local/bin/pip2.7
sudo rm -rf /Library/Python/2.7
sudo find /usr/local -name '*python*2.7*' -exec rm -rf {} \;
sudo rm -f /Library/LaunchDaemons/org.python.Python.plist
