# FoxyRetroMDK
 Setup MCP + Forge Legacy MDK Versions 1.1 - 1.6.4 Working in 2024 :)

 # How to use windows
 * download & install JDK 8 with JDK 8 being first in your path
 * extract zip to "FoxyRetroMDK"
 * double click FoxyRetroMDK.cmd
 * enter the minecraft version
 * link eclipse to the MDK/eclipse for 1.5.2 or lower and MDK/mcp/eclipse for 1.6x
 * Newer Eclipse's right click --> project --> properties --> java build path --> libraries --> select use alternative JDK --> select JDK 8

# How to use mac and linux
 * download & install JDK 8 with JDK 8 being first in your path
 * extract zip to "FoxyRetroMDK"
 * open terminal and run these commands `cd FoxyRetroMDK` (linux only: `sudo bash Install-Linux-Deps.sh`)
 * run `bash FoxyRetroMDK.sh "mc_version"` replacing mc_version with what you need
 * link eclipse to the MDK/eclipse for 1.5.2 or lower and MDK/mcp/eclipse for 1.6x
 * Newer Eclipse's right click --> project --> properties --> java build path --> libraries --> select use alternative JDK --> select JDK 8

# MDK's Portability
* Linux --> Mac
* Linux --> Windows
* Windows --> Mac
* Mac --> Windows

Since Linux Has Additional Deps that are only created When Installing an MDK on Linux It's not Possible to Move an MDK over to linux without copying "bin_linux" Folder over to your MDK first

# Changing Java Notes
Changing Java on an MDK that's already been compiled from an Upgrade Java 6 --> Java 7 or a downgrade Java 8 --> Java 7 Will Cause MCP to think every single class is modified when calling `reobfuscate` or `reobfuscate_srg`. **This is a limition of MCP not handling proper detection for modified classes**. First Step is to go into `cache/jdkfinder-target.cfg` and change the target to the desired java version. Now in order to Get around it you **MUST backup your src** folder and **copy it to a location outside the MDK**. Then you can go and run forge/install.cmd or forge/install.sh (non windows) for 1.5.2 and lower or the MDK/install.sh for 1.6x. This will re-install forge wipe your MDK and update the MD5's. Replace the src folder back with your current modding workspace and MCP should detect what classes are actually modified again
