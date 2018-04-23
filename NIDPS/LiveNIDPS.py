from scapy.all import *
from netfilterqueue import NetfilterQueue
from DetectionModules.ABD import ABDModule
from DetectionModules.SBD import SBDModule
from DetectionModules.Static import StaticModule
import VotingModule as vm
from ParsingModule import ParsingModule
from pymodbus.client.sync import ModbusTcpClient
import NetworkEncoder as ne
from contextlib import contextmanager
import re

class NIDPS():
    def __init__(self, abdPkl, abdEnc, sbdPkl, sbdEnc, staticConf):
        self.parser = ParsingModule(1492)
        self.abd = ABDModule(abdPkl, abdEnc)
        self.sbd = SBDModule(sbdPkl, sbdEnc)
        self.sm = StaticModule(staticConf)
        self.vm = vm.VotingModule()
        self.caseVerdicts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0}
        self.normalSigs = ["ARP", "DNS", "IPv6 TCP", "NTP", "Modbus", "TCP", "ICMP", "SSH", "Normal"]
        self.injectionExp = re.compile("A[CR]IA.*")
        self.injectionBlocks = {}
        self.furtherCommandsInvalid = False

    @contextmanager
    def nohup(self):
        with open(os.devnull, "w") as devnull:
            out1 = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = out1

    def run(self):
        os.system("iptables-restore < /etc/iptables/intall")
        nfqueue = NetfilterQueue()
        nfqueue.bind(1, self.callback)
        try:
            nfqueue.run()
        except KeyboardInterrupt:
            nfqueue.unbind()
            os.system("iptables-restore < /etc/iptables/clean")

    def callback(self, pkt):
        alert, block, signature, violation = self.runPacket(pkt)

        if alert:
            print("[*] ALERT")
            print("    Type " + violation + " violation")
            if(int(violation) % 2 == 0)
                print("    Suspected packet type: " + signature)
            else:
                print("    Signature packet type: CONFLICT!")

        if block:
            if TCP in pkt:
                if self.injectionExp.match(signature):
                    if pkt[IP].src in self.injectionBlocks:
                        if self.injectionBlocks[pkt[IP].src] > 5 or self.furtherCommandsInvalid:
                            if pkt[IP].src == '10.10.2.101':
                                #MITM the CI Attack
                                outputs = []
                                outputs = ne.modbusEncode(0, 2, 2, outputs)
                                outputs = ne.modbusEncode(0, 2, 0, outputs)

                                payload = ""

                                for reg in outputs:
                                    add = str(hex(reg))[2:]
                                    for x in range(len(add), 4):
                                        add = '0' + str(add)
                                    payload += self.plx(add[0:2]) + self.plx(add[2:4])

                                pkt[Raw].load = pkt[Raw].load[0:13] + payload

                                del pkt[IP].chksum
                                del pkt[TCP].chksum

                                #Remove scapy's annoying output
                                with self.nohup():
                                    pkt.show2()

                                self.injectionBlocks[pkt[IP].src] += 1
                                pkt.set_payload(str(pkt))
                                pkt.accept()
                                return

                            elif pkt[IP].src == '10.10.4.101':
                                #RIA
                                client = ModbusTcpClient('10.10.3.101')
                                outputs = []
                                outputs = ne.modbusEncode(0, 2, 2, outputs)
                                outputs = ne.modbusEncode(0, 2, 0, outputs)
                                client.write(outputs)
                                self.injectionBlocks[pkt[IP].src] += 1
                                self.furtherCommandsInvalid = True
                                pkt.drop()
                                return
                        self.injectionBlocks[pkt[IP].src] += 1
                        pkt.accept()
                    else:
                        self.injectionBlocks[pkt[IP].src] = 1
                        pkt.accept()
                else:
                    # TCP RST return to sender
                    ip = IP(src=pkt[IP].dst, dst=pkt[IP].src)
                    rst = TCP(ack=pkt[TCP].seq + 1, seq=0, sport=pkt[TCP].dport, dport=pkt[TCP].sport, flags="RA")
                    send(ip/rst)
                    pkt.drop()
            #Just drop these
            elif UDP in pkt:
                pkt.drop()
            elif ICMP in pkt:
                pkt.drop()
        else:
            if pkt[IP].src in self.injectionBlocks:
                if pkt[IP].src == '10.10.4.101':
                    self.furtherCommandsInvalid = False
                self.injectionBlocks[pkt[IP].src] = 0
            pkt.accept()

    # Where the magic happens
    def runPacket(self, packet):
        #NB Returns of True = block the packet
        parsed_pkt = self.parser.parse(packet)
        ABDverdict = self.abd.checkPacket(parsed_pkt)
        SBDverdict, SBDSig = self.sbd.checkPacket(parsed_pkt)
        staticVerdict = self.sm.checkPacket(packet)

        # Given these verdicts what do we do next?
        alert, block, caseVerdict = self.vm.verify(ABDverdict, SBDverdict, staticVerdict)
        self.caseVerdicts[caseVerdict] += 1

        return alert, block, SBDSig, caseVerdict

filePrefix = "optimalmodels/"
abdPath = filePrefix + "ABD.hdf5"
abdPkl = filePrefix + "ABDEnc.pkl"
sbdPath = filePrefix + "SBD.pkl"
sbdPkl = filePrefix + "SBDEnc.pkl"
staticConf = filePrefix + "StaticRules.conf"
liveNIDPS = NIDPS(abdPath, abdPkl, sbdPath, sbdPkl, staticConf)
liveNIDPS.run()