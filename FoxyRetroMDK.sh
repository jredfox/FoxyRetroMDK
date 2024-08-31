#Take in Arguments
mc_ver=$1
mdk_dir=$2

#Get Script's Absolute Path
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
# Define global boolean-like variables
false_val=0
true_val=1

#Change this MC Release Version between 1.1 through 1.5.2
#NOTE: 1.3.2-1.4.7 requires java 7 compliance jars else forge's ASM library will throw a fit and crash
if [[ -z "$mc_ver" ]] 
then
	mc_ver="1.5.2"
fi

if [[ -z "$mdk_dir" ]] 
then
	mdk_dir="$SCRIPTPATH/MDK-$mc_ver"
fi

#Change the Title
echo -n -e "\033]0;Foxy Retro MDK - $mc_ver\007"

#Temp Files
temp="$mdk_dir/tmp"

################# Functions Start #################

#Author jredfox
#This Download-Mediafire function is free to use, copy, and distribute
function Download-Mediafire () {
	local mediafire_url="$1"
	local mediafire_file="$2"

	# Initialize variables
    local inDownloadDiv=false
    local inputFound=false
    local downloadLink=""
    local mediafire_html="$mediafire_file.html"

    #Download the temp HTML file
    curl -ss -o "$mediafire_html" "$mediafire_url"

    # Read the file line by line
	while IFS= read -r line; do
	    # Check if the line contains the <div class="download_link">
	    if [[ "$line" =~ '<div class="download_link' ]]; then
	        inDownloadDiv=true
	    fi

	    # If we are inside the <div> block, check for <a class="input" (with possible additional class names)
	    if $inDownloadDiv && [[ "$line" =~ '<a class="input' ]]; then
	        inputFound=true
	    fi

	    # Extract the link from href value using a regular expression
	    if $inDownloadDiv && $inputFound && [[ "$line" =~ href=\"([^\"]+)\" ]]; then
	        downloadLink="${BASH_REMATCH[1]}"
	        #echo "Download link found: $downloadLink"
	        break # Exit the loop once the download link is found
	    fi
	done < "$mediafire_html"

    # Output the download link
    echo "Downloading file:$downloadLink"
    curl -ss -o "$mediafire_file" "$downloadLink"

    # Delete temp HTML file
    rm -f "$mediafire_html"
}

function Create-Jar {
    local Dir="$1"
    local Jar="$2"

    local temp_cd=$(pwd)
    cd "$Path"
    echo "Creating Jar $Jar"
    jar cvf "$Jar" "."
    cd "$temp_cd"
}

function Unsupported-Version {
    echo "Invalid or Unsupported MC Version $mc_ver" >&2
    exit -1
}

#cleanup previous installation attempts
function MDK-Cleanup {

if [ -d "$mdk_dir" ]; then
	read -p "The folder '$mdk_dir' already exists. Do you want to delete it and continue? (Y/N) " user_input
	if [[ "$user_input" == "Y" || "$user_input" == "y" ]]; then
    	rm -rf "$mdk_dir"
    else
    	exit 0
    fi
fi

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
		mcp_ver = "mcp8.09"
		mcp_url="https://archive.org/download/mcp809/mcp809.zip"
		forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.3-9.11.0.878/forge-1.6.3-9.11.0.878-src.zip"
		mc_client_url="https://launcher.mojang.com/v1/objects/f9af8a0a0fe24c891c4175a07e9473a92dc71c1a/client.jar"
		mc_server_url="https://launcher.mojang.com/v1/objects/5a4c69bdf7c4a9aa9580096805d8497ba7721e05/server.jar"
	elif [[ "$mc_ver" == "1.6.2" ]]; then
		mcp_ver = "mcp8.04"
		mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.6.2/mcp804.zip"
		forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.2-9.10.0.848/forge-1.6.2-9.10.0.848-src.zip"
		mc_client_url="https://launcher.mojang.com/v1/objects/b6cb68afde1d9cf4a20cbf27fa90d0828bf440a4/client.jar"
		mc_server_url="https://launcher.mojang.com/v1/objects/01b6ea555c6978e6713e2a2dfd7fe19b1449ca54/server.jar"
	elif [[ "$mc_ver" == "1.6.1" ]]; then
		mcp_ver = "mcp8.03"
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
    curl -o "$temp/forge.zip" "$forge_url"
    unzip -o -q "$temp/forge.zip" -d "$temp"
    mv -f "$temp/forge/"* "$mdk_dir"
    #Move-Item -Path "$temp\forge\*" -Destination "$mdk_dir" -Force | out-null
}

################# End Functions   #################

if [[ "$mc_ver" == 1.6* ]]; then
    Install-1.6x
    exit 0
fi
#Download-Mediafire "http://www.mediafire.com/file/rgzgdnjm3ozlnsb/ModLoader_1.2.4.zip" "/Users/jredfox/Documents/GitHub/FoxyRetroMDK/Modloader.zip"

