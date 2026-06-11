import sys
import os
import shutil
import urllib
import zipfile
from contextlib import closing
from hashlib import sha1

def download_file(url, target, sha1, extract=False):
    print('downloading:' + url)
    urllib.urlretrieve(url, target)
    downloaded_sha1 = get_sha1(target)
    if (not sha1 is None) and downloaded_sha1 != sha1:
        print('Download Failed Removing:' + target)
        os.remove(target)
        sys.exit(1)
    if extract:
        with zipfile.ZipFile(target, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(target))

def get_sha1(file):
    if not os.path.isfile(file):
        return None
    with closing(open(file, 'rb')) as fh:
        return sha1(fh.read()).hexdigest().lower()

def del_dir(d):
    if os.path.isdir(dir_natives):
        shutil.rmtree(dir_natives)

def del_file(file):
    if(os.path.isfile(file)):
        os.remove(file)

if __name__ == "__main__":
    lwjgl_ver = sys.argv[1].lower().replace('"', '').replace("'", '').replace(' ', '')
    if lwjgl_ver == '' or lwjgl_ver == 'latest':
        lwjgl_ver = '2.9.4-nightly-20150209'
    if lwjgl_ver != '2.9.0' and lwjgl_ver != '2.9.1' and (not lwjgl_ver.startswith('2.9.4-')) and lwjgl_ver != '2.9.4':
        print('LWJGL Version Must be 2.9.0, 2.9.1, 2.9.4, 2.9.4-<nightlybuild>, or latest')
        print('For Testing Older LWJGL: LWJGL Version 2.9.0 works best for windows, LWJGL Version 2.9.1 Works best on linux, while macOS with JDK-8 works best with the latest version')
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

    dir_bin = os.path.join(os.path.dirname(os.path.realpath(__file__)), "jars", "bin")
    dir_natives = os.path.join(dir_bin, 'natives')
    lwjgl_jar = os.path.join(dir_bin, 'lwjgl.jar')
    lwjgl_util_jar = os.path.join(dir_bin, 'lwjgl_util.jar')
    lwjgl_natives_windows_natives_jar = os.path.join(dir_natives, 'windows_natives.jar')
    lwjgl_natives_macosx_natives_jar = os.path.join(dir_natives, 'macosx_natives.jar')
    lwjgl_natives_linux_natives_jar = os.path.join(dir_natives, 'linux_natives.jar')
    
    #delete previous lwjgl
    del_dir(dir_natives)
    del_file(lwjgl_jar)
    del_file(lwjgl_util_jar)
    os.makedirs(dir_natives)

    #download & install lwjgl
    lwjgl_url = 'https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl/' + lwjgl_ver + '/lwjgl-' + lwjgl_ver + '.jar'
    lwjgl_util_url = 'https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl_util/' + lwjgl_ver + '/lwjgl_util-' + lwjgl_ver + '.jar'
    lwjgl_natives_base = "https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl-platform/" + lwjgl_ver + '/lwjgl-platform-' + lwjgl_ver + "-natives-"
    download_file(lwjgl_url, lwjgl_jar, lwjgl_sha1, False)
    download_file(lwjgl_util_url, lwjgl_util_jar, lwjgl_util_sha1, False)
    download_file(lwjgl_natives_base + "windows.jar", lwjgl_natives_windows_natives_jar, lwjgl_windows_sha1, True)
    download_file(lwjgl_natives_base + "osx.jar", lwjgl_natives_macosx_natives_jar, lwjgl_macosx_sha1, True)
    download_file(lwjgl_natives_base + "linux.jar", lwjgl_natives_linux_natives_jar, lwjgl_linux_sha1, True)