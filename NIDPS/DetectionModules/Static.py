from scapy.all import *
import scipy
import pandas as pd
import numpy as np
import sys
from netaddr import IPNetwork, IPAddress
# from NIDPS import ParsingModule as pm
from sklearn.metrics import cohen_kappa_score

class StaticModule():
    def __init__(self, rulesetPath):
        #Rule structure = protocol sourceIP sourcePort >>> destIP destPort
        self.ruleset = pd.read_csv(filepath_or_buffer=rulesetPath, header=None, sep=' ')
        self.normalSigs = ["ARP", "DNS", "IPv6 TCP", "NTP", "Modbus", "TCP", "ICMP", "SSH", "Normal"]

    # def runCSV(self, csvFile):
    #     csvData = pd.read_csv(filepath_or_buffer=csvFile, header=None, sep=',')
    #     cols = ['Proto']
    #
    #     for i in range(1, csvData.shape[1]):
    #         cols.append('Byte' + str(i))
    #
    #     csvData.columns = cols
    #     csvData.dropna(how="all", inplace=True)
    #     csvData.tail()
    #
    #     parser = pm.ParsingModule(1500)
    #     score = 0.0
    #
    #     preds = []
    #     actuals = []
    #     simpleactuals = []
    #
    #     for index, i in csvData.iterrows():
    #         packet_type, packet = parser.dfSeriesToPacket(i)
    #
    #         actuals.append(packet_type)
    #         verdict = self.checkPacket(packet)
    #
    #         if packet_type in self.normalSigs:
    #             simpleactuals.append("Normal")
    #         else:
    #             simpleactuals.append("Malicious")
    #
    #         if (verdict == True and (packet_type in self.normalSigs)) or \
    #             (verdict == False and not (packet_type in self.normalSigs)):
    #             score += 1
    #
    #         # if(index % 1000 == 0):
    #         #     print(index)
    #
    #         if verdict == True:
    #             preds.append("Normal")
    #         else:
    #             preds.append("Malicious")
    #
    #
    #     actuals = np.array(actuals)
    #     preds = np.array(preds)
    #     conf = pd.crosstab(actuals, preds, rownames=['Actual'], colnames=['Predicted'])
    #
    #     print(conf)
    #     print(float(score)/len(csvData))
    #     print("KAP " + str(cohen_kappa_score(simpleactuals, preds)))

    def checkPacket(self, pkt):
        permit = True

        if not IP in pkt:
            return False

        for x, rule in self.ruleset.iterrows():
            localVerdict = []
            localVerdict.append(self.checkProto(pkt, rule[0]))
            if(not localVerdict[0]):
                continue
            localVerdict.append(self.checkSourceIP(pkt, rule[1]))
            localVerdict.append(self.checkSourcePort(pkt, rule[2]))
            localVerdict.append(self.checkDestIP(pkt, rule[4]))
            localVerdict.append(self.checkDestPort(pkt, rule[5]))

            #Checks whether all along axis evaluate to true
            # print(localVerdict)

            if(scipy.all(localVerdict)):
                permit = False
                break

        block = not permit
        return block

    def checkNegation(self, value, negate):
        if negate:
            return not value
        else:
            return value

    #Return True if critera met; could be blocked
    def checkProto(self, pkt, protoCheck):
        if protoCheck == 'ip':
            return IP in pkt
        if protoCheck == 'tcp':
            return TCP in pkt
        if protoCheck == 'icmp':
            return ICMP in pkt
        if protoCheck == 'udp':
            return UDP in pkt
        return True

    # Return True if critera met; could be blocked
    def checkSourceIP(self, pkt, ipCheck):
        negation = False
        if ipCheck[0] == "!":
            negation = True
            ipCheck = ipCheck[1:]

        if ipCheck == "any":
            return self.checkNegation(True, negation)
        if ipCheck == "public":
            return self.checkNegation(self.validPublicIP(pkt[IP].src), negation)
        return self.checkNegation(IPAddress(pkt[IP].src) in IPNetwork(ipCheck), negation)

    def checkSourcePort(self, pkt, portCheck):
        negation = False
        if portCheck[0] == "!":
            negation = True
            portCheck = portCheck[1:]

        if portCheck == "any":
            return self.checkNegation(True, negation)
        if TCP in pkt:
            return self.checkNegation(IPAddress(pkt[TCP].sport) == str(portCheck), negation)
        if UDP in pkt:
            return self.checkNegation(IPAddress(pkt[UDP].sport) == str(portCheck), negation)
        else:
            return False

    def checkDestIP(self, pkt, ipCheck):
        negation = False
        if ipCheck[0] == "!":
            negation = True
            ipCheck = ipCheck[1:]

        if ipCheck == "any":
            return self.checkNegation(True, negation)
        if ipCheck == "public":
            return self.checkNegation(self.validPublicIP(pkt[IP].dst), negation)
        return self.checkNegation(IPAddress(pkt[IP].dst) in IPNetwork(ipCheck), negation)

    def checkDestPort(self, pkt, portCheck):
        negation = False
        if portCheck[0] == "!":
            negation = True
            portCheck = portCheck[1:]

        if portCheck == "any":
            return self.checkNegation(True, negation)
        if TCP in pkt:
            return self.checkNegation(IPAddress(pkt[TCP].dport) == str(portCheck), negation)
        if UDP in pkt:
            return self.checkNegation(IPAddress(pkt[UDP].dport) == str(portCheck), negation)
        else:
            return False

    def validPublicIP(self, ipAddress):
        octets = ipAddress.split('.')
        oct1 = int(octets[0])
        oct2 = int(octets[1])
        oct3 = int(octets[2])

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
