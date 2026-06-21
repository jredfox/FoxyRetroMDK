import sys
import os

if __name__ == "__main__":
    
    #Patch MC 1.1 - 1.2.5 macOS graphical glitches on java 8!
    mdk = os.path.realpath(sys.argv[1])
    dir_resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
    
    #Patch Start.java
    start_patch = os.path.join(dir_resources, 'Start.java.patch')
    start_file = os.path.join(mdk, 'src', 'minecraft', 'Start.java')
    #MC 1.1 support
    if not os.path.exists(start_file):
        start_file = os.path.join(mdk, 'forge', 'conf', 'patches', 'Start.java')
    with open(start_patch, 'r') as f:
        lines_start_patch = f.read()
    with open(start_file, 'r') as f:
        lines = f.read()
    if 'FoxyRetroMDK.noapplet' not in lines:
        print('Patching Start.java')
        lines = lines.replace('Minecraft.main(args);', 'if(Character.toUpperCase(System.getProperty("FoxyRetroMDK.noapplet", "false").charAt(0)) == \'T\')\n            Minecraft.main(args);\n        else\n            start(args);', 1)
        targ = lines.rfind('}')
        lines = lines[:targ] + '\n' + lines_start_patch + '\n}\n'
        with open(start_file, 'wb') as f:
            f.write(lines)
    
    #Copy MinecraftAppletStub.java
    print('Copying MinecraftAppletStub.java')
    with open(os.path.join(dir_resources, 'MinecraftAppletStub.java'), 'r') as f:
        lines = f.read()
    with open(os.path.join(mdk, 'src', 'minecraft', 'MinecraftAppletStub.java'), 'wb') as f:
        f.write(lines)
    
    #Patch MinecraftApplet.java
    print('Patching MinecraftApplet.java')
    with open(os.path.join(mdk, 'src', 'minecraft', 'MinecraftApplet.java'), 'r') as f:
        lines = f.read()
    lines = lines.replace('private ', 'public ').replace('protected ', 'public ')
    if 'this.mcThread.setPriority(10);' not in lines:
        lines = lines.replace('mcThread.start();', 'this.mcThread.setPriority(10);\n        this.mcThread.start();').replace('mcThread = new', 'this.mcThread = new')
    
    #Update MCP
    from runtime.updatenames import updatenames
    from runtime.updatemd5 import updatemd5
    print('Updating Names')
    updatenames(None, True)
    print('Updating MD5')
    updatemd5(None, True)
    print('FoxyRetroMDK Added Applet Launcher to fix graphical issues on macOS!')