import os
import subprocess
import re

# Pyton Script to find JDK-8 from the path
def find_JDK8():
    path_dirs = os.getenv('PATH', '').split(os.pathsep)
    path_jdk8 = None
    path_jdk7 = None
    path_jdk6 = None

    for directory in path_dirs:
        # Check if javac exists in the directory
        javac_path = os.path.join(directory, 'javac')
        if os.path.isfile(javac_path) or os.path.isfile(javac_path + '.exe'):
            java_path = os.path.join(directory, 'java')
            if os.path.isfile(java_path) or os.path.isfile(java_path + '.exe'):
                try:
                    # Run 'java -version' command to check the version
                    version_output = subprocess.check_output([java_path, '-version'], stderr=subprocess.STDOUT)
                    line = version_output.decode('utf-8').splitlines()[0]  # Get the first line of the output
                    version_info = re.search(r'"(.*?)(?<!\\)"', line).group(1)
                    
                    # Check if the version is 1.8 (Java 8)
                    if version_info.startswith('1.8.'):
                        path_jdk8 = directory
                        break
                    elif version_info.startswith('1.7.'):
                        path_jdk7 = directory
                    elif version_info.startswith('1.6.'):
                        path_jdk6 = directory
                except subprocess.CalledProcessError:
                    continue
                except Exception:
                    continue
    
    if path_jdk8:
        print(path_jdk8)
    elif path_jdk7:
        print(path_jdk7)
    elif path_jdk6:
        print(path_jdk6)
        
if __name__ == "__main__":
    find_JDK8()
