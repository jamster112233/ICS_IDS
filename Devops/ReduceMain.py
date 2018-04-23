import sys
TOTAL_DATA_POINTS = 175000
SCALER = float(TOTAL_DATA_POINTS) / 10000

desiredValues = {"ARP" :    1616,
                    "DNS" :     3359,
                    "IPv6 TCP" :   50,
                    "NTP" :     220,
                    "Modbus" :    105053,
                    "TCP" :    17462,
                    "ICMP" :   1240,
                    "SSH" :   1259,
                    "SCIA1" :   1472,
                    "SCIA2" :    2421,
                    "SCIA3" :    3449,
                    "SCIA4" :    4510,
                    "SRIA1" :    1373,
                    "SRIA2" :    2460,
                    "SRIA3" :    3517,
                    "SRIA4" :    4600,
                    "ACIA1" :   614,
                    "ACIA2" :   966,
                    "ACIA3" :    1409,
                    "ACIA4" :    1726,
                    "ARIA1" :   617,
                    "ARIA2" :   980,
                    "ARIA3" :   1066,
                    "ARIA4" :   1234,
                    "Malicious ICMP" :   1430,
                    "Smurf" :   1055,
                    "SYN Flood" :   1062,
                    "UDP Flood" :   1079,
                    "Amap" :    2119,
                    "Nmap" :    2078,
                    "PLC Scan" :    2087,
                    "Malicious SSH" :   721,
                    "Telnet" :  696
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



