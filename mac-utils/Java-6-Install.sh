sdir="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd "$sdir"
osascript JRE-6-Install.applescript

#Uncomment this for non-interactive package installer
#sudo installer -pkg "$HOME/Desktop/Java.pkg" -target /

#Open the PKG Installer
open -W "$HOME/Desktop/Java.pkg"

# Important removal jvm.cfg it will cause libjvm.dylib to not be found. (Minecraft will have Graphical Errors)
sudo rm -f /Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Home/lib/jvm.cfg
