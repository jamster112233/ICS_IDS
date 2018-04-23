
import warnings
from sklearn.preprocessing import LabelEncoder
import numpy as np
from keras.utils import np_utils
import pandas as pd
import sys
from sklearn import neighbors
import os
from sklearn.metrics import cohen_kappa_score
from sklearn.decomposition import PCA

warnings.simplefilter('ignore', FutureWarning)
warnings.simplefilter('ignore', DeprecationWarning)

trainName = sys.argv[1]
testName = sys.argv[2]

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
Xtest = dftest.ix[:,1:dftrain.shape[1]].values
Ytest = dftest.ix[:,0].values

encoder = LabelEncoder()
encoder.fit(Ytrain)
encYtrain = encoder.transform(Ytrain)

encoder = LabelEncoder()
encoder.fit(Ytest)
encYtest = encoder.transform(Ytest)

directory = "models/SBD/KNN/"
if not os.path.exists(directory):
    os.makedirs(directory)

n_neighbors = 20

for z in xrange(0,1):
    logfile = directory + "log-" + str(z) + ".csv"
    with open(logfile, "w") as file:
        file.write("test,PCALevel,acc,val_acc,kap\n")

    for x in xrange(1, 71):
        pca = PCA(n_components=x)
        Xtrain = pca.fit_transform(dftrain.ix[:,1:dftrain.shape[1]].values)
        Xtest = pca.transform(dftest.ix[:,1:dftrain.shape[1]].values)

        clf = neighbors.KNeighborsClassifier(n_neighbors, leaf_size=30, weights='distance', n_jobs=4)
        clf.fit(Xtrain, Ytrain)
        testPred = clf.predict(Xtest)

        score = 0.0
        for i in xrange(0, len(testPred)):
            if testPred[i] == encoder.inverse_transform(encYtest[i]):
                score += 1
        testAcc = float(score) / len(testPred)

        kap = cohen_kappa_score(encYtest, encoder.transform(testPred))

        print("Test " + str(testAcc))
        print("K " + str(kap))

        with open(logfile, "a") as file:
            file.write(str(z) + "," + str(x) + ",0.0," + str(testAcc) + "," + str(kap) + "\n")

# preds = classesPred
# if(len(preds) > 0):
# 	preds = np.array(list(encoder.inverse_transform(preds)))

# df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
# df.to_csv('ConfusionMatrixLDA.csv')

