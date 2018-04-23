import pandas as pd
import numpy as np
import sys
import warnings
from keras.callbacks import ModelCheckpoint
from keras.callbacks import CSVLogger
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.utils import np_utils
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import cohen_kappa_score
import os
import time
from keras.callbacks import Callback
import h5py
from sklearn.externals import joblib

warnings.simplefilter('ignore', DeprecationWarning)

trainName = sys.argv[1]
testName = sys.argv[2]

networkTopologies = [["M-M", 50 , 50]]

# Create an object called iris with the iris Data
dftrain = pd.read_csv(filepath_or_buffer=trainName, header=None, sep=',')
dftest = pd.read_csv(filepath_or_buffer=testName, header=None, sep=',')

cols = ['Proto']
for i in range(1,dftrain.shape[1]):
    cols.append('Byte' + str(i))

dftrain.columns=cols
dftrain.dropna(how="all", inplace=True)
dftrain.tail()

dftest.columns=cols
dftest.dropna(how="all", inplace=True)
dftest.tail()

Xtrain = dftrain.ix[:,1:dftrain.shape[1]].values
Ytrain = dftrain.ix[:,0].values
Xtest = dftest.ix[:,1:dftest.shape[1]].values
Ytest = dftest.ix[:,0].values

encoder = LabelEncoder()
encoder.fit(Ytrain)
encYtrain = encoder.transform(Ytrain)
dummyYtrain = np_utils.to_categorical(encYtrain)

encoder = LabelEncoder()
encoder.fit(Ytest)
encYtest = encoder.transform(Ytest)
dummyYtest = np_utils.to_categorical(encYtest)

joblib.dump(encoder, "SBDSigEnc.pkl")

exit(0)

filename = "models/SBD/NN/log-0.csv"

class Metrics(Callback):
    def on_train_begin(self, logs={}):
        with open(filename, "w") as file:
            file.write("epoch,kap\n")

    def on_epoch_end(self, epoch, logs={}):
        print(self.model.predict(self.validation_data[0]))
        print(self.validation_data[1])

        val_predict = []
        for i in self.model.predict(self.validation_data[0]):
            val_predict.append(np.argmax(i))

        val_targ = []
        for i in self.validation_data[1]:
            val_targ.append(np.argmax(i))

        kap = cohen_kappa_score(val_targ, val_predict)

        print("K ", kap)

        with open(filename, "a") as file:
            file.write(str(epoch) + "," + str(kap) + "\n")
        return

kapMet = Metrics()

#Step into new dir
for i in xrange(0, len(networkTopologies)):
    for j in xrange(0, 1):
        print("[*] STARTING NN")
        print("    Topology   : " + networkTopologies[i][0])

        dir = str(int(time.time()))[::-1]
        directory = "models/SBD/NN/" + str(j)

        if not os.path.exists(directory):
            os.makedirs(directory)

        model = Sequential()
        model.add(Dense(networkTopologies[i][1],activation='relu',input_shape=(dftrain.shape[1]-1,)))
        model.add(Dropout(0.5))

        for k in xrange(2, len(networkTopologies)):
            model.add(Dense(networkTopologies[i][k], activation='relu'))
            model.add(Dropout(0.5))

        model.add(Dense(dummyYtest.shape[1],activation='softmax'))
        model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=0.001)
        log = CSVLogger(directory + "/log.csv", separator=',', append=True)
        checkpoint = ModelCheckpoint(directory + "/weights.{epoch:04d}-{val_acc:.04f}.hdf5", monitor='val_acc', verbose=0, save_best_only=False, save_weights_only=False, mode='auto', period=1)
        model.fit(Xtrain, dummyYtrain, batch_size=64, epochs=100, verbose=1, validation_data=(Xtest,dummyYtest), callbacks=[reduce_lr, kapMet, log, checkpoint])

        # preds = [model.predict_classes(Xtest, batch_size=32)]
        #
        # if (len(preds) > 0):
        #     preds = list(encoder.inverse_transform(preds))
        #
        # print(dftest['Proto'].head())
        # df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
        # df.to_csv('ConfusionMatrix.csv')

# # evaluate the model
# scores = model.evaluate(Xtest, dummyYtest, batch_size=128)
# print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
#
# # Create actual english names for the plants for each predicted plant class

# certainties = model.predict(Xtest, batch_size=32)
#
# numRecords = certainties.shape[0]
# probRunner = 0.0
# for i in certainties:
# 	probRunner += np.amax(i)
#
# probRunner /= numRecords
# print("Avg certainty : " + str(probRunner))
#








