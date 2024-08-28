#import C# zip tools
Add-Type -AssemblyName 'System.IO.Compression.FileSystem'

#global variables
$mc_ver = "1.5.2"
$mcp_ver = "mcp751"
#Temp Files
$mcp_dir = "$PSScriptRoot\MDK-$mc_ver"
$temp = "$mcp_dir\tmp"
#URLS
$mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.5.2/$mcp_ver.zip"
$forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.5.2-7.8.1.738/forge-1.5.2-7.8.1.738-src.zip"
$forge_lib_url = "https://web.archive.org/web/20160126150649id_/http://files.minecraftforge.net/fmllibs/fml_libs_dev15.zip"
$mc_url = "https://launcher.mojang.com/v1/objects/465378c9dc2f779ae1d6e8046ebc46fb53a57968/client.jar"
$mc_server_url = "https://launcher.mojang.com/v1/objects/f9ae3f651319151ce99a0bfad6b34fa16eb6775f/server.jar"
$argo_url = "https://web.archive.org/web/20160305211940id_/https://files.minecraftforge.net/fmllibs/argo-small-3.2.jar"
$asm_url = "https://web.archive.org/web/20160305133607id_/https://files.minecraftforge.net/fmllibs/asm-all-4.1.jar"
$bcprov_url = "https://web.archive.org/web/20130708220724id_/http://files.minecraftforge.net/fmllibs/bcprov-jdk15on-148.jar"
$mcp_srg_url = "https://web.archive.org/web/20150324115021id_/https://files.minecraftforge.net/fmllibs/deobfuscation_data_1.5.2.zip"
$guava_url = "https://web.archive.org/web/20150324120717id_/https://files.minecraftforge.net/fmllibs/guava-14.0-rc3.jar"
$scala_lib_url = "https://web.archive.org/web/20130708223654id_/http://files.minecraftforge.net/fmllibs/scala-library.jar"
$jinput_url = "https://libraries.minecraft.net/net/java/jinput/jinput/2.0.5/jinput-2.0.5.jar"
$lwjgl_url = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl/2.9.0/lwjgl-2.9.0.jar"
$lwjgl_util_url = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl_util/2.9.0/lwjgl_util-2.9.0.jar"
$win_natives_url = "https://libraries.minecraft.net/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-windows.jar"
$win_natives_url2 = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/2.9.0/lwjgl-platform-2.9.0-natives-windows.jar"
$legacy_assets_url = "https://launchermeta.mojang.com/v1/packages/3d8e55480977e32acd9844e545177e69a52f594b/pre-1.6.json"
$resources_url = "https://resources.download.minecraft.net/"

#cleanup previous installation attempts
if ([System.IO.Directory]::Exists("$mcp_dir"))
{
    $shouldStop = Read-Host "The folder '$mcp_dir' already exists. Do you want to delete it and continue? (Y/N)"
    if ($shouldStop.StartsWith('N') -or $shouldStop.StartsWith('n')) 
    {
        exit 0
    }
    [System.IO.Directory]::Delete("$mcp_dir", $true)
}

#Create Directories
New-Item -Path "$temp/natives" -ItemType "directory" -Force | out-null
New-Item -Path "$mcp_dir/jars/lib" -ItemType "directory" -Force | out-null
New-Item -Path "$mcp_dir/jars/bin/natives" -ItemType "directory" -Force | out-null

#Download & Extract MCP
Invoke-WebRequest -Uri "$mcp_url" -OutFile "$temp\$mcp_ver.zip"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp\$mcp_ver.zip", $mcp_dir)

#Download & Extract Forge Source
Invoke-WebRequest -Uri "$forge_url" -OutFile "$temp/forge.zip"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/forge.zip", "$mcp_dir")

#Download Forge lib Folder and Install it
Invoke-WebRequest -Uri "$forge_lib_url" -OutFile "$temp/forge_lib.zip"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/forge_lib.zip", "$mcp_dir/lib")

#Download & Install Forge Runtime Libs
Invoke-WebRequest -Uri "$argo_url" -OutFile "$mcp_dir/jars/lib/argo-small-3.2.jar"
Invoke-WebRequest -Uri "$asm_url" -OutFile "$mcp_dir/jars/lib/asm-all-4.1.jar"
Invoke-WebRequest -Uri "$bcprov_url" -OutFile "$mcp_dir/jars/lib/bcprov-jdk15on-148.jar"
Invoke-WebRequest -Uri "$mcp_srg_url" -OutFile "$mcp_dir/jars/lib/deobfuscation_data_1.5.2.zip"
Invoke-WebRequest -Uri "$guava_url" -OutFile "$mcp_dir/jars/lib/guava-14.0-rc3.jar"
Invoke-WebRequest -Uri "$scala_lib_url" -OutFile "$mcp_dir/jars/lib/scala-library.jar"

#Download minecraft.jar & minecraft_server.jar and Install it
Invoke-WebRequest -Uri "$mc_url" -OutFile "$mcp_dir/jars/bin/minecraft.jar"
Invoke-WebRequest -Uri "$mc_server_url" -OutFile "$mcp_dir/jars/minecraft_server.jar"

#Download Minecraft Bin Libs
Invoke-WebRequest -Uri "$jinput_url" -OutFile "$mcp_dir/jars/bin/jinput.jar"
Invoke-WebRequest -Uri "$lwjgl_url" -OutFile "$mcp_dir/jars/bin/lwjgl.jar"
Invoke-WebRequest -Uri "$lwjgl_util_url" -OutFile "$mcp_dir/jars/bin/lwjgl_util.jar"

#Download Windows Natives & Extract then Install them (We are Powershell :( We can't support MacOs and Linux )
Invoke-WebRequest -Uri "$win_natives_url" -OutFile "$temp/win_natives.jar"
Invoke-WebRequest -Uri "$win_natives_url2" -OutFile "$temp/win_natives2.jar"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/win_natives.jar", "$temp/natives")
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/win_natives2.jar", "$temp/natives")
[System.IO.Compression.ZipFile]::CreateFromDirectory("$temp/natives", "$mcp_dir/jars/bin/natives/windows_natives.jar") # Re-Zips the natives and installs it to the correct location
[System.IO.Compression.ZipFile]::ExtractToDirectory("$mcp_dir/jars/bin/natives/windows_natives.jar", "$mcp_dir/jars/bin/natives") # Un-Zips all Windows Natives to the correct location
Copy-Item -Path "$mcp_dir/jars/bin/natives/windows_natives.jar" -Destination "$mcp_dir/jars/bin/natives/macosx_natives.jar" -Force | out-null # Creates new Dummy Files to prevent forge install from crashing trying to extract other
Copy-Item -Path "$mcp_dir/jars/bin/natives/windows_natives.jar" -Destination "$mcp_dir/jars/bin/natives/linux_natives.jar" -Force | out-null

#Download Minecraft Resources
$progress_org = "$ProgressPreference"
try
{
    $ProgressPreference = 'SilentlyContinue'
    $jsonFile = "$temp/assets.json"
    Invoke-WebRequest -Uri "$legacy_assets_url" -OutFile "$jsonFile"
    $jsonData = Get-Content -Path "$jsonFile" -Raw | ConvertFrom-Json
    $objects = $jsonData.objects
    foreach ($key in $objects.PSObject.Properties.Name) 
    {
        $hash = $objects.$key.hash
        $resource = $resources_url + $hash.Substring(0, 2) + "/$hash"
        $resource_file = "$mcp_dir\jars\resources\$key"
        Write-Output "Downloading Resource URL:$resource"
        $rd = Split-Path "$resource_file" -Parent #build resource directory path
        New-Item -Path "$rd" -ItemType "directory" -Force | out-null #create resource directories if required
        Invoke-WebRequest -Uri "$resource" -OutFile "$resource_file"
    }
}
catch
{
    Write-Host An Error Occured Obtaining Minecraft Resources Please manually Download and insert them into $mcp_dir\jars\resources
}
$ProgressPreference = "$progress_org"

#Run Forge's Install Script
Set-Location -Path "$mcp_dir\forge"
Start-Process -FilePath "$mcp_dir\forge\install.cmd" -Wait -NoNewWindow
