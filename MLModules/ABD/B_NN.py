import pandas as pd
import numpy as np
import sys
from keras.callbacks import ModelCheckpoint
from keras.callbacks import CSVLogger
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.utils import np_utils
from sklearn.preprocessing import LabelEncoder
import os
import time
import h5py
import numpy as np
from keras.callbacks import Callback
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.externals import joblib

trainName = sys.argv[1]
testName = sys.argv[2]

networkTopologies = [["M-M", 15, 15]]

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

encoder = LabelEncoder()
encoder.fit(Ytest)
encYtest = encoder.transform(Ytest)

joblib.dump(encoder, "NNENC.pkl")

filename = "models/ABD/NN/f1.csv"

class Metrics(Callback):
    def on_train_begin(self, logs={}):
        with open(filename, "w") as file:
            file.write("epoch,f1\n")

    def on_epoch_end(self, epoch, logs={}):
        val_predict = (np.asarray(self.model.predict(self.validation_data[0]))).round()
        val_targ = self.validation_data[1]
        f1 = f1_score(val_targ, val_predict)
        with open(filename, "a") as file:
            file.write(str(epoch) + "," + str(f1) + "\n")
        return

f1Cal = Metrics()

directory = "models/ABD/NN/"
if not os.path.exists(directory):
    os.makedirs(directory)

#Step into new dir
for i in xrange(0, 1):
    logfile = directory + "log-" + str(i) + ".csv"

    print("[*] STARTING NN")
    print("    Topology   : " + networkTopologies[0][0])

    model = Sequential()
    model.add(Dense(networkTopologies[0][1],activation='relu', kernel_initializer='uniform', input_shape=(dftrain.shape[1]-1,)))
    model.add(Dropout(0.5))

    for k in xrange(2, len(networkTopologies)):
        model.add(Dense(networkTopologies[0][k],activation='relu', kernel_initializer='uniform',))
        model.add(Dropout(0.5))

    model.add(Dense(1, activation='sigmoid', kernel_initializer='uniform',))
    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])

    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=0.001)
    log = CSVLogger(logfile, separator=',', append=True)
    checkpoint = ModelCheckpoint(directory + "/weights.{epoch:04d}-{val_acc:.04f}.hdf5", monitor='val_acc', verbose=0,
                                 save_best_only=True, save_weights_only=False, mode='auto', period=1)
    model.fit(Xtrain, encYtrain, batch_size=64, epochs=100, verbose=1, validation_data=(Xtest,encYtest),
              callbacks=[log, reduce_lr, f1Cal, checkpoint])



    # # evaluate the model
    # scores = model.evaluate(Xtest, encYtest, batch_size=128)
    # print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
    #
    # # Create actual english names for the plants for each predicted plant class
    # preds = [model.predict_classes(Xtest, batch_size=32)]
    # certainties = model.predict(Xtest, batch_size=32)
    #
    # numRecords = certainties.shape[0]
    # probRunner = 0.0
    # for i in certainties:
    #     probRunner += np.amax(i)
    #
    # probRunner /= numRecords
    # print("Avg certainty : " + str(probRunner))
    #
    # if(len(preds) > 0):
    #     preds = list(encoder.inverse_transform(preds))

# print(dftest['Proto'].head())
# df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
# df.to_csv('BinaryConfusionMatrix.csv')










