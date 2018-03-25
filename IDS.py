from netfilterqueue import NetfilterQueue
from scapy.all import *
import IPGenerator as ipg

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
    sc_pkt = IP(pkt.get_payload())

    spoof = False
    if spoof:
        ipSrc, ipDst, ipTTL = ipg.spoofIP(sc_pkt[IP].src, sc_pkt[IP].dst)
        sc_pkt[IP].src = ipSrc
        sc_pkt[IP].dst = ipDst
        sc_pkt[IP].ttl = ipTTL

    if(IP in sc_pkt):
        print("IP/", end='')
        del sc_pkt[IP].chksum

    if(TCP in sc_pkt):
        print("TCP/", end='')
        del sc_pkt[TCP].chksum

    if(UDP in sc_pkt):
        print("UDP/", end='')
        del sc_pkt[UDP].chksum

    if(ICMP in sc_pkt):
        print("ICMP/", end='')
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

def fileOutAndAccept(pkt):
    runAttack(pkt)

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
