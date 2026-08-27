############################################################################################################
### @purpose Merge Zip Files Skipping Duplicate Entries as to not be overwritten
### @author jredfox
############################################################################################################
import zipfile
import sys
from copy import copy

def merge_zips(*zips):
    with zipfile.ZipFile(zips[0], 'a') as z1:  # Open the first zip in append mode
        existing_files = set(z1.namelist())
        for fname in zips[1:]:
            with zipfile.ZipFile(fname, 'r') as zf:  # Open each subsequent zip
                for item in zf.infolist():
                    info = copy(item)
                    n = info.filename
                    if n.endswith('/') or n in existing_files:
                        continue
                    existing_files.add(n)
                    # Read the file and write to the first zip
                    z1.writestr(info, zf.read(n))

if __name__ == "__main__":

    zips = sys.argv[1:]
    merge_zips(zips)