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
	echo Hello World
}

################# End Functions   #################

if [[ "$mc_ver" == 1.6* ]]; then
    Install-1.6x
    exit 0
fi
#Download-Mediafire "http://www.mediafire.com/file/rgzgdnjm3ozlnsb/ModLoader_1.2.4.zip" "/Users/jredfox/Documents/GitHub/FoxyRetroMDK/Modloader.zip"

