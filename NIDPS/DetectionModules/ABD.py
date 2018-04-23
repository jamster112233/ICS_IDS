from keras.models import load_model
from sklearn.preprocessing import LabelEncoder
import cPickle
import warnings
import tensorflow as tf
import sys
from copy_reg import pickle
from types import MethodType

class ABDModule():
    def __init__(self, strABDModel, encoderPickle):
        self.clf = load_model(strABDModel)
        self.enc = LabelEncoder()

        with open(encoderPickle, 'rb') as fEnc:
           self.enc.classes_ = cPickle.load(fEnc)

        self.clf._make_predict_function()
        self.graph = tf.get_default_graph()
        self.normalSigs = ["Normal"]
        warnings.simplefilter('ignore', DeprecationWarning)

    def checkPacket(self, parsed_pkt):
        with self.graph.as_default():
            predictedCode = self.clf.predict_classes(parsed_pkt, batch_size=1)
        predictedSignature = self.enc.inverse_transform(predictedCode[0])
        verdict = predictedSignature not in self.normalSigs
        return verdict
