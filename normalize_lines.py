import os
import sys

if __name__ == "__main__":

    script_path = os.path.realpath(__file__)
    mcp = os.path.realpath(sys.argv[1])
    winlf = False if (len(sys.argv) < 3) else (sys.argv[2][0].upper() == 'T')
    printOnly = False if (len(sys.argv) < 4) else (sys.argv[3][0].upper() == 'T')
    #EXTENSIONS = ('.sh', '.cfg', '.srg', '.exc', '.cvs', '.patch')
    EXTENSIONS = ('.sh', '.cfg')

    for root, dirs, files in os.walk(mcp):
        #Skip bin_linux
        if os.path.basename(root) == 'bin_linux':
            dirs[:] = []  # Don't recurse further
            continue

        for fname in files:
            if fname.endswith(EXTENSIONS):
                fpath = os.path.realpath(os.path.join(root, fname))
                if fpath != script_path:
                    try:
                        with open(fpath, 'rb') as f:
                            data = f.read()
                        if not winlf:
                            if '\r' in data:
                                if not printOnly:
                                    data = data.replace('\r\n', '\n').replace('\r', '\n')
                                    with open(fpath, 'wb') as f:
                                        f.write(data)
                                print("normalized lines:" + fpath)
                        elif not printOnly:
                            data = data.replace('\r\n', '\n').replace('\r','\n').replace('\n', '\r\n')
                            with open(fpath, 'wb') as f:
                                f.write(data)
                            print("normalized lines:" + fpath)
                        else:
                            print("normalized lines:" + fpath)
                    except Exception as e:
                        print("Error processing file:" + fpath + " " + str(e))
    