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
from sklearn.metrics import f1_score

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

directory = "models/ABD/LDA/"
if not os.path.exists(directory):
    os.makedirs(directory)

logfile = directory + "log-0.csv"
with open(logfile, "w") as file:
    file.write("PCAlevel,acc,val_acc,f1\n")

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

    f1 = f1_score(encYtest, testPred)
    accs.append(testAcc)
    fscores.append(f1)

    print("Train " + str(trainAcc))
    print("Test " + str(testAcc))
    print("F1 " + str(f1))

    with open(logfile, "a") as file:
        file.write(str(q) + "," + str(trainAcc) + "," + str(testAcc) + "," + str(f1) + "\n")

    if q == 2:
        fig = plt.figure()
        stepTrain = 20
        stepTest = 10
        for z in xrange(0, len(Xtrain_pca), stepTrain):
            if Ytrain[z] == "Normal":
                plt.scatter(Xtrain_pca[z][0], Xtrain_pca[z][1], color=["#DDDDDD"], label=Ytrain[z] + "    (Training)", alpha=0.6, marker='o')

        for z in xrange(0, len(Xtrain_pca), stepTrain):
            if Ytrain[z] == "Malicious":
                plt.scatter(Xtrain_pca[z][0], Xtrain_pca[z][1], color=["#AAAAAA"], label=Ytrain[z] + " (Training)", alpha=0.6, marker='o')

        for z in xrange(0, len(Xtest_pca), stepTest):
            if Ytest[z] == "Normal":
                plt.scatter(Xtest_pca[z][0], Xtest_pca[z][1], color=["#888888"], label=Ytest[z] + "    (Testing)", alpha=0.6, marker='^')

        for z in xrange(0, len(Xtest_pca), stepTest):
            if Ytest[z] == "Malicious":
                plt.scatter(Xtest_pca[z][0], Xtest_pca[z][1], color=["#555555"], label=Ytest[z] + " (Testing)", alpha=0.6, marker='^')

        lda = clf
        qda = joblib.load('QDA2.pkl')

        xx, yy = np.meshgrid(np.linspace(-3.5, 5, 200), np.linspace(-2, 4.25, 200))
        X_grid = np.c_[xx.ravel(), yy.ravel()]
        zz_lda = lda.predict_proba(X_grid)[:, 1].reshape(xx.shape)
        zz_qda = qda.predict_proba(X_grid)[:, 1].reshape(xx.shape)

        plt.contour(xx, yy, zz_lda, [0.5], linewidths=1., colors='k')
        plt.contour(xx, yy, zz_qda, [0.5], linewidths=1., colors='k')

        prop_font = font_manager.FontProperties(family='Times New Roman', style='normal', size=11)

        ax = plt.subplot()

        handles, labels = ax.get_legend_handles_labels()
        handle_list, label_list = [], []
        for handle, label in zip(handles, labels):
            if label not in label_list:
                handle_list.append(handle)
                label_list.append(label)
        plt.legend(handle_list, label_list, loc=1, prop=prop_font)
        plt.xlabel("PC1", fontproperties=prop_font)
        plt.ylabel("PC2", fontproperties=prop_font)
        plt.show()

        plt.savefig('myimage.svg', format='svg', dpi=1200)


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
