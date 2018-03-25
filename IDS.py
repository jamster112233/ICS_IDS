from netfilterqueue import NetfilterQueue
from scapy.all import *
from random import randint
import pandas as pd
import os
import sys

MODBUS_SLAVE = 'ms.ics.example.com'
response = ''

class IDS():
    def run(self):
        f = open("IDS.txt", "w+")
        f.write("START\n")
        f.close()
        os.system("iptables-restore < /etc/iptables/intall")
        os.system("cat ScrambledIPs.txt | tail -n 500 > ScrambledIPs.txt")
        nfqueue = NetfilterQueue()
        nfqueue.bind(1, self.callback, 1024)
        try:
            nfqueue.run()
        except KeyboardInterrupt:
            nfqueue.unbind()
            os.system("iptables-restore < /etc/iptables/clean")

    def callback(self, pkt):
        sc_pkt = IP(pkt.get_payload())

        spoof = True
        if spoof:
            ipSrc, ipDst, ipTTL = self.spoofIP(sc_pkt[IP].src, sc_pkt[IP].dst)
            sc_pkt[IP].src = ipSrc
            sc_pkt[IP].dst = ipDst
            sc_pkt[IP].ttl = ipTTL

        if(IP in sc_pkt):
            print "IP/", sys.stdout.write('')
            del sc_pkt[IP].chksum

        if(TCP in sc_pkt):
            print "TCP/", sys.stdout.write('')
            del sc_pkt[TCP].chksum

        if(UDP in sc_pkt):
            print "UDP/", sys.stdout.write('')
            del sc_pkt[UDP].chksum

        if(ICMP in sc_pkt):
            print "ICMP/", sys.stdout.write('')
            del sc_pkt[ICMP].chksum

        log = False
        if log:
            print("Logging Packet")
            #packetIt = 0
            f = open("IDS.txt", "a")
            f.write('hping')
            #while packetIt < len(ip_hex):
                #f.write("," + str(float(int(ip_hex[packetIt:packetIt+2],16))/255))
                #packetIt += 2
            f.write("\n")
            f.close()

        sc_pkt.show2()
        pkt.set_payload(str(sc_pkt))
        pkt.accept()

    def spoofIP(self, ipSrc, ipDst, ipTTL):
        spoofIP, realIP, spoofTTL = self.fileContainsIP(ipDst)
        if spoofIP == None:
            if randint(1, 100) <= 30:
                spoofIP = self.generateRandomIP()
                # Are we using this IP?
                spoofIPres, realIP, spoofTTLres = self.fileContainsIP(spoofIP)
                if spoofIPres == None:
                    spoofTTL = randint(32, 60)
                    f = open("ScrambledIPs.txt", "a")
                    f.write(spoofIP + "," + ipSrc + "," + spoofTTL + "\n")
                    f.close()
            else:
                # 70% random source
                spoofIP, spoofTTL = self.getRandomIPFile()
                return spoofIP, ipDst, spoofTTL
        else:
            # only backwards
            return ipSrc, realIP, ipTTL

        def getRandomIPFile(self):
            if (os.stat("ScrambledIPs.txt").st_size == 0):
                return None, None, None
            df = pd.read_csv(filepath_or_buffer='ScrambledIPs.txt', header=None, sep=',')
            df.columns = ['IPSpoof', 'TrueIP', 'TTL']
            df.dropna(how="all", inplace=True)
            df.tail()
            allScrambled = df.ix[:, 0:3].values
            index = randint(0, len(allScrambled))
            return allScrambled[index][0], allScrambled[index][2]

        def fileContainsIP(self, ipStr):
            if (os.stat("ScrambledIPs.txt").st_size == 0):
                return None, None, None
            df = pd.read_csv(filepath_or_buffer='ScrambledIPs.txt', header=None, sep=',')
            df.columns = ['IPSpoof', 'TrueIP', 'TTL']
            df.dropna(how="all", inplace=True)
            df.tail()
            allScrambled = df.ix[:, 0:3].values
            for ip in range(0, len(allScrambled)):
                if allScrambled[ip][0] == ipStr:
                    return allScrambled[ip][0], allScrambled[ip][1], allScrambled[ip][2]
            return None, None, None

        def generateRandomIP(self):
            validIP = False
            while (validIP == False):
                octet1 = randint(1, 223)
                octet2 = randint(0, 255)
                octet3 = randint(0, 255)
                # Not a blatantly obvious network or broadcast address
                octet4 = randint(1, 254)
                if (validPublicIP(octet1, octet2, octet3)):
                    validIP = True
            return str(octet1) + "." + str(octet2) + "." + \
                   str(octet3) + "." + str(octet4)

        def validPublicIP(self, oct1, oct2, oct3):
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

    # convert string to hex
    def toHex(self, s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '')
            if len(hv) == 1:
                hv = '0' + hv
            lst.append(hv)
        return reduce(lambda x, y: x + y, lst)

    def plx(self, x):
        val = int(x, 16)
        return chr(val)

ids = IDS()
ids.run()
