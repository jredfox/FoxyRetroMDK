import os
import sys
import glob

#global vars
plat = sys.platform.lower()
isMac = plat == 'darwin'
isLinux = os.name != 'darwin' and os.name != 'nt' #I am aware that most of the time it will return linux but there are 50 other strings it could be and since I only support 3 OS's this is better

mcp_sh_patch = (
	'## FoxyRetroMDK START ##\n'
	'mcp="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"\n'
	'cd "$mcp"\n'
	'isa="$(uname -m)"\n'
	'JDK8=$("$mcp/bin_linux/$isa/python2.7/python2.7" "$mcp/jdk-finder.py" | xargs)\n'
	'export PATH="$JDK8:$mcp/bin_linux/$isa/python2.7:$mcp/bin_linux/$isa/astyle:$PATH"\n'
	'## FoxyRetroMDK END ##\n'
)

mcp_batch_patch = (
	'REM ## FoxyForgeMDK JDK-8 Patch ##\n'
    'FOR /F "delims=" %%I IN (\'runtime\\bin\\python\\python_mcp find-jdk.py\') DO SET "JAVA_DIR=%%I"\n'
    'set "PATH=%JAVA_DIR%;%PATH%"\n'
    'REM ## FoxyForgeMDK JDK-8 Patch ##\n'
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
				lines.insert(1, (mcp_sh_patch.replace('isa="$(uname -m)"\n', 'isa="$(uname -m)"\nmcp="$(dirname "$mcp")"\n') if isSh else mcp_batch_patch.replace('runtime\\bin\\python', '..\\runtime\\bin\\python')))
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
				lines.insert(1, (mcp_sh_patch.replace('isa="$(uname -m)"\n', 'isa="$(uname -m)"\nmcp="$(dirname "$mcp")"\nmcp="$(dirname "$mcp")"\n') if isSh else mcp_batch_patch.replace('runtime\\bin\\python', '..\\..\\runtime\\bin\\python')))
				with open(file, 'w') as f:
					f.writelines(lines)
					print("Patching Path:" + file)
	else:
		for file in glob.glob(mdk + "/*"):
			isSh = file.endswith(".sh")
			if isSh or file.endswith(".bat") or file.endswith(".cmd"):
				with open(file, 'r') as f:
					lines = f.readlines()
				lines.insert(1, (mcp_sh_patch.replace('bin_linux', 'mcp/bin_linux').replace('jdk-finder.py', 'mcp/jdk-finder.py') if isSh else mcp_batch_patch.replace('runtime\\bin\\python\\python_mcp find-jdk.py', 'mcp\\runtime\\bin\\python\\python_mcp mcp\\find-jdk.py')))
				with open(file, 'w') as f:
					f.writelines(lines)
				if isSh:
					lines = [line.replace("python", "python2.7") for line in lines]
					print("Patching Path:" + file)
		for file in glob.glob(mdk + "/fml/*"):
			isSh = file.endswith(".sh")
			if isSh or file.endswith(".bat") or file.endswith(".cmd"):
				with open(file, 'r') as f:
					lines = f.readlines()
				if isSh:
					lines = [line.replace("python", "python2.7") for line in lines]
				lines.insert(1, (mcp_sh_patch.replace('bin_linux', 'mcp/bin_linux').replace('jdk-finder.py', 'mcp/jdk-finder.py').replace('isa="$(uname -m)"\n', 'isa="$(uname -m)"\nmcp="$(dirname "$mcp")"\n') if isSh else mcp_batch_patch.replace('runtime\\bin\\python\\python_mcp find-jdk.py', '..\\mcp\\runtime\\bin\\python\\python_mcp ..\\mcp\\find-jdk.py')))
				with open(file, 'w') as f:
					f.writelines(lines)
					print("Patching Path:" + file)
