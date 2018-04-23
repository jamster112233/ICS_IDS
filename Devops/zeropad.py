import sys
import operator
import csv
import random
maxValues = {}
iterableValues = {}

def main(file):
    file = zeroPad(file)
    # file = fileSet(file)
    [file1, file2] = fileSlice(file, 80, ["80", "20"])
    #file1 = fileOrder(file2)
    #file2 = fileOrder(file2)

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

def fileSlice(file, upper, labels):
    contents = getFileContent(file)
    for line in contents:
        key = line.split(',')[0]
        if key in maxValues:
            maxValues[key] += 1
        else:
            maxValues[key] = 1
            iterableValues[key] = 0

    trainName = file[0:file.find(".")] + "_" + labels[0] + ".csv"
    testName = file[0:file.find(".")] + "_" + labels[1] + ".csv"

    returnNames = []
    returnNames.append(trainName)
    returnNames.append(testName)

    fTrain = open(trainName, "w+")
    fTest = open(testName, "w+")

    for line in contents:
        key = line.split(',')[0]
        if iterableValues[key] < float(maxValues[key]) * (float(upper)/100):
            fTrain.write(line)
        else:
            fTest.write(line)
        iterableValues[key] += 1



    fTrain.close()
    fTest.close()

    return returnNames

def fileShuffle(file):
    content = getFileContent(file)
    outFile = file[0:file.find(".")] + "_shuffled.csv"
    random.shuffle(content)
    fileWrite(outFile, content)
    return outFile

def fileOrder(file):
    print("CSV READING")
    reader = csv.reader(open(file), delimiter=",")
    sortedPackets = sorted(reader, key=operator.itemgetter(0), reverse=False)
    outFile = file[0:file.find(".")] + "_ordered.csv"

    print("CSV WRITING")

    with open(outFile, "w") as out_file:
        writer = csv.writer(out_file, delimiter=',')
        for line in sortedPackets:
            writer.writerow(line)

    return outFile

def fileSet(file):
    content = getFileContent(file)
    uniquePackets = list(set(content))
    outFile = file[0:file.find(".")] + "_set.csv"
    fileWrite(outFile, uniquePackets)
    return outFile

def zeroPad(file):
    commaChamp = 0
    outFile = file[0:file.find(".")] + "_padded.csv"
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
