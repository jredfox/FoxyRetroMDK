import os
import sys
import glob

#global vars
isWindows = os.name == 'nt'
isMac = sys.platform.lower() == 'darwin'
isLinux = not isMac and not isWindows

if isLinux:
    mcp_sh_patch = (
        '## FoxyRetroMDK START ##\n'
        'mdk="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"\n'
        'cd "$mdk"\n'
        'isa="$(uname -m)"\n'
        'JDK8=$("$mdk/bin_linux/$isa/python2.7/python2.7" "$mdk/jdk-finder.py" | xargs)\n'
        'export PATH="$JDK8:$mdk/bin_linux/$isa/python2.7:$mdk/bin_linux/$isa/astyle:$PATH"\n'
        'export JAVA_HOME=$(dirname "$JDK8")\n'
        '## FoxyRetroMDK END ##\n'
    )
else:
    mcp_sh_patch = (
        '## FoxyRetroMDK START ##\n'
        'mdk="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"\n'
        'cd "$mdk"\n'
        'JDK8=$("python2.7" "$mdk/jdk-finder.py" | xargs)\n'
        'export PATH="$JDK8:$PATH"\n'
        'export JAVA_HOME=$(dirname "$JDK8")\n'
        '## FoxyRetroMDK END ##\n'
    )

mcp_batch_patch = (
    'REM ## FoxyForgeMDK JDK-8 START Patch ##\r\n'
    'FOR /F "delims=" %%I IN (\'call "runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"\') DO SET "JAVA_DIR=%%I"\r\n'
    'set "PATH=%JAVA_DIR%;%PATH%"\r\n'
    'FOR %%I IN ("%JAVA_DIR%\..") DO SET "JAVA_HOME=%%~fI"\r\n'
    'REM ## FoxyForgeMDK JDK-8 END Patch ##\r\n'
)

if __name__ == "__main__":

    mdk = os.path.normpath(sys.argv[1])
    mcpInForge = sys.argv[2][0].lower() == 't'
    mcp = (mdk + "/mcp") if mcpInForge else mdk

    for file in glob.glob(os.path.normpath(mcp + "/*")):
        isSh = file.endswith(".sh")
        if isSh or file.endswith(".bat") or file.endswith(".cmd"):
            with open(file, 'r') as f:
                lines = (f.read().replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + mcp_sh_patch, 1) ) if isSh else (f.read().replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + mcp_batch_patch, 1))
            with open(file, 'wb') as f:
                f.write(lines)
                print("Patching Path:" + file)
    if mcpInForge:
        #Modify Patches based on Directory
        str_mdk_sh = mcp_sh_patch.replace('bin_linux', 'mcp/bin_linux').replace('jdk-finder.py', 'mcp/jdk-finder.py')
        str_mdk_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"mcp\\runtime\\bin\\python\\python_mcp.exe" "mcp\\jdk-finder.py"')
        str_fml_sh = mcp_sh_patch.replace('bin_linux', 'mcp/bin_linux').replace('jdk-finder.py', 'mcp/jdk-finder.py').replace('cd "$mdk"\n', 'cd "$mdk"\nmdk="$(dirname "$mdk")"\n')
        str_fml_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\mcp\\runtime\\bin\\python\\python_mcp.exe" "..\\mcp\\jdk-finder.py"')
        
        for file in glob.glob(os.path.normpath(mdk + "/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                with open(file, 'r') as f:
                    lines = ( f.read().replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_mdk_sh, 1) ) if isSh else f.read().replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_mdk_cmd, 1)
                with open(file, 'wb') as f:
                    f.write(lines)
                    print("Patching Path:" + file)
        for file in glob.glob(os.path.normpath(mdk + "/fml/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                with open(file, 'r') as f:
                    lines = ( f.read().replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_fml_sh, 1) ) if isSh else f.read().replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_fml_cmd, 1)
                with open(file, 'wb') as f:
                    f.write(lines)
                    print("Patching Path:" + file)
    else:
        #Modify Patches based on Directory
        str_forge_sh = mcp_sh_patch.replace('cd "$mdk"\n', 'cd "$mdk"\nmdk="$(dirname "$mdk")"\n')
        str_forge_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\runtime\\bin\\python\\python_mcp.exe" "..\\jdk-finder.py"')
        str_fml_sh = mcp_sh_patch.replace('cd "$mdk"\n', 'cd "$mdk"\nmdk="$(dirname "$mdk")"\nmdk="$(dirname "$mdk")"\n')
        str_fml_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\..\\runtime\\bin\\python\\python_mcp.exe" "..\\..\\jdk-finder.py"')
        
        for file in glob.glob(os.path.normpath(mdk + "/forge/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                with open(file, 'r') as f:
                    lines = ( f.read().replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_forge_sh, 1) ) if isSh else f.read().replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_forge_cmd, 1)
                with open(file, 'wb') as f:
                    f.write(lines)
                    print("Patching Path:" + file)
        for file in glob.glob(os.path.normpath(mdk + "/forge/fml/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                with open(file, 'r') as f:
                    lines = ( f.read().replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_fml_sh, 1) ) if isSh else f.read().replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_fml_cmd, 1)
                with open(file, 'wb') as f:
                    f.write(lines)
                    print("Patching Path:" + file)
