import sys

def replace_in_file(filename, old_str, new_str):
    with open(filename, 'r') as file:
        data = file.read()

    data = data.replace(old_str, new_str)

    with open(filename, 'w') as file:
        file.write(data)

if __name__ == "__main__":
    filename = sys.argv[1]
    for i in range(2, len(sys.argv), 2):
        old_str = sys.argv[i]
        new_str = sys.argv[i + 1]
        replace_in_file(filename, old_str, new_str)
