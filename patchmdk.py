import os
import sys
import glob
import shutil

#global vars
sh_portability = 'python2.7 patchportability.py "$mcp" "${BASH_SOURCE[0]:-$0}"\n' if ( os.getenv("patchoneone") == "T" ) else ""
sh_portability_forge = 'python2.7 "$mcp/patchportability.py" "$mcp" "${BASH_SOURCE[0]:-$0}"\n'
batch_portability = 'call "runtime\\bin\\python\\python_mcp.exe" "patchportability.py" "" "%~0"\r\n' if ( os.getenv("patchoneone") == "T" ) else ""
batch_portability_forge = 'call "..\\runtime\\bin\\python\\python_mcp.exe" "..\\patchportability.py" ".." "%~0"\r\n'

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

lwjgl_version_changer_cmd = (
    '@ECHO OFF\r\n'
    'REM ## Foxy Retro MDK START ##\r\n'
    'cd /D "%~dp0"\r\n'
    'set lwjgl_ver=%~1\r\n'
    'IF /I "%lwjgl_ver%" == "" (\r\n'
        'set /p lwjgl_ver="Enter LWJGL Version: "\r\n'
    ')\r\n'
    'call "%APPDATA%\\FoxyRetroMDK\\python2.7\\python.exe" "lwjglversionchanger.py" "%lwjgl_ver%"\r\n'
    'pause\r\n'
    'REM ## Foxy Retro MDK END ##\r\n'
)

lwjgl_version_changer_sh = (
    '#!/bin/bash\n'
    '## Foxy Retro MDK START ##\n'
    'mcp="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"\n'
    'cd "$mcp"\n'
    'isa="$(uname -m)"\n'
    'export PATH="$mcp/bin_linux/$isa/python2.7:$PATH"\n'
    'chmod -R 777 "$mcp/bin_linux" 2>/dev/null\n'
    'python2.7 "lwjglversionchanger.py" "$1"\n'
    '## Foxy Retro MDK END ##\n'
)

def patch_forge_install(lines, isSh, fml_script=False):
    if isSh:
        lines = lines.replace('./cleanup.sh', './cleanup.sh -f')
        if applet_patch:
            lines = lines + '\npython2.7 "$mcp/forge/patch_applet.py" "$mcp"'
    else:
        lines = lines.replace('runtime\\cleanup.py', 'runtime\\cleanup.py -f').replace('runtime/cleanup.py', 'runtime/cleanup.py -f')
        if applet_patch:
            lines = lines[:lines.rfind('pause')] + 'cd /D "%~dp0.."\r\nruntime\\bin\\python\\python_mcp forge\\patch_applet.py "."\r\npause'
    return lines

def patch_forge_cleanup(install_py_file):
    if os.path.isfile(install_py_file):
        with open(install_py_file, 'r') as f:
            lines = f.read()
        if 'cleanup(None, False' in lines:
            print("Patching Path:" + install_py_file)
            lines = lines.replace("\r\n", "\n").replace('cleanup(None, False)', 'cleanup(None, True)').replace('cleanup(None, False, False)', 'cleanup(None, True, False)')
            with open(install_py_file, 'wb') as f:
                f.write(lines)

if __name__ == "__main__":

    mdk = os.path.normpath(sys.argv[1])
    mcpInForge = sys.argv[2][0].lower() == 't'
    mcp = os.path.normpath((mdk + "/mcp")) if mcpInForge else mdk
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
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
        shutil.copyfile(os.path.join(script_dir, 'forge_install_prompt.py'), os.path.join(mdk, 'forge_install_prompt.py') )
        shutil.make_archive(os.path.join(mcp, 'runtime', 'eclipse'), 'zip', os.path.join(mdk, 'fml', 'eclipse'))
        useMojang = os.getenv("useFMLMaven") != 'T'
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
                name = lib.get("name", "").lower()
                if 'lwjgl' in name and ('org.lwjgl.lwjgl:lwjgl:' in name or 'org.lwjgl.lwjgl:lwjgl_util:' in name or 'org.lwjgl.lwjgl:lwjgl-platform:' in name):
                    url = lib.get("url")
                    if useMojang:
                        if url is not None:
                            del lib["url"]
                    else:
                        lib["url"] = "https://repo.maven.apache.org/maven2"
            fmlJSONText = json.dumps(data, indent=2).replace('\r\n', '\n')
            with open(fmlJSONFile, 'wb') as f:
                for line in fmlJSONText.split('\n'):
                    f.write(line.rstrip() + '\n')
        
        #Makes LWJGL 2.9.1's sources download
        fmlpyf = os.path.normpath(os.path.join(mdk, 'fml/fml.py'))
        if os.path.exists(fmlpyf):
            print('Patching Path:' + fmlpyf)
            fml_py_patch = (
                '## Foxy Retro MDK Start ##\n'
                '            try:\n'
                '                headers = get_headers(url)\n'
                '            except:\n'
                '                url = url.replace(\'https://libraries.minecraft.net\', \'https://repo.maven.apache.org/maven2\', 1)\n'
                '                headers = get_headers(url)\n'
                '            ## Foxy Retro MDK End ##'
            )
            with open(fmlpyf, 'r') as f:
                lines = f.read()
            lines = lines.replace('headers = get_headers(url)', fml_py_patch, 1)
            with open(fmlpyf, 'wb') as f:
                f.write(lines)
        
        #Modify Patches based on Directory
        str_mdk_sh = mcp_sh_patch.replace('cd "$mcp"\n', 'cd "$mcp"\nmcp="${mcp}/mcp"\n', 1).replace('## Foxy Retro MDK END ##\n', 'python2.7 forge_install_prompt.py "$mcp" || exit 1\n## Foxy Retro MDK END ##\n', 1)
        str_mdk_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"mcp\\runtime\\bin\\python\\python_mcp.exe" "mcp\\jdk-finder.py"').replace('REM ## Foxy Retro MDK END ##\r\n', 'call "%APPDATA%\\FoxyRetroMDK\\python2.7\\python.exe" "forge_install_prompt.py" "mcp" || exit /b 1\r\nREM ## Foxy Retro MDK END ##\r\n', 1)
        str_fml_sh = str_mdk_sh.replace('cd "$mcp"\n', 'mcp="$(dirname "$mcp")"\ncd "$mcp"\n', 1)
        str_fml_cmd = str_mdk_cmd.replace('cd /D "%~dp0"\r\n', 'cd /D "%~dp0.."\r\n', 1)
        
        #Patch Forge's & fml's cleanup so that it doesn't prompt
        patch_forge_cleanup(os.path.join(mdk, 'fml', 'fml.py'))
        
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
        shutil.copyfile(os.path.join(script_dir, 'forge_install_prompt.py'), os.path.join(mdk, 'forge', 'forge_install_prompt.py') )
        eclipse_dir = os.path.join(mdk, 'forge', 'fml', 'eclipse')
        if not os.path.isdir(eclipse_dir):
            eclipse_dir = os.path.join(mdk, 'eclipse')
        shutil.make_archive(os.path.join(mcp, 'runtime', 'eclipse'), 'zip', eclipse_dir)
        #Modify Patches based on Directory
        str_forge_sh = mcp_sh_patch.replace('cd "$mcp"\n', 'cd "$mcp"\nmcp="$(dirname "$mcp")"\n', 1).replace('## Foxy Retro MDK END ##\n', 'python2.7 forge_install_prompt.py "$mcp" || exit 1\n## Foxy Retro MDK END ##\n', 1)
        str_forge_cmd = mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\runtime\\bin\\python\\python_mcp.exe" "..\\jdk-finder.py"').replace('REM ## Foxy Retro MDK END ##\r\n', 'call "%APPDATA%\\FoxyRetroMDK\\python2.7\\python.exe" "forge_install_prompt.py" ".." || exit /b 1\r\nREM ## Foxy Retro MDK END ##\r\n', 1)
        
        #Modify Patches for MC 1.4x
        if os.getenv("patch_21") == "T":
            str_forge_sh = str_forge_sh.replace('## Foxy Retro MDK END ##\n', 'java -jar "$mcp/forge/PatchRenderPlayer.jar" "$mcp/forge"\n## Foxy Retro MDK END ##\n', 1)
            str_forge_cmd = str_forge_cmd.replace('REM ## Foxy Retro MDK END ##\r\n', 'java -jar PatchRenderPlayer.jar ""\r\nREM ## Foxy Retro MDK END ##\r\n', 1)
        
        #Make MC 1.1 - 1.2.5 Portabable when re-installing forge from non windows
        if os.getenv("patch_portability") == "T":
            str_forge_sh = str_forge_sh.replace('mcp="$(dirname "$mcp")"\n', 'mcp="$(dirname "$mcp")"\n## Portability Patch Start ##\nchmod +x "$mcp"/*.sh\nchmod +x "$mcp/forge"/*.sh\nchmod +x "$mcp/forge/fml"/*.sh 2>/dev/null\n## Portability Patch End ##\n', 1)
            str_forge_sh = str_forge_sh.replace('xattr -r -d com.apple.quarantine "$mcp/runtime/bin"\n', 'xattr -r -d com.apple.quarantine "$mcp/runtime/bin"\n    ## Portability Patch Start ##\n    xattr -d com.apple.quarantine "$mcp/forge"/*.sh 2>/dev/null\n    xattr -d com.apple.quarantine "$mcp/forge/fml"/*.sh 2>/dev/null\n    xattr -d com.apple.quarantine "$mcp"/*.sh 2>/dev/null\n    ## Portability Patch End ##\n', 1)
            str_forge_sh = str_forge_sh.replace('## Foxy Retro MDK END ##\n', sh_portability_forge + '## Foxy Retro MDK END ##\n', 1)
            str_forge_cmd = str_forge_cmd.replace('REM ## Foxy Retro MDK END ##\r\n', batch_portability_forge + 'REM ## Foxy Retro MDK END ##\r\n', 1)
        
        #Set FML Scripts
        str_fml_sh = str_forge_sh.replace('cd "$mcp"\n', 'mcp="$(dirname "$mcp")"\ncd "$mcp"\n', 1)
        str_fml_cmd = str_forge_cmd.replace('cd /D "%~dp0"\r\n', 'cd /D "%~dp0.."\r\n', 1)
        
        #Patch MC 1.2.5 FML's Install scripts to replace the conf folder during the install like previous and newer versions
        if os.getenv("patch_conf_fml") == "T":
            str_fml_sh = str_fml_sh.replace('## Foxy Retro MDK END ##\n', '## patch_conf_fml ##\npushd .. > /dev/null\nrm -rf conf\nmkdir conf\ncp -r forge/conf/* conf\npopd > /dev/null\n## Foxy Retro MDK END ##\n')
            str_fml_cmd = str_fml_cmd.replace('REM ## Foxy Retro MDK END ##\r\n', 'REM ## patch_conf_fml ##\r\npushd .. >nul\r\nxcopy /Y /E /I forge\\conf\\* conf\r\npopd >nul\r\nREM ## Foxy Retro MDK END ##\r\n')
        
        #Patch MC 1.1 - 1.2.5 macOS graphical glitches on java 8!
        applet_patch = os.getenv("patch_applet") == "T"
        if applet_patch:
            cleanup_file = os.path.join(mdk, 'runtime', 'cleanup.py')
            print("Patching Path:" + cleanup_file)
            with open(cleanup_file, 'r') as f:
                lines = f.read().replace("\r\n", "\n")
            targ = lines.find('\n', lines.find('def cleanup('))
            lines = lines[:targ] + '\n    ## Foxy Retro MDK Start ##\n    import shutil\n    dir_mdk = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))\n    shutil.copyfile(os.path.join(dir_mdk, \'forge\', \'conf\', \'patches\', \'Start.java\'), os.path.join(dir_mdk, \'conf\', \'patches\', \'Start.java\'))\n    ## Foxy Retro MDK End ##' + lines[targ:]
            with open(cleanup_file, 'wb') as f:
                f.write(lines)
        
        #Patch Forge's & fml's cleanup so that it doesn't prompt
        patch_forge_cleanup(os.path.join(mdk, 'forge', 'install.py'))
        patch_forge_cleanup(os.path.join(mdk, 'forge', 'fml', 'fml.py'))
        
        for file in glob.glob(os.path.normpath(mdk + "/forge/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                print("Patching Path:" + file)
                with open(file, 'r') as f:
                    lines = f.read()
                lines = ( lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_forge_sh, 1) ) if isSh else lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_forge_cmd, 1)
                lines = patch_forge_install(lines, isSh)
                with open(file, 'wb') as f:
                    f.write(lines)
                
        for file in glob.glob(os.path.normpath(mdk + "/forge/fml/*")):
            isSh = file.endswith(".sh")
            if isSh or file.endswith(".bat") or file.endswith(".cmd"):
                print("Patching Path:" + file)
                with open(file, 'r') as f:
                    lines = f.read()
                lines = ( lines.replace("\r\n", "\n").replace("python", "python2.7").replace("\n", "\n" + str_fml_sh, 1) ) if isSh else lines.replace("\r\n", "\n").replace("\n", "\r\n").replace("\n", "\n" + str_fml_cmd, 1)
                lines = patch_forge_install(lines, isSh, True)
                with open(file, 'wb') as f:
                    f.write(lines)
        
        #Attatch lwjgl sources
        from lwjglversionchanger import attatch_src
        forge_classpath = os.path.join(mcp, 'forge', 'fml', 'eclipse', 'Minecraft', '.classpath')
        if os.path.exists(forge_classpath):
            #MC 1.3.2 - 1.5.2
            attatch_src(forge_classpath)
            attatch_src(os.path.join(mcp, 'eclipse', 'Minecraft', '.classpath'), True)
        else:
            #MC 1.1 - 1.2.5
            attatch_src(os.path.join(mcp, 'eclipse', 'Client', '.classpath'))
            attatch_src(os.path.join(mcp, 'eclipse', 'Server', '.classpath'))
        print('LWJGL Sources Attatched!')
    #Copy lwjglversionchanger into MCP
    with open(os.path.join(mcp, 'lwjglversionchanger.sh'), 'wb') as f:
        f.write(lwjgl_version_changer_sh)
    with open(os.path.join(mcp, 'lwjglversionchanger.cmd'), 'wb') as f:
        f.write(lwjgl_version_changer_cmd)
    