############################################################################################################
### @purpose to find JDK-<target> and if no target is found it tries to get JDK 6 - 8 with 8 being preferred
### @author jredfox
### @notes: not python 3 compatible, doesn't detect JDK 5 or lower or any JRE
### Feel Free to copy, modify, distribute and publically display this script
#############################################################################################################

import os
import sys
import glob
import re
import subprocess

VERSION = '1.0.12'
jdk_ver = None
jdk_8 = None
jdk_7 = None
jdk_6 = None
pfirst = True
cached_path = None
isWindows = os.name == 'nt'
isMac = sys.platform.lower() == 'darwin'
isLinux = not isMac and not isWindows
exe = '.exe' if isWindows else ''
VOLUME_WIN_REGEX = re.compile(
    r'(\\\\|\\)[\?\.]{1,2}\\Volume\{[0-9a-f\-]+\}\\Windows(?:\\|$)',
    re.IGNORECASE
)
checked = [ "" ]
debug = False
#Change this to False if "JDK/bin/javac" is a symlink (non standard openjdk specification)
resolve_javac = True

def save(jdk_path, cache):
    if cache and not debug:
        with open(cached_path, "wb") as file:
            file.write(jdk_path)
    print(jdk_path)
    sys.exit(0)

def chk_jdk(jdk_path):
    #Get the Real Absolute Path of the File / Directory Always
    if( not os.path.isabs(jdk_path) and not (isWindows and (":" in jdk_path or jdk_path.startswith('\\\\') or jdk_path.startswith('\\??'))) ):
        jdk_path = os.path.realpath(os.path.join(os.getcwd(), jdk_path))
    else:
        jdk_path = os.path.realpath(jdk_path)
    #Resolve Symbolic Links from java executable
    if resolve_javac:
        jc = os.path.join(jdk_path, 'javac' + exe)
        if not os.path.isfile(jc):
            return
        jdk_path = os.path.dirname(os.path.realpath(jc))
    #Skip Already checked paths for faster JDK result
    if jdk_path in checked:
        return
    checked.append(jdk_path)
    #Skip "C:\Windows\*" to Prevent False Positive JDK Installations on Windows
    low = jdk_path.lower()
    if isWindows:
        if ":" in low:
            win_str = low.split(":", 1)[1]
            if (win_str.startswith('\\windows\\') or win_str == '\\windows'):
                return
        elif bool(VOLUME_WIN_REGEX.match(low)):
            return
    #Skip "/usr/bin" & "/bin" to to Prevent False Postive JDK Installations on Unix(linux / macOS)
    elif low == '/usr/bin' or low == '/bin':
        return
    #Skip Fake JDK Installations as we need the actual installation folder with the lib dir
    parent = os.path.dirname(jdk_path)
    if not os.path.isdir(os.path.join(parent, 'lib')) and not os.path.isdir(os.path.join(parent, 'libs')):
        return
    if debug:
        print("checking:" + jdk_path)
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
                save(jdk_path, True)
            if jdk_8 is None and version_info.startswith('1.8.'):
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
        path_dirs.append(os.path.join(jhome, 'bin'))
    
    if pfirst:
        for directory in path_dirs:
            chk_jdk(directory)

    if isMac:
        # Add directories to search
        mac_paths = [
            '/Library/Java/JavaVirtualMachines/*/Contents/Home/bin',
            '/System/Library/Java/JavaVirtualMachines/*/Contents/Home/bin',
            '/Applications/Java/JavaVirtualMachines/*/Contents/Home/bin',
            '/Library/PreferencePanes/JavaControlPanel.prefPane/Contents/Home/bin',
            '/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin',
            '/usr/local/java/*/Contents/Home/bin',
            '/opt/java/*/Contents/Home/bin'
        ]
        for path in mac_paths:
            for jdk_path in glob.glob(path):
                if os.path.isdir(jdk_path):
                    chk_jdk(jdk_path)

    if isLinux:
        linux_paths = [
            #Standard Installations
            '/usr/lib/jvm*/*/bin', #Most Common installations and seems to be the new standard
            '/usr/lib*/jvm*/*/bin', #Also Search for lib32 lib64 etc...
            '/usr/java/*/bin', #Some oracle Installations
            '/etc/alternatives/j*/bin', #RPM redhat linux
            '/etc/alternatives/j*/*/bin',
            #Check opt Installations by user or some programs
            '/opt/j*/bin', #Covers odd installations like j8u40/bin, j.8xx/bin, j.r.e-xxx/bin etc... as well as /opt/jvm*/bin
            '/opt/*jvm*/bin',
            '/opt/*jdk*/bin',
            '/opt/*java*/bin',
            '/opt/*jre*/bin',
            '/opt/*jvm*/*/bin',
            '/opt/*jdk*/*/bin',
            '/opt/*java*/*/bin',
            '/opt/*jre*/*/bin',
            #Non Standard Installations
            '/usr/lib*/j*/bin', #Covers odd installations like j8u40/bin, j.8xx/bin, j.d.k-xxx/bin etc...
            '/usr/lib*/*jvm*/bin', #Causes Duplication search since we need to check for graaljvm-8u50/bin
            '/usr/lib*/*jdk*/bin',
            '/usr/lib*/*java*/bin',
            '/usr/lib*/*jre*/bin',
            '/usr/lib*/*jvm*/*/bin',
            '/usr/lib*/*jdk*/*/bin',
            '/usr/lib*/*java*/*/bin',
            '/usr/lib*/*jre*/*/bin',
            '/usr/local/j*/bin', #Covers /usr/local/java.*/bin /usr/local/jre.*/bin /usr/local/jdk.*/bin /usr/local/jvm.*/bin
            '/usr/local/*jvm*/bin',
            '/usr/local/*jdk*/bin',
            '/usr/local/*java*/bin',
            '/usr/local/*jre*/bin',
            '/usr/local/*jvm*/*/bin',
            '/usr/local/*jdk*/*/bin',
            '/usr/local/*java*/*/bin',
            '/usr/local/*jre*/*/bin'
        ]
        lpaths = []
        for path in linux_paths:
            for jdk_path in glob.glob(path):
                if not jdk_path in lpaths:
                    lpaths.append(jdk_path)
        for jdk_path in lpaths:
            if os.path.isdir(jdk_path):
                chk_jdk(jdk_path)
    
    if not pfirst:
        for directory in path_dirs:
            chk_jdk(directory)

    #If Target cannot be found print JDK-6, JDK-7 or JDK-8 without saving it to the cache
    major = get_major(jdk_ver)
    if major <= 6 and jdk_6:
        save(jdk_6, False)
    elif major <= 7 and jdk_7:
        save(jdk_7, False)
    elif jdk_8:
        save(jdk_8, False)
    elif jdk_7:
        save(jdk_7, False)
    elif jdk_6:
        save(jdk_6, False)

def get_major(v):
    try:
        parts = v.replace('-', '.').replace('_', '.').split('.')
        major = int(parts[0])
        if major < 2:
            return int(parts[1])
        return major
    except Exception as e:
        pass
    return 8

if __name__ == "__main__":
    working_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cache")
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    #Parse Arguments
    if len(sys.argv) >= 2 and sys.argv[1]:
        jdk_ver = sys.argv[1]
        if len(sys.argv) > 2:
            pfirst = sys.argv[2].lower().startswith('t')
    else:
        jdk_ver = "1.8."
        jdk_targ_file = os.path.join(working_dir, "jdkfinder-target.cfg")
        if os.path.isfile(jdk_targ_file):
            with open(jdk_targ_file, "r") as file:
                jdk_ver = file.readline().strip()
                if jdk_ver == '':
                    jdk_ver = '1.8.'
        with open(jdk_targ_file, "wb") as file:
            file.write(jdk_ver)
    
    #Parsed Cached JDK
    cached_path = os.path.join(working_dir, "jdkfinder-" + jdk_ver.strip('.') + ".cfg")
    if(os.path.isfile(cached_path)):
        with open(cached_path, "r") as file:
            cached_jkd = file.readline().strip().replace("\r\n", "\n")
        chk_jdk(cached_jkd)

    find_jdk()
    sys.exit(1)
