import sys
import os
import shutil
import urllib
import zipfile
import json
from collections import OrderedDict
from contextlib import closing
from hashlib import sha1
from urllib2 import urlopen

def download_file(url, target, sha1, extract=False):
    pdir = os.path.dirname(target)
    if onesix and (not os.path.isdir(pdir)):
        os.makedirs(pdir)
    try:
        print('downloading: ' + url)
        urllib.urlretrieve(url, target)
        if (not sha1 is None):
            downloaded_sha1 = get_sha1(target)
            if downloaded_sha1 != sha1:
                del_file(target)
                if url.startswith('https://libraries.minecraft.net'):
                    download_file(url.replace('https://libraries.minecraft.net', 'https://repo.maven.apache.org/maven2', 1), target, sha1, extract)
                else:
                    print('Download Failed Removed: ' + target)
                    sys.exit(1)
    except Exception as e:
        del_file(target)
        print('Download Failed With Exception: ' + str(e))
        if url.startswith('https://libraries.minecraft.net'):
            download_file(url.replace('https://libraries.minecraft.net', 'https://repo.maven.apache.org/maven2', 1), target, sha1, extract)
    if extract:
        with zipfile.ZipFile(target, 'r') as zip_ref:
            zip_ref.extractall(dir_natives)

def get_sha1(file):
    if not os.path.isfile(file):
        return None
    with closing(open(file, 'rb')) as fh:
        return sha1(fh.read()).hexdigest().lower()

def del_dir(d):
    if os.path.isdir(d):
        shutil.rmtree(d)

def del_file(file):
    if(os.path.isfile(file)):
        os.remove(file)

def has_wifi(url='http://www.google.com', timeout=5):
    try:
        urlopen(url, timeout=timeout)
        return True
    except Exception:
        return False

def patch_libs(libJSONFile):
    if os.path.exists(libJSONFile):
        useMojang = lwjgl_ver != '2.9.2'
        print('Patching: ' + os.path.basename(libJSONFile))
        with open(libJSONFile, 'r') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
        libraries = data.get('libraries', [])
        for lib in libraries:
            oname = lib.get("name", "")
            name = oname.lower()
            if 'lwjgl' in name and ('org.lwjgl.lwjgl:lwjgl:' in name or 'org.lwjgl.lwjgl:lwjgl_util:' in name or 'org.lwjgl.lwjgl:lwjgl-platform:' in name):
                lib["name"] = (oname[:oname.rfind(":")] + ":" + lwjgl_ver)
                url = lib.get("url")
                if useMojang:
                    if url is not None:
                        del lib["url"]
                else:
                    lib["url"] = "https://repo.maven.apache.org/maven2"
        libJSONText = json.dumps(data, indent=2).replace('\r\n', '\n')
        with open(libJSONFile, 'wb') as f:
            for line in libJSONText.split('\n'):
                f.write(line.rstrip() + '\n')
    else:
        print('Skipping Patching: ' + libJSONFile)
    
def patch_classpath(file, printSkip=False):
    if os.path.isfile(file):
        print('Patching: ' + file)
        with open(file, 'r') as f:
            lines = f.read().replace('\r\n', '\n').replace('\\', '/')
        target = 'jars/libraries/org/lwjgl/lwjgl/lwjgl/'
        start = lines.rfind(target) + len(target)
        end = lines.find('/', start)
        version = lines[start:end]
        cpp_lwjgl = 'jars/libraries/org/lwjgl/lwjgl/lwjgl/' + version + '/lwjgl-' + version + '.jar'
        cpp_lwjgl_util = 'jars/libraries/org/lwjgl/lwjgl/lwjgl_util/' + version + '/lwjgl_util-' + version + '.jar'
        str_lwjgl = 'jars/libraries/org/lwjgl/lwjgl/lwjgl/' + lwjgl_ver + '/lwjgl-' + lwjgl_ver + '.jar'
        str_lwjgl_util = 'jars/libraries/org/lwjgl/lwjgl/lwjgl_util/' + lwjgl_ver + '/lwjgl_util-' + lwjgl_ver + '.jar'
        lines = lines.replace(cpp_lwjgl, str_lwjgl)
        lines = lines.replace(cpp_lwjgl_util, str_lwjgl_util)
        lines = lines.replace((cpp_lwjgl[:-4] + "-sources.jar"), (str_lwjgl[:-4] + "-sources.jar"))
        lines = lines.replace((cpp_lwjgl_util[:-4] + "-sources.jar"), (str_lwjgl_util[:-4] + "-sources.jar"))
        with open(file, 'wb') as f:
            f.write(lines)
    elif not printSkip:
        print('Skipping Patching: ' + file)

def attatch_src(file, printSkip=False):
    if os.path.isfile(file):
        print('Patching: ' + file)
        with open(file, 'r') as f:
            lines = f.read().replace('\r\n', '\n').replace('\\', '/')
        if not has_src_path(lines, 'path="jars/bin/lwjgl.jar"'):
            lines = lines.replace('path="jars/bin/lwjgl.jar"', 'path="jars/bin/lwjgl.jar" sourcepath="lib/lwjgl-sources.zip"')
        if not has_src_path(lines, 'path="jars/bin/lwjgl_util.jar"'):
            lines = lines.replace('path="jars/bin/lwjgl_util.jar"', 'path="jars/bin/lwjgl_util.jar" sourcepath="lib/lwjgl_util-sources.zip"')
        with open(file, 'wb') as f:
            f.write(lines)
        project_file = os.path.join(os.path.dirname(file), '.project')
        with open(project_file, 'r') as f:
            lines = f.read().replace('\r\n', '\n').replace('\\', '/').replace('    ', '\t').replace('   ', '\t')
        if os.path.isfile(project_file):
            print('Patching: ' + project_file)
            project_patch = '\t<link>\n\t\t\t<name>lib</name>\n\t\t\t<type>2</type>\n\t\t\t<locationURI>MCP_LOC/lib</locationURI>\n\t\t</link>\n\t'
            tag_start = lines.find('<linkedResources>')
            tag_end = lines.find('</linkedResources>')
            if tag_start != -1 and tag_end != -1:
                if lines.rfind('MCP_LOC/lib', tag_start, tag_end) == -1:
                    lines = lines.replace('</linkedResources>', (project_patch + '</linkedResources>'), 1)
                    with open(project_file, 'wb') as f:
                        f.write(lines)
    elif not printSkip:
        print('Skipping Patching: ' + file)

def del_lwjgl_natives(dir_natives):
    del_dir(os.path.join(dir_natives, 'META-INF'))
    names = set([
        'liblwjgl.so',
        'liblwjgl32.so',
        'liblwjgl64.so',
        'libopenal.so',
        'libopenal32.so',
        'libopenal64.so',
        'lwjgl.dll',
        'lwjgl32.dll',
        'lwjgl64.dll',
        'openal.dll',
        'openal32.dll', 
        'openal64.dll',
        'liblwjgl.dylib',
        'liblwjgl.jnilib',
        'openal.dylib',
        'openal.jnilib'
    ])
    for fname in os.listdir(dir_natives):
        if fname.lower() in names:
            print('del file: ' + fname)
            del_file(os.path.join(dir_natives, fname))

def download_natives():
    if onesix:
        #delete lwjgl jar natives
        del_file(lwjgl_natives_windows_natives_jar)
        del_file(lwjgl_natives_macosx_natives_jar)
        del_file(lwjgl_natives_linux_natives_jar)
    #if natives directory doesn't exist re-create the natives from scratch
    if not os.path.isdir(dir_natives):
        os.makedirs(dir_natives)
        #download jinput jar natives
        jinput_base_url = 'https://libraries.minecraft.net/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-'
        download_file(jinput_base_url + 'windows.jar', lwjgl_natives_windows_natives_jar, None, True)
        download_file(jinput_base_url + 'osx.jar', lwjgl_natives_macosx_natives_jar, None, True)
        download_file(jinput_base_url + 'linux.jar', lwjgl_natives_linux_natives_jar, None, True)
    else:
        del_lwjgl_natives(dir_natives)
    #download lwjgl jar natives and extract
    download_file(lwjgl_natives_base + "windows.jar", lwjgl_natives_windows_natives_jar + '.tmp', lwjgl_windows_sha1, True)
    download_file(lwjgl_natives_base + "osx.jar", lwjgl_natives_macosx_natives_jar + '.tmp', lwjgl_macosx_sha1, True)
    download_file(lwjgl_natives_base + "linux.jar", lwjgl_natives_linux_natives_jar + '.tmp', lwjgl_linux_sha1, True)
    #rebuild the jar natives
    merge_zips((lwjgl_natives_windows_natives_jar + '.tmp'), lwjgl_natives_windows_natives_jar)
    merge_zips((lwjgl_natives_macosx_natives_jar + '.tmp'), lwjgl_natives_macosx_natives_jar)
    merge_zips((lwjgl_natives_linux_natives_jar + '.tmp'), lwjgl_natives_linux_natives_jar)
    
def merge_zips(*zips):
    with zipfile.ZipFile(zips[0], 'a') as z1:  # Open the first zip in append mode
        existing_files = set(z1.namelist())
        for fname in zips[1:]:
            with zipfile.ZipFile(fname, 'r') as zf:  # Open each subsequent zip
                for n in zf.namelist():
                    # Skip dirs and duplicates
                    if n.endswith('/') or n in existing_files:
                        continue
                    print('adding: ' + n)
                    existing_files.add(n)
                    # Read the file and write to the first zip
                    z1.writestr(n, zf.read(n))

def has_src_path(lines, target):
    start = lines.find(target)
    if start == -1:
        return False
    tag_start = lines.rfind('<', 0, start)
    tag_end = lines.find('>', start)
    return (tag_start != -1) and (tag_end != -1) and (lines.find('sourcepath="', tag_start, tag_end) != -1)

if __name__ == "__main__":
    if (not has_wifi('https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl/2.9.0/lwjgl-2.9.0.jar.sha1')) and (not has_wifi('https://repo.maven.apache.org/maven2/org/lwjgl/lwjgl/lwjgl/2.9.0/lwjgl-2.9.0.jar.sha1')):
        print('Internet is down, or both https://libraries.minecraft.net and https://repo.maven.apache.org are down :(')
        sys.exit(1)
    lwjgl_ver = sys.argv[1].lower().replace('"', '').replace("'", '').replace(' ', '')
    onesix = False
    mc_ver = ""
    dir_mcp = os.path.dirname(os.path.realpath(__file__))
    if os.path.isdir(os.path.join(dir_mcp, 'jars', 'versions')) and os.path.isdir(os.path.join(dir_mcp, 'jars', 'libraries')):
        onesix = True
        for f in os.listdir(os.path.join(dir_mcp, 'jars')):
            fname = os.path.basename(f)
            if fname.startswith('minecraft_server.1.6.') and fname.endswith('.jar'):
                mc_ver = fname[17:-4]
                break
        if mc_ver == "":
            print("Minecraft Version Cannot Be determined because minecraft_server.<mc version>.jar is missing!")
            sys.exit(1)
    if lwjgl_ver == '' or lwjgl_ver == 'latest' or lwjgl_ver == '2.9.4':
        lwjgl_ver = '2.9.4-nightly-20150209'
    if lwjgl_ver != '2.9.0' and lwjgl_ver != '2.9.1' and lwjgl_ver != '2.9.3' and (not lwjgl_ver.startswith('2.9.4-')) and lwjgl_ver != '2.9.4' and lwjgl_ver != '2.9.2':
        print('LWJGL Version Must be 2.9.0, 2.9.1, 2.9.2, 2.9.3(bugged), 2.9.4, 2.9.4-<nightlybuild>, or latest')
        print('For Testing Older LWJGL: LWJGL Version 2.9.0 works best for windows, LWJGL Version 2.9.1 Works best on linux, LWJGL Version 2.9.4-nightly-20150209 (latest) for macOS with JDK-8')
        sys.exit(1)

    lwjgl_sha1 = lwjgl_util_sha1 = lwjgl_windows_sha1 = lwjgl_macosx_sha1 = lwjgl_linux_sha1 = lwjgl_src_sha1 = lwjgl_util_src_sha1 = None
    if lwjgl_ver == '2.9.0':
        lwjgl_sha1 = '5654d06e61a1bba7ae1e7f5233e1106be64c91cd'
        lwjgl_util_sha1 = 'a778846b64008fc7f48ead2377f034e547991699'
        lwjgl_windows_sha1 = '3f11873dc8e84c854ec7c5a8fd2e869f8aaef764'
        lwjgl_macosx_sha1 = '6621b382cb14cc409b041d8d72829156a87c31aa'
        lwjgl_linux_sha1 = '2ba5dcb11048147f1a74eff2deb192c001321f77'
        lwjgl_src_sha1 = 'c93326bd0f3a21f3b2c8c22b6f345ab6ca1dd683'
        lwjgl_util_src_sha1 = 'a7449c197615515f4f9cbf03e6a185ca5bf946e3'
    elif lwjgl_ver == '2.9.1':
        lwjgl_sha1 = 'f58c5aabcef0e41718a564be9f8e412fff8db847'
        lwjgl_util_sha1 = '290d7ba8a1bd9566f5ddf16ad06f09af5ec9b20e'
        lwjgl_windows_sha1 = '4c517eca808522457dd95ee8fc1fbcdbb602efbe'
        lwjgl_macosx_sha1 = '2d12c83fdfbc04ecabf02c7bc8cc54d034f0daac'
        lwjgl_linux_sha1 = 'aa9aae879af8eb378e22cfc64db56ec2ca9a44d1'
        lwjgl_src_sha1 = 'ccedb5b6f96913c6f78bc10249e747ded90baa51'
        lwjgl_util_src_sha1 = '9f350d8a760247f2ae88e996b55f8f7121346c79'
    elif lwjgl_ver == '2.9.4-nightly-20150209':
        lwjgl_sha1 = '697517568c68e78ae0b4544145af031c81082dfe'
        lwjgl_util_sha1 = 'd51a7c040a721d13efdfbd34f8b257b2df882ad0'
        lwjgl_windows_sha1 = 'b84d5102b9dbfabfeb5e43c7e2828d98a7fc80e0'
        lwjgl_macosx_sha1 = 'bcab850f8f487c3f4c4dbabde778bb82bd1a40ed'
        lwjgl_linux_sha1 = '931074f46c795d2f7b30ed6395df5715cfd7675b'
        lwjgl_src_sha1 = '7da2cff65127b558a66e8e38456174161723d3a7'
        lwjgl_util_src_sha1 = '002e3787f55c68a245e994f88755795b3a7684b3'
    elif lwjgl_ver == '2.9.2':
        lwjgl_sha1 = 'a9d80fe5935c7a9149f6584d9777cfd471f65489'
        lwjgl_util_sha1 = '4b9e37300a87799856e0bd15ed81663cdb6b0947'
        lwjgl_windows_sha1 = '510c7d317f5e9e700b9cfaac5fd38bdebf0702e0'
        lwjgl_macosx_sha1 = 'd55b46b40b40249d627a83a7f7f22649709d70c3'
        lwjgl_linux_sha1 = 'd276cdf61fe2b516c7b7f4aa1b8dea91dbdc8d56'
        lwjgl_src_sha1 = '4d114b5ef3ad3bf571b1f090cb00855991067e0b'
        lwjgl_util_src_sha1 = '308d4ebe8d7b240d3490b6a7e0424807ea3ad98b'
    elif lwjgl_ver == '2.9.3':
        print('WARNING LWJGL Version 2.9.3 contains lots of graphical issues! Please use a different version')
        lwjgl_sha1 = '3df168ac74e4a8c96562cdff24ad352e255bf89c'
        lwjgl_util_sha1 = '751f06b62424da056954c67288fd5c494431e350'
        lwjgl_windows_sha1 = 'fbc2afb3e288578e9942578decb6291a490549a0'
        lwjgl_macosx_sha1 = '6686cf6ddaa20b4290aa6599a09bc0d17369be05'
        lwjgl_linux_sha1 = 'b1eafe80093381c56415731e1d64279e6140bcd0'
        lwjgl_src_sha1 = '34682f36cee6cded40df9829bb352f2bdce5b14e'
        lwjgl_util_src_sha1 = '0ca58b77b6393794ca34e12b32e9c6d9c912acb3'

    if not onesix:
        dir_bin = os.path.join(dir_mcp, "jars", "bin")
        dir_natives = os.path.join(dir_bin, 'natives')
        dir_src = os.path.join(dir_mcp, 'lib')
        lwjgl_jar = os.path.join(dir_bin, 'lwjgl.jar')
        lwjgl_util_jar = os.path.join(dir_bin, 'lwjgl_util.jar')
        lwjgl_src_jar = os.path.join(dir_src, 'lwjgl-sources.zip')
        lwjgl_util_src_jar = os.path.join(dir_src, 'lwjgl_util-sources.zip')
        lwjgl_natives_windows_natives_jar = os.path.join(dir_natives, 'windows_natives.jar')
        lwjgl_natives_macosx_natives_jar = os.path.join(dir_natives, 'macosx_natives.jar')
        lwjgl_natives_linux_natives_jar = os.path.join(dir_natives, 'linux_natives.jar')
        #Attach sources to classpath
        #MC 1.1 - 1.2.5
        attatch_src(os.path.join(dir_mcp, 'eclipse', 'Client', '.classpath'))
        attatch_src(os.path.join(dir_mcp, 'eclipse', 'Server', '.classpath'))
        #MC 1.3.2 - 1.5.2
        attatch_src(os.path.join(dir_mcp, 'forge', 'fml', 'eclipse', 'Minecraft', '.classpath'))
        attatch_src(os.path.join(dir_mcp, 'eclipse', 'Minecraft', '.classpath'))
    else:
        dir_base = os.path.join(dir_mcp, "jars")
        dir_libs = os.path.join(dir_base, "libraries", 'org', 'lwjgl', 'lwjgl')
        dir_version = os.path.join(dir_base, "versions", mc_ver)
        dir_natives = os.path.join(dir_version, (mc_ver + '-natives'))
        lwjgl_jar = os.path.join(dir_libs, 'lwjgl', lwjgl_ver, ('lwjgl-' + lwjgl_ver + '.jar') )
        lwjgl_util_jar = os.path.join(dir_libs, 'lwjgl_util', lwjgl_ver, ('lwjgl_util-' + lwjgl_ver + '.jar') )
        lwjgl_src_jar = (lwjgl_jar[:-4] + "-sources.jar")
        lwjgl_util_src_jar =(lwjgl_util_jar[:-4] + "-sources.jar")
        lwjgl_natives_windows_natives_jar = os.path.join(dir_libs, 'lwjgl-platform', lwjgl_ver, ('lwjgl-platform-' + lwjgl_ver + '-natives-windows.jar') )
        lwjgl_natives_macosx_natives_jar = os.path.join(dir_libs, 'lwjgl-platform', lwjgl_ver, ('lwjgl-platform-' + lwjgl_ver + '-natives-osx.jar') )
        lwjgl_natives_linux_natives_jar = os.path.join(dir_libs, 'lwjgl-platform', lwjgl_ver, ('lwjgl-platform-' + lwjgl_ver + '-natives-linux.jar') )
        #patch lwjgl version strings
        dir_fml = os.path.join(os.path.dirname(dir_mcp), 'fml')
        patch_libs(os.path.join(dir_fml, 'fml.json'))
        patch_libs(os.path.join(dir_version, (mc_ver + '.json') ))
        patch_classpath(os.path.join(dir_fml, 'eclipse', 'Minecraft', '.classpath'))
        patch_classpath(os.path.join(dir_mcp, 'eclipse', 'Minecraft', '.classpath'))
        patch_classpath(os.path.join(dir_mcp, 'eclipse', 'Client', '.classpath'), True)
        patch_classpath(os.path.join(dir_mcp, 'eclipse', 'Server', '.classpath'), True)
    
    #delete previous lwjgl jars
    del_file(lwjgl_jar)
    del_file(lwjgl_util_jar)
    del_file(lwjgl_src_jar)
    del_file(lwjgl_util_src_jar)

    #download & install lwjgl
    lwjgl_url = 'https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl/' + lwjgl_ver + '/lwjgl-' + lwjgl_ver + '.jar'
    lwjgl_util_url = 'https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl_util/' + lwjgl_ver + '/lwjgl_util-' + lwjgl_ver + '.jar'
    lwjgl_natives_base = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/" + lwjgl_ver + '/lwjgl-platform-' + lwjgl_ver + "-natives-"
    if lwjgl_ver == '2.9.2':
        lwjgl_url = 'https://repo.maven.apache.org/maven2/org/lwjgl/lwjgl/lwjgl/2.9.2/lwjgl-2.9.2.jar'
        lwjgl_util_url = 'https://repo.maven.apache.org/maven2/org/lwjgl/lwjgl/lwjgl_util/2.9.2/lwjgl_util-2.9.2.jar'
        lwjgl_natives_base = 'https://repo.maven.apache.org/maven2/org/lwjgl/lwjgl/lwjgl-platform/2.9.2/lwjgl-platform-2.9.2-natives-'
    download_file(lwjgl_url, lwjgl_jar, lwjgl_sha1)
    download_file(lwjgl_util_url, lwjgl_util_jar, lwjgl_util_sha1)
    download_file((lwjgl_url[:-4] + "-sources.jar"), lwjgl_src_jar, lwjgl_src_sha1)
    download_file((lwjgl_util_url[:-4] + "-sources.jar"), lwjgl_util_src_jar, lwjgl_util_src_sha1)
    download_natives()