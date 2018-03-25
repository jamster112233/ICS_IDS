import sys
import operator
import csv
import random

def main(file):
    file = zeroPad(file)
    file = fileSet(file)
    file = fileShuffle(file)
    [file10, file90] = fileSlice(file, [100, 900], ["100", "900"])
    file10 = fileOrder(file10)
    file90 = fileOrder(file90)

def getFileContent(file):
    f = open(file, "r")
    content = f.readlines()
    f.close()
    return content

def fileWrite(file, content):
    f = open(file, "w+")
    for line in content:
        f.write(line)
    f.close()

def fileSlice(file, bins, labels):
    content = getFileContent(file)
    returnNames = []
    indexRunner = 0
    for index in range(0,len(bins)):
        outFile = file[0:file.find(".")] + "_" + labels[index] + ".txt"
        fileWrite(outFile, content[indexRunner:indexRunner+bins[index]])
        indexRunner += bins[index]
        returnNames.append(outFile)

    return returnNames

def fileShuffle(file):
    content = getFileContent(file)
    outFile = file[0:file.find(".")] + "_shuffled.txt"
    random.shuffle(content)
    fileWrite(outFile, content)
    return outFile

def fileOrder(file):
    reader = csv.reader(open(file), delimiter=",")
    sortedPackets = sorted(reader, key=operator.itemgetter(0), reverse=False)
    outFile = file[0:file.find(".")] + "_ordered.txt"

    with open(outFile, "w") as out_file:
        writer = csv.writer(out_file, delimiter=',')
        for line in sortedPackets:
            writer.writerow(line)

    return outFile

def fileSet(file):
    content = getFileContent(file)
    uniquePackets = list(set(content))
    outFile = file[0:file.find(".")] + "_set.txt"
    fileWrite(outFile, uniquePackets)
    return outFile

def zeroPad(file):
    commaChamp = 0
    outFile = file[0:file.find(".")] + "_padded.txt"
    content = getFileContent(file)

    for line in content:
        commaChamp = max(commaChamp, line.count(","))

    f = open(outFile, "w+")
    for line in content:
        append = ""
        for x in range(0, commaChamp - line.count(",")):
            append += "," + "0.0"
        line = line.replace("\n", append + "\n")
        f.write(line)
    f.close()
    return outFile

main(sys.argv[1])
