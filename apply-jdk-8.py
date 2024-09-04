import os
import sys

def patch_mcpjdk8(directory):
    patch_code = (
        'REM ## FoxyForgeMDK JDK-8 Patch ##\n'
        'FOR /F "delims=" %%I IN (\'runtime\\bin\\python\\python_mcp find-jdk.py\') DO SET "JAVA_DIR=%%I"\n'
        'set "PATH=%JAVA_DIR%;%PATH%"\n'
        'REM ## FoxyForgeMDK JDK-8 Patch ##\n'
    )

    for filename in os.listdir(directory):
        if filename.endswith('.bat'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                lines = file.readlines()
                
            # Inject Code
            lines.insert(1, patch_code)
                
            # Save file
            with open(file_path, 'w') as file:
                file.writelines(lines)
                print("Patch MCP for JDK-8: {}".format(filename))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python apply-jdk-8.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    patch_mcpjdk8(directory)
