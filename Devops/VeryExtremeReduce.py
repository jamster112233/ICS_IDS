import sys
TOTAL_DATA_POINTS = 1710

#(round (ln x)) * 10) - 10
desiredValues = {"SSH": 50 ,
                         "IPv6 TCP": 20 ,
                         "ARP": 50 ,
                         "ICMP": 50 ,
                         "DNS": 60 ,
                         "Modbus": 90 ,
                         "TCP": 80 ,
                         "NTP": 40 ,
                         "SCIA1": 50 ,
                         "SCIA2": 60 ,
                         "SCIA3": 60 ,
                         "SCIA4": 60 ,
                         "ACIA1": 40 ,
                         "ACIA2": 50 ,
                         "ACIA3": 50 ,
                         "ACIA4": 50 ,
                         "SRIA1": 50 ,
                         "SRIA2": 60 ,
                         "SRIA3": 60 ,
                         "SRIA4": 60 ,
                         "ARIA1": 40 ,
                         "ARIA2": 50 ,
                         "ARIA3": 50 ,
                         "ARIA4": 50 ,
                         "UDP Flood": 50 ,
                         "SYN Flood": 50 ,
                         "Malicious ICMP": 50 ,
                         "Smurf": 50 ,
                         "Amap": 50 ,
                         "Nmap" : 50 ,
                         "PLC Scan": 50 ,
                         "Malicious SSH": 40 ,
                         "Telnet": 40
              }

actualValues = {}

# runner = 0
# for i in desiredValues.keys():
#      runner += desiredValues[i]
#
# print(runner)
# exit(0)

def printData(fileName):
     file = open(fileName, "r")
     for line in file:
          key = line.split(',')[0]
          if key in actualValues:
               actualValues[key] += 1
          else:
               actualValues[key] = 1
     file.close()

     for key in actualValues.keys():
          print(key + (" " * (20 - len(key))) + str(actualValues[key]))

def reduceData(fileNameIn):
     fileIn = open(fileNameIn, "r")
     fileNameOut = fileNameIn[0:fileNameIn.find(".")] + "_reduced_" + str(TOTAL_DATA_POINTS) + ".csv"
     fileOut = open(fileNameOut, "w+")
     for line in fileIn:
          key = line.split(',')[0]
          if key in desiredValues:
               if desiredValues[key] > 0:
                    fileOut.write(line)
                    desiredValues[key] -= 1

fileName = sys.argv[1]
printData(fileName)
reduceData(fileName)



































actualValues = {}

# runner = 0
# for i in desiredValues.keys():
#      runner += desiredValues[i]
#
# print(runner)
# exit(0)

def printData(fileName):
	file = open(fileName, "r")
	for line in file:
		key = line.split(',')[0]
		if key in actualValues:
			actualValues[key] += 1
		else:
			actualValues[key] = 1
	file.close()

	for key in actualValues.keys():
		print(key + (" " * (20 - len(key))) + str(actualValues[key]))

def reduceData(fileNameIn):
     fileIn = open(fileNameIn, "r")
     fileNameOut = fileNameIn[0:fileNameIn.find(".")] + "_reduced_" + str(TOTAL_DATA_POINTS) + ".csv"
     fileOut = open(fileNameOut, "w+")
     for line in fileIn:
          key = line.split(',')[0]
          if key in desiredValues:
               if desiredValues[key] > 0:
                    fileOut.write(line)
                    desiredValues[key] -= 1

fileName = sys.argv[1]
printData(fileName)
reduceData(fileName)



