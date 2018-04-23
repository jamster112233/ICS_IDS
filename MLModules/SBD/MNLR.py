
import warnings
from sklearn.preprocessing import LabelEncoder
import numpy as np
from keras.utils import np_utils
import pandas as pd
import sys
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import cohen_kappa_score
import os
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

Xtrain1 = dftrain.ix[:,1:dftrain.shape[1]].values
Ytrain = dftrain.ix[:,0].values
Xtest1 = dftest.ix[:,1:dftrain.shape[1]].values
Ytest = dftest.ix[:,0].values

encoder = LabelEncoder()
encoder.fit(Ytrain)
encYtrain = encoder.transform(Ytrain)

encoder = LabelEncoder()
encoder.fit(Ytest)
encYtest = encoder.transform(Ytest)

directory = "models/SBD/MNLR/"
if not os.path.exists(directory):
    os.makedirs(directory)

for z in xrange(0,1):
    logfile = directory + "log-" + str(z) + ".csv"
    with open(logfile, "w") as file:
        file.write("test,PCALevel,acc,val_acc,kap\n")

    for j in xrange(1,151):
        Xtest = dftest.ix[:, 1:dftrain.shape[1]].values
        pca = PCA(n_components=j)
        # Xtrain = pca.fit_transform(Xtrain)
        # Xtest = pca.transform(Xtest)
        Xtrain = pca.fit_transform(Xtrain1)
        Xtest = pca.fit_transform(Xtest1)

        clf = LogisticRegression(penalty='l2', dual=False, tol=0.0001, C=1.0, fit_intercept=True, intercept_scaling=1,
                                 class_weight=None, random_state=None, solver='lbfgs', max_iter=100,
                                 multi_class='multinomial', verbose=0, warm_start=False, n_jobs=4)
        clf = clf.fit(Xtrain, encYtrain)
        testPred = clf.predict(Xtest)

        score = 0.0
        for i in xrange(0, len(testPred)):
            if testPred[i] == encYtest[i]:
                score += 1
        testAcc = float(score) / len(testPred)

        kap = cohen_kappa_score(encYtest, testPred)
        print("Test " + str(testAcc))
        print("K " + str(kap))
        with open(logfile, "a") as file:
            file.write(str(z) + "," + str(j) + ",0.0," + str(testAcc) + "," +str(kap) + "\n")

# preds = classesPred
# if(len(preds) > 0):
# 	preds = np.array(list(encoder.inverse_transform(preds)))

# df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
# df.to_csv('ConfusionMatrixLDA.csv')

