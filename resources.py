import os
import sys
import json

if __name__ == "__main__":
    base_url = sys.argv[2]
    if not base_url.endswith('/'):
        base_url = base_url + '/'
    dir_resource = sys.argv[3]
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    objects = data.get('objects', {})
    with open((sys.argv[1] + '.txt'), 'w') as out:
        for name, info in objects.items():
            hash_value = info.get('hash')
            resources_url = base_url + hash_value[:2] + '/' + hash_value
            rfile = os.path.join(dir_resource, name)
            if os.path.exists(rfile):
                continue
            pdir = os.path.dirname(rfile)
            if not os.path.exists(pdir):
                os.makedirs(pdir)
            out.write(name + ',' + resources_url + '\n')