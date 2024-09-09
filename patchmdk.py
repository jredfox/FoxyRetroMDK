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
	'REM ## FoxyForgeMDK JDK-8 START Patch ##\n'
    'FOR /F "delims=" %%I IN (\'call "runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"\') DO SET "JAVA_DIR=%%I"\n'
    'set "PATH=%JAVA_DIR%;%PATH%"\n'
    'FOR %%I IN ("%JAVA_DIR%\..") DO SET "JAVA_HOME=%%~fI"'
    'REM ## FoxyForgeMDK JDK-8 END Patch ##\n'
)

if __name__ == "__main__":

	mdk = sys.argv[1]
	forgeInMCP = sys.argv[2][0].lower() == 't'
	mcp = (mdk + "/mcp") if forgeInMCP else mdk

	for file in glob.glob(mcp + "/*"):
		isSh = file.endswith(".sh")
		if isSh or file.endswith(".bat") or file.endswith(".cmd"):
			with open(file, 'r') as f:
				lines = f.readlines()
			if isSh:
				lines = [line.replace("python", "python2.7") for line in lines]
			lines.insert(1, (mcp_sh_patch if isSh else mcp_batch_patch))
			with open(file, 'w') as f:
				f.writelines(lines)
				print("Patching Path:" + file)

	if not forgeInMCP:
		for file in glob.glob(mdk + "/forge/*"):
			isSh = file.endswith(".sh")
			if isSh or file.endswith(".bat") or file.endswith(".cmd"):
				with open(file, 'r') as f:
					lines = f.readlines()
				if isSh:
					lines = [line.replace("python", "python2.7") for line in lines]
				lines.insert(1, (mcp_sh_patch.replace('cd "$mdk"\n', 'cd "$mdk"\nmdk="$(dirname "$mdk")"\n') if isSh else mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\runtime\\bin\\python\\python_mcp.exe" "..\\jdk-finder.py"') ))
				with open(file, 'w') as f:
					f.writelines(lines)
					print("Patching Path:" + file)
		for file in glob.glob(mdk + "/forge/fml/*"):
			isSh = file.endswith(".sh")
			if isSh or file.endswith(".bat") or file.endswith(".cmd"):
				with open(file, 'r') as f:
					lines = f.readlines()
				if isSh:
					lines = [line.replace("python", "python2.7") for line in lines]
				lines.insert(1, (mcp_sh_patch.replace('cd "$mdk"\n', 'cd "$mdk"\nmdk="$(dirname "$mdk")"\nmdk="$(dirname "$mdk")"\n') if isSh else mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\..\\runtime\\bin\\python\\python_mcp.exe" "..\\..\\jdk-finder.py"')))
				with open(file, 'w') as f:
					f.writelines(lines)
					print("Patching Path:" + file)
	else:
		for file in glob.glob(mdk + "/*"):
			isSh = file.endswith(".sh")
			if isSh or file.endswith(".bat") or file.endswith(".cmd"):
				with open(file, 'r') as f:
					lines = f.readlines()
				if isSh:
					lines = [line.replace("python", "python2.7") for line in lines]
				lines.insert(1, (mcp_sh_patch.replace('bin_linux', 'mcp/bin_linux').replace('jdk-finder.py', 'mcp/jdk-finder.py') if isSh else mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"mcp\\runtime\\bin\\python\\python_mcp.exe" "mcp\\jdk-finder.py"')))
				with open(file, 'w') as f:
					f.writelines(lines)
					print("Patching Path:" + file)
		for file in glob.glob(mdk + "/fml/*"):
			isSh = file.endswith(".sh")
			if isSh or file.endswith(".bat") or file.endswith(".cmd"):
				with open(file, 'r') as f:
					lines = f.readlines()
				if isSh:
					lines = [line.replace("python", "python2.7") for line in lines]
				lines.insert(1, (mcp_sh_patch.replace('bin_linux', 'mcp/bin_linux').replace('jdk-finder.py', 'mcp/jdk-finder.py').replace('cd "$mdk"\n', 'cd "$mdk"\nmdk="$(dirname "$mdk")"\n') if isSh else mcp_batch_patch.replace('"runtime\\bin\\python\\python_mcp.exe" "jdk-finder.py"', '"..\\mcp\\runtime\\bin\\python\\python_mcp.exe" "..\\mcp\\jdk-finder.py"')))
				with open(file, 'w') as f:
					f.writelines(lines)
					print("Patching Path:" + file)
