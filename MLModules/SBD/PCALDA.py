import numpy as np
from keras.utils import np_utils
import pandas as pd
import sys
from sklearn.preprocessing import LabelEncoder
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
import os
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from collections import OrderedDict
import pylab as pl
from scipy import linalg
from sklearn.externals import joblib
from sklearn.metrics import cohen_kappa_score

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

directory = "models/SBD/LDA/"
if not os.path.exists(directory):
    os.makedirs(directory)

logfile = directory + "log-0.csv"
with open(logfile, "w") as file:
    file.write("PCAlevel,acc,val_acc,kap\n")

fscores = []
accs = []
for q in xrange(1,151):
    pca = PCA(n_components=q)
    Xtrain_pca = pca.fit_transform(Xtrain)
    Xtest_pca = pca.transform(Xtest)

    Ytrain = dftrain.ix[:,0].values
    Ytest = dftest.ix[:,0].values

    clf = LinearDiscriminantAnalysis(n_components=None, priors=None, shrinkage=None, solver='svd',
                                     store_covariance=False, tol=0.0001)
    clf.fit_transform(Xtrain_pca, encYtrain)

    trainPred = clf.predict(Xtrain_pca)
    testPred = clf.predict(Xtest_pca)

    score = 0.0
    for i in xrange(0, len(trainPred)):
        if trainPred[i] == encYtrain[i]:
            score += 1
    trainAcc = float(score) / len(trainPred)

    score = 0.0
    for i in xrange(0, len(testPred)):
        if testPred[i] == encYtest[i]:
            score += 1
    testAcc = float(score) / len(testPred)

    kap = cohen_kappa_score(encYtest, testPred)
    accs.append(testAcc)
    fscores.append(kap)

    print("Train " + str(trainAcc))
    print("Test " + str(testAcc))
    print("K " + str(kap))

    with open(logfile, "a") as file:
        file.write(str(q) + "," + str(trainAcc) + "," + str(testAcc) + "," + str(kap) + "\n")


print("Val Acc max" + str(max(accs)))
print("FMAX " + str(max(fscores)))


# print(str(q) + ":" + str((float(score)/len(classesPred)*100)) + "%")
# colors = ['navy', 'turquoise', 'darkorange']
# lw = 2
#
# for color, i, target_name in zip(colors, [0, 1, 2], target_names):
#     plt.scatter(X_r[y == i, 0], X_r[y == i, 1], color=color, alpha=.8, lw=lw,
#                 label=target_name)
#
#
# preds = classesPred
# if(len(preds) > 0):
# 	preds = np.array(list(encoder.inverse_transform(preds)))
#
# df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
# df.to_csv('ConfusionMatrixLDA.csv')
#
