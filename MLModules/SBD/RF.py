
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import sys
import cPickle
import os
from sklearn.metrics import cohen_kappa_score

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

directory = "models/SBD/RF/"
logfile = directory + "log.csv"

if not os.path.exists(directory):
    os.makedirs(directory)

for w in xrange(0, 1):
    with open(logfile, "w") as file:
        file.write("trees,test,acc,val_acc,kap\n")

    for z in xrange(1, 26):
        # Create a random forest Classifier. By convention, clf means 'Classifier'
        clf = RandomForestClassifier(n_estimators=z, criterion='gini', max_depth=10,
                                        min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0,
                                        max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0,
                                        min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=4,
                                        random_state=None, verbose=1, warm_start=False, class_weight=None)

        # Train the Classifier to take the training features and learn how they relate
        # to the training y (the species)
        clf.fit(Xtrain, encYtrain)

        # Apply the Classifier we trained to the test Data (which, remember, it has never seen before)
        preds = clf.predict(Xtest)

        score = 0.0
        for i in xrange(0, len(preds)):
            if preds[i] == encYtest[i]:
                score += 1

        percentageAcc = float(score)/len(preds)

        print(percentageAcc)

        kap = cohen_kappa_score(encYtest, preds)
        print("Test " + str(percentageAcc))
        print("K " + str(kap))

        with open(logfile, "a") as file:
            file.write(str(z) + ",0.0," + str(percentageAcc) + "," + str(kap) + "\n")

        with open(directory + str(w) + "-" + str(z) + ".cpickle", 'wb') as f:
            cPickle.dump(clf, f)

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