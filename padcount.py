import sys

def main():
    commaChamp = 0
    filename = sys.argv[1]
    f = open(filename, "r")
    content = f.readlines()
    print(content)
    f.close()

    for line in content:
        print(line.count(","))

main()
