import os
import sys
import glob

#global vars
sh_portability = 'python2.7 patchportability.py "$mcp" "${BASH_SOURCE[0]:-$0}"\n' if ( os.getenv("patchoneone") == "T" ) else ""
sh_portability_forge = 'python2.7 ../patchportability.py "$mcp" "${BASH_SOURCE[0]:-$0}"\n'
batch_portability = 'call "runtime\\bin\\python\\python_mcp.exe" "patchportability.py" "" "%~0"\n' if ( os.getenv("patchoneone") == "T" ) else ""
batch_portability_forge = 'call "..\\runtime\\bin\\python\\python_mcp.exe" "..\\patchportability.py" ".." "%~0"\n'

mcp_sh_patch = (
    '## Foxy Retro MDK START ##\n'
    'mcp="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"\n'
    'cd "$mcp"\n'
    'if [[ "$(echo "$(uname)" | tr \'[:upper:]\' \'[:lower:]\')" == "darwin" ]]; then\n'
    '    chmod -R 777 "$mcp/runtime/bin"\n'
    '    xattr -r -d com.apple.quarantine "$mcp/runtime/bin"\n'
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
    'cd /D "%~dp0"\r\n'
    'FOR /F "delims=" %%I IN (\'call "runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"\') DO SET "JAVA_DIR=%%I"\r\n'
    'set "PATH=%JAVA_DIR%;%PATH%"\r\n'
    'FOR %%I IN ("%JAVA_DIR%\\..") DO SET "JAVA_HOME=%%~fI"\r\n'
    'REM ## Foxy Retro MDK END ##\r\n'
)

mcp_commands_py_patch = (
'    ## Foxy Retro MDK START ##\n'
'        if SIDE_NAME[side].upper() == "SERVER":\n'
'            print(\'> Packing blank.txt into server_recomp.jar for JDK 6 Compatibility\')\n'
'            txtfile = os.path.join(self.binservertmp, \'blank.txt\')\n'
'            with open(txtfile, \'w\') as f:\n'
'                f.write(\'blank\')\n'
'            with zipfile.ZipFile(self.cmpjarserver, "a") as zipf:\n'
'                if \'blank.txt\' not in zipf.namelist():\n'
'                    zipf.write(txtfile, \'blank.txt\')\n'
'        ## Foxy Retro MDK END ##\n\n    '
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
    data = data.replace("\r\n", "\n").replace('\t', '    ').replace('def checkjava(self):', 'def checkjava(self):\n        ## Foxy Retro MDK Start ##\n        jdk_finder = True\n        if jdk_finder:\n            exe = \'.exe\' if ( self.osname == \'win\' ) else \'\'\n            self.cmdjava =  \'"%s"\' % ( \'java\' + exe )\n            self.cmdjavac = \'"%s"\' % ( \'javac\' + exe )\n            return\n        ## Foxy Retro MDK End ##', 1)
    if not mcpInForge:
        start = data.find('def packbin(') + 5
        index = data.find('def ', start)
        data = data[:index] + mcp_commands_py_patch + data[index:]
    with open(commandspy, 'wb') as f:
        f.write(data)
    
    str_mcp_sh_patch = mcp_sh_patch.replace('## Foxy Retro MDK END ##\n', sh_portability + '## Foxy Retro MDK END ##\n', 1)
    str_mcp_batch_patch = mcp_batch_patch.replace('REM ## Foxy Retro MDK END ##\r\n', batch_portability + 'REM ## Foxy Retro MDK END ##\r\n', 1)
    for file in glob.glob(os.path.normpath(mcp + "/*")):
        isSh = file.endswith(".sh")
        if isSh or file.endswith(".bat") or file.endswith(".cmd"):
            print("Patching Path:" + file)
            with open(file, 'r') as f:
                lines = f.read()
            lines = (lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_mcp_sh_patch, 1) ) if isSh else (lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_mcp_batch_patch, 1))
            with open(file, 'wb') as f:
                f.write(lines)
            
    if mcpInForge:
        import json
        from collections import OrderedDict
        #Patch fml.json
        fmlJSONFile = os.path.normpath(os.path.join(mdk, 'fml/fml.json'))
        if os.path.exists(fmlJSONFile):
            print('Patching Path:' + fmlJSONFile)
            with open(fmlJSONFile, 'r') as f:
                data = json.load(f, object_pairs_hook=OrderedDict)
            libraries = data.get('libraries', [])
            for lib in libraries:
                name = lib.get("name", "") 
                url = lib.get("url")
                if "lwjgl" in name.lower() and url is not None:
                    del lib["url"]
            fmlJSONText = json.dumps(data, indent=2).replace('\r\n', '\n')
            with open(fmlJSONFile, 'wb') as f:
                for line in fmlJSONText.split('\n'):
                    f.write(line.rstrip() + '\n')
            
        #Modify Patches based on Directory
        str_mdk_sh = mcp_sh_patch.replace('cd "$mcp"\n', 'cd "$mcp"\nmcp="${mcp}/mcp"\n')
        str_fml_sh = mcp_sh_patch.replace('cd "$mcp"\n', 'mcp="$(dirname "$mcp")"\ncd "$mcp"\nmcp="${mcp}/mcp"\n')
        str_mdk_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"mcp\\runtime\\bin\\python\\python_mcp.exe" "mcp\\jdk-finder.py"')
        str_fml_cmd = str_mdk_cmd.replace('cd /D "%~dp0"\r\n', 'cd /D "%~dp0\\.."\r\n', 1)
        
        for file in glob.glob(os.path.normpath(mdk + "/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                print("Patching Path:" + file)
                with open(file, 'r') as f:
                    lines = f.read()
                lines = ( lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_mdk_sh, 1) ) if isSh else lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_mdk_cmd, 1)
                if isSh and not '$@' in lines:
                    lines = lines.replace('python2.7 install.py', 'python2.7 install.py "$@"')
                elif not isSh and not '%*' in lines:
                    lines = lines.replace('python_fml install.py', 'python_fml install.py %*')
                with open(file, 'wb') as f:
                    f.write(lines)
                
        for file in glob.glob(os.path.normpath(mdk + "/fml/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                print("Patching Path:" + file)
                with open(file, 'r') as f:
                    lines = f.read()
                lines = ( lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_fml_sh, 1) ) if isSh else lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_fml_cmd, 1)
                if isSh and not '$@' in lines:
                    lines = lines.replace('python2.7 install.py', 'python2.7 install.py "$@"')
                elif not isSh and not '%*' in lines:
                    lines = lines.replace('python_fml install.py', 'python_fml install.py %*')
                with open(file, 'wb') as f:
                    f.write(lines)
                
    else:
        #Modify Patches based on Directory
        str_forge_sh = mcp_sh_patch.replace('cd "$mcp"\n', 'cd "$mcp"\nmcp="$(dirname "$mcp")"\n')
        str_fml_sh = mcp_sh_patch.replace('cd "$mcp"\n', 'mcp="$(dirname "$mcp")"\ncd "$mcp"\nmcp="$(dirname "$mcp")"\n')
        str_forge_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\runtime\\bin\\python\\python_mcp.exe" "..\\jdk-finder.py"')
        
        #Modify Patches for MC 1.4x
        if os.getenv("patch_21") == "T":
            str_forge_sh = str_forge_sh.replace('## Foxy Retro MDK END ##\n', 'java -jar "$mcp/forge/PatchRenderPlayer.jar" "$mcp/forge"\n## Foxy Retro MDK END ##\n')
            str_fml_sh = str_fml_sh.replace('## Foxy Retro MDK END ##\n', 'java -jar "$mcp/forge/PatchRenderPlayer.jar" "$mcp/forge"\n## Foxy Retro MDK END ##\n')
            str_forge_cmd = str_forge_cmd.replace('REM ## Foxy Retro MDK END ##\r\n', 'java -jar PatchRenderPlayer.jar "%~dp0"\r\nREM ## Foxy Retro MDK END ##\r\n')
        
        #Make MC 1.1 - 1.2.5 Portabable when re-installing forge from non windows
        if os.getenv("patch_portability") == "T":
            str_forge_sh = str_forge_sh.replace('mcp="$(dirname "$mcp")"\n', 'mcp="$(dirname "$mcp")"\n## Portability Patch Start ##\nchmod +x "$mcp"/*.sh\nchmod +x "$mcp/forge"/*.sh\nchmod +x "$mcp/forge/fml"/*.sh 2>/dev/null\n## Portability Patch End ##\n', 1)
            str_forge_sh = str_forge_sh.replace('xattr -r -d com.apple.quarantine "$mcp/runtime/bin"\n', 'xattr -r -d com.apple.quarantine "$mcp/runtime/bin"\n    ## Portability Patch Start ##\n    xattr -d com.apple.quarantine "$mcp/forge"/*.sh 2>/dev/null\n    xattr -d com.apple.quarantine "$mcp/forge/fml"/*.sh 2>/dev/null\n    xattr -d com.apple.quarantine "$mcp"/*.sh 2>/dev/null\n    ## Portability Patch End ##\n', 1)
            str_forge_sh = str_forge_sh.replace('## Foxy Retro MDK END ##\n', sh_portability_forge + '## Foxy Retro MDK END ##\n', 1)
            str_forge_cmd = str_forge_cmd.replace('REM ## Foxy Retro MDK END ##\r\n', batch_portability_forge + 'REM ## Foxy Retro MDK END ##\r\n', 1)
        
        #Set the fml shell values
        str_fml_cmd = str_forge_cmd.replace('cd /D "%~dp0"\r\n', 'cd /D "%~dp0\\.."\r\n', 1)
        
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
                
