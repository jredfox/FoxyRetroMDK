import sys
import os
import tarfile
import zipfile
        
if __name__ == "__main__":
    mcp = sys.argv[1].replace('"', '').replace("'", '')
    asm_tarball = os.path.join(mcp, 'lib', 'asm-4.1.tar.gz')
    if os.path.exists(asm_tarball):
        print('Extracting asm-4.1.tar.gz')
        prefix = 'asm-4.1/src/'
        with tarfile.open(asm_tarball, "r:gz") as tar:
            with zipfile.ZipFile(os.path.join(mcp, 'lib', 'asm-all-4.1-source.zip'), 'w', zipfile.ZIP_DEFLATED) as zipf:
                for member in tar.getmembers():
                    if member.isfile() and member.name.startswith(prefix):
                        arcname = 'src/' + member.name[len(prefix):]
                        source = tar.extractfile(member)
                        zipf.writestr(arcname, source.read())