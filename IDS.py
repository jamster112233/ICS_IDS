import random
import NetworkEncoder as ne
from netfilterqueue import NetfilterQueue
from pymodbus.client.sync import ModbusTcpClient
from scapy.all import *

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

def runAttack(response, pkt):
    sc_pkt = IP(pkt.get_payload())
    if(TCP in sc_pkt):
        print("Logging TCP")
    elif(UDP in sc_pkt):
        print("Logging UDP")
    elif(ICMP in sc_pkt):
        print("Logging ICMP")
    else:
        print("WTF is this")

    ip_hex = toHex(str(sc_pkt))
    print(ip_hex)

def fileOutAndAccept(pkt):
    runAttack(mode, pkt)
    pkt.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, fileOutAndAccept)

try:
    nfqueue.run()
except KeyboardInterrupt:
    print('')

nfqueue.unbind()
