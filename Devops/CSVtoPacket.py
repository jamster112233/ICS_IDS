from scapy.all import *
from scapy.layers.l2 import Ether
import pandas as pd

class PacketTester():

    def bytesModifyBytes(self, X, Y):
        bytes = ""
        enumerate = X.split(',')

        for i in enumerate:
            bytes += chr(int(round(float(i) * 255)))

        if(Y == "ARP"):
            packet = Ether(bytes)
        elif(Y == "ICMP"):
            packet = IP(bytes)
            packet.time = 0

            packet[ICMP].time = 0
            if(packet[ICMP].type == 13 or packet[ICMP].type == "timestamp-request" or
                       packet[ICMP].type == 14 or packet[ICMP].type == "timestamp-reply"):
                packet.show()
        elif(Y[0:4] == "IPv6"):
            packet = IPv6(bytes)
        else:
            packet = IP(bytes)
            packet.time = 0
            if TCP in packet:
                packet[TCP].time = 0
                for i in xrange(len(packet[TCP].options)):
                    if(packet[TCP].options[i][0] == "Timestamp"):
                        packet[TCP].options[i] = ("Timestamp", (0,0))
                packet[TCP].seq = 0
                packet[TCP].ack = 0
            elif UDP in packet:
                packet.time = 0
                packet[UDP].time = 0
            elif ICMP in packet:
                packet = IP(bytes)
                packet.time = 0
                packet[ICMP].time = 0
            else:
                packet = IP(bytes)
                packet.show()
                packet.time = 0

        return self.packetToBytes(packet)

    def packetToBytes(self, packet):
        packetIt = 0
        bytes = ""

        hx_pkt = self.toHex(str(packet))
        str(float(int(hx_pkt[packetIt:packetIt + 2], 16)) / 255)
        packetIt += 2

        while packetIt < len(hx_pkt):
            bytes += "," + str(float(int(hx_pkt[packetIt:packetIt + 2], 16)) / 255)
            packetIt += 2

        return bytes

    def toHex(self, string):
        list = []
        for char in string:
            hxval = hex(ord(char)).replace('0x', '')
            if len(hxval) == 1:
                hxval = '0' + hxval
            list.append(hxval)
        return reduce(lambda x, y: x + y, list)

testName = sys.argv[1]
outName = "out_" + testName
pt = PacketTester()

with open(testName) as f1:
    with open(outName, 'a+') as f2:
        for i, line in enumerate(f1):
            if random.randint(0, 3) < 1:
                elements = line.split(",", 1)
                pkt = pt.bytesModifyBytes(elements[1], elements[0])
                f2.write(pkt + "\n")
        f1.close()
        f2.close()
