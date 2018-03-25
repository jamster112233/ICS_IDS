import random
import NetworkEncoder as ne
from netfilterqueue import NetfilterQueue
from pymodbus.client.sync import ModbusTcpClient
from scapy.all import *
import os

MODBUS_SLAVE = 'ms.ics.example.com'

random.seed(100)
response = ''

# convert string to hex
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0' + hv
        lst.append(hv)
    return reduce(lambda x, y: x + y, lst)

def plx(x):
    val = int(x, 16)
    return chr(val)

def runAttack(pkt):
    print("running")
    sc_pkt = IP(pkt.get_payload())

    spoof = False
    if spoof:
        ipSrc, ipDst, ipTTL = spoofIP(sc_pkt[IP].src, sc_pkt[IP].dst)
        sc_pkt[IP].src = ipSrc
        sc_pkt[IP].dst = ipDst
        sc_pkt[IP].ttl = ipTTL

    print(str(sc_pkt))
    prot = ""
    counter = 0
    if(TCP in sc_pkt):
        print("Logging TCP")
        prot = "TCP"
    elif(UDP in sc_pkt):
        print("Logging UDP")
        prot = "UDP"
    elif(ICMP in sc_pkt):
        print("Logging ICMP")
        prot = "ICMP"
    else:
        print("WTF is this")
        prot = "WTF"
    
    ip_hex = toHex(str(sc_pkt))
    srcIP = sc_pkt[IP].src
    dstIP = sc_pkt[IP].dst
    print("RECV")
    print(srcIP)
    print(dstIP)
    if((srcIP == '10.10.3.101' and dstIP == '10.10.3.100')):
        print("Logging FOSHO")
        packetIt = 0
        f = open("IDS.txt", "a")
        f.write('hping')
        #while packetIt < len(ip_hex):
            #f.write("," + str(float(int(ip_hex[packetIt:packetIt+2],16))/255))
            #packetIt += 2
        f.write("\n")
        f.close()
    del sc_pkt[IP].chksum

    del sc_pkt[TCP].chksum
    del sc_pkt[ICMP].chksum

    del sc_pkt[UDP].chksum
    sc_pkt.show2()
    pkt.set_payload(str(sc_pkt))
    return pkt

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

def spoofIP(ipSrc, ipDst, ipTTL):
    spoofIP, realIP, spoofTTL = fileContainsIP(ipDst)
    if spoofIP == None:
        if random.randint(1,100) <= 30:
            spoofIP = generateRandomIP()
            #Are we using this IP?
            spoofIPres, realIP, spoofTTLres = fileContainsIP(spoofIP):
            if spoofIPres == None:
                spoofTTL = random.randint(32,60)
                f = open("ScrambledIPs.txt", "a")
                f.write(ipSpoof + "," + ipSrc + "," + spoofTTL + "\n")
        else:
            #70% random source
            spoofIP, spoofTTL = getRandomIPTTL()
        return spoofIP, ipDst, spoofTTL
    else:
        #only backwards
        return ipSrc, realIP, ipTTL

def getRandomIPTTL()
    df = pd.read_csv(filepath_or_buffer='ScrambledIPs.txt', header=None, sep=',')
    df.columns=['IPSpoof', 'TrueIP', 'TTL']
    df.dropna(how="all", inplace=True) 
    df.tail()
    allScrambled = df.ix[:,0:3].values
    index = random.randin(0, len(allScrambled))
    return allScrambled[index][0], allScrambled[index][1], allScrambled[index][2]

def fileContainsIP(ipStr):
    df = pd.read_csv(filepath_or_buffer='ScrambledIPs.txt', header=None, sep=',')
    df.columns=['IPSpoof', 'TrueIP', 'TTL']
    df.dropna(how="all", inplace=True)
    df.tail()
    allScrambled = df.ix[:,0:3].values
    for ip in range(0,len(allScrambled)):
        if allScrambled[ip][0] == ipStr:
            return allScrambled[ip][0], allScrambled[ip][1], allScrambled[ip][2]
    return None, None, None

def fileOutAndAccept(pkt):
    pkt = runAttack(pkt)
    pkt.accept()

f = open("IDS.txt", "w+")
f.write("START\n")
f.close()
nfqueue = NetfilterQueue()
nfqueue.bind(1, fileOutAndAccept, 1024)

try:
    nfqueue.run()
except KeyboardInterrupt:
    print('')

nfqueue.unbind()
