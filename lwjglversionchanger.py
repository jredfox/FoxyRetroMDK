import sys
import os
import shutil
import urllib
import zipfile
from contextlib import closing
from hashlib import sha1

def download_file(url, target, sha1, extract=False):
    pdir = os.path.dirname(target)
    if onesix and (not os.path.isdir(pdir)):
        os.makedirs(pdir)
    print('downloading: ' + url)
    urllib.urlretrieve(url, target)
    if (not sha1 is None):
        downloaded_sha1 = get_sha1(target)
        if downloaded_sha1 != sha1:
            print('Download Failed Removing: ' + target)
            os.remove(target)
            sys.exit(1)
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

if __name__ == "__main__":
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

    lwjgl_sha1 = lwjgl_util_sha1 = lwjgl_windows_sha1 = lwjgl_macosx_sha1 = lwjgl_linux_sha1 = None
    if lwjgl_ver == '2.9.0':
        lwjgl_sha1 = '5654d06e61a1bba7ae1e7f5233e1106be64c91cd'
        lwjgl_util_sha1 = 'a778846b64008fc7f48ead2377f034e547991699'
        lwjgl_windows_sha1 = '3f11873dc8e84c854ec7c5a8fd2e869f8aaef764'
        lwjgl_macosx_sha1 = '6621b382cb14cc409b041d8d72829156a87c31aa'
        lwjgl_linux_sha1 = '2ba5dcb11048147f1a74eff2deb192c001321f77'
    elif lwjgl_ver == '2.9.1':
        lwjgl_sha1 = 'f58c5aabcef0e41718a564be9f8e412fff8db847'
        lwjgl_util_sha1 = '290d7ba8a1bd9566f5ddf16ad06f09af5ec9b20e'
        lwjgl_windows_sha1 = '4c517eca808522457dd95ee8fc1fbcdbb602efbe'
        lwjgl_macosx_sha1 = '2d12c83fdfbc04ecabf02c7bc8cc54d034f0daac'
        lwjgl_linux_sha1 = 'aa9aae879af8eb378e22cfc64db56ec2ca9a44d1'
    elif lwjgl_ver == '2.9.4-nightly-20150209':
        lwjgl_sha1 = '697517568c68e78ae0b4544145af031c81082dfe'
        lwjgl_util_sha1 = 'd51a7c040a721d13efdfbd34f8b257b2df882ad0'
        lwjgl_windows_sha1 = 'b84d5102b9dbfabfeb5e43c7e2828d98a7fc80e0'
        lwjgl_macosx_sha1 = 'bcab850f8f487c3f4c4dbabde778bb82bd1a40ed'
        lwjgl_linux_sha1 = '931074f46c795d2f7b30ed6395df5715cfd7675b'
    elif lwjgl_ver == '2.9.2':
        lwjgl_sha1 = 'A9D80FE5935C7A9149F6584D9777CFD471F65489'.lower()
        lwjgl_util_sha1 = '4B9E37300A87799856E0BD15ED81663CDB6B0947'.lower()
        lwjgl_windows_sha1 = '510C7D317F5E9E700B9CFAAC5FD38BDEBF0702E0'.lower()
        lwjgl_macosx_sha1 = 'D55B46B40B40249D627A83A7F7F22649709D70C3'.lower()
        lwjgl_linux_sha1 = 'D276CDF61FE2B516C7B7F4AA1B8DEA91DBDC8D56'.lower()
    elif lwjgl_ver == '2.9.3':
        print('WARNING LWJGL Version 2.9.3 contains lots of graphical issues! Please use a different version')

    if not onesix:
        dir_bin = os.path.join(dir_mcp, "jars", "bin")
        dir_natives = os.path.join(dir_bin, 'natives')
        lwjgl_jar = os.path.join(dir_bin, 'lwjgl.jar')
        lwjgl_util_jar = os.path.join(dir_bin, 'lwjgl_util.jar')
        lwjgl_natives_windows_natives_jar = os.path.join(dir_natives, 'windows_natives.jar')
        lwjgl_natives_macosx_natives_jar = os.path.join(dir_natives, 'macosx_natives.jar')
        lwjgl_natives_linux_natives_jar = os.path.join(dir_natives, 'linux_natives.jar')
    else:
        dir_base = os.path.join(dir_mcp, "jars")
        dir_libs = os.path.join(dir_base, "libraries", 'org', 'lwjgl', 'lwjgl')
        dir_natives = os.path.join(dir_base, "versions", mc_ver, (mc_ver + '-natives'))
        lwjgl_jar = os.path.join(dir_libs, 'lwjgl', lwjgl_ver, ('lwjgl-' + lwjgl_ver + '.jar') )
        lwjgl_util_jar = os.path.join(dir_libs, 'lwjgl_util', lwjgl_ver, ('lwjgl_util-' + lwjgl_ver + '.jar') )
        lwjgl_natives_windows_natives_jar = os.path.join(dir_libs, 'lwjgl-platform', lwjgl_ver, ('lwjgl-platform-' + lwjgl_ver + '-natives-windows.jar') )
        lwjgl_natives_macosx_natives_jar = os.path.join(dir_libs, 'lwjgl-platform', lwjgl_ver, ('lwjgl-platform-' + lwjgl_ver + '-natives-osx.jar') )
        lwjgl_natives_linux_natives_jar = os.path.join(dir_libs, 'lwjgl-platform', lwjgl_ver, ('lwjgl-platform-' + lwjgl_ver + '-natives-linux.jar') )
        #patch lwjgl version strings
        dir_fml = os.path.join(os.path.dirname(dir_base), 'fml')

        #delete lwjgl jar natives
        del_file(lwjgl_natives_windows_natives_jar)
        del_file(lwjgl_natives_macosx_natives_jar)
        del_file(lwjgl_natives_linux_natives_jar)
    
    #delete previous lwjgl
    del_dir(dir_natives)
    del_file(lwjgl_jar)
    del_file(lwjgl_util_jar)
    os.makedirs(dir_natives)

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
    download_file(lwjgl_natives_base + "windows.jar", lwjgl_natives_windows_natives_jar, lwjgl_windows_sha1, True)
    download_file(lwjgl_natives_base + "osx.jar", lwjgl_natives_macosx_natives_jar, lwjgl_macosx_sha1, True)
    download_file(lwjgl_natives_base + "linux.jar", lwjgl_natives_linux_natives_jar, lwjgl_linux_sha1, True)