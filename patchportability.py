import os
import sys

if __name__ == "__main__":

    mcp = os.path.realpath(sys.argv[1])
    script_path = os.path.realpath(sys.argv[2])
    winlf = (os.name == 'nt') if (len(sys.argv) < 4) else (sys.argv[3][0].upper() == 'T')
    printOnly = False if (len(sys.argv) < 5) else (sys.argv[4][0].upper() == 'T')
    
    SCANDIRS = (mcp, os.path.join(mcp, 'forge'), os.path.join(mcp, 'forge', 'fml'), os.path.join(mcp, 'temp'), os.path.join(mcp, 'tmp'), os.path.join(mcp, 'conf'), os.path.join(mcp, 'forge', 'conf') )
    for root in SCANDIRS:
        if os.path.exists(root):
            for fname in os.listdir(root):
                cfg = fname.endswith('.cfg')
                if cfg or fname.endswith('.sh'):
                    fpath = os.path.realpath(os.path.join(root, fname))
                    if fpath == script_path:
                        print('ignoring:' + script_path)
                        continue
                    with open(fpath, 'rb') as f:
                        data = f.read()
                    if not winlf:
                        if ('\r' in data or (cfg and '\\' in data)):
                            data = data.replace('\r\n', '\n').replace('\r', '\n')
                            if cfg:
                                data = data.replace('\\', '/')
                            if not printOnly:
                                with open(fpath, 'wb') as f:
                                    f.write(data)
                            print('patched portability:' + fpath)
                    elif cfg:
                        new_data = data.replace('\r\n', '\n').replace('\r', '\n').replace('\\', '/')
                        if data != new_data:
                            if not printOnly:
                                with open(fpath, 'wb') as f:
                                    f.write(new_data)
                            print('patched portability:' + fpath)
    