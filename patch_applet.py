import sys
import os

if __name__ == "__main__":
    
    #Patch MC 1.1 - 1.2.5 macOS graphical glitches on java 8!
    mdk = os.path.realpath(sys.argv[1])
    dir_resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
    
    #Patch Start.java
    start_patch = os.path.join(dir_resources, 'Start.java.patch')
    start_file = os.path.join(mdk, 'src', 'minecraft', 'Start.java')
    start_file_mcp = None
    start_file_forge = os.path.join(mdk, 'forge', 'conf', 'patches', 'Start.java')
    #Create backup of Start.java
    start_file_forge_bck = start_file_forge + '.bck'
    if not os.path.exists(start_file_forge_bck):
        with open(start_file_forge, 'r') as f:
            lines = f.read().replace('\r\n', '\n')
        with open(start_file_forge_bck, 'wb') as f:
            f.write(lines)
    #MC 1.1 support
    if not os.path.exists(start_file):
        start_file = start_file_forge
        start_file_mcp = os.path.join(mdk, 'conf', 'patches', 'Start.java')
    with open(start_file, 'r') as f:
        lines = f.read().replace('\r\n', '\n')
    if 'FoxyRetroMDK.noapplet' not in lines:
        print('Patching Start.java')
        with open(start_patch, 'r') as f:
            lines_start_patch = f.read().replace('\r\n', '\n')
        lines = lines.replace('Minecraft.main(args);', 'if(Character.toUpperCase(System.getProperty("FoxyRetroMDK.noapplet", "false").charAt(0)) == \'T\')\n            Minecraft.main(args);\n        else\n            start(args);', 1)
        targ = lines.rfind('}')
        lines = lines[:targ] + '\n' + lines_start_patch + '\n}\n'
        with open(start_file, 'wb') as f:
            f.write(lines)
        if start_file_mcp is not None:
            with open(start_file_mcp, 'wb') as f:
                f.write(lines)
    
    #Copy MinecraftAppletStub.java
    print('Copying MinecraftAppletStub.java')
    with open(os.path.join(dir_resources, 'MinecraftAppletStub.java'), 'r') as f:
        lines = f.read().replace('\r\n', '\n')
    with open(os.path.join(mdk, 'src', 'minecraft', 'MinecraftAppletStub.java'), 'wb') as f:
        f.write(lines)
    
    #Patch MinecraftApplet.java
    print('Patching MinecraftApplet.java')
    mcapplet = os.path.join(mdk, 'src', 'minecraft', 'net', 'minecraft', 'client', 'MinecraftApplet.java')
    with open(mcapplet, 'r') as f:
        lines = f.read().replace('\r\n', '\n')
    if 'this.mcThread.setPriority(10);' not in lines:
        lines = lines.replace('mcThread.start();', 'this.mcThread.setPriority(10);\n            this.mcThread.start();').replace('mcThread = new', 'this.mcThread = new').replace('this.this.', 'this.')
        with open(mcapplet, 'wb') as f:
            f.write(lines)
    
    #Update MCP
    oneone = False
    os.chdir(mdk)
    sys.path.insert(0, os.path.join(mdk, 'runtime'))
    from updatenames import updatenames
    from updatemd5 import updatemd5
    print('Updating Names')
    try:
        updatenames(None, True)
    except TypeError:
        oneone = True
        from commands import Commands, CLIENT, SERVER
        commands = Commands(None)
        commands.logger.info('== Client ==')
        commands.logger.info('> Renaming sources')
        commands.process_rename(CLIENT)
        commands.logger.info('> Creating reobfuscation tables')
        commands.renamereobsrg(CLIENT)
    print('Updating MD5')
    if not oneone:
        updatemd5(None, True)
    else:
        updatemd5(None)
    print('FoxyRetroMDK Added Applet Launcher to fix graphical issues on macOS!')