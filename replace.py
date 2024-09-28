import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        data = file.read().replace("\r\n", "\n")

    for i in range(2, len(sys.argv), 2):
        old_str = sys.argv[i].replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")
        new_str = sys.argv[i + 1].replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")
        data = data.replace(old_str, new_str)

    with open(filename, 'wb') as file:
        file.write(data)
        
    sys.exit(0)
