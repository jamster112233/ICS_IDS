
import warnings
from sklearn.preprocessing import LabelEncoder
import numpy as np
from keras.utils import np_utils
import pandas as pd
import sys
from sklearn import neighbors
import os
from sklearn.decomposition import PCA
from sklearn.metrics import f1_score

warnings.simplefilter('ignore', FutureWarning)
warnings.simplefilter('ignore', DeprecationWarning)

trainName = sys.argv[1]
testName = sys.argv[2]
cont = float(sys.argv[3])

# Create an object called iris with the iris Data
dftrain = pd.read_csv(filepath_or_buffer=trainName, header=None, sep=',')
# dftest = pd.read_csv(filepath_or_buffer=testName, header=None, sep=',')

cols = ['Proto']
for i in range(1,dftrain.shape[1]):
    cols.append('Byte' + str(i))

dftrain.columns=cols
dftrain.dropna(how="all", inplace=True)
dftrain.tail()

# dftest.columns=cols
# dftest.dropna(how="all", inplace=True)
# dftest.tail()

Xtrain = dftrain.ix[:,1:dftrain.shape[1]]
Ytrain = dftrain.ix[:,0]
# Xtest = dftest.ix[:,1:dftrain.shape[1]]
# Ytest = dftest.ix[:,0]

Xall = Xtrain.values
Yall = Ytrain.values

# dfXall = Xtrain.append(Xtest, ignore_index=True)
# Xall = dfXall.values
# dfYall = Ytrain.append(Ytest, ignore_index=True)
# Yall = dfYall.values

directory = "models/ABD/LOF/"
if not os.path.exists(directory):
    os.makedirs(directory)

n_neighbors = 20

fscores = []
accs = []
for z in xrange(0,1):
    logfile = directory + "log-" + str(z) + ".csv"
    with open(logfile, "w") as file:
        file.write("test,PCALevel,acc,val_acc,f1\n")

    for x in xrange(1,71):
        pca = PCA(n_components=x)
        Xall = pca.fit_transform(dftrain.ix[:, 1:dftrain.shape[1]].values)
        clf = neighbors.LocalOutlierFactor(n_neighbors=n_neighbors, algorithm='auto',
                                            leaf_size=30, metric='minkowski', p=2,
                                            metric_params=None, contamination=cont, n_jobs=4)
        testPred = clf.fit_predict(Xall)

        print(len(Xall))
        score = 0.0
        for i in xrange(0, len(Xall)):
            if (testPred[i] == 1 and Yall[i] == "Normal") or (testPred[i] == -1 and Yall[i] == "Malicious"):
                score += 1
        testAcc = float(score) / len(Yall)

        preds = testPred
        if(len(preds) > 0):
            df = pd.crosstab(dftrain['Proto'], preds, rownames=['Actual'], colnames=['Predicted'])
            print(df)

        groundTrue = []
        for i in Yall:
            if i == "Normal":
                groundTrue.append(1)
            elif i == "Malicious":
                groundTrue.append(-1)

        f1 = f1_score(groundTrue, preds)

        accs.append(testAcc)
        fscores.append(f1)
        print("Test " + str(testAcc))
        print("F1 " + str(f1))

        with open(logfile, "a") as file:
            file.write(str(z) + "," + str(x) + ",0.0," + str(testAcc) + "," + str(f1) + "\n")

print(max(accs))
print(max(fscores))