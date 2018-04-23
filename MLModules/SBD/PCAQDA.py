import numpy as np
from keras.utils import np_utils
import pandas as pd
import sys
from sklearn.preprocessing import LabelEncoder
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QDA
from sklearn.decomposition import PCA

trainName = sys.argv[1]
testName = sys.argv[2]

for q in xrange(1,300):
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

    pca = PCA(n_components=q)
    Xtrain_pca = pca.fit_transform(Xtrain)
    Xtest_pca = pca.transform(Xtest)

    print(Xtrain_pca.shape)

    Ytrain = dftrain.ix[:,0].values
    Ytest = dftest.ix[:,0].values

    clf = QDA(priors=None, reg_param=0.0)
    clf.fit(Xtrain_pca, encYtrain)

    classesPred = clf.predict(Xtest_pca)
    probRunner = 0.0
    score = 0

    for i in xrange(0, len(classesPred)):
    	if classesPred[i] == encYtest[i]:
    		score += 1

    print(str(q) + ":" + str((float(score)/len(classesPred)*100)) + "%")

preds = classesPred
if(len(preds) > 0):
	preds = np.array(list(encoder.inverse_transform(preds)))

df = pd.crosstab(dftest['Proto'], preds, rownames=['Actual Protocol'], colnames=['Predicted Protocol'])
df.to_csv('ConfusionMatrixLDA.csv')

