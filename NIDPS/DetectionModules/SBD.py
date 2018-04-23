from sklearn.externals import joblib
import cPickle
from sklearn.preprocessing import LabelEncoder
import warnings

class SBDModule():
    def __init__(self, strSBDModel, encoderPickle):
        self.clf = joblib.load(strSBDModel)
        self.enc = LabelEncoder()

        with open(encoderPickle, 'rb') as fEnc:
            self.enc.classes_ = cPickle.load(fEnc)

        self.normalSigs = ["ARP", "DNS", "IPv6 TCP", "NTP", "Modbus", "TCP", "ICMP", "SSH"]
        warnings.simplefilter('ignore', DeprecationWarning)

    def checkPacket(self, parsed_pkt):
        predictedCode = self.clf.predict(parsed_pkt)
        predictedSignature = self.enc.inverse_transform(predictedCode[0])
        verdict = predictedSignature not in self.normalSigs
        return verdict, predictedSignature
