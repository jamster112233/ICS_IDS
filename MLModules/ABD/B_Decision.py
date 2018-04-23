import warnings
from sklearn.preprocessing import LabelEncoder
import numpy as np
from keras.utils import np_utils
import pandas as pd
import sys
import os
from sklearn import tree
from sklearn.tree import export_graphviz

warnings.simplefilter('ignore', FutureWarning)
warnings.simplefilter('ignore', DeprecationWarning)

trainName = sys.argv[1]
testName = sys.argv[2]

# Create an object called iris with the iris Data
dftrain = pd.read_csv(filepath_or_buffer=trainName, header=None, sep=',')
dftest = pd.read_csv(filepath_or_buffer=testName, header=None, sep=',')

cols = ['Proto']
for i in range(1,dftrain.shape[1]):
    cols.append('Byte ' + str(i))

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

directory = "models/ABD/Decision/"
if not os.path.exists(directory):
    os.makedirs(directory)

for z in xrange(0,5):
    logfile = directory + "log-" + str(z) + ".csv"

    with open(logfile, "w") as file:
        file.write("test,acc,val_acc\n")

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(Xtrain, encYtrain)
    trainPred = clf.predict(Xtrain)
    testPred  = clf.predict(Xtest)

    score = 0.0
    for i in xrange(0, len(trainPred)):
        if trainPred[i] == encYtrain[i]:
            score += 1
    trainAcc = float(score)/len(trainPred)

    score = 0.0
    for i in xrange(0, len(testPred)):
        if testPred[i] == encYtest[i]:
            score += 1
    testAcc = float(score) / len(testPred)

    print("Train " + str(trainAcc))
    print("Test " + str(testAcc))

    with open(logfile, "a") as file:
        file.write(str(z) + "," + str(trainAcc) + "," + str(testAcc) + "\n")

    if z == 3:
        labels = []
        for i in xrange(0, len(clf.classes_)):
            labels.append(encoder.inverse_transform(i))

        export_graphviz(clf, feature_names=cols[1:dftrain.shape[1]], class_names=labels, max_depth=5, out_file=directory+str(z)+'tree.dot')

# preds = classesPred
# if(len(preds) > 0):
# 	preds = np.array(list(encoder.inverse_transform(preds)))

# df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
# df.to_csv('ConfusionMatrixLDA.csv')

