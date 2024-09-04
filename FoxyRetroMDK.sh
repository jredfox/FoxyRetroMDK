#!/bin/bash

#Take in Arguments
mc_ver="$1"
mdk_dir="$2"
if [[ "$3" == T* || "$3" == t* ]]; then
    dl_rc=false
else
    dl_rc=true
fi

#Get Script's Absolute Path
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

#Change this MC Release Version between 1.1 through 1.5.2
if [[ -z "$mc_ver" ]] 
then
	mc_ver="1.5.2"
fi

#Change the Title
echo -n -e "\033]0;Foxy Retro MDK - $mc_ver\007"

#Flag if we are on mac or linux
NAME_OS="$(uname)"
isMac=false
isLinux=false
if [ "$NAME_OS" == "Darwin" ]; then
	isMac=true
else
	isLinux=true
fi

################# Functions Start #################

function Check-Python () {
	if [[ "$isMac" == "true" ]]; then
		#Patch Python Installer bug that prevents HTTPS from working on macOS
		bash /Applications/Python*/Install\ Certificates.command > /dev/null 2>&1

		if ! command -v python2.7 &> /dev/null
		then
			echo "Python 2.7.15 Is Required to running MCP & Forge. Installing Python 2.7.15 ISA: x64"
			curl -ss -L -o "$SCRIPTPATH/python-2.7.15-macosx10.9.pkg" "https://www.python.org/ftp/python/2.7.15/python-2.7.15-macosx10.9.pkg"
			open "$SCRIPTPATH/python-2.7.15-macosx10.9.pkg"
			echo "Please re-run the script once Python has been installed"
			exit 0
		fi
        if [[ "$dl_rc" == "true" ]] && ! command -v jq &> /dev/null; then
            echo "Installing jq"
            brew install jq
            echo ""
        fi
	else
		echo "WIP LINUX"
	fi
}

#Author jredfox
#This Download-Mediafire function is free to use, copy, and distribute
function Download-Mediafire () {
    local mediafire_url="$1"
    local mediafire_file="$2"

    # Initialize variables
    local inDownloadDiv="false"
    local inputFound="false"
    local downloadLink=""
    local mediafire_html="$mediafire_file.html"

    #Download the temp HTML file
    curl -ss -o "$mediafire_html" "$mediafire_url"

    # Read the file line by line
    while IFS= read -r line; do
        # Check if the line contains the <div class="download_link">
        if [[ "$line" =~ '<div class="download_link' ]]; then
            inDownloadDiv="true"
        fi

        # If we are inside the <div> block, check for <a class="input" (with possible additional class names)
        if [[ "$inDownloadDiv" == "true" ]] && [[ "$line" =~ '<a class="input' ]]; then
            inputFound="true"
        fi

        # Extract the link from href value using a regular expression
        if [[ "$inDownloadDiv" == "true" ]] && [[ "$inputFound" == "true" ]] && [[ "$line" =~ href=\"([^\"]+)\" ]]; then
            downloadLink="${BASH_REMATCH[1]}"
            break # Exit the loop once the download link is found
        fi
    done < "$mediafire_html"

    # Output the download link
    echo "Downloading file:$downloadLink"
    curl -ss -L -o "$mediafire_file" "$downloadLink"

    # Delete temp HTML file
    rm -f "$mediafire_html"

}

function Unsupported-Version {

    echo "Invalid or Unsupported MC Version $mc_ver" >&2
    exit -1
}

#cleanup previous installation attempts
function MDK-Cleanup {

if [ -d "$mdk_dir" ]; then
	read -p "The folder '$mdk_dir' already exists. Do you want to delete it and continue? (Y/N) " user_input
	if [[ "$user_input" == Y* || "$user_input" == y* ]]; then
    	rm -rf "$mdk_dir"
    else
    	exit 0
    fi
fi

}

function Patch-MDKPY {

	find "$mdk_dir" -type f -name "*.sh" | while read -r file; do
    	echo "Patching python call $(basename "$file")"
    	sed -i -e 's/python/python2.7/g' "$file"
	done
}

function Install-1.6x {

	#Start URL's
	local assets_json_url="https://launchermeta.mojang.com/v1/packages/770572e819335b6c0a053f8378ad88eda189fc14/legacy.json"
	local assets_base_url="https://resources.download.minecraft.net"
	local python_url="https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi"
	local forge_164_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.4-9.11.1.1345/forge-1.6.4-9.11.1.1345-src.zip"

	if [[ "$mc_ver" == "1.6.4" ]]; then
		mcp_ver="mcp8.11"
		mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.6.4/mcp811.zip"
		forge_url="$forge_164_url"
		mc_client_url="https://launcher.mojang.com/v1/objects/1703704407101cf72bd88e68579e3696ce733ecd/client.jar"
		mc_server_url="https://vault.omniarchive.uk/archive/java/server-release/1.6/1.6.4-201309191549.jar" #weird server jar link look into later
	elif [[ "$mc_ver" == "1.6.3" ]]; then
		mcp_ver="mcp8.09"
		mcp_url="https://archive.org/download/mcp809/mcp809.zip"
		forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.3-9.11.0.878/forge-1.6.3-9.11.0.878-src.zip"
		mc_client_url="https://launcher.mojang.com/v1/objects/f9af8a0a0fe24c891c4175a07e9473a92dc71c1a/client.jar"
		mc_server_url="https://launcher.mojang.com/v1/objects/5a4c69bdf7c4a9aa9580096805d8497ba7721e05/server.jar"
	elif [[ "$mc_ver" == "1.6.2" ]]; then
		mcp_ver="mcp8.04"
		mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.6.2/mcp804.zip"
		forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.2-9.10.0.848/forge-1.6.2-9.10.0.848-src.zip"
		mc_client_url="https://launcher.mojang.com/v1/objects/b6cb68afde1d9cf4a20cbf27fa90d0828bf440a4/client.jar"
		mc_server_url="https://launcher.mojang.com/v1/objects/01b6ea555c6978e6713e2a2dfd7fe19b1449ca54/server.jar"
	elif [[ "$mc_ver" == "1.6.1" ]]; then
		mcp_ver="mcp8.03"
		mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.6.1/mcp803.zip"
		forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.1-8.9.0.775/forge-1.6.1-8.9.0.775-src.zip"
		mc_client_url="https://launcher.mojang.com/v1/objects/17e2c28fb54666df5640b2c822ea8042250ef592/client.jar"
		mc_server_url="https://launcher.mojang.com/v1/objects/0252918a5f9d47e3c6eb1dfec02134d1374a89b4/server.jar"
    else
        Unsupported-Version
    fi

    #Cleanup Previous MDK installation
    MDK-Cleanup

    #Notify the User of Starting Forge MDK Installation
    echo "Creating Forge MDK for $mc_ver"

    #Create Dirs
    mkdir -p "$temp/forge164"
    mkdir -p "$mdk_dir/mcp/jars/versions/$mc_ver"

    #Download & Extract Forge
    curl -ss -L -o "$temp/forge.zip" "$forge_url"
    unzip -q -o "$temp/forge.zip" -d "$temp"
    mv -f "$temp/forge/"* "$mdk_dir"

    #Patch fml.py for version 1.6-1.6.3
	if [[ "$mc_ver" != "1.6.4" ]]; then
        curl -ss -L -o "$temp/forge164.zip" "$forge_164_url"
        unzip -o -q "$temp/forge164.zip" -d "$temp/forge164"
        rm -f "$mdk_dir/fml/fml.py"
		cp -f "$temp/forge164/forge/fml/fml.py" "$mdk_dir/fml/fml.py"
    fi

    #Download & Extract MCP into forge
    curl -ss -L -o "$mdk_dir/fml/$mcp_ver.zip" "$mcp_url"
    unzip -q -o "$mdk_dir/fml/$mcp_ver.zip" -d "$mdk_dir/mcp"

    #Download & Install minecraft.jar & minecraft_server.jar
    curl -ss -L -o "$mdk_dir/mcp/jars/versions/$mc_ver/${mc_ver}.jar" "$mc_client_url"
    curl -ss -L -o "$mdk_dir/mcp/jars/minecraft_server.${mc_ver}.jar" "$mc_server_url"

    # Patch fml.json
	sed -i -e 's|http:|https:|g' "$mdk_dir/fml/fml.json"

	# Patch fml.py
	sed -i -e "s|http://resources.download.minecraft.net|$assets_base_url|g" "$mdk_dir/fml/fml.py"
	sed -i -e "s|https://s3.amazonaws.com/Minecraft.Download/indexes/legacy.json|$assets_json_url|g" "$mdk_dir/fml/fml.py"

	#Remove Temp Folder
	rm -rf "$temp"

	#patch MCP & Forge python calls to python2.7 which enforces 2.7x is called and not python3+ is called
	Patch-MDKPY

	echo "Running Forge install.cmd"
	cd "$mdk_dir"
	bash "$mdk_dir/install.sh"
}

#Download Linus or OSX Natives & Extract then Install them
function DL-Natives () {

    local natives_url="$1"
    local natives_url2="$2"
    local natives_name="$3"
    local natives_name2="${natives_name%.*}2.jar"
    local uzip="$4"
    curl -L -o "$temp/$natives_name" "$natives_url"
    curl -L -o "$temp/$natives_name2" "$natives_url2"
    unzip -q -o "$temp/$natives_name" -d "$temp/natives"
    unzip -q -o "$temp/$natives_name2" -d "$temp/natives"
    rm -rf "$temp/natives/META-INF"
    pushd "$temp/natives" > /dev/null 2>&1
    #prevents openal intialization error. Comment out if an older java or macOS version is throwing a fit
    mv -f "openal.dylib" "openal.jnilib" > /dev/null 2>&1
    zip -r "$natives_name" *
    mv -f "$natives_name" "$mdk_dir/jars/bin/natives/$natives_name"
    popd > /dev/null 2>&1
    if [ "$uzip" = "true" ]; then
        unzip -q -o "$mdk_dir/jars/bin/natives/$natives_name" -d "$mdk_dir/jars/bin/natives"
    fi
    rm -f "$temp/natives/"*

}

################# End Functions   #################

#Make sure python gets installed before continuing
Check-Python

#Correct directory
mdk_dir=$(python2.7 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$mdk_dir")
if [[ "$mdk_dir" ==  "$SCRIPTPATH" ]]; then
    mdk_dir="$SCRIPTPATH/MDK-$mc_ver"
fi

#Temp Files
temp="$mdk_dir/tmp"

#Enforce JDK-8 is being used
JDK8=$("python2.7" "$SCRIPTPATH/find-jdk-8.py" | xargs)
export PATH="$JDK8:$PATH"

#Install 1.6x versions
if [[ "$mc_ver" == 1.6* ]]; then
    Install-1.6x
    exit 0
fi

#URL Start
argo_url="https://web.archive.org/web/20160305211940id_/https://files.minecraftforge.net/fmllibs/argo-small-3.2.jar"
asm_url="https://web.archive.org/web/20160305133607id_/https://files.minecraftforge.net/fmllibs/asm-all-4.1.jar"
bcprov_url="https://web.archive.org/web/20130708220724id_/http://files.minecraftforge.net/fmllibs/bcprov-jdk15on-148.jar"
guava_url="https://web.archive.org/web/20150324120717id_/https://files.minecraftforge.net/fmllibs/guava-14.0-rc3.jar"
scala_lib_url="https://web.archive.org/web/20130708223654id_/http://files.minecraftforge.net/fmllibs/scala-library.jar"
jinput_url="https://web.archive.org/web/20150608205828if_/http://s3.amazonaws.com/MinecraftDownload/jinput.jar" #This lib Requires the embedded jutils.jar version of jinput pre 1.6 launcher
lwjgl_url="https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl/2.9.0/lwjgl-2.9.0.jar"
lwjgl_util_url="https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl_util/2.9.0/lwjgl_util-2.9.0.jar"
natives_mac_url="https://libraries.minecraft.net/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-osx.jar"
natives_mac_url2="https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/2.9.0/lwjgl-platform-2.9.0-natives-osx.jar"
natives_linux_url="https://libraries.minecraft.net/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-linux.jar"
natives_linux_url2="https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/2.9.0/lwjgl-platform-2.9.0-natives-linux.jar"
natives_windows_url="https://libraries.minecraft.net/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-windows.jar"
natives_windows_url2="https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/2.9.0/lwjgl-platform-2.9.0-natives-windows.jar"

legacy_assets_url="https://launchermeta.mojang.com/v1/packages/3d8e55480977e32acd9844e545177e69a52f594b/pre-1.6.json"
resources_url="https://resources.download.minecraft.net/"
mcp72_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.3.2/mcp72.zip"

#URLS that change based upon MC Version
if [[ "$mc_ver" == "1.5.2" ]]; then
    mcp_ver="mcp751"
    mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.5.2/mcp751.zip"
    mcp_srg_url="https://web.archive.org/web/20150324115021id_/https://files.minecraftforge.net/fmllibs/deobfuscation_data_1.5.2.zip"
    forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.5.2-7.8.0.689/forge-1.5.2-7.8.0.689-src.zip" #Blackscreen on macOS "https://maven.minecraftforge.net/net/minecraftforge/forge/1.5.2-7.8.1.738/forge-1.5.2-7.8.1.738-src.zip"
    mc_url="https://launcher.mojang.com/v1/objects/465378c9dc2f779ae1d6e8046ebc46fb53a57968/client.jar"
    mc_server_url="https://launcher.mojang.com/v1/objects/f9ae3f651319151ce99a0bfad6b34fa16eb6775f/server.jar"
    forge_lib_url="https://web.archive.org/web/20160126150649id_/http://files.minecraftforge.net/fmllibs/fml_libs_dev15.zip"

elif [[ "$mc_ver" == "1.5.1" ]]; then
    mcp_ver="mcp744"
    mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.5.1/mcp744.zip"
    mcp_srg_url="https://web.archive.org/web/20160306034852if_/http://files.minecraftforge.net/fmllibs/deobfuscation_data_1.5.1.zip"
    forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.5.1-7.7.2.682/forge-1.5.1-7.7.2.682-src.zip"
    mc_url="https://launcher.mojang.com/v1/objects/047136381a552f34b1963c43304a1ad4dc0d2d8e/client.jar"
    mc_server_url="https://launcher.mojang.com/v1/objects/d07c71ee2767dabb79fb32dad8162e1b854d5324/server.jar"
    forge_lib_url="https://web.archive.org/web/20160126150649id_/http://files.minecraftforge.net/fmllibs/fml_libs_dev15.zip"

elif [[ "$mc_ver" == "1.5" ]]; then
    mcp_ver="mcp742"
    mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.5/mcp742.zip"
    mcp_srg_url="https://web.archive.org/web/20140720003820if_/http://files.minecraftforge.net/fmllibs/deobfuscation_data_1.5.zip"
    forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.5-7.7.0.598/forge-1.5-7.7.0.598-src.zip"
    mc_url="https://launcher.mojang.com/v1/objects/a3da981fc9b875a51975d8f8100cc0c201c2ce54/client.jar"
    mc_server_url="https://launcher.mojang.com/v1/objects/aedad5159ef56d69c5bcf77ed141f53430af43c3/server.jar"
    forge_lib_url="https://web.archive.org/web/20160126150649id_/http://files.minecraftforge.net/fmllibs/fml_libs_dev15.zip"

elif [[ "$mc_ver" == 1.4* ]]; then

	if [[ "$mc_ver" == "1.4.7" ]]; then
        mcp_ver="mcp726a"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.7/mcp726a.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.7-6.6.2.534/forge-1.4.7-6.6.2.534-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/53ed4b9d5c358ecfff2d8b846b4427b888287028/client.jar"
        mc_server_url="https://launcher.mojang.com/v1/objects/2f0ec8efddd2f2c674c77be9ddb370b727dec676/server.jar"
        bcprov_dev="T" #Adds bcprov_dev to forge's compile time libraries
    elif [[ "$mc_ver" == "1.4.6" ]]; then
        mcp_ver="mcp725"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.6/mcp725.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.6-6.5.0.489/forge-1.4.6-6.5.0.489-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/116758f41b32e8d1a71a4ad6236579acd724bca7/client.jar"
        mc_server_url="https://launcher.mojang.com/v1/objects/a0aeb5709af5f2c3058c1cf0dc6b110a7a61278c/server.jar"
        bcprov_dev="T" #Adds bcprov_dev to forge's compile time libraries
    elif [[ "$mc_ver" == "1.4.5" ]]; then
        mcp_ver="mcp723"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.5/mcp723.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.5-6.4.2.448/forge-1.4.5-6.4.2.448-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/7a8a963ababfec49406e1541d3a87198e50604e5/client.jar"
        mc_server_url="https://launcher.mojang.com/v1/objects/c12fd88a8233d2c517dbc8196ba2ae855f4d36ea/server.jar"
        bcprov_dev="T" #Adds bcprov_dev to forge's compile time libraries
    elif [[ "$mc_ver" == "1.4.4" ]]; then
        mcp_ver="mcp721"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.4/mcp721.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.4-6.3.0.378/forge-1.4.4-6.3.0.378-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/b9b2a9e9adf1bc834647febc93a4222b4fd6e403/client.jar"
        mc_server_url="https://launcher.mojang.com/v1/objects/4215dcadb706508bf9d6d64209a0080b9cee9e71/server.jar"
    elif [[ "$mc_ver" == "1.4.3" ]]; then
        mcp_ver="mcp721"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.4/mcp721.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.3-6.2.1.358/forge-1.4.3-6.2.1.358-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/f7274b201219b5729055bf85683eb6ef4f8024b4/client.jar"
        mc_server_url="https://launcher.mojang.com/v1/objects/9be68adf6e80721975df12f2445fa24617328d18/server.jar"
    elif [[ "$mc_ver" == "1.4.2" ]]; then
        mcp_ver="mcp719"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.2/mcp719.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.2-6.0.1.355/forge-1.4.2-6.0.1.355-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/42d6744cfbbd2958f9e6688dd6e78d86d658d0d4/client.jar"
        mc_server_url="https://launcher.mojang.com/v1/objects/5be700523a729bb78ef99206fb480a63dcd09825/server.jar"
    elif [[ "$mc_ver" == "1.4.1" ]]; then
        mcp_ver="mcp719"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.2/mcp719.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.1-6.0.0.329/forge-1.4.1-6.0.0.329-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/67604a9c206697032165fc067b6255e333e06275/client.jar"
        mc_server_url="https://launcher.mojang.com/v1/objects/baa4e4a7adc3dc9fbfc5ea36f0777b68c9eb7f4a/server.jar"
    elif [[ "$mc_ver" == "1.4" ]]; then
        mcp_ver="mcp719"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.2/mcp719.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.0-5.0.0.326/forge-1.4.0-5.0.0.326-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/2007097b53d3eb43b2c1f3f78caab4a4ef690c7a/client.jar"
        mc_server_url="https://launcher.mojang.com/v1/objects/9470a2bb0fcb8a426328441a01dba164fbbe52c9/server.jar"
    else
        Unsupported-Version
    fi

    patch_21="T" #patch forge's code to compile using java 7 or newer
    forge_lib_url="https://web.archive.org/web/20130305145719if_/http://files.minecraftforge.net/fmllibs/fml_libs_dev.zip"
    #Older then 1.5 Forge Uses Older Runtime Libraries
    argo_url="https://web.archive.org/web/20130313100037if_/http://files.minecraftforge.net:80/fmllibs/argo-2.25.jar"
    asm_url="https://web.archive.org/web/20130313081705if_/http://files.minecraftforge.net:80/fmllibs/asm-all-4.0.jar"
    bcprov_url="https://web.archive.org/web/20130322004354if_/http://files.minecraftforge.net:80/fmllibs/bcprov-jdk15on-147.jar"
    guava_url="https://web.archive.org/web/20130313081716if_/http://files.minecraftforge.net:80/fmllibs/guava-12.0.1.jar"
    scala_lib_url=""
    mcp_srg_url="" #MCP_SRG doesn't exist pre 1.5

elif [[ "$mc_ver" == "1.3.2" ]]; then
    mcp_ver="mcp72"
    mcp_url="$mcp72_url"
    forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.3.2-4.3.5.318/forge-1.3.2-4.3.5.318-src.zip"
    mc_url="https://launcher.mojang.com/v1/objects/c2efd57c7001ddf505ca534e54abf3d006e48309/client.jar"
    mc_server_url="https://launcher.mojang.com/v1/objects/3de2ae6c488135596e073a9589842800c9f53bfe/server.jar"
    forge_lib_url="https://web.archive.org/web/20130305145719if_/http://files.minecraftforge.net/fmllibs/fml_libs_dev.zip"
    
    #Older then 1.5 Forge Uses Older Runtime Libraries
    argo_url="https://web.archive.org/web/20130313100037if_/http://files.minecraftforge.net:80/fmllibs/argo-2.25.jar"
    asm_url="https://web.archive.org/web/20130313081705if_/http://files.minecraftforge.net:80/fmllibs/asm-all-4.0.jar"
    bcprov_url="" #not required below 1.4
    guava_url="https://web.archive.org/web/20130313081716if_/http://files.minecraftforge.net:80/fmllibs/guava-12.0.1.jar"
    scala_lib_url=""
    mcp_srg_url="" #MCP_SRG doesn't exist pre 1.5

elif [[ "$mc_ver" == 1.2* ]]; then
    #Works Mc Forge 1.2.5-3.2.5.125+ Older versions require an older method that involves also downloading mod loader
    if [[ "$mc_ver" == "1.2.5" ]]; then
        mcp_ver="mcp62"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.2.5/mcp62.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.2.5-3.3.8.164/forge-1.2.5-3.3.8.164-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/4a2fac7504182a97dcbcd7560c6392d7c8139928/client.jar"
        mc_server_url="https://launcher.mojang.com/v1/objects/d8321edc9470e56b8ad5c67bbd16beba25843336/server.jar"
    elif [[ "$mc_ver" == "1.2.4" ]]; then
        mcp_ver="mcp61"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.2.4/mcp61.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.2.4-2.0.0.68/forge-1.2.4-2.0.0.68-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/ad6d1fe7455857269d4185cb8f24e62cc0241aaf/client.jar"
        mc_server_url="http://files.betacraft.uk/server-archive/release/1.2/1.2.4.jar"
        modloader_url="https://www.mediafire.com/file/rgzgdnjm3ozlnsb/ModLoader_1.2.4.zip"
   elif [[ "$mc_ver" == "1.2.3" ]]; then
        mcp_ver="mcp60"
        mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.2.3/mcp60.zip"
        forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.2.3-1.3.4.34/forge-1.2.3-1.3.4.34-src.zip"
        mc_url="https://launcher.mojang.com/v1/objects/5134e433afeba375c00bbdcd8aead1d3222813ee/client.jar"
        mc_server_url="http://files.betacraft.uk/server-archive/release/1.2/1.2.3.jar"
        modloader_url="https://www.mediafire.com/file/t93tjpkjae5u7if/ModLoader+1.2.3.zip"
    else
        Unsupported-Version
    fi
    
    #1.2.5 and below Require no Forge Runtime Libraries but do require compile time libraries?
    forge_lib_url="https://web.archive.org/web/20130305145719if_/http://files.minecraftforge.net/fmllibs/fml_libs_dev.zip"
    argo_url=""
    asm_url=""
    bcprov_url=""
    guava_url=""
    scala_lib_url=""
    mcp_srg_url=""

    fernflower_dl="T"  #Enable Fernflower Download From newer MCP
    server_skip="T" #Skip Forge Servers in versions less then 1.3 as forge never fully supported servers until 1.3 when they were forced to support it

elif [[ "$mc_ver" == "1.1" ]]; then
    if [[ "$isMac" == "true" ]]; then
        echo "MCP + Forge Installation Scripts for Minecraft 1.1 do not work on macOS Please use Windows for this version :("
        exit -1
    fi
    mcp_ver="mcp56"
    mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.1.0/mcp56.zip"
    forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.1-1.3.4.29/forge-1.1-1.3.4.29-src.zip"
    mc_url="https://launcher.mojang.com/v1/objects/f690d4136b0026d452163538495b9b0e8513d718/client.jar"
    mc_server_url="http://files.betacraft.uk/server-archive/release/1.1/1.1.jar"
    #Mod loader is a dep of forge for 1.1
    modloader_url="https://www.mediafire.com/file/wby6ddco9velug4/ModLoader+1.1.zip"

    #1.2.5 and below Require no Forge Runtime Libraries but do require compile time libraries?
    forge_lib_url="https://web.archive.org/web/20130305145719if_/http://files.minecraftforge.net/fmllibs/fml_libs_dev.zip"
    argo_url=""
    asm_url=""
    bcprov_url=""
    guava_url=""
    scala_lib_url=""
    mcp_srg_url=""

    fernflower_dl="T"  #Enable Fernflower Download From newer MCP
    server_skip="T" #Skip Forge Servers in versions less then 1.3 as forge never fully supported servers until 1.3 when they were forced to support it
else
    Unsupported-Version
fi

echo "Creating Forge MDK for $mc_ver"

#Cleanup previous installations
MDK-Cleanup

#Create Directories
mkdir -p "$temp/natives"
mkdir -p "$mdk_dir/jars/lib"
mkdir -p "$mdk_dir/jars/bin/natives"

#Download & Extract MCP
curl -L -o "$temp/$mcp_ver.zip" "$mcp_url"
unzip -q -o "$temp/$mcp_ver.zip" -d "$mdk_dir"
#Download FernFlower for MCP 1.1-1.2.5 Forge
if [[ "$fernflower_dl" == "T" ]]; then
    curl -ss -L -o "$temp/mcp72.zip" "$mcp72_url"
    unzip -q -o "$temp/mcp72.zip" -d "$temp/mcp72"
    cp -f "$temp/mcp72/runtime/bin/fernflower.jar" "$mdk_dir/runtime/bin/fernflower.jar"
fi

#Download & Extract Forge Source
curl -L -o "$temp/forge.zip" "$forge_url"
unzip -q -o "$temp/forge.zip" -d "$mdk_dir"

#patch MCP & Forge python calls to python2.7 which enforces 2.7x is called and not python3+ is called
Patch-MDKPY

#Download Forge lib Folder and Install it
curl -L -o "$temp/forge_lib.zip" "$forge_lib_url"
unzip -q -o "$temp/forge_lib.zip" -d "$mdk_dir/lib"
if [[ "$bcprov_dev" == "T" ]]; then
    curl -L -o "${mdk_dir}/lib/$(basename "$bcprov_url")" "$bcprov_url"
fi

#Download & Install Forge Runtime Libs if they Exist for this MC & Forge Version
if [[ "$argo_url" != "" ]]; then
    curl -ss -L -o "${mdk_dir}/jars/lib/$(basename "$argo_url")" "$argo_url"
fi
if [[ "$asm_url" != "" ]]; then
	curl -ss -L -o "${mdk_dir}/jars/lib/$(basename "$asm_url")" "$asm_url"
fi
if [[ "$bcprov_url" != "" ]]; then
	curl -ss -L -o "${mdk_dir}/jars/lib/$(basename "$bcprov_url")" "$bcprov_url"
fi
if [[ "$mcp_srg_url" != "" ]]; then
    curl -ss -L -o "${mdk_dir}/jars/lib/$(basename "$mcp_srg_url")" "$mcp_srg_url"
fi
if [[ "$guava_url" != "" ]]; then
    curl -ss -L -o "${mdk_dir}/jars/lib/$(basename "$guava_url")" "$guava_url"
fi
if [[ "$scala_lib_url" != "" ]]; then
    curl -ss -L -o "${mdk_dir}/jars/lib/$(basename "$scala_lib_url")" "$scala_lib_url"
fi

#Download minecraft.jar & minecraft_server.jar and Install it
curl -ss -L -o "$mdk_dir/jars/bin/minecraft.jar" "$mc_url"
if [[ "$server_skip" != "T" ]]; then
    curl -ss -L -o "$mdk_dir/jars/minecraft_server.jar" "$mc_server_url"
fi

#Download and install Modloader for 1.1 - 1.2.4 as Forge requires Modloader in these versions
if [ -n "$modloader_url" ]; then
    Download-Mediafire "$modloader_url" "$temp/modloader.zip"
    #Install Mod Loader now
    unzip -q -o "$mdk_dir/jars/bin/minecraft.jar" -d "$temp/minecraft"
    unzip -q -o "$temp/modloader.zip" -d "$temp/minecraft"
    rm -rf "$temp/minecraft/META-INF"
    rm -f "$mdk_dir/jars/bin/minecraft.jar"
    pushd "$temp/minecraft" > /dev/null 2>&1
        zip -r "minecraft.jar" * > /dev/null 2>&1
    popd > /dev/null 2>&1
    mv -f "$temp/minecraft/minecraft.jar" "$mdk_dir/jars/bin/minecraft.jar"
fi

#Download Minecraft Bin Libs
curl -L -o "$mdk_dir/jars/bin/jinput.jar" "$jinput_url"
curl -L -o "$mdk_dir/jars/bin/lwjgl.jar" "$lwjgl_url"
curl -L -o "$mdk_dir/jars/bin/lwjgl_util.jar" "$lwjgl_util_url"

#Download & Install the natives
DL-Natives "$natives_windows_url" "$natives_windows_url2" "windows_natives.jar" "false"
DL-Natives "$natives_mac_url" "$natives_mac_url2" "macosx_natives.jar" "$isMac"
DL-Natives "$natives_linux_url" "$natives_linux_url2" "linux_natives.jar" "$isLinux"

#Make MCP & Forge 1.4x compile with java 7 or higher
if [[ "$patch_21" == "T" ]]; then
    echo "Patching Forge's RenderPlayer.java.patch"
    patch_file="$mdk_dir/forge/patches/minecraft/net/minecraft/src/RenderPlayer.java.patch"

    if [[ ! -f "$patch_file" ]]; then
        patch_file="$mdk_dir/forge/patches/minecraft/net/minecraft/client/renderer/entity/RenderPlayer.java.patch" # Redirects Patch file between 1.4.5-1.4.7
    fi

    if [[ -f "$patch_file" ]]; then
        sed -i -e "s|for (int var27 = 0; var27 < var21.getItem().getRenderPasses(var21.getItemDamage()); ++var27)|for (int var27 = 0; var27 < var22.getItem().getRenderPasses(var22.getItemDamage()); ++var27)|g" "$patch_file"
        sed -i -e "s|for (var27 = 0; var27 < var21.getItem().getRenderPasses(var21.getItemDamage()); ++var27)|for (var27 = 0; var27 < var22.getItem().getRenderPasses(var22.getItemDamage()); ++var27)|g" "$patch_file"
    fi
fi

# Download Minecraft Resources
if [[ "$dl_rc" == "true" ]]; then
    jsonFile="$temp/assets.json"
    curl -ss -L -o "$jsonFile" "$legacy_assets_url"

    # Parse JSON & Download Resources
    appls=$(jq -c -r '.objects | to_entries[] | "\(.key),\(.value.hash)"' "${jsonFile}")
    while IFS=, read -r key hash; do
      resource="$resources_url${hash:0:2}/$hash"
      resource_file="$mdk_dir/jars/resources/$key"
      echo "Downloading Resource URL: $resource"

      # Create necessary directories
      rd=$(dirname "$resource_file")
      mkdir -p "$rd"

      # Download the resource file
      curl -ss -L -o "$resource_file" "$resource"
    done <<< "${appls}"
fi

#Clear the temp folder Comment out if you encounter a bug and want to see what it's done so far
rm -rf "$temp"

#Run Forge's Install Script
cd "$mdk_dir/forge"
echo "Running Forge install.sh"
bash "$mdk_dir/forge/install.sh"
echo "Forge MDK Installation Completed"
