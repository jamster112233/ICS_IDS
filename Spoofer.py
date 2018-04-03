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

PROB_GEN_NEW_IP = 0.3

#TCP Flags
FIN = 0x01
SYN = 0x02
RST = 0x04
PSH = 0x08
ACK = 0x10
URG = 0x20
ECE = 0x40
CWR = 0x80

class Spoofer():
    def __init__(self, type):
        self.type = type
        #Map source port from TCP SYN to SpoofIP index
        self.sourcePortMap = {}

        self.spoofIPs = {}
        self.staticAttackers = {}#\
#            {'8.8.8.8': ['10.10.16.101', 60]}
#             '8.8.4.4': ['10.10.16.101', 45],\
#             '1.1.1.1': ['10.10.16.101', 55]}

        self.ipSource = '10.10.16.101'

        conf.verb = 0
        validIPs = 0

        while validIPs < 50:
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
        spoof = False
        sc_pkt = IP(pkt.get_payload())
        ip_hex = self.toHex(str(sc_pkt))

        print("[*] Raw Credentials")
        print("Source IP     :" + sc_pkt[IP].src)
        print("Destination IP:" + sc_pkt[IP].dst)

        if self.isWhitelistedPacket(sc_pkt):
            pkt.accept()
            return

        if self.isSpoofPacket():
            sc_pkt = self.checksumStrip(sc_pkt)
            spoof = True

        if TCP in sc_pkt:
            if sc_pkt[TCP].flags == SYN:
                spoofIP = self.generateRandomIP()

                #Not overwriting, but will add
                if not spoofIP in self.spoofIPs:
                    spoofTTL = randint(32, 60)
                    self.spoofIPs[spoofIP] = [self.ipSource, spoofTTL]

                #Will overwrite by port, assume timeout
                self.sourcePortMap[sc_pkt[TCP].sport] = spoofIP
                self.spoofIPPointer = spoofIP

            #Lookup by port
            else:
                self.spoofIPPointer = self.sourcePortMap[sc_pkt[TCP].sport]
        else:
            #ICMP/UDP, do we really care?
            print("Other")

        if spoof:
            if self.type == 1:
                sc_pkt = self.externalSpoof(sc_pkt)
            elif self.type == 2:
                sc_pkt = self.chaosSpoof(sc_pkt)

            print("[*] Spoofed Credentials")
            print("Source IP     :" + sc_pkt[IP].src)
            print("Destination IP:" + sc_pkt[IP].dst)

        #TODO
        sc_pkt.show2()
        send(sc_pkt, verbose=False)
        pkt.drop()

    def isSpoofPacket(self, packet):
        verdict = False
        if (IP in packet):
            verdict = True

        if (TCP in packet):
            verdict = True

        if (UDP in packet):
            return False

        if (ICMP in packet):
            return False

        if (DNS in packet):
            return False

        return verdict

    def isWhitelistedPacket(self, packet):
        #DNS Query
        if packet[IP].dst == "10.10.255.254" and packet[TCP].dport == 53:
            return True
        #DNS Response
        if packet[IP].src == "10.10.255.254" and packet[TCP].sport == 53:
            return True

        return False

    def checksumStrip(self, packet):
        packetStruct = ""
        if (IP in packet):
            packetStruct += "IP/"
            del packet[IP].chksum

        if (TCP in packet):
            packetStruct += "TCP/"
            del packet[TCP].chksum

        if (UDP in packet):
            packetStruct += "UDP/"
            del packet[UDP].chksum

        if (ICMP in packet):
            packetStruct += "ICMP/"
            del packet[ICMP].chksum

        if (DNS in packet):
            packetStruct += "DNS/"

        return packet

    def mbReturnToSender(self, packet, nfqPkt):
        tmpIP = packet[IP].dst
        packet[IP].dst = packet[IP].src
        packet[IP].src = tmpIP
        packet[IP].ttl = 64
        packet[Raw].load = packet[Raw].load[0:4] + chr(int('06', 16)) + packet[Raw].load[6:13]
        packet.show2()
        send(packet, verbose=False)
        nfqPkt.drop()

    def craft(self, packet, ipSrc, ipDst, ipTTL):
        packet[IP].src = ipSrc
        packet[IP].dst = ipDst
        packet[IP].ttl = ipTTL

    def chaosSpoof(self, packet):
        ipSrc = packet[IP].src
        ipDst = packet[IP].dst
        ipTTL = packet[IP].ttl

        if len(self.staticAttackers) > 0:
            #V -> A
            if ipDst in self.staticAttackers:
                return self.craft(packet, ipSrc, self.staticAttackers[ipDst][0], ipTTL)
            #A -> V / need spoofing
            else:
                spoofIP, ipReal, spoofTTL = self.getRandomSAIP()
                return self.craft(packet, spoofIP, ipDst, spoofTTL)

        #V -> A
        if ipDst in self.spoofIPs:
            # only backwards
            return self.craft(packet, ipSrc, self.spoofIPs[ipDst][0], ipTTL)
        #A -> V / need spoofing
        else:
            #Generating new IP 30%
            if randint(1, 100) <= (PROB_GEN_NEW_IP * 100):
                spoofIP = self.generateRandomIP()
                spoofTTL = randint(32, 60)
                # Are we using this IP?
                if spoofIP in self.spoofIPs:
                    spoofTTL = self.spoofIPs[spoofIP][1]
                else:
                    self.spoofIPs[spoofIP] = [ipSrc, spoofTTL]
                return self.craft(packet, spoofIP, ipDst, spoofTTL)
            #Using random existing IP
            else:
                spoofIP, ipReal, spoofTTL = self.getRandomIP()
                return self.craft(packet, spoofIP, ipDst, spoofTTL)

    def externalSpoof(self, packet):
        ipSrc = packet[IP].src
        ipDst = packet[IP].dst
        ipTTL = packet[IP].ttl

        if len(self.staticAttackers) > 0:
            # V -> A
            if ipDst == self.spoofIPPointer:
                return self.craft(packet, ipSrc, self.staticAttackers[ipDst][0], ipTTL)
            # A -> V / need spoofing
            else:
                return self.craft(packet, self.spoofIPPointer, self.staticAttackers[self.spoofIPPointer][0],
                                       self.staticAttackers[self.spoofIPPointer][1])

        # V -> A
        if ipDst == self.spoofIPPointer:
            # only backwards
            return self.craft(packet, ipSrc, self.spoofIPs[ipDst][0], ipTTL)
        # A -> V / need spoofing
        else:
            return self.craft(packet, self.spoofIPPointer, ipDst, self.spoofIPs[self.spoofIPPointer][1])

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
    def toHex(self, string):
        list = []
        for char in string:
            nib = hex(ord(char)).replace('0x', '')
            if len(nib) == 1:
                nib = '0' + nib
            list.append(nib)
        return reduce(lambda x, y: x + y, list)

    def plx(self, x):
        val = int(x, 16)
        return chr(val)

#Type 1 = Syn Spoof
spf = Spoofer(1)
spf.run()
