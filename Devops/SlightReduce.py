import sys
TOTAL_DATA_POINTS = 50000
SCALER = float(TOTAL_DATA_POINTS) / 10000

desiredValues = {"SSH":  1760 ,
                         "IPv6 TCP":    20 ,
                         "ARP":  2310 ,
                         "ICMP":  1760 ,
                         "DNS":  4930 ,
                         "Modbus":150010 ,
                         "TCP": 25010 ,
                         "NTP":   100 ,
                         "SCIA1":  2060 ,
                         "SCIA2":  3510 ,
                         "SCIA3":  5010 ,
                         "SCIA4":  6510 ,
                         "ACIA1":   885 ,
                         "ACIA2":  1385 ,
                         "ACIA3":  2010 ,
                         "ACIA4":  2510 ,
                         "SRIA1":  2060 ,
                         "SRIA2":  3510 ,
                         "SRIA3":  5010 ,
                         "SRIA4":  6510 ,
                         "ARIA1":   885 ,
                         "ARIA2":  1385 ,
                         "ARIA3":  1510 ,
                         "ARIA4":  1760 ,
                         "UDP Flood":  1510 ,
                         "SYN Flood":  1510 ,
                         "Malicious ICMP":  2010 ,
                         "Smurf":  1510 ,
                         "Amap":  3010 ,
                         "Nmap" :  3010 ,
                         "PLC Scan":  3010 ,
                         "Malicious SSH":  1010 ,
                         "Telnet":  1010
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
printData(fileNameIn[0:fileNameIn.find(".")] + "_reduced_" + str(TOTAL_DATA_POINTS) + ".csv")



