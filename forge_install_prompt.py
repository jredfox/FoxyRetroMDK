import sys
import os
import subprocess

#Check returns True if it's safe to delete the eclipse folder
#NOTE: deletes eclipse's lock file on windows
def chk_eclipse(d):
    lck_file = os.path.join(d, '.metadata', '.lock')
    if not os.path.isfile(lck_file):
        return True
    #Support Windows if deletion fails assumed eclipse's lock file is locked
    if os.name == 'nt':
        try:
            os.remove(lck_file)
            return (not os.path.isfile(lck_file))
        except:
            return False
    try:
        with open(os.devnull, 'w') as devnull:
            exit_code = subprocess.call(['lsof', lck_file], stdout=devnull, stderr=devnull)
        return exit_code != 0
    except:
        return True

#Forge Installation Startup Prompt Script. Doesn't prompt the first install
if __name__ == "__main__":
    mcp = os.path.realpath(sys.argv[1])
    installed_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'installed')
    #Prompt User on Forge Re-Install
    if os.path.isfile(installed_file):
        print('WARNING: Re-Installing Forge will DELETE ALL Folders created by MCP including the src folder which contains your modifications!')
        print('Do you wish to Continue Yes or No: ')
        answer = raw_input().lower()
        if not answer.startswith('y'):
            sys.exit(1)
    #Check for Eclipse Lock
    if not chk_eclipse(os.path.join(mcp, 'eclipse')):
        print('Eclipse has the workspace already opened! Close Eclipse and try again')
        sys.exit(1)
    #Create the installed file
    with open(installed_file, 'wb') as f:
        f.write('placeholder')
    #Copy Start.java.bck to Start.java
    start_file_forge = os.path.join('conf', 'patches', 'Start.java')
    start_file_forge_bck = start_file_forge + '.bck'
    if os.path.isfile(start_file_forge_bck):
        with open(start_file_forge_bck, 'r') as f:
            lines = f.read().replace('\r\n', '\n')
        with open(start_file_forge, 'wb') as f:
            f.write(lines)
    