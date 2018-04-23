
import warnings
from sklearn.preprocessing import LabelEncoder
import numpy as np
from keras.utils import np_utils
import pandas as pd
import sys
from sklearn.svm import OneClassSVM
import os
from sklearn.metrics import f1_score
from sklearn.decomposition import PCA

warnings.simplefilter('ignore', FutureWarning)
warnings.simplefilter('ignore', DeprecationWarning)

trainName = sys.argv[1]
testName = sys.argv[2]
nu = float(sys.argv[3])

# Create an object called iris with the iris Data
dftrain = pd.read_csv(filepath_or_buffer=trainName, header=None, sep=',')
dftest = pd.read_csv(filepath_or_buffer=testName, header=None, sep=',')

cols = ['Proto']
for i in range(1,dftrain.shape[1]):
    cols.append('Byte' + str(i))

dftrain.columns=cols
dftrain.dropna(how="all", inplace=True)
dftrain.tail()
dfnormal = dftrain.filter(like='Normal', axis=0)

dftest.columns=cols
dftest.dropna(how="all", inplace=True)
dftest.tail()

Xtrain = dftrain.ix[:,1:dftrain.shape[1]].values
Ytrain = dftrain.ix[:,0].values
Xtest = dftest.ix[:,1:dftrain.shape[1]].values
Ytest = dftest.ix[:,0].values

directory = "models/ABD/SVM/"

if not os.path.exists(directory):
    os.makedirs(directory)

fscores = []
accs = []
for w in xrange(0, 1):
    logfile = directory + "log-" + str(w) + ".csv"
    with open(logfile, "w") as file:
        file.write("test,PCALevel,acc,val_acc,f1\n")

    for j in xrange(1,70):
        Xtest = dftest.ix[:, 1:dftrain.shape[1]].values
        pca = PCA(n_components=j)
        # Xtrain = pca.fit_transform(Xtrain)
        # Xtest = pca.transform(Xtest)
        Xtest = pca.fit_transform(Xtest)

        clf = OneClassSVM(kernel='rbf', degree=3, gamma='auto', coef0=0.0, tol=0.001, nu=nu,
                        shrinking=True, cache_size=2000, verbose=True, max_iter=-1, random_state=None)
        clf.fit(Xtest)
        testPred = clf.predict(Xtest)

        score = 0.0
        for i in xrange(0, len(testPred)):
            if (testPred[i] == 1 and Ytest[i] == "Normal") or (testPred[i] == -1 and Ytest[i] == "Malicious"):
                score += 1
        testAcc = float(score) / len(testPred)

        groundTrue = []
        for i in Ytest:
            if i == "Normal":
                groundTrue.append(1)
            elif i == "Malicious":
                groundTrue.append(-1)

        f1 = f1_score(groundTrue, testPred)
        accs.append(testAcc)
        fscores.append(f1)

        with open(logfile, "a") as file:
            file.write(str(w) + "," + str(j) + ",0.0," + str(testAcc) + "," + str(f1) + "\n")

print("Val Acc max" + str(max(accs)))
print("FMAX " + str(max(fscores)))

# preds = classesPred
# if(len(preds) > 0):
# 	preds = np.array(list(encoder.inverse_transform(preds)))

# df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
# df.to_csv('ConfusionMatrixLDA.csv')

