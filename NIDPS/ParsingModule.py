from scapy.layers.l2 import Ether
from scapy.all import *
from pandas import DataFrame as df

class ParsingModule():
    def __init__(self, packetLen):
        self.packetLen = packetLen

    def parse(self, packet):
        packetIt = 0
        packet = self.zeroPacketStamps(packet)
        hx_pkt = self.toHex(str(packet))
        parsed_pkt = []

        while packetIt < len(hx_pkt):
            parsed_pkt.append(float(int(hx_pkt[packetIt:packetIt+2],16))/255)
            packetIt += 2

        for i in xrange(len(hx_pkt) / 2, self.packetLen):
            parsed_pkt.append(0.0)

        return df(parsed_pkt).T

    def zeroPacketStamps(self, packet):
        packet.time = 0

        if TCP in packet:
            packet[TCP].time = 0
            for i in xrange(len(packet[TCP].options)):
                if (packet[TCP].options[i][0] == "Timestamp"):
                    packet[TCP].options[i] = ("Timestamp", (0, 0))
            packet[TCP].seq = 0
            packet[TCP].ack = 0
        elif UDP in packet:
            packet[UDP].time = 0
        elif ICMP in packet:
            packet = IP(bytes)

        return packet

    def dfSeriesToPacket(self, series):
        series.tolist()
        bytes = ""
        label = series[0]
        enumerate = series[1:]

        for i in enumerate:
            bytes += chr(int(round(float(i) * 255)))

        if(label == "ARP"):
            packet = Ether(bytes)
        elif(label == "ICMP"):
            packet = IP(bytes)
            packet.time = 0

            packet[ICMP].time = 0
            if(packet[ICMP].type == 13 or packet[ICMP].type == "timestamp-request" or
                       packet[ICMP].type == 14 or packet[ICMP].type == "timestamp-reply"):
                packet.show()
        elif(label[0:4] == "IPv6"):
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
        return label, packet

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