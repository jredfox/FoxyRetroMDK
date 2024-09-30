import sys
import os.path

def patch_slash(file):
    if not os.path.exists(file):
        return
    with open(file, 'r') as f:
        lines = f.read().replace("\r\n", "\n").replace("\\", "/")
    with open(file, 'wb') as f:
        f.write(lines)

if __name__ == "__main__":
    patch_slash("temp/client_rg.cfg")
    patch_slash("temp/client_ro.cfg")
    patch_slash("temp/server_rg.cfg")
    patch_slash("temp/server_ro.cfg")
    sys.exit(0)