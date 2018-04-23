import warnings
from sklearn.preprocessing import LabelEncoder
import numpy as np
from keras.utils import np_utils
import pandas as pd
import sys
import os
from sklearn import tree
from sklearn.tree import export_graphviz
from sklearn.metrics import cohen_kappa_score
from sklearn.externals import joblib

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
print(encYtrain)
print(encoder.inverse_transform(encYtrain))

encoder = LabelEncoder()
encoder.fit(Ytest)
encYtest = encoder.transform(Ytest)

joblib.dump(encoder, "CARTENC.pkl")

directory = "models/SBD/Decision/"
if not os.path.exists(directory):
    os.makedirs(directory)

for z in xrange(0,1):
    logfile = directory + "log-" + str(z) + ".csv"

    with open(logfile, "w") as file:
        file.write("test,depth,acc,val_acc,kap\n")

    for j in xrange(1, 100):
        clf = tree.DecisionTreeClassifier(max_depth=j)
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
            file.write(str(z) + "," + str(j) + ",0.0," + str(testAcc) + "," + str(kap) + "\n")

        if j == 99:
            labels = []
            for i in xrange(0,len(clf.classes_)):
                labels.append(encoder.inverse_transform(i))
            export_graphviz(clf, feature_names=cols[1:dftrain.shape[1]], class_names=labels, max_depth=2, out_file=directory+str(j)+'XTree.dot')

            joblib.dump(clf, "CART" + str(kap) + ".pkl")
            preds = testPred
            if(len(preds) > 0):
                preds = np.array(list(encoder.inverse_transform(preds)))
            df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
            df.to_csv('CARTConfusion.csv')

