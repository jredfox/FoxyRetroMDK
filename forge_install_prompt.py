import sys
import os
import traceback

#Forge Installation Startup Prompt Script. Doesn't prompt the first install
def main():
    global should_pause
    mcp = os.path.realpath(sys.argv[1])
    dir_forge = os.path.dirname(os.path.realpath(__file__))
    installed_file = os.path.join(dir_forge, 'installed')
    installed_forge = os.path.isfile(installed_file)
    #Prompt User on Forge Re-Install
    if installed_forge:
        print('WARNING: Re-Installing Forge will DELETE ALL Folders created by MCP including the "src" folder which contains your modifications!')
        answer = raw_input('Do you wish to Continue Yes or No? [Y/N]: ').lower().replace(' ', '')
        if not answer.startswith('y'):
            should_pause = False
            sys.exit(1)
    #Check for Eclipse Lock
    sys.path.insert(0, mcp)
    from lwjglversionchanger import reset_eclipse
    eclipse_client = os.path.join(mcp, 'eclipse', 'Client')
    if installed_forge or (not os.path.isfile(eclipse_client, '.classpath')) or os.path.isdir(os.path.join(eclipse_client, 'bin')):
        print('resetting eclipse...')
        reset_eclipse(mcp, os.path.join(dir_forge, 'fml'), os.path.join(mcp, 'eclipse'))
    #Create the installed file
    with open(installed_file, 'wb') as f:
        f.write('placeholder')
    
    #Exit Normally Enforcing Exit Code 0 to avoid python bugs or "features"
    sys.exit(0)

if __name__ == "__main__":
    try:
        should_pause = (os.name == 'nt')
        main()
    except SystemExit as e:
        if e.code is None:
            exit_code = 0
        else:
            exit_code = e.code if isinstance(e.code, int) else 1
        #Pause if an error happened and we should pause
        if exit_code != 0 and should_pause:
            v = raw_input('Press Enter to Continue... ')
        sys.exit(exit_code)
    except Exception:
        traceback.print_exc()
        if should_pause:
            v = raw_input('Press Enter to Continue... ')
        sys.exit(1)