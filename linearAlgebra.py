import numpy as np
import math
from scipy.stats import multivariate_normal
import sys

def calcMu(yVals):
    return np.sum(yVals)/len(yVals)

def calcSigSq(yVals, mu):
    retVal = 0
    for i in yVals:
        retVal += (i - mu) ** 2
    return retVal/len(yVals)

def matrixRotate(matrix, angle):
    rotationMat = np.matrix([[math.cos(angle), math.sin(angle) * -1],
                             [math.sin(angle), math.cos(angle)]])
    return np.dot(rotationMat, matrix).transpose()

def calculateY(w, xn):
    return np.dot(w, xn)

def calcFisherRatio(muA, muB, sigmaASq, sigmaBSq, pointsA, pointsB):
    numerator = math.fabs(muA - muB)
    denomA = (pointsA * sigmaASq)/(pointsA + pointsB)
    denomB = (pointsB * sigmaBSq ** 2)/(pointsA + pointsB)
    return float(numerator/(denomA + denomB))

def calcWithinClassScatter(classes, means, classSizes):
    runningMatrix = np.zeros(shape=(len(classes[0][0]), len(classes[0][0])))
    meanCount = 0
    for category in classes:
        for val in category:
            currentMat = np.matrix(val - means[meanCount])
            currentMat = np.dot(currentMat.transpose(), currentMat)
            runningMatrix += currentMat
        meanCount += 1
    return 1/np.sum(classSizes) * runningMatrix

def calcBetweenClassScatter(classes, meanMean, classSizes):
    runningMatrix = np.zeros(shape=(len(classes[0][0]), len(classes[0][0])))
    sizeCount = 0
    for category in classes:
        for val in category:
            currentMat = np.matrix(val - meanMean)
            currentMat = classSizes[sizeCount] * np.dot(currentMat.transpose(), currentMat)
            runningMatrix += currentMat
        sizeCount += 1

    return runningMatrix

def lncp(x, mu, sigma):
    x = np.matrix(x).transpose()
    mu = np.matrix(mu).transpose()

    first = -0.5 * np.matrix(x - mu).transpose()
    second = np.linalg.inv(sigma)
    third = np.matrix(x - mu)
    return np.dot(np.dot(first, second), third) - 0.5 * np.linalg.det(sigma)

def logit(x, meanA, meanB, covA, covB):
    probA = lncp(x, meanA, covA)
    probB = lncp(x, meanB, covB)
    if probA == 0:
        return lncp([[-1 * sys.maxsize][-1 * sys.maxsize]], meanA, covA)
    if probB == 0:
        return lncp([[sys.maxsize][sys.maxsize]], meanB, covB)
    return (probA - probB).item(0)

def probability(x, mean, cov):
    var = multivariate_normal(mean=mean, cov=cov)
    return var.pdf(x)

def sigmoid(x, beta):
    return 1/1+math.pow(math.e, -1 * np.dot(beta, x))


