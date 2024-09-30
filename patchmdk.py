import os
import sys
import glob

#global vars
oneone = "python2.7 patchoneone.py\n" if ( os.getenv("patchoneone") == "T" ) else ""

mcp_sh_patch = (
    '## Foxy Retro MDK START ##\n'
    'mcp="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"\n'
    'cd "$mcp"\n'
    'if [[ "$(echo "$(uname)" | tr \'[:upper:]\' \'[:lower:]\')" == "darwin" ]]; then\n'
    '    xattr -r -d com.apple.quarantine "$mcp/runtime/bin"\n'
    '    chmod -R 777 "$mcp/runtime/bin"\n'
    'else\n'
    '    isa="$(uname -m)"\n'
    '    export PATH="$mcp/bin_linux/$isa/python2.7:$mcp/bin_linux/$isa/astyle:$PATH"\n'
    '    chmod -R 777 "$mcp/runtime/bin"\n'
    '    chmod -R 777 "$mcp/bin_linux"\n'
    'fi\n'
    'JDK8=$("python2.7" "$mcp/jdk-finder.py" | xargs)\n'
    'export PATH="$JDK8:$PATH"\n'
    'export JAVA_HOME=$(dirname "$JDK8")\n'
    '## Foxy Retro MDK END ##\n'
)

mcp_batch_patch = (
    'REM ## Foxy Retro MDK START ##\r\n'
    'FOR /F "delims=" %%I IN (\'call "runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"\') DO SET "JAVA_DIR=%%I"\r\n'
    'set "PATH=%JAVA_DIR%;%PATH%"\r\n'
    'FOR %%I IN ("%JAVA_DIR%\\..") DO SET "JAVA_HOME=%%~fI"\r\n'
    'REM ## Foxy Retro MDK END ##\r\n'
)

if __name__ == "__main__":

    mdk = os.path.normpath(sys.argv[1])
    mcpInForge = sys.argv[2][0].lower() == 't'
    mcp = (mdk + "/mcp") if mcpInForge else mdk
    
    # Patch MCP commands.py to use java & javac found in PATH
    commandspy = os.path.normpath(mcp + "/runtime/commands.py")
    print("Patching Path:" + commandspy)
    with open(commandspy, 'r') as f:
        data = f.read()
    data = data.replace("\r\n", "\n").replace('def checkjava(self):', 'def checkjava(self):\n        ## Foxy Retro MDK Start ##\n        jdk_finder = True\n        if jdk_finder:\n            exe = \'.exe\' if ( self.osname == \'win\' ) else \'\'\n            self.cmdjava =  \'"%s"\' % ( \'java\' + exe )\n            self.cmdjavac = \'"%s"\' % ( \'javac\' + exe )\n            return\n        ## Foxy Retro MDK End ##', 1)
    with open(commandspy, 'wb') as f:
        f.write(data)
    
    str_mcp_sh_patch = mcp_sh_patch.replace('## Foxy Retro MDK END ##\n', oneone + '## Foxy Retro MDK END ##\n')
    for file in glob.glob(os.path.normpath(mcp + "/*")):
        isSh = file.endswith(".sh")
        if isSh or file.endswith(".bat") or file.endswith(".cmd"):
            print("Patching Path:" + file)
            with open(file, 'r') as f:
                lines = f.read()
            lines = (lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_mcp_sh_patch, 1) ) if isSh else (lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + mcp_batch_patch, 1))
            with open(file, 'wb') as f:
                f.write(lines)
            
    if mcpInForge:
        #Modify Patches based on Directory
        str_mdk_sh = replace('cd "$mcp"\n', 'cd "$mcp"\nmcp="${mcp}/mcp"\n')
        str_fml_sh = replace('cd "$mcp"\n', 'cd "$mcp"\nmcp="$(dirname "$mcp")"\nmcp="${mcp}/mcp"\n')
        str_mdk_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"mcp\\runtime\\bin\\python\\python_mcp.exe" "mcp\\jdk-finder.py"')
        str_fml_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\mcp\\runtime\\bin\\python\\python_mcp.exe" "..\\mcp\\jdk-finder.py"')
        
        for file in glob.glob(os.path.normpath(mdk + "/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                print("Patching Path:" + file)
                with open(file, 'r') as f:
                    lines = f.read()
                lines = ( lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_mdk_sh, 1) ) if isSh else lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_mdk_cmd, 1)
                with open(file, 'wb') as f:
                    f.write(lines)
                
        for file in glob.glob(os.path.normpath(mdk + "/fml/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                print("Patching Path:" + file)
                with open(file, 'r') as f:
                    lines = f.read()
                lines = ( lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_fml_sh, 1) ) if isSh else lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_fml_cmd, 1)
                with open(file, 'wb') as f:
                    f.write(lines)
                
    else:
        #Modify Patches based on Directory
        str_forge_sh = mcp_sh_patch.replace('cd "$mcp"\n', 'cd "$mcp"\nmcp="$(dirname "$mdk")"\n')
        str_fml_sh = mcp_sh_patch.replace('cd "$mcp"\n', 'cd "$mcp"\nmcp="$(dirname "$mdk")"\nmcp="$(dirname "$mdk")"\n')
        str_forge_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\runtime\\bin\\python\\python_mcp.exe" "..\\jdk-finder.py"')
        str_fml_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\..\\runtime\\bin\\python\\python_mcp.exe" "..\\..\\jdk-finder.py"')
        
        for file in glob.glob(os.path.normpath(mdk + "/forge/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                print("Patching Path:" + file)
                with open(file, 'r') as f:
                    lines = f.read()
                lines = ( lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_forge_sh, 1) ) if isSh else lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_forge_cmd, 1)
                with open(file, 'wb') as f:
                    f.write(lines)
                
        for file in glob.glob(os.path.normpath(mdk + "/forge/fml/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                print("Patching Path:" + file)
                with open(file, 'r') as f:
                    lines = f.read()
                lines = ( lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_fml_sh, 1) ) if isSh else lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_fml_cmd, 1)
                with open(file, 'wb') as f:
                    f.write(lines)
                
