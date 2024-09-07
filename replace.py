import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        data = file.read()

    for i in range(2, len(sys.argv), 2):
        old_str = sys.argv[i]
        new_str = sys.argv[i + 1]
        data = data.replace(old_str, new_str)

    with open(filename, 'w') as file:
        file.write(data)
        
    sys.exit(0)
