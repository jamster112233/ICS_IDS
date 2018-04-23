import sys
TOTAL_DATA_POINTS = 1000000
SCALER = float(TOTAL_DATA_POINTS) / 1000000

desiredValues = { "SSH": 7500 * SCALER,
			   		"IPv6 Net Disc": 150 * SCALER,
               		"IPv6 TCP": 50 * SCALER,
               		"ARP": 6000 * SCALER,
               		"ICMP": 7000 * SCALER,
               		"DNS": 18000 * SCALER,
               		"Modbus": 640000 * SCALER,
               		"TCP": 100000 * SCALER,
               		"IPv6/Other": 10 * SCALER,
               		"Non-IP/Other": 10 * SCALER,
               		"NTP": 180 * SCALER,
               		"SCIA1": 6000 * SCALER,
               		"SCIA2": 12000 * SCALER,
               		"SCIA3": 18000 * SCALER,
               		"SCIA4": 24000 * SCALER,
               		"ACIA1": 2500 * SCALER,
               		"ACIA2": 5500 * SCALER,
               		"ACIA3": 8000 * SCALER,
               		"ACIA4": 10000 * SCALER,
               		"SRIA1": 6000 * SCALER,
               		"SRIA2": 12000 * SCALER,
               		"SRIA3": 18000 * SCALER,
               		"SRIA4": 24000 * SCALER,
               		"ARIA1": 900 * SCALER,
               		"ARIA2": 1100 * SCALER,
               		"ARIA3": 1400 * SCALER,
               		"ARIA4": 1700 * SCALER,
               		"UDP Flood": 6000 * SCALER,
               		"SYN Flood": 6000 * SCALER,
               		"Malicious ICMP": 8000 * SCALER,
               		"Smurf": 6000 * SCALER,
               		"Amap": 12000 * SCALER,
               		"Nmap" : 12000 * SCALER,
               		"PLC Scan": 12000 * SCALER,
               		"Malicious SSH": 4000 * SCALER,
               		"Telnet": 4000 * SCALER
              }

actualValues = {}

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
		print(key + (" " * (15 - len(key))) + str(actualValues[key]))

def reduceData(fileNameIn):
	fileIn = open(fileNameIn, "r")
	fileNameOut = fileNameIn[0:fileNameIn.find(".")] + "_reduced_" + str(TOTAL_DATA_POINTS) + ".csv"
	fileOut = open(fileNameOut, "w+")
	for line in fileIn:
		key = line.split(',')[0]
		if desiredValues[key] > 0:
			fileOut.write(line)
			desiredValues[key] -= 1

fileName = sys.argv[1]
printData(fileName)
reduceData(fileName)



