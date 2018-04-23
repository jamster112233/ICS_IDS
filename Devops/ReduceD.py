import sys
TOTAL_DATA_POINTS = 50000
SCALER = float(TOTAL_DATA_POINTS) / 10000

desiredValues = {"ARP" :  1132,
                    "DNS" :   2408,
                    "IPv6 TCP" :   20,
                    "NTP" :    100,
                    "Modbus" :  75215,
                    "TCP" :  12502,
                    "ICMP" :  914,
                    "SSH" :  904,
                    "SCIA1" :  972,
                    "SCIA2" :  1669,
                    "SCIA3" :  2451,
                    "SCIA4" :  3195,
                    "SRIA1" :  1021,
                    "SRIA2" :  1779,
                    "SRIA3" :  2483,
                    "SRIA4" :  3296,
                    "ACIA1" :  436,
                    "ACIA2" :  676,
                    "ACIA3" :  1027,
                    "ACIA4" :  1234,
                    "ARIA1" :  424,
                    "ARIA2" :  684,
                    "ARIA3" :  752,
                    "ARIA4" :  885,
                    "Malicious ICMP" :  993,
                    "Smurf" :  772,
                    "SYN Flood" :  731,
                    "UDP Flood" :  773,
                    "Amap" :  1549,
                    "Nmap" :  1499,
                    "PLC Scan" :  1518,
                    "Malicious SSH" :  492,
                    "Telnet" :  494
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



