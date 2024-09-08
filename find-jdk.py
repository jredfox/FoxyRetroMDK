############################################################################################################
### @purpose to find JDK-<target> and if no target is found it tries to get JDK 6 - 8 with 8 being prefered
### @author jredfox
### Feel Free to copy, modify, distribute and publically display this script
#############################################################################################################

import os
import sys
import glob
import subprocess
import re

jdk_ver = None
jdk_targ = None
jdk_8 = None
jdk_7 = None
jdk_6 = None
exe = ""
plat = sys.platform.lower()
isMac = plat == 'darwin'
isLinux = os.name != 'darwin' and os.name != 'nt'

def chk_jdk(jdk_path):
    global jdk_ver
    global jdk_targ
    global jdk_8
    global jdk_7
    global jdk_6

    # Search JDK if it's the proper version
    java_path = os.path.join(jdk_path, 'java' + exe)
    if os.path.isfile(java_path) and os.path.isfile(os.path.join(jdk_path, "javac" + exe)):
        try:
            # Run 'java -version' command to check the version
            version_output = subprocess.check_output([java_path, '-version'], stderr=subprocess.STDOUT)
            line = version_output.decode('utf-8').splitlines()[0]  # Get the first line of the output
            version_info = re.search(r'"(.*?)(?<!\\)"', line).group(1)
            
            # Check if the version is 1.8 (Java 8)
            if version_info.startswith(jdk_ver):
                jdk_targ = jdk_path
                print(jdk_targ)
                exit(0)
            elif jdk_8 is None and version_info.startswith('1.8.'):
                jdk_8 = jdk_path
            elif jdk_7 is None and version_info.startswith('1.7.'):
                jdk_7 = jdk_path
            elif jdk_6 is None and version_info.startswith('1.6.'):
                jdk_6 = jdk_path

        except Exception:
            return

def find_jdk():
    # Add directories to search
    mac_paths = [
        '/Library/Java/JavaVirtualMachines/*/Contents/Home/bin',
        '/System/Library/Java/JavaVirtualMachines/*/Contents/Home/bin',
        '/Applications/Java/JavaVirtualMachines/*/Contents/Home/bin',
        '/usr/local/java/*/Contents/Home/bin'
        '/opt/java/*/Contents/Home/bin'
    ]

    if isMac:
        for path in mac_paths:
            for jdk_path in glob.glob(path):
                if os.path.isdir(jdk_path):
                    chk_jdk(jdk_path)

    #Check JDKs from the PATH first before resorting to mac madness
    path_dirs = os.getenv('PATH', '').split(os.pathsep)
    for directory in path_dirs:
        chk_jdk(directory)

    if isMac:
        chk_jdk("/Library/PreferencePanes/JavaControlPanel.prefPane/Contents/Home/bin")
        chk_jdk("/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin")

    #Start Linux checks
    linux_paths = [
        #Standard Installations
        '/usr/lib/jvm/*/bin', #Most Common installations and seems to be the new standard
        '/usr/lib*/jvm/*/bin', #lib64 and lib32 etc may also exist
        '/usr/java/*/bin', #Some oracle Installations
        '/etc/alternatives/*/bin', #RPM redhat linux
        '/usr/java/*/bin', #RPM redhat linux
        #Check opt Installations by user or some programs
        '/opt/jre*/*/bin',
        '/opt/jdk*/*/bin',
        '/opt/java*/*/bin',
        '/opt/jvm*/*/bin',
        #Non Standard Installations
        '/usr/lib/java/*/bin',
        '/usr/lib/jdk*/*/bin',
        '/usr/lib/jre*/*/bin',
        '/usr/lib/jvm*/*/bin',
        '/usr/local/java/*/bin'
    ]

    if isLinux:
        for path in linux_paths:
            for jdk_path in glob.glob(path):
                if os.path.isdir(jdk_path):
                    chk_jdk(jdk_path)
#                    print("checked:" + jdk_path)

    #If the methods cannot find the target get JDK-8 or earlier
    if jdk_8:
        print(jdk_8)
        exit(0)
    elif jdk_7:
        print(jdk_7)
        exit(0)
    elif jdk_6:
        print(jdk_6)
        exit(0)

if __name__ == "__main__":
    #Parse Arguments
    if len(sys.argv) == 2 and sys.argv[1]:
        jdk_ver = sys.argv[1]
    else:
        jdk_ver = "1.8."

    if os.name == 'nt':
        exe = ".exe"

    find_jdk()
    sys.exit(0)
