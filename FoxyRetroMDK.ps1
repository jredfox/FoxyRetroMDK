param(
	[string]$mc_ver,
	[string]$mdk_dir,
	[string]$skip_rc
)

#import C# zip tools
Add-Type -AssemblyName 'System.IO.Compression.FileSystem'

& {

#Change this MC Release Version between 1.1 through 1.5.2
if ([string]::IsNullOrEmpty($mc_ver)) 
{
    $mc_ver = "1.5.2"
}

#Set the mcp(MDK) dir
if ([string]::IsNullOrEmpty($mdk_dir) -Or ([System.IO.Path]::GetFullPath("$mdk_dir") -eq "$PSScriptRoot")) 
{
    $mdk_dir = "$PSScriptRoot\MDK-$mc_ver"
}

#Set the title
$host.ui.RawUI.WindowTitle = "Foxy Retro MDK - $mc_ver"

#Temp Files
$temp = "$mdk_dir\tmp"

#Resource URLS
$resources_json_url = "https://launchermeta.mojang.com/v1/packages/3d8e55480977e32acd9844e545177e69a52f594b/pre-1.6.json"
$assets_json_url = "https://launchermeta.mojang.com/v1/packages/770572e819335b6c0a053f8378ad88eda189fc14/legacy.json"
$resources_url = "https://resources.download.minecraft.net/"

################# Functions Start #################

#Author jredfox
#This Download-Mediafire function is free to use, copy, and distribute
function Download-Mediafire {
    param (
        [string]$mediafire_url,         # The URL to download from
        [string]$mediafire_file     # The local file path to save the file
    )

    # Initialize variables
    $inDownloadDiv = $false
    $inputFound = $false
    $downloadLink = ""
    $mediafire_html = "$mediafire_file.html"

    #Download the temp HTML file
    Invoke-WebRequest -Uri "$mediafire_url" -OutFile "$mediafire_html"
    $lines = Get-Content "$mediafire_html" #Parse Lines

    # Loop through each line of the file
    foreach ($line in $lines) {
        # Check if the line contains the <div class="download_link">
        if ($line -match '<div class="download_link') {
            $inDownloadDiv = $true
        }

        # If we are inside the <div> block, check for <a class="input" (with possible additional class names)
        if ($inDownloadDiv -and $line -match '<a class="[^"]*input[^"]*"') {
            $inputFound = $true
        }

        # Extract the link from href value using a regular expression
        if ($inDownloadDiv -and $inputFound -and $line -match 'href="([^"]+)"') {
            $downloadLink = $matches[1]
            break # Exit the loop once the download link is found
        }
    }

    # Output the download link
    Write-Output "Download file:$downloadLink"
    Invoke-WebRequest -Uri "$downloadLink" -OutFile "$mediafire_file"

    # Delete temp HTML file
    Remove-Item -Path "$mediafire_html" -Force -ErrorAction SilentlyContinue
 }

function Create-Jar {
    param (
        [string]$Path,         # The Path of the root directory of the classes
        [string]$Jar     # The Path of the Jar file to save it as.
    )

    $temp_cd = Get-Location
    Set-Location "$Path"
    Write-Host "Creating Jar $Jar"
    & "jar" cvf "$Jar" "."
    Set-Location "$temp_cd"
}

function Unsupported-Version {
    Write-Error "Invalid or Unsupported MC Version $mc_ver"
    exit -1
}

#cleanup previous installation attempts
function MDK-Cleanup {

if ([System.IO.Directory]::Exists("$mdk_dir")) {
    $shouldStop = Read-Host "The folder '$mdk_dir' already exists. Do you want to delete it and continue? (Y/N)"
    if ($shouldStop.StartsWith('Y') -or $shouldStop.StartsWith('y')) {
        [System.IO.Directory]::Delete("$mdk_dir", $true)
    }
    else {
        exit 0
    }
}

}

#Download Minecraft Resources
function DL-Resources {
    param (
        [string]$JsonURL,
        [string]$Resources
    )

#Skip Resource Downloading if it's enabled
if($skip_rc -like "T*") {
    Write-Host "Skipping Resource Downloading"
    return
}

$progress_org = "$ProgressPreference"
$ProgressPreference = 'SilentlyContinue'
try
{
    $jsonFile = "$temp/assets.json"
    Invoke-WebRequest -Uri "$JsonURL" -OutFile "$jsonFile"
    $jsonData = Get-Content -Path "$jsonFile" -Raw | ConvertFrom-Json
    $objects = $jsonData.objects
    foreach ($key in $objects.PSObject.Properties.Name) 
    {
        $hash = $objects.$key.hash
        $resource = $resources_url + $hash.Substring(0, 2) + "/$hash"
        $resource_file = "$Resources\$key"
        Write-Output "Downloading Resource URL:$resource"
        $rd = Split-Path "$resource_file" -Parent #build resource directory path
        New-Item -Path "$rd" -ItemType "directory" -Force | out-null #create resource directories if required
        Invoke-WebRequest -Uri "$resource" -OutFile "$resource_file"
    }
}
catch
{
    Write-Error "An Error Occured Obtaining Minecraft Resources Please manually Download and insert them into $Resources"
}
$ProgressPreference = "$progress_org"

}

function Install-1.6x {
    
    #Start URL's
	$assets_base_url="https://resources.download.minecraft.net"
	$python_url="https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi"
	$forge_164_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.4-9.11.1.1345/forge-1.6.4-9.11.1.1345-src.zip"

	if($mc_ver -eq "1.6.4"){
		$mcp_ver = "mcp8.11"
		$mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.6.4/mcp811.zip"
		$forge_url="$forge_164_url"
		$mc_client_url="https://launcher.mojang.com/v1/objects/1703704407101cf72bd88e68579e3696ce733ecd/client.jar"
		$mc_server_url="https://vault.omniarchive.uk/archive/java/server-release/1.6/1.6.4-201309191549.jar" #weird server jar link look into later
	}
	elseif($mc_ver -eq "1.6.3"){
		$mcp_ver = "mcp8.09"
		$mcp_url="https://archive.org/download/mcp809/mcp809.zip"
		$forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.3-9.11.0.878/forge-1.6.3-9.11.0.878-src.zip"
		$mc_client_url="https://launcher.mojang.com/v1/objects/f9af8a0a0fe24c891c4175a07e9473a92dc71c1a/client.jar"
		$mc_server_url="https://launcher.mojang.com/v1/objects/5a4c69bdf7c4a9aa9580096805d8497ba7721e05/server.jar"
	}
	elseif($mc_ver -eq "1.6.2"){
		$mcp_ver = "mcp8.04"
		$mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.6.2/mcp804.zip"
		$forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.2-9.10.0.848/forge-1.6.2-9.10.0.848-src.zip"
		$mc_client_url="https://launcher.mojang.com/v1/objects/b6cb68afde1d9cf4a20cbf27fa90d0828bf440a4/client.jar"
		$mc_server_url="https://launcher.mojang.com/v1/objects/01b6ea555c6978e6713e2a2dfd7fe19b1449ca54/server.jar"
	}
	elseif($mc_ver -eq "1.6.1"){
		$mcp_ver = "mcp8.03"
		$mcp_url="https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.6.1/mcp803.zip"
		$forge_url="https://maven.minecraftforge.net/net/minecraftforge/forge/1.6.1-8.9.0.775/forge-1.6.1-8.9.0.775-src.zip"
		$mc_client_url="https://launcher.mojang.com/v1/objects/17e2c28fb54666df5640b2c822ea8042250ef592/client.jar"
		$mc_server_url="https://launcher.mojang.com/v1/objects/0252918a5f9d47e3c6eb1dfec02134d1374a89b4/server.jar"
	}
    else {
        Unsupported-Version
    }

    #Cleanup Previous MDK installation
    MDK-Cleanup

    #Notify the User of Starting Forge MDK Installation
    Write-Host "Creating Forge MDK for $mc_ver"

    #Create Dirs
    New-Item -Path "$temp\forge164" -ItemType "directory" -Force | out-null
    New-Item -Path "$mdk_dir\mcp\jars\versions\$mc_ver" -ItemType "directory" -Force | out-null

    #Download & Extract Forge
    Invoke-WebRequest "$forge_url" -OutFile "$temp\forge.zip"
    [System.IO.Compression.ZipFile]::ExtractToDirectory("$temp\forge.zip", $temp)
    Move-Item -Path "$temp\forge\*" -Destination "$mdk_dir" -Force | out-null

    #Patch fml.py for version 1.6-1.6.3
    if($mc_ver -ne "1.6.4")
    {
        Invoke-WebRequest "$forge_164_url" -OutFile "$temp\forge164.zip"
		[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp\forge164.zip", "$temp\forge164")
        Remove-Item -Path "$mdk_dir\fml\fml.py" -Force | out-null
		Copy-Item -Path "$temp\forge164\forge\fml\fml.py" -Destination "$mdk_dir\fml\fml.py" -Force | out-null
    }

    #Download & Extract MCP into forge
    Invoke-WebRequest "$mcp_url" -OutFile "$mdk_dir\fml\$mcp_ver.zip"
    [System.IO.Compression.ZipFile]::ExtractToDirectory("$mdk_dir\fml\$mcp_ver.zip", "$mdk_dir\mcp")

    #Download & Install minecraft.jar & minecraft_server.jar
    Invoke-WebRequest "$mc_client_url" -OutFile "$mdk_dir\mcp\jars\versions\$mc_ver\$mc_ver.jar"
    Invoke-WebRequest "$mc_server_url" -OutFile "$mdk_dir\mcp\jars\minecraft_server.$mc_ver.jar"

    #Patch fml.json
    (Get-Content "$mdk_dir\fml\fml.json").replace("http:", "https:") | Set-Content "$mdk_dir\fml\fml.json"
    
    #Patch fml.py
	(Get-Content "$mdk_dir\fml\fml.py").replace("http://resources.download.minecraft.net", "$assets_base_url").replace("https://s3.amazonaws.com/Minecraft.Download/indexes/legacy.json", "$assets_json_url") | Set-Content "$mdk_dir\fml\fml.py"

    #Upgrade python to 2.7.9 x86(runs on x64 and arm64 windows) to support HTTPS
    Write-Host "Upgrading Forge's python to 2.7.9 ISA: x86"
	Remove-Item -Path "$mdk_dir\fml\python\*" -Force | out-null
	Invoke-WebRequest "$python_url" -OutFile "$temp\python.msi"
	Start-process msiexec -ArgumentList "/a `"$temp\python.msi`" /qn TARGETDIR=`"$temp\python`"" -Wait
	Move-Item -Path "$temp\python\DLLs\*" -Destination "$mdk_dir\fml\python\" -Force | out-null
	Move-Item -Path "$temp\python\python27.dll" -Destination "$mdk_dir\fml\python\" -Force | out-null
	Move-Item -Path "$temp\python\python.exe" -Destination "$mdk_dir\fml\python\python_fml.exe" -Force | out-null
	Compress-Archive -Path "$temp\python\Lib\*" -DestinationPath "$temp\python27.zip"
	Move-Item -Path "$temp\python27.zip" -Destination "$mdk_dir\fml\python\" -Force | out-null

    #Download Resources to as powershell does it 3-5x faster then 1.6x's method
    DL-Resources -JsonURL "$assets_json_url" -Resources "$mdk_dir\mcp\jars\assets"

    #Clear the Temp Folder
	Remove-Item -Path "$temp" -Recurse -Force | out-null

    #Start Forge install.cmd
    Write-Host "Running Forge install.cmd"
	Set-Location -Path "$mdk_dir"
	Start-Process -FilePath "$mdk_dir\install.cmd" -Wait -NoNewWindow
}

function DL-Natives
{
    param (
        [string]$URL,
        [string]$URL2,
        [string]$FileName,
        [string]$uzip
    )

    Invoke-WebRequest -Uri "$URL" -OutFile "$temp/$FileName.jar"
    Invoke-WebRequest -Uri "$URL2" -OutFile "$temp/$FileName`2.jar"
    [System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/$FileName.jar", "$temp/natives")
    [System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/$FileName`2.jar", "$temp/natives")
    [System.IO.Compression.ZipFile]::CreateFromDirectory("$temp/natives", "$mdk_dir/jars/bin/natives/$FileName.jar") # Re-Zips the natives and installs it to the correct
    #Unzip Windows Natives
    if ($uzip -eq "T") {
        [System.IO.Compression.ZipFile]::ExtractToDirectory("$mdk_dir/jars/bin/natives/$FileName.jar", "$mdk_dir/jars/bin/natives") # Un-Zips all Windows Natives to the correct location
    }
    #Cleanup When Done
    Remove-Item "$temp\natives\*" -Recurse -Force
}

################# End Functions   #################

if ($mc_ver.StartsWith("1.6")) 
{
    Install-1.6x
    exit 0
}

#URL Start
$argo_url = "https://web.archive.org/web/20160305211940id_/https://files.minecraftforge.net/fmllibs/argo-small-3.2.jar"
$asm_url = "https://web.archive.org/web/20160305133607id_/https://files.minecraftforge.net/fmllibs/asm-all-4.1.jar"
$bcprov_url = "https://web.archive.org/web/20130708220724id_/http://files.minecraftforge.net/fmllibs/bcprov-jdk15on-148.jar"
$guava_url = "https://web.archive.org/web/20150324120717id_/https://files.minecraftforge.net/fmllibs/guava-14.0-rc3.jar"
$scala_lib_url = "https://web.archive.org/web/20130708223654id_/http://files.minecraftforge.net/fmllibs/scala-library.jar"
$jinput_url = "https://web.archive.org/web/20150608205828if_/http://s3.amazonaws.com/MinecraftDownload/jinput.jar" #This lib Requires the embedded jutils.jar version of jinput pre 1.6 launcher
$lwjgl_url = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl/2.9.0/lwjgl-2.9.0.jar"
$lwjgl_util_url = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl_util/2.9.0/lwjgl_util-2.9.0.jar"
#Native URLS
$natives_mac_url="https://libraries.minecraft.net/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-osx.jar"
$natives_mac_url2="https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/2.9.0/lwjgl-platform-2.9.0-natives-osx.jar"
$natives_linux_url="https://libraries.minecraft.net/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-linux.jar"
$natives_linux_url2="https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/2.9.0/lwjgl-platform-2.9.0-natives-linux.jar"
$natives_windows_url="https://libraries.minecraft.net/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-windows.jar"
$natives_windows_url2="https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/2.9.0/lwjgl-platform-2.9.0-natives-windows.jar"
$mcp72_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.3.2/mcp72.zip"
#URLS that change based upon MC Version
if ($mc_ver -eq "1.5.2")
{
    $mcp_ver = "mcp751"
    $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.5.2/$mcp_ver.zip"
    $mcp_srg_url = "https://web.archive.org/web/20150324115021id_/https://files.minecraftforge.net/fmllibs/deobfuscation_data_1.5.2.zip"
    $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.5.2-7.8.1.738/forge-1.5.2-7.8.1.738-src.zip"
    $mc_url = "https://launcher.mojang.com/v1/objects/465378c9dc2f779ae1d6e8046ebc46fb53a57968/client.jar"
    $mc_server_url = "https://launcher.mojang.com/v1/objects/f9ae3f651319151ce99a0bfad6b34fa16eb6775f/server.jar"
    $forge_lib_url = "https://web.archive.org/web/20160126150649id_/http://files.minecraftforge.net/fmllibs/fml_libs_dev15.zip"
}
elseif ($mc_ver -eq "1.5.1")
{
    $mcp_ver = "mcp744"
    $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.5.1/mcp744.zip"
    $mcp_srg_url = "https://web.archive.org/web/20160306034852if_/http://files.minecraftforge.net/fmllibs/deobfuscation_data_1.5.1.zip"
    $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.5.1-7.7.2.682/forge-1.5.1-7.7.2.682-src.zip"
    $mc_url = "https://launcher.mojang.com/v1/objects/047136381a552f34b1963c43304a1ad4dc0d2d8e/client.jar"
    $mc_server_url = "https://launcher.mojang.com/v1/objects/d07c71ee2767dabb79fb32dad8162e1b854d5324/server.jar"
    $forge_lib_url = "https://web.archive.org/web/20160126150649id_/http://files.minecraftforge.net/fmllibs/fml_libs_dev15.zip"
}
elseif ($mc_ver -eq "1.5")
{
    $mcp_ver = "mcp742"
    $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.5/mcp742.zip"
    $mcp_srg_url = "https://web.archive.org/web/20140720003820if_/http://files.minecraftforge.net/fmllibs/deobfuscation_data_1.5.zip"
    $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.5-7.7.0.598/forge-1.5-7.7.0.598-src.zip"
    $mc_url = "https://launcher.mojang.com/v1/objects/a3da981fc9b875a51975d8f8100cc0c201c2ce54/client.jar"
    $mc_server_url = "https://launcher.mojang.com/v1/objects/aedad5159ef56d69c5bcf77ed141f53430af43c3/server.jar"
    $forge_lib_url = "https://web.archive.org/web/20160126150649id_/http://files.minecraftforge.net/fmllibs/fml_libs_dev15.zip"
}
elseif ($mc_ver.StartsWith("1.4"))
{
    if ($mc_ver -eq "1.4.7")
    {
        $mcp_ver = "mcp726a"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.7/mcp726a.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.7-6.6.2.534/forge-1.4.7-6.6.2.534-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/53ed4b9d5c358ecfff2d8b846b4427b888287028/client.jar"
        $mc_server_url = "https://launcher.mojang.com/v1/objects/2f0ec8efddd2f2c674c77be9ddb370b727dec676/server.jar"
        $bcprov_dev = "T" #Adds bcprov_dev to forge's compile time libraries
    }
    elseif ($mc_ver -eq "1.4.6")
    {
        $mcp_ver = "mcp725"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.6/mcp725.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.6-6.5.0.489/forge-1.4.6-6.5.0.489-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/116758f41b32e8d1a71a4ad6236579acd724bca7/client.jar"
        $mc_server_url = "https://launcher.mojang.com/v1/objects/a0aeb5709af5f2c3058c1cf0dc6b110a7a61278c/server.jar"
        $bcprov_dev = "T" #Adds bcprov_dev to forge's compile time libraries
    }
    elseif ($mc_ver -eq "1.4.5")
    {
        $mcp_ver = "mcp723"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.5/mcp723.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.5-6.4.2.448/forge-1.4.5-6.4.2.448-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/7a8a963ababfec49406e1541d3a87198e50604e5/client.jar"
        $mc_server_url = "https://launcher.mojang.com/v1/objects/c12fd88a8233d2c517dbc8196ba2ae855f4d36ea/server.jar"
        $bcprov_dev = "T" #Adds bcprov_dev to forge's compile time libraries
    }
    elseif ($mc_ver -eq "1.4.4")
    {
        $mcp_ver = "mcp721"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.4/mcp721.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.4-6.3.0.378/forge-1.4.4-6.3.0.378-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/b9b2a9e9adf1bc834647febc93a4222b4fd6e403/client.jar"
        $mc_server_url = "https://launcher.mojang.com/v1/objects/4215dcadb706508bf9d6d64209a0080b9cee9e71/server.jar"
    }
    elseif ($mc_ver -eq "1.4.3")
    {
        $mcp_ver = "mcp721"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.4/mcp721.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.3-6.2.1.358/forge-1.4.3-6.2.1.358-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/f7274b201219b5729055bf85683eb6ef4f8024b4/client.jar"
        $mc_server_url = "https://launcher.mojang.com/v1/objects/9be68adf6e80721975df12f2445fa24617328d18/server.jar"
    }
    elseif ($mc_ver -eq "1.4.2")
    {
        $mcp_ver = "mcp719"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.2/mcp719.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.2-6.0.1.355/forge-1.4.2-6.0.1.355-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/42d6744cfbbd2958f9e6688dd6e78d86d658d0d4/client.jar"
        $mc_server_url = "https://launcher.mojang.com/v1/objects/5be700523a729bb78ef99206fb480a63dcd09825/server.jar"
    }
    elseif ($mc_ver -eq "1.4.1")
    {
        $mcp_ver = "mcp719"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.2/mcp719.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.1-6.0.0.329/forge-1.4.1-6.0.0.329-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/67604a9c206697032165fc067b6255e333e06275/client.jar"
        $mc_server_url = "https://launcher.mojang.com/v1/objects/baa4e4a7adc3dc9fbfc5ea36f0777b68c9eb7f4a/server.jar"
    }
    elseif ($mc_ver -eq "1.4")
    {
        $mcp_ver = "mcp719"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.4.2/mcp719.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.4.0-5.0.0.326/forge-1.4.0-5.0.0.326-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/2007097b53d3eb43b2c1f3f78caab4a4ef690c7a/client.jar"
        $mc_server_url = "https://launcher.mojang.com/v1/objects/9470a2bb0fcb8a426328441a01dba164fbbe52c9/server.jar"
    }
    else
    {
        Unsupported-Version
    }
    
    $patch_21 = "T" #patch forge's code to compile using java 7 or newer
    $forge_lib_url = "https://web.archive.org/web/20130305145719if_/http://files.minecraftforge.net/fmllibs/fml_libs_dev.zip"
    #Older then 1.5 Forge Uses Older Runtime Libraries
    $argo_url = "https://web.archive.org/web/20130313100037if_/http://files.minecraftforge.net:80/fmllibs/argo-2.25.jar"
    $asm_url = "https://web.archive.org/web/20130313081705if_/http://files.minecraftforge.net:80/fmllibs/asm-all-4.0.jar"
    $bcprov_url = "https://web.archive.org/web/20130322004354if_/http://files.minecraftforge.net:80/fmllibs/bcprov-jdk15on-147.jar"
    $guava_url = "https://web.archive.org/web/20130313081716if_/http://files.minecraftforge.net:80/fmllibs/guava-12.0.1.jar"
    $scala_lib_url = ""
    $mcp_srg_url = "" #MCP_SRG doesn't exist pre 1.5
}
elseif ($mc_ver -eq "1.3.2")
{
    $mcp_ver = "mcp72"
    $mcp_url = "$mcp72_url"
    $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.3.2-4.3.5.318/forge-1.3.2-4.3.5.318-src.zip"
    $mc_url = "https://launcher.mojang.com/v1/objects/c2efd57c7001ddf505ca534e54abf3d006e48309/client.jar"
    $mc_server_url = "https://launcher.mojang.com/v1/objects/3de2ae6c488135596e073a9589842800c9f53bfe/server.jar"
    $forge_lib_url = "https://web.archive.org/web/20130305145719if_/http://files.minecraftforge.net/fmllibs/fml_libs_dev.zip"
    
    #Older then 1.5 Forge Uses Older Runtime Libraries
    $argo_url = "https://web.archive.org/web/20130313100037if_/http://files.minecraftforge.net:80/fmllibs/argo-2.25.jar"
    $asm_url = "https://web.archive.org/web/20130313081705if_/http://files.minecraftforge.net:80/fmllibs/asm-all-4.0.jar"
    $bcprov_url = "" #not required below 1.4
    $guava_url = "https://web.archive.org/web/20130313081716if_/http://files.minecraftforge.net:80/fmllibs/guava-12.0.1.jar"
    $scala_lib_url = ""
    $mcp_srg_url = "" #MCP_SRG doesn't exist pre 1.5
}
elseif ($mc_ver.StartsWith("1.2"))
{
    #Works Mc Forge 1.2.5-3.2.5.125+ Older versions require an older method that involves also downloading mod loader
    if ($mc_ver -eq "1.2.5")
    {
        $mcp_ver = "mcp62"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.2.5/mcp62.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.2.5-3.4.9.171/forge-1.2.5-3.4.9.171-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/4a2fac7504182a97dcbcd7560c6392d7c8139928/client.jar"
        $mc_server_url = "https://launcher.mojang.com/v1/objects/d8321edc9470e56b8ad5c67bbd16beba25843336/server.jar"
    }
    elseif ($mc_ver -eq "1.2.4")
    {
        $mcp_ver = "mcp61"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.2.4/mcp61.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.2.4-2.0.0.68/forge-1.2.4-2.0.0.68-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/ad6d1fe7455857269d4185cb8f24e62cc0241aaf/client.jar"
        $mc_server_url = "http://files.betacraft.uk/server-archive/release/1.2/1.2.4.jar"
        $modloader_url = "https://www.mediafire.com/file/rgzgdnjm3ozlnsb/ModLoader_1.2.4.zip"
    }
    elseif ($mc_ver -eq "1.2.3")
    {
        $mcp_ver = "mcp60"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.2.3/mcp60.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.2.3-1.4.1.64/forge-1.2.3-1.4.1.64-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/5134e433afeba375c00bbdcd8aead1d3222813ee/client.jar"
        $mc_server_url = "http://files.betacraft.uk/server-archive/release/1.2/1.2.3.jar"
        $modloader_url = "https://www.mediafire.com/file/t93tjpkjae5u7if/ModLoader+1.2.3.zip"
    }
    else
    {
        Unsupported-Version
    }
    
    #1.2.5 and below Require no Forge Runtime Libraries but do require compile time libraries?
    $forge_lib_url = "https://web.archive.org/web/20130305145719if_/http://files.minecraftforge.net/fmllibs/fml_libs_dev.zip"
    $argo_url = ""
    $asm_url = ""
    $bcprov_url = ""
    $guava_url = ""
    $scala_lib_url = ""
    $mcp_srg_url = ""

    $fernflower_dl = "T"  #Enable Fernflower Download From newer MCP
    $server_skip = "T" #Skip Forge Servers in versions less then 1.3 as forge never fully supported servers until 1.3 when they were forced to support it
}
elseif ($mc_ver -eq "1.1")
{
    $mcp_ver = "mcp56"
    $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.1.0/mcp56.zip"
    $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.1-1.3.4.29/forge-1.1-1.3.4.29-src.zip"
    $mc_url = "https://launcher.mojang.com/v1/objects/f690d4136b0026d452163538495b9b0e8513d718/client.jar"
    $mc_server_url = "http://files.betacraft.uk/server-archive/release/1.1/1.1.jar"
    #Mod loader is a dep of forge for 1.1
    $modloader_url = "https://www.mediafire.com/file/wby6ddco9velug4/ModLoader+1.1.zip"

    #1.2.5 and below Require no Forge Runtime Libraries but do require compile time libraries?
    $forge_lib_url = "https://web.archive.org/web/20130305145719if_/http://files.minecraftforge.net/fmllibs/fml_libs_dev.zip"
    $argo_url = ""
    $asm_url = ""
    $bcprov_url = ""
    $guava_url = ""
    $scala_lib_url = ""
    $mcp_srg_url = ""

    $fernflower_dl = "T"  #Enable Fernflower Download From newer MCP
    $server_skip = "T" #Skip Forge Servers in versions less then 1.3 as forge never fully supported servers until 1.3 when they were forced to support it
    $patchMDKJDK8 = "T" #patch all batch files to enforce JDK-8 is used for all scripts
}
else
{
    Unsupported-Version
}

Write-Host "Creating Forge MDK for $mc_ver"

#Cleanup previous installations
MDK-Cleanup

#Create Directories
New-Item -Path "$temp/natives" -ItemType "directory" -Force | out-null
New-Item -Path "$mdk_dir/jars/lib" -ItemType "directory" -Force | out-null
New-Item -Path "$mdk_dir/jars/bin/natives" -ItemType "directory" -Force | out-null

#Download & Extract MCP
Invoke-WebRequest -Uri "$mcp_url" -OutFile "$temp\$mcp_ver.zip"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp\$mcp_ver.zip", "$mdk_dir")
#Download FernFlower for MCP 1.1-1.2.5 Forge
if ($fernflower_dl -eq "T")
{
    Invoke-WebRequest -Uri "$mcp72_url" -OutFile "$temp\mcp72.zip"
    [System.IO.Compression.ZipFile]::ExtractToDirectory("$temp\mcp72.zip", "$temp\mcp72")
    Copy-Item -Path "$temp\mcp72\runtime\bin\fernflower.jar" -Destination "$mdk_dir\runtime\bin\fernflower.jar" -Force | out-null
}

#Download & Extract Forge Source
Invoke-WebRequest -Uri "$forge_url" -OutFile "$temp/forge.zip"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/forge.zip", "$mdk_dir")

#Enforce JDK-8 in Path during setup for legacy versions
$JDK8 = (& "$mdk_dir\runtime\bin\python\python_mcp.exe" "$PSScriptRoot\find-jdk-8.py").Trim()
$env:PATH = "$JDK8;$env:PATH"
if ($patchMDKJDK8 -eq "T") {
& "$mdk_dir\runtime\bin\python\python_mcp.exe" "$PSScriptRoot\apply-jdk-8.py" "$mdk_dir"
Copy-Item -Path "$PSScriptRoot\find-jdk-8.py" -Destination "$mdk_dir\find-jdk-8.py" -Force | out-null
}

#Download Forge lib Folder and Install it
Invoke-WebRequest -Uri "$forge_lib_url" -OutFile "$temp/forge_lib.zip"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/forge_lib.zip", "$mdk_dir/lib")
if ($bcprov_dev -eq "T")
{
    Invoke-WebRequest -Uri "$bcprov_url" -OutFile ("$mdk_dir/lib/" + [System.IO.Path]::GetFileName("$bcprov_url"))
}

#Download & Install Forge Runtime Libs if they Exist for this MC & Forge Version
if ($argo_url -ne "") {
    Invoke-WebRequest -Uri "$argo_url" -OutFile ("$mdk_dir/jars/lib/" + [System.IO.Path]::GetFileName("$argo_url"))
}
if ($asm_url -ne "") {
    Invoke-WebRequest -Uri "$asm_url" -OutFile ("$mdk_dir/jars/lib/" + [System.IO.Path]::GetFileName("$asm_url"))
}
if ($bcprov_url -ne "") {
    Invoke-WebRequest -Uri "$bcprov_url" -OutFile ("$mdk_dir/jars/lib/" + [System.IO.Path]::GetFileName("$bcprov_url"))
}
if ($mcp_srg_url -ne "") {
    Invoke-WebRequest -Uri "$mcp_srg_url" -OutFile ("$mdk_dir/jars/lib/" + [System.IO.Path]::GetFileName("$mcp_srg_url"))
}
if ($guava_url -ne "") {
    Invoke-WebRequest -Uri "$guava_url" -OutFile ("$mdk_dir/jars/lib/" + [System.IO.Path]::GetFileName("$guava_url"))
}
if ($scala_lib_url -ne "") {
    Invoke-WebRequest -Uri "$scala_lib_url" -OutFile ("$mdk_dir/jars/lib/" + [System.IO.Path]::GetFileName("$scala_lib_url"))
}

#Download minecraft.jar & minecraft_server.jar and Install it
Invoke-WebRequest -Uri "$mc_url" -OutFile "$mdk_dir/jars/bin/minecraft.jar"
if (-Not $server_skip -eq "T" ) {
    Invoke-WebRequest -Uri "$mc_server_url" -OutFile "$mdk_dir/jars/minecraft_server.jar"
}

#Download and install Modloader for 1.1 - 1.2.4 as Forge requires Modloader in these versions
if (-Not [string]::IsNullOrEmpty($modloader_url)) {
    Download-Mediafire -mediafire_url "$modloader_url" -mediafire_file "$temp/modloader.zip"
    #Install Mod Loader now
    [System.IO.Compression.ZipFile]::ExtractToDirectory("$mdk_dir\jars\bin\minecraft.jar", "$temp\minecraft")
    [System.IO.Compression.ZipFile]::ExtractToDirectory("$temp\modloader.zip", "$temp\modloader")
    Copy-Item -Force -Recurse -Path "$temp\modloader\*" -Destination "$temp\minecraft"
    [System.IO.Directory]::Delete("$temp\minecraft\META-INF", $true)
    Remove-Item -Path "$mdk_dir/jars/bin/minecraft.jar" -Force -ErrorAction SilentlyContinue
    Create-Jar -Path "$temp/minecraft" -Jar "$mdk_dir/jars/bin/minecraft.jar"
}

#Download Minecraft Bin Libs
Invoke-WebRequest -Uri "$jinput_url" -OutFile "$mdk_dir/jars/bin/jinput.jar"
Invoke-WebRequest -Uri "$lwjgl_url" -OutFile "$mdk_dir/jars/bin/lwjgl.jar"
Invoke-WebRequest -Uri "$lwjgl_util_url" -OutFile "$mdk_dir/jars/bin/lwjgl_util.jar"

#Download Windows Natives & Extract then Install
DL-Natives -URL "$natives_windows_url" -URL2 "$natives_windows_url2" -FileName "windows_natives" "T"
DL-Natives -URL "$natives_mac_url" -URL2 "$natives_mac_url2" -FileName "macosx_natives" "F"
DL-Natives -URL "$natives_linux_url" -URL2 "$natives_linux_url2" -FileName "linux_natives" "F"

#Make MCP & Forge 1.4x compile with java 7 or higher
if ($patch_21 -eq "T")
{
    Write-Host "Patching Forge's RenderPlayer.java.patch"
    $patch_file = "$mdk_dir\forge\patches\minecraft\net\minecraft\src\RenderPlayer.java.patch"
    if (-Not [System.IO.Directory]::Exists("$patch_file"))
    {
        $patch_file = "$mdk_dir\forge\patches\minecraft\net\minecraft\client\renderer\entity\RenderPlayer.java.patch" #Redirects Patch file between 1.4.5-1.4.7
    }
    try
    {
        (Get-Content "$patch_file").replace("for (int var27 = 0; var27 < var21.getItem().getRenderPasses(var21.getItemDamage()); ++var27)", "for (int var27 = 0; var27 < var22.getItem().getRenderPasses(var22.getItemDamage()); ++var27)").replace("for (var27 = 0; var27 < var21.getItem().getRenderPasses(var21.getItemDamage()); ++var27)", "for (var27 = 0; var27 < var22.getItem().getRenderPasses(var22.getItemDamage()); ++var27)") | Set-Content "$patch_file"
    }
    catch
    {
        Write-Error "Failed to patch $patch_file"
    }
}

#Download Minecraft Resources
DL-Resources -JsonURL "$resources_json_url" -Resources "$mdk_dir\jars\resources"

#Run Forge's Install Script
Set-Location -Path "$mdk_dir\forge"
Write-Host "Running Forge install.cmd"
Start-Process -FilePath "$mdk_dir\forge\install.cmd" -Wait -NoNewWindow
Write-Host "Forge MDK Installation Completed"
}
