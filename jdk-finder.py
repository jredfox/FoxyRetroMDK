############################################################################################################
### @purpose to find JDK-<target> and if no target is found it tries to get JDK 6 - 8 with 8 being prefered
### @author jredfox
### Feel Free to copy, modify, distribute and publically display this script
#############################################################################################################

import os
import sys
import glob
import re
import subprocess

jdk_ver = None
jdk_targ = None
jdk_8 = None
jdk_7 = None
jdk_6 = None
pfirst = True
cached_path = None
isWindows = os.name == 'nt'
isMac = sys.platform.lower() == 'darwin'
isLinux = not isMac and not isWindows
exe = '.exe' if isWindows else ''
debug = False

def save(jdk_path, cache):
    if cache and not debug:
        with open(cached_path, "wb") as file:
            file.write(jdk_path)
    print(jdk_path)
    sys.exit(0)

def chk_jdk(jdk_path):
    if jdk_path and jdk_path[1:].startswith(":\\Windows\\") or jdk_path[1:] == ":\\Windows":
        return
    if debug:
        print("checking:" + jdk_path)
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
            version_info = re.search(r'"(.*?)(?<!\\)"', line).group(1) #version_info = line.split()[1]
            
            if version_info.startswith(jdk_ver):
                jdk_targ = jdk_path
                save(jdk_path, True)
            elif jdk_8 is None and version_info.startswith('1.8.'):
                jdk_8 = jdk_path
            elif jdk_7 is None and version_info.startswith('1.7.'):
                jdk_7 = jdk_path
            elif jdk_6 is None and version_info.startswith('1.6.'):
                jdk_6 = jdk_path

        except Exception as e: 
            print(e)
            return

def find_jdk():

    #Check JDKs from the PATH first before resorting to mac & linux madness
    path_dirs = os.getenv('PATH', '').split(os.pathsep)
    jhome = os.getenv('JAVA_HOME')
    if not ( '' in path_dirs ):
        path_dirs.append('')
    if jhome:
        path_dirs.append(os.path.join(jhome + 'bin'))
    
    if pfirst:
        for directory in path_dirs:
            chk_jdk(directory)

    if isMac:
        # Add directories to search
        mac_paths = [
            '/Library/Java/JavaVirtualMachines/*/Contents/Home/bin',
            '/System/Library/Java/JavaVirtualMachines/*/Contents/Home/bin',
            '/Applications/Java/JavaVirtualMachines/*/Contents/Home/bin',
            '/usr/local/java/*/Contents/Home/bin'
            '/opt/java/*/Contents/Home/bin',
            '/Library/PreferencePanes/JavaControlPanel.prefPane/Contents/Home/bin'
            '/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin'
        ]
        for path in mac_paths:
            for jdk_path in glob.glob(path):
                if os.path.isdir(jdk_path):
                    chk_jdk(jdk_path)

    if isLinux:
        linux_paths = [
            #Standard Installations
            '/usr/lib/jvm/*/bin', #Most Common installations and seems to be the new standard
            '/usr/lib*/jvm/*/bin', #lib64 and lib32 etc may also exist
            '/usr/java/*/bin', #Some oracle Installations
            '/etc/alternatives/*/bin', #RPM redhat linux
            '/usr/java/*/bin', #RPM redhat linux
            #Check opt Installations by user or some programs
            '/opt/j*/bin', #Covers /opt/java.*/bin /opt/jre.*/bin /opt/jdk.*/bin /opt/jvm.*/bin
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
        for path in linux_paths:
            for jdk_path in glob.glob(path):
                if os.path.isdir(jdk_path):
                    chk_jdk(jdk_path)
    
    if not pfirst:
        for directory in path_dirs:
            chk_jdk(directory)

    #If Target cannot be found print JDK-8 without saving it to the cache
    if jdk_8:
        save(jdk_8, False)
    elif jdk_7:
        save(jdk_7, False)
    elif jdk_6:
        save(jdk_6, False)

if __name__ == "__main__":
    working_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cache")
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    #Parse Arguments
    if len(sys.argv) >= 2 and sys.argv[1]:
        jdk_ver = sys.argv[1]
        if len(sys.argv) > 2:
            pfirst = sys.argv[2].lower() == 'true'
    else:
        jdk_ver = "1.8."
        jdk_targ_file = os.path.join(working_dir, "jdkfinder-target.cfg")
        if os.path.isfile(jdk_targ_file):
            with open(jdk_targ_file, "r") as file:
                jdk_ver = file.readline()
        with open(jdk_targ_file, "wb") as file: 
            file.write(jdk_ver)
    
    #Parsed Cached JDK
    cached_path = os.path.join(working_dir, "jdkfinder-" + jdk_ver.strip('.') + ".cfg")
    if(os.path.isfile(cached_path)):
        with open(cached_path, "r") as file:
            cached_jkd = file.readline().strip().replace("\r\n", "\n")
        chk_jdk(cached_jkd)

    find_jdk()
    sys.exit(0)
