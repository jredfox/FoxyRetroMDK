import os
import sys
import glob

#global vars
plat = sys.platform.lower()
isMac = plat == 'darwin'
isLinux = os.name != 'darwin' and os.name != 'nt' #I am aware that most of the time it will return linux but there are 50 other strings it could be and since I only support 3 OS's this is better

mcp_sh_patch = (
	'## FoxyRetroMDK START ##\n'
	'SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"\n'
	'cd "$SCRIPTPATH"\n'
	'isa="$(uname -m)"\n'
	'JDK8=$("$SCRIPTPATH/bin_linux/$isa/python2.7/python2.7" "$SCRIPTPATH/jdk-finder.py" | xargs)\n'
	'export PATH="$JDK8:$SCRIPTPATH/bin_linux/$isa/python2.7:$SCRIPTPATH/bin_linux/$isa/astyle:$PATH"\n'
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
	if sys.argv[2][0].lower() == 't':
		paths = [
			mdk + "/mcp/*.sh",
			mdk + "/*.sh",
			mdk + "/fml/*.sh",
		]
	else:
		paths = [
			mdk + "/*",
			mdk + "/forge/*",
			mdk + "/forge/fml/*",
		]

	for p in paths:
		for file in glob.glob(p):
			if file.endswith(".sh") or file.endswith(".bat") or file.endswith(".cmd"):
				isSh = file.endswith(".sh")
				with open(file, 'r') as f:
					lines = f.readlines()
				if isSh:
					lines = [line.replace("python", "python2.7") for line in lines]
				lines.insert(1, (mcp_sh_patch if isSh else mcp_batch_patch))
				with open(file, 'w') as f:
					f.writelines(lines)
					print(file)
