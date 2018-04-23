import sys


types = ["ARP", "DNS", "IPv6 TCP", "NTP", "Modbus", "TCP", "ICMP", "SSH", "SCIA1", "SCIA2", "SCIA3", "SCIA4", "SRIA1", 
"SRIA2", "SRIA3", "SRIA4", "ACIA1", "ACIA2", "ACIA3", "ACIA4", "ARIA1", "ARIA2", "ARIA3", "ARIA4", "Malicious ICMP", "Smurf", 
"SYN Flood", "UDP Flood", "Amap", "Nmap", "PLC Scan", "Malicious SSH", "Telnet" ]

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
    keys = actualValues.keys()
    keys.sort()
    for key in keys:
        print(key + (" " * (20 - len(key))) + str(actualValues[key]))

def printDataOrdered(fileName):
    file = open(fileName, "r")
    for line in file:
        key = line.split(',')[0]
        if key in actualValues:
            actualValues[key] += 1
        else:
            actualValues[key] = 1
    file.close()
    sum = 0
    for key in types:
        print(key + (" " * (20 - len(key))) + str(actualValues[key]))
        sum += actualValues[key]
    print("SUM: " + str(sum))

    print("LaTeXable:")
    for key in types:
        print(str(actualValues[key]) + ((" ") * (5 - len(str(actualValues[key])))))

fileName = sys.argv[1]
order = sys.argv[2]

if(order == "1"):
    printDataOrdered(fileName)
else:
    printData(fileName)