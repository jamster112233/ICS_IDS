import pandas as pd
import sys
from multiprocessing import Pool
from DetectionModules.ABD import ABDModule
from DetectionModules.SBD import SBDModule
from DetectionModules.Static import StaticModule
import VotingModule as vm
from ParsingModule import ParsingModule
import timeit
from sklearn.metrics import f1_score
from sklearn.metrics import cohen_kappa_score
import numpy as np
from pathos.multiprocessing import ProcessPool

class NIDPS():
    def __init__(self, abdPkl, abdEnc, sbdPkl, sbdEnc, staticConf):
        self.parser = ParsingModule(1492)
        self.abd = ABDModule(abdPkl, abdEnc)
        self.sbd = SBDModule(sbdPkl, sbdEnc)
        self.sm = StaticModule(staticConf)
        self.vm = vm.VotingModule()
        self.caseVerdicts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0}
        self.addedLatency = 0.0
        self.normalSigs = ["ARP", "DNS", "IPv6 TCP", "NTP", "Modbus", "TCP", "ICMP", "SSH", "Normal"]
        self.timeABD = 0.0
        self.timeSBD = 0.0
        self.timeSM = 0.0

    def runCSV(self, csvFile):
        csvData = pd.read_csv(filepath_or_buffer=csvFile, header=None, sep=',')
        csvData.dropna(how="all", inplace=True)
        csvData.tail()

        accscore = 0.0
        customscore = 0.0
        timecumulative = 0.0
        sigactuals = []
        boolactuals = []
        preds = []

        for index, i in csvData.iterrows():
            pkt_type, pkt = self.parser.dfSeriesToPacket(i)
            tic = timeit.default_timer()
            alert, block = self.runPacket(pkt)
            toc = timeit.default_timer()
            timecumulative += toc - tic

            #Ground true sig
            sigactuals.append(pkt_type)

            #Ground true bool
            if pkt_type in self.normalSigs:
                boolactuals.append("Normal")
            else:
                boolactuals.append("Malicious")

            #Translate to prediction
            if block:
                preds.append("Malicious")
                if not pkt_type in self.normalSigs:
                    accscore += 1
                    customscore += 1
            elif alert:
                preds.append("Normal")
                if not pkt_type in self.normalSigs:
                    customscore += 0.5
            elif not block:
                preds.append("Normal")
                if(pkt_type in self.normalSigs):
                    accscore += 1
                    customscore +=1

            if(index % 1000 == 0):
                print(index)

        print(self.caseVerdicts)

        print("ABD = " + str(self.timeABD))
        print("SBD = " + str(self.timeSBD))
        print("SM = " + str(self.timeSM))
        print("Time elapsed total: " + str(timecumulative))
        print("Added latency per packet (ms): " + str((timecumulative * 1000) / len(csvData)))
        print("val_acc = " + str(accscore / len(csvData)))

        df = pd.crosstab(np.array(sigactuals), np.array(preds), rownames=['Actual Protocol'],
                         colnames=['Predicted Protocol'])
        print(df)

        kap = cohen_kappa_score(boolactuals, preds)
        print("K = " + str(kap))
        print("cust_acc = " + str(customscore / len(csvData)))

    def createConfusionMatrix(self, csvFile):
        csvData = pd.read_csv(filepath_or_buffer=csvFile, header=None, sep=',')
        csvData.dropna(how="all", inplace=True)
        csvData.tail()

        actuals = []
        preds = []

        for index, i in csvData.iterrows():
            packet_type, packet = self.parser.dfSeriesToPacket(i)
            pkt = self.parser.parse(packet)
            SBDVerdict, pred = self.abd.checkPacket(pkt)

            actuals.append(packet_type)
            preds.append(pred)

        df = pd.crosstab(np.array(actuals), np.array(preds), rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
        print(df)
        df.to_csv('NNSBDConfusion.csv')

    # The bulk method
    # def runPacket(self, packet):
    #     # True = block the packet
    #     pool = Pool(processes=2)
    #
    #     Sm = pool.apply_async(smwork, (packet,))
    #     parsed_pkt = self.parser.parse(packet)
    #     SBDm = pool.apply_async(sbdwork, (parsed_pkt,))
    #     pool.close()
    #     ABDverdict = self.abd.checkPacket(parsed_pkt)
    #     pool.join()
    #
    #     staticVerdict = Sm.get()
    #     SBDverdict, SBDsig = SBDm.get()
    #
    #     # Given these verdicts
    #     alert, block, caseVerdict = self.vm.verify(ABDverdict, SBDverdict, staticVerdict)
    #     self.caseVerdicts[caseVerdict] += 1
    #
    #     return alert, block


    #The bulk method
    def runPacket(self, packet):
        #True = block the packet
        parsed_pkt = self.parser.parse(packet)

        tic = timeit.default_timer()
        ABDverdict = self.abd.checkPacket(parsed_pkt)
        toc = timeit.default_timer()
        self.timeABD += toc - tic

        tic = timeit.default_timer()
        SBDverdict, SBDSig = self.sbd.checkPacket(parsed_pkt)
        toc = timeit.default_timer()
        self.timeSBD += toc - tic

        tic = timeit.default_timer()
        staticVerdict = self.sm.checkPacket(packet)
        toc = timeit.default_timer()
        self.timeSM += toc - tic

        #Given these verdicts
        alert, block, caseVerdict = self.vm.verify(ABDverdict, SBDverdict, staticVerdict)
        self.caseVerdicts[caseVerdict] += 1

        return alert, block

csvFile = sys.argv[1]

filePrefix = "optimalmodels/"
#The actual ones
abdPath = filePrefix + "ABD.hdf5"
abdPkl = filePrefix + "ABDEnc.pkl"

#To generate the confusion matrix
# abdPath = filePrefix + "ABDSig.hdf5"
# abdPkl = filePrefix + "SBDSigEnc.pkl"

#Actual SBD
sbdPath = filePrefix + "SBD.pkl"
sbdPkl = filePrefix + "SBDEnc.pkl"
#Static rules
staticConf = filePrefix + "StaticRules.conf"

nidps = NIDPS(abdPath, abdPkl, sbdPath, sbdPkl, staticConf)

# def smwork(packet):
#     return nidps.sm.checkPacket(packet)
#
# def sbdwork(packet):
#     return nidps.sbd.checkPacket(packet)

nidps.runCSV(csvFile)