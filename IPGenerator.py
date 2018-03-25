from random import randint
import pandas as pd
import os

def spoofIP(ipSrc):
    print(ipSrc)
    spoofIP, realIP, spoofTTL = fileContainsIP(ipDst)
    if spoofIP == None:
        if randint(1,100) <= 30:
            spoofIP = generateRandomIP()
            #Are we using this IP?
            spoofIPres, realIP, spoofTTLres = fileContainsIP(spoofIP)
            if spoofIPres == None:
                spoofTTL = randint(32,60)
                f = open("ScrambledIPs.txt", "a")
                f.write(spoofIP + "," + ipSrc + "," + spoofTTL + "\n")
                f.close()
        else:
            #70% random source
            spoofIP, spoofTTL = getRandomIPFile()
        return spoofIP, ipDst, spoofTTL
    else:
        #only backwards
        return ipSrc, realIP, ipTTL

def getRandomIPFile():
    if (os.stat("ScrambledIPs.txt").st_size == 0):
        return None, None, None
    df = pd.read_csv(filepath_or_buffer='ScrambledIPs.txt', header=None, sep=',')
    df.columns=['IPSpoof', 'TrueIP', 'TTL']
    df.dropna(how="all", inplace=True)
    df.tail()
    allScrambled = df.ix[:,0:3].values
    index = randint(0, len(allScrambled))
    return allScrambled[index][0], allScrambled[index][2]

def fileContainsIP(ipStr):
    if(os.stat("ScrambledIPs.txt").st_size == 0):
        return None, None, None
    df = pd.read_csv(filepath_or_buffer='ScrambledIPs.txt', header=None, sep=',')
    df.columns=['IPSpoof', 'TrueIP', 'TTL']
    df.dropna(how="all", inplace=True)
    df.tail()
    allScrambled = df.ix[:,0:3].values
    for ip in range(0,len(allScrambled)):
        if allScrambled[ip][0] == ipStr:
            return allScrambled[ip][0], allScrambled[ip][1], allScrambled[ip][2]
    return None, None, None

def generateRandomIP():
    validIP = False
    while(validIP == False):
        octet1 = randint(1,223)
        octet2 = randint(0, 255)
        octet3 = randint(0, 255)
        #Not a blatantly obvious network or broadcast address
        octet4 = randint(1, 254)
        if(validPublicIP(octet1, octet2, octet3)):
            validIP = True
    return str(octet1) + "." + str(octet2) + "." + \
           str(octet3) + "." + str(octet4)

def validPublicIP(oct1, oct2, oct3):
    if oct1 == 10:
        return False
    if oct1 == 100 and oct2 >= 64 and oct2 <= 127:
        return False
    if oct1 == 127:
        return False
    if oct1 == 169 and oct2 == 254:
        return False
    if oct1 == 172 and oct2 >= 16 and oct2 <= 31:
        return False
    if oct1 == 192 and oct2 == 0 and (oct3 == 0 or oct3 == 2):
        return False
    if oct1 == 192 and oct2 == 88 and oct3 == 99:
        return False
    if oct1 == 192 and oct2 == 168:
        return False
    if oct1 == 198 and oct2 >= 18 and oct2 <= 19:
        return False
    if oct1 == 198 and oct2 == 51 and oct3 == 100:
        return False
    if oct1 == 203 and oct2 == 0 and oct3 == 113:
        return False
    return True

ipSrc = "10.10.16.101"
f = open("ScrambledIPs.txt", "w+")
f.close()

for i in range(0, 10):
    spoofIP = generateRandomIP()
    spoofIPres, realIP, spoofTTLres = fileContainsIP(spoofIP)
    if spoofIPres == None:
        spoofTTL = randint(32, 60)
        f = open("ScrambledIPs.txt", "a")
        f.write(spoofIP + "," + ipSrc + "," + str(spoofTTL) + "\n")
        f.close()
