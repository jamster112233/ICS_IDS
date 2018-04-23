
import warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import sys
import cPickle
import os
from sklearn.tree import export_graphviz

warnings.simplefilter('ignore', FutureWarning)
warnings.simplefilter('ignore', DeprecationWarning)

trainName = sys.argv[1]
testName = sys.argv[2]

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

directory = "models/ABD/RF/"

if not os.path.exists(directory):
    os.makedirs(directory)

for w in xrange(0, 5):
    logfile = directory + "log-" + str(w) + ".csv"
    with open(logfile, "w") as file:
        file.write("test,trees,acc,val_acc\n")

    for z in xrange(1, 31):
        # Create a random forest Classifier. By convention, clf means 'Classifier'
        clf = RandomForestClassifier(n_estimators=z, criterion='gini', max_depth=9,
                                        min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0,
                                        max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0,
                                        min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=4,
                                        random_state=None, verbose=1, warm_start=False, class_weight=None)

        # Train the Classifier to take the training features and learn how they relate
        # to the training y (the species)
        clf.fit(Xtrain, encYtrain)
        trainPred = clf.predict(Xtrain)
        testPred = clf.predict(Xtest)

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

        with open(logfile, "a") as file:
            file.write(str(w) + "," + str(z) + "," + str(trainAcc) + "," + str(testAcc) + "\n")

        with open(directory + str(w) + "-" + str(z) + ".pkl", 'wb') as f:
            cPickle.dump(clf, f)

        print("Train " + str(trainAcc))
        print("Test " + str(testAcc))

        if z == 4:
            labels = []
            for s in xrange(0, len(clf.estimators_)):
                if s == 0:
                    for i in xrange(0, len(clf.classes_)):
                        labels.append(encoder.inverse_transform(i))

                export_graphviz(clf.estimators_[s], feature_names=cols[1:dftrain.shape[1]], class_names=labels, max_depth=3,
                                out_file=directory+str(s)+'tree.dot')


# if(len(preds) > 0):
# 	preds = list(encoder.inverse_transform(preds))
#
# print(dftest['Proto'].head())
# df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
# df.to_csv('ConfusionMatrix.csv')

# # View the predicted probabilities of the first 10 observations
# print(clf.predict_proba(dftest[features])[0:10])
#
# # Create actual english names for the plants for each predicted plant class
# preds = iris.target_names[clf.predict(dftest[features])]
# # View the PREDICTED species for the first five observations
# print(preds[0:5])
#
# # View the ACTUAL species for the first five observations
# print(dftest['Proto'].head())
#
# # Create confusion matrix
# print(pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol']))
#
# # View a list of the features and their importance scores
# print(list(zip(dftrain[features], clf.feature_importances_)))