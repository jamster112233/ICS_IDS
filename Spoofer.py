from scapy.all import *
from netfilterqueue import NetfilterQueue
from random import randint
import pandas as pd
import NetworkEncoder as ne
import os
import sys

MODBUS_SLAVE = 'ms.ics.example.com'
MODBUS_SLAVE_IP = '10.10.3.101'
response = ''

class Spoofer():
    def __init__(self):
        self.spoofIPs = {}
        self.staticAttackers = {}#\
#            {'8.8.8.8': ['10.10.16.101', 60]}
#             '8.8.4.4': ['10.10.16.101', 45],\
#             '1.1.1.1': ['10.10.16.101', 55]}


        self.ipSource = '10.10.16.101'

        conf.verb = 0
        validIPs = 0
        while validIPs < 300:
            spoofIP = self.generateRandomIP()
            if not spoofIP in self.spoofIPs:
                spoofTTL = randint(32, 60)
                self.spoofIPs[spoofIP] = [self.ipSource, spoofTTL]
                validIPs += 1

        self.spoofIPPointer = list(self.spoofIPs.keys())[0]

    def run(self):
        f = open("IDS.txt", "w+")
        f.write("START\n")
        f.close()
        os.system("iptables-restore < /etc/iptables/fwdint")
        nfqueue = NetfilterQueue()
        nfqueue.bind(1, self.callback)
        try:
            nfqueue.run()
        except KeyboardInterrupt:
            nfqueue.unbind()
            os.system("iptables-restore < /etc/iptables/rules.v4")

    def callback(self, pkt):
        sc_pkt = IP(pkt.get_payload())
        ip_hex = self.toHex(str(sc_pkt))
        spoof = True
        print(sc_pkt[IP].src)
        print(sc_pkt[IP].dst)
        if (IP in sc_pkt):
            print "IP/", sys.stdout.write('')
            del sc_pkt[IP].chksum

        if (TCP in sc_pkt):
            print "TCP/", sys.stdout.write('')
            del sc_pkt[TCP].chksum
            spoof = True

        if (UDP in sc_pkt):
            print "UDP/", sys.stdout.write('')
            del sc_pkt[UDP].chksum

        if (ICMP in sc_pkt):
            print "ICMP/", sys.stdout.write('')
            del sc_pkt[ICMP].chksum

        if (DNS in sc_pkt):
            print "DNS/", sys.stdout.write('')
            spoof = False

        if IP in sc_pkt and TCP in sc_pkt:
            #RIA
            if sc_pkt[IP].dst == MODBUS_SLAVE_IP and sc_pkt[TCP].dport == 502 and ip_hex[118:120] == '10' \
                    and ip_hex[124:130] == '001224':
                # Decode
                registers = []

                for i in range(0, 18):
                    index = 130 + (4 * i)
                    registers.append(int(ip_hex[index:index + 4], 16))

                waterLevel = ne.modbusDecode(0, 4, 4, registers)
                waterTemp = ne.modbusDecode(4, 2, 2, registers)
                powerOut = ne.modbusDecode(6, 6, 2, registers)
                steamStep = ne.modbusDecode(10, 2, 4, registers)
                powerIn = ne.modbusDecode(13, 6, 2, registers)
                serverSeconds = ne.modbusDecode(17, 2, 0, registers)

            # reset and boomerang
                if (waterLevel + waterTemp + powerOut + steamStep + powerIn + serverSeconds) == 0:
                    tmpIP = sc_pkt[IP].dst
                    sc_pkt[IP].dst = sc_pkt[IP].src
                    sc_pkt[IP].src = tmpIP
                    sc_pkt[Raw].load = sc_pkt[Raw].load[0:4] + chr(int('06', 16)) + sc_pkt[Raw].load[6:13]
                    self.spoofIPPointer = list(self.spoofIPs.keys())[randint(0, len(self.spoofIPs.keys()) - 1)]
                    sc_pkt.show2()
                    send(sc_pkt, verbose=False)
                    pkt.drop()
                    return
            #CIA
            if sc_pkt[IP].dst == MODBUS_SLAVE_IP and sc_pkt[TCP].dport == 502 and ip_hex[118:120] == '10' \
                    and ip_hex[128:130] == '06':
                    # Decode
                    registers = []

                    for i in range(0, 3):
                        index = 130 + (4 * i)
                        registers.append(int(ip_hex[index:index + 4], 16))

                    addWater = ne.modbusDecode(0, 2, 2, registers)
                    addFire = ne.modbusDecode(2, 2, 0, registers)

                    # reset and boomerang
                    if addFire == 3:
                        tmpIP = sc_pkt[IP].dst
                        sc_pkt[IP].dst = sc_pkt[IP].src
                        sc_pkt[IP].src = tmpIP
                        sc_pkt[Raw].load = sc_pkt[Raw].load[0:4] + chr(int('06', 16)) + sc_pkt[Raw].load[6:13]
                        self.spoofIPPointer = list(self.spoofIPs.keys())[randint(0, len(self.spoofIPs.keys()) - 1)]
                        sc_pkt.show2()
                        send(sc_pkt, verbose=False)
                        pkt.drop()
                        return

        if sc_pkt[IP].dst == "10.10.255.254":
            pkt.accept()
            return

        if spoof:
            ipSrc, ipDst, ipTTL = self.spoofIP(sc_pkt[IP].src, sc_pkt[IP].dst, sc_pkt[IP].ttl)
            print(ipSrc, ipDst, ipTTL)
            sc_pkt[IP].src = ipSrc
            sc_pkt[IP].dst = ipDst
            sc_pkt[IP].ttl = ipTTL

        #TODO
        sc_pkt.show2()
        send(sc_pkt, verbose=False)
        pkt.drop()

    def spoofIP(self, ipSrc, ipDst, ipTTL):
        if len(self.staticAttackers) > 0:
            #V -> A
            if ipDst in self.staticAttackers:
                print "V>A", ipSrc, self.staticAttackers[ipDst][0], ipTTL
                return ipSrc, self.staticAttackers[ipDst][0], ipTTL
            #A -> V / need spoofing
            else:
                spoofIP, ipReal, spoofTTL = self.getRandomSAIP()
                return spoofIP, ipDst, spoofTTL

        #V -> A
        if ipDst in self.spoofIPs:
            # only backwards
            return ipSrc, self.spoofIPs[ipDst][0], ipTTL
        #A -> V / need spoofing
        else:
            #Generating new IP 30%
            if randint(1, 100) <= 3:
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

    def semiSpoofIP(self, ipSrc, ipDst, ipTTL):
        if len(self.staticAttackers) > 0:
            # V -> A
            if ipDst == self.spoofIPPointer:
                return ipSrc, self.staticAttackers[ipDst][0], ipTTL
            # A -> V / need spoofing
            else:
                return self.spoofIPPointer, self.staticAttackers[self.spoofIPPointer][0], self.staticAttackers[self.spoofIPPointer][1]

        # V -> A
        if ipDst == self.spoofIPPointer:
            # only backwards
            return ipSrc, self.spoofIPs[ipDst][0], ipTTL
        # A -> V / need spoofing
        else:
            return self.spoofIPPointer, ipDst, self.spoofIPs[self.spoofIPPointer][1]

    def getRandomSAIP(self):
        index = randint(0, len(self.staticAttackers.keys()) - 1)
        key = list(self.staticAttackers.keys())[index]
        return key, self.staticAttackers[key][0], self.staticAttackers[key][1]

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

spf = Spoofer()
spf.run()
