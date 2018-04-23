import sys
TOTAL_DATA_POINTS = 3350
SCALER = float(TOTAL_DATA_POINTS) / 10000

desiredValues = {"SSH":100,
                         "IPv6 TCP":10,
                         "ARP":100,
                         "ICMP":90,
                         "DNS":120,
                         "Modbus":190,
                         "TCP":160,
                         "NTP":40,
                         "SCIA1":100,
                         "SCIA2":120,
                         "SCIA3":120,
                         "SCIA4":120,
                         "ACIA1":80,
                         "ACIA2":100,
                         "ACIA3":100,
                         "ACIA4":100,
                         "SRIA1":100,
                         "SRIA2":120,
                         "SRIA3":120,
                         "SRIA4":120,
                         "ARIA1":80,
                         "ARIA2":100,
                         "ARIA3":100,
                         "ARIA4":100,
                         "UDP Flood":100,
                         "SYN Flood":100,
                         "Malicious ICMP":100,
                         "Smurf":100,
                         "Amap":100,
                         "Nmap":100,
                         "PLC Scan":100,
                         "Malicious SSH":80,
                         "Telnet":80
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

