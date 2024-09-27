############################################################################################################
### @purpose Merge Zip Files Skipping Duplicate Entries as to not be overwritten
### @author jredfox
############################################################################################################
import zipfile as z
import sys

if __name__ == "__main__":

    zips = sys.argv[1:]
    with z.ZipFile(zips[0], 'a') as z1:  # Open the first zip in append mode
        existing_files = set(z1.namelist())
        for fname in zips[1:]:
            with z.ZipFile(fname, 'r') as zf:  # Open each subsequent zip
                for n in zf.namelist():
                    # Skip dirs and duplicates
                    if n.endswith('/') or n in existing_files:
                        continue
                    # Read the file and write to the first zip
                    z1.writestr(n, zf.read(n))