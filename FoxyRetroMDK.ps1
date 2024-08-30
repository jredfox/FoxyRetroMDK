#import C# zip tools
Add-Type -AssemblyName 'System.IO.Compression.FileSystem'

& {

#Change this mc release version between 1.1 through 1.5.2
#NOTE: 1.3.2-1.4.7 requires java 7 jars else forge's ASM library will throw a fit and crash
$mc_ver = "1.2.5" #TODO: change this to if ($mc_ver is null or empty) change it to 1.5.2

#Temp Files
$mcp_dir = "$PSScriptRoot\MDK-$mc_ver"
$temp = "$mcp_dir\tmp"
#URL Start
$argo_url = "https://web.archive.org/web/20160305211940id_/https://files.minecraftforge.net/fmllibs/argo-small-3.2.jar"
$asm_url = "https://web.archive.org/web/20160305133607id_/https://files.minecraftforge.net/fmllibs/asm-all-4.1.jar"
$bcprov_url = "https://web.archive.org/web/20130708220724id_/http://files.minecraftforge.net/fmllibs/bcprov-jdk15on-148.jar"
$guava_url = "https://web.archive.org/web/20150324120717id_/https://files.minecraftforge.net/fmllibs/guava-14.0-rc3.jar"
$scala_lib_url = "https://web.archive.org/web/20130708223654id_/http://files.minecraftforge.net/fmllibs/scala-library.jar"
$jinput_url = "https://libraries.minecraft.net/net/java/jinput/jinput/2.0.5/jinput-2.0.5.jar"
$lwjgl_url = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl/2.9.0/lwjgl-2.9.0.jar"
$lwjgl_util_url = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl_util/2.9.0/lwjgl_util-2.9.0.jar"
$win_natives_url = "https://libraries.minecraft.net/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-windows.jar"
$win_natives_url2 = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/2.9.0/lwjgl-platform-2.9.0-natives-windows.jar"
$legacy_assets_url = "https://launchermeta.mojang.com/v1/packages/3d8e55480977e32acd9844e545177e69a52f594b/pre-1.6.json"
$resources_url = "https://resources.download.minecraft.net/"
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
    $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.3.2/mcp72.zip"
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
    #TODO get mod loader installed into minecraft.jar & delete META-INF
    #TODO 1.2X get LWJGL updated and merging jars as a hack and delete META-INF so it can run without exceptions
    elseif ($mc_ver -eq "1.2.4")
    {
        $mcp_ver = "mcp61"
        $mcp_url = "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.2.4/mcp61.zip"
        $forge_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.2.4-2.0.0.68/forge-1.2.4-2.0.0.68-src.zip"
        $mc_url = "https://launcher.mojang.com/v1/objects/ad6d1fe7455857269d4185cb8f24e62cc0241aaf/client.jar"
        $mc_server_url = "https://assets.minecraft.net/1_2_5/minecraft_server.jar"
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
else
{
    Write-Error "Invalid or Unsupported MC Version $mc_ver"
    exit -1
}


#cleanup previous installation attempts
if ([System.IO.Directory]::Exists("$mcp_dir"))
{
    $shouldStop = Read-Host "The folder '$mcp_dir' already exists. Do you want to delete it and continue? (Y/N)"
    if ($shouldStop.StartsWith('Y') -or $shouldStop.StartsWith('y')) {
        [System.IO.Directory]::Delete("$mcp_dir", $true)
    }
    else {
        exit 0
    }
}

#Create Directories
New-Item -Path "$temp/natives" -ItemType "directory" -Force | out-null
New-Item -Path "$mcp_dir/jars/lib" -ItemType "directory" -Force | out-null
New-Item -Path "$mcp_dir/jars/bin/natives" -ItemType "directory" -Force | out-null

#Download & Extract MCP
Invoke-WebRequest -Uri "$mcp_url" -OutFile "$temp\$mcp_ver.zip"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp\$mcp_ver.zip", "$mcp_dir")
#Download FernFlower for MCP 1.1-1.2.5 Forge
if ($fernflower_dl -eq "T")
{
    Invoke-WebRequest -Uri "https://archive.org/download/minecraftcoderpack/minecraftcoderpack.zip/minecraftcoderpack/1.3.2/mcp72.zip" -OutFile "$temp\mcp72.zip"
    [System.IO.Compression.ZipFile]::ExtractToDirectory("$temp\mcp72.zip", "$temp\mcp72")
    Copy-Item -Path "$temp\mcp72\runtime\bin\fernflower.jar" -Destination "$mcp_dir\runtime\bin\fernflower.jar" -Force | out-null
}

#Download & Extract Forge Source
Invoke-WebRequest -Uri "$forge_url" -OutFile "$temp/forge.zip"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/forge.zip", "$mcp_dir")

#Download Forge lib Folder and Install it
Invoke-WebRequest -Uri "$forge_lib_url" -OutFile "$temp/forge_lib.zip"
[System.IO.Compression.ZipFile]::ExtractToDirectory("$temp/forge_lib.zip", "$mcp_dir/lib")
if ($bcprov_dev -eq "T")
{
    Invoke-WebRequest -Uri "$bcprov_url" -OutFile ("$mcp_dir/lib/" + [System.IO.Path]::GetFileName("$bcprov_url"))
}

#Download & Install Forge Runtime Libs if they Exist for this MC & Forge Version
if ($argo_url -ne "") {
    Invoke-WebRequest -Uri "$argo_url" -OutFile ("$mcp_dir/jars/lib/" + [System.IO.Path]::GetFileName("$argo_url"))
}
if ($asm_url -ne "") {
    Invoke-WebRequest -Uri "$asm_url" -OutFile ("$mcp_dir/jars/lib/" + [System.IO.Path]::GetFileName("$asm_url"))
}
if ($bcprov_url -ne "") {
    Invoke-WebRequest -Uri "$bcprov_url" -OutFile ("$mcp_dir/jars/lib/" + [System.IO.Path]::GetFileName("$bcprov_url"))
}
if ($mcp_srg_url -ne "") {
    Invoke-WebRequest -Uri "$mcp_srg_url" -OutFile ("$mcp_dir/jars/lib/" + [System.IO.Path]::GetFileName("$mcp_srg_url"))
}
if ($guava_url -ne "") {
    Invoke-WebRequest -Uri "$guava_url" -OutFile ("$mcp_dir/jars/lib/" + [System.IO.Path]::GetFileName("$guava_url"))
}
if ($scala_lib_url -ne "") {
    Invoke-WebRequest -Uri "$scala_lib_url" -OutFile ("$mcp_dir/jars/lib/" + [System.IO.Path]::GetFileName("$scala_lib_url"))
}

#Download minecraft.jar & minecraft_server.jar and Install it
Invoke-WebRequest -Uri "$mc_url" -OutFile "$mcp_dir/jars/bin/minecraft.jar"
if (-Not $server_skip -eq "T" ) {
    Write-Host "Downloading Server: $mc_server_url"
    Invoke-WebRequest -Uri "$mc_server_url" -OutFile "$mcp_dir/jars/minecraft_server.jar"
}

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

#Make MCP & Forge 1.4x compile with java 7 or higher
if ($patch_21 -eq "T")
{
    Write-Host "Patching Forge's RenderPlayer.java.patch"
    $patch_file = "$mcp_dir\forge\patches\minecraft\net\minecraft\src\RenderPlayer.java.patch"
    if (-Not [System.IO.Directory]::Exists("$patch_file"))
    {
        $patch_file = "$mcp_dir\forge\patches\minecraft\net\minecraft\client\renderer\entity\RenderPlayer.java.patch" #Redirects Patch file between 1.4.5-1.4.7
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
$progress_org = "$ProgressPreference"
$ProgressPreference = 'SilentlyContinue'
try
{
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
    Write-Error "An Error Occured Obtaining Minecraft Resources Please manually Download and insert them into $mcp_dir\jars\resources"
}
$ProgressPreference = "$progress_org"

#Run Forge's Install Script
Set-Location -Path "$mcp_dir\forge"
Start-Process -FilePath "$mcp_dir\forge\install.cmd" -Wait -NoNewWindow
}
