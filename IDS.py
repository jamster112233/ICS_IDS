from scapy.all import *
from netfilterqueue import NetfilterQueue
from random import randint
import pandas as pd
import os
import sys

MODBUS_SLAVE = 'ms.ics.example.com'
response = ''

class IDS():
    def __init__(self):
        self.spoofIPs = {}
        self.staticAttackers = {'8.8.8.8': ['10.10.16.99',60]}
        self.ipSource = '10.10.16.99'

        validIPs = 0
        while validIPs < 10:
            spoofIP = self.generateRandomIP()
            if not spoofIP in self.spoofIPs:
                spoofTTL = randint(32, 60)
                self.spoofIPs[spoofIP] = [self.ipSource, spoofTTL]
                validIPs += 1

    def run(self):
        f = open("IDS.txt", "w+")
        f.write("START\n")
        f.close()
        os.system("iptables-restore < /etc/iptables/intall")
        nfqueue = NetfilterQueue()
        nfqueue.bind(1, self.callback)
        try:
            nfqueue.run()
        except KeyboardInterrupt:
            nfqueue.unbind()
            os.system("iptables-restore < /etc/iptables/clean")

    def callback(self, pkt):
        sc_pkt = IP(pkt.get_payload())
        spoof = False

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
            spoof = True

        if spoof:
            ipSrc, ipDst, ipTTL = self.spoofIP(sc_pkt[IP].src, sc_pkt[IP].dst, sc_pkt[IP].ttl, 1)
            print(ipSrc, ipDst, ipTTL)
            sc_pkt[IP].src = ipSrc
            sc_pkt[IP].dst = ipDst
            sc_pkt[IP].ttl = int(ipTTL)

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
        send(sc_pkt)
        pkt.drop()

    def spoofIP(self, ipSrc, ipDst, ipTTL, packCount):
        print(self.spoofIPs)
        #V -> A
        if ipDst in self.staticAttackers:
            # only backwards
            return ipSrc, self.staticAttackers[ipDst][0], ipTTL
        if len(self.staticAttackers) > 0:
            return "8.8.8.8", ipDst, self.staticAttackers["8.8.8.8"][1]

        #V -> A
        if ipDst in self.spoofIPs:
            # only backwards
            return ipSrc, self.spoofIPs[ipDst][0], ipTTL
        #A -> V / need spoofing
        else:
            #Generating new IP 30%
            if randint(1, 100) <= 30:
                spoofIP = self.generateRandomIP()
                spoofTTL = randint(32, 60)
                # Are we using this IP?
                if spoofIP in self.spoofIPs:
                    spoofTTL = self.spoofIPs[spoofIP][1]
                else:
                    self.spoofIPs[spoofIP] = [ipSrc, spoofTTL]
                return spoofIP, ipDst, spoofTTL
            #Using random existing IP
            else:
                spoofIP, ipReal, spoofTTL = self.getRandomIP()
                return spoofIP, ipDst, spoofTTL

    def getRandomIP(self):
        index = randint(0, len(self.spoofIPs.keys()) - 1)
        key = list(self.spoofIPs.keys())[index]
        return key, self.spoofIPs[key][0], self.spoofIPs[key][1]

    def generateRandomIP(self):
        validIP = False
        print("generating")
        while (validIP == False):
            octet1 = randint(1, 223)
            octet2 = randint(0, 255)
            octet3 = randint(0, 255)
            # Not a blatantly obvious network or broadcast address
            octet4 = randint(1, 254)
            if self.validPublicIP(octet1, octet2, octet3):
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
