import sys
import json

if __name__ == "__main__":
    base_url = sys.argv[2]
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    objects = data.get('objects', {})
    with open((sys.argv[1] + '.txt'), 'w') as out:
        for name, info in objects.items():
            hash_value = info.get('hash')
            resources_url = base_url + hash_value[:2] + "/" + hash_value
            out.write(name + ',' + resources_url + '\n')