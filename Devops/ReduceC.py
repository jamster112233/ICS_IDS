import sys
TOTAL_DATA_POINTS = 50000
SCALER = float(TOTAL_DATA_POINTS) / 10000

desiredValues = {"SSH": 70 * SCALER,
                         "IPv6 TCP": 4 * SCALER,
                         "ARP": 92 * SCALER,
                         "ICMP": 70 * SCALER,
                         "DNS": 190 * SCALER,
                         "Modbus": 6000 * SCALER,
                         "TCP": 1000 * SCALER,
                         "NTP": 20 * SCALER,
                         "SCIA1": 82 * SCALER,
                         "SCIA2": 140 * SCALER,
                         "SCIA3": 200 * SCALER,
                         "SCIA4": 260 * SCALER,
                         "ACIA1": 35 * SCALER,
                         "ACIA2": 55 * SCALER,
                         "ACIA3": 80 * SCALER,
                         "ACIA4": 100 * SCALER,
                         "SRIA1": 82 * SCALER,
                         "SRIA2": 140 * SCALER,
                         "SRIA3": 200 * SCALER,
                         "SRIA4": 260 * SCALER,
                         "ARIA1": 35 * SCALER,
                         "ARIA2": 55 * SCALER,
                         "ARIA3": 60 * SCALER,
                         "ARIA4": 70 * SCALER,
                         "UDP Flood": 60 * SCALER,
                         "SYN Flood": 60 * SCALER,
                         "Malicious ICMP": 80 * SCALER,
                         "Smurf": 60 * SCALER,
                         "Amap": 120 * SCALER,
                         "Nmap" : 120 * SCALER,
                         "PLC Scan": 120 * SCALER,
                         "Malicious SSH": 40 * SCALER,
                         "Telnet": 40 * SCALER
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
reduceData(fileName)
printData(fileName[0:fileName.find(".")] + "_reduced_" + str(TOTAL_DATA_POINTS) + ".csv")



