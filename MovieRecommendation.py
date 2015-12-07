#!/usr/bin/python
from utility import *
import math
import operator

BLOCKSIZE = 20
trainUserRatings = []
trainRatingMeans = []
numTrainUsers = 200
trainUserRatingSquare = [0 for x in xrange(numTrainUsers)]
itemToItemSimilarity = [ [0 for x in range(1000)] for x in range(1000)]
numTestUsers = 100
k = 10



def calculateItemToItemSimilarity():
    for i in range(1000):
        for j in range(0,i):
            num = sum(trainUserRatings[:, i] * trainUserRatings[:, j])
            coli = trainUserRatings[:,i]
            colj = trainUserRatings[:,j]
            sumi = 0
            sumj = 0
            for k in range(len(coli)):
                if coli[k] !=0 and colj[k] != 0:
                    sumi += coli[k] ** 2
                    sumj += colj[k] ** 2
            denom = math.sqrt(sumi * sumj)
            if denom != 0:
                itemToItemSimilarity[i][j] = (num * 1.0) / denom
            else:
                itemToItemSimilarity[i][j] = 0.0
            itemToItemSimilarity[j][i] = itemToItemSimilarity[i][j]
    ''' 
    for i in range(1000):
        for j in range(1000):
            if i == j:
                print str(itemToItemSimilarity[i][j]) + " "
        print "\n"
    '''

def calculateMovieMeans(nonZeroRatingInfo):
    meansOfRatedMovie = {}
    for key in nonZeroRatingInfo.keys():
        sumOfRatings = sum(trainUserRatings[:,(key - 1)])
        numOfUsersRated = len(filter(lambda item: item != 0, trainUserRatings[:, key - 1]))
        
        if numOfUsersRated != 0:
            meansOfRatedMovie[key] = sumOfRatings / (1.0 * numOfUsersRated)
        else:
            meansOfRatedMovie[key] = 0.0

    return meansOfRatedMovie


def predictVoteItemCF(invalidMovie, nonZeroRatingInfo, meanMap, meanCurrTestUser, blockSize):
    sumOfSimilarityValue = 0
    invalidMovieMean = 0
    param = 0
    
    inValidMovieRatingClmn = trainUserRatings[:, (invalidMovie -1)]
    numTrainUsers = len(filter(lambda item: item != 0, inValidMovieRatingClmn))
    
    if numTrainUsers != 0:
        invalidMovieMean = (1.0 * sum(trainUserRatings[:, (invalidMovie -1)])) / numTrainUsers
    else:
        invalidMovieMean = 0.0
    
    for movies in nonZeroRatingInfo.keys():
        sumOfSimilarityValue += itemToItemSimilarity[invalidMovie - 1][movies - 1]
        param += itemToItemSimilarity[movies - 1][invalidMovie - 1] * (nonZeroRatingInfo[movies] - meanMap[movies]) 
   
    if sumOfSimilarityValue != 0.0:
        finalValue = (1.0 * param) / sumOfSimilarityValue
    else:
        finalValue = 0.0
    
    finalValue += invalidMovieMean

    if finalValue == 0.0 or finalValue == 0:
        finalValue = 2
 
    #print "Param: " + str(param) + " Sum Of Sim: " + str(sumOfSimilarityValue) + "\n"

    return finalValue


def predictVoteCustomK(coefficientMap, myMeanCurrUser, zeroRatingList, currUser):
    sumOfCoefficient = 0
    myRatingMap = {}
    for coefValue in coefficientMap.values():
        if coefValue < 0:
            coefValue = abs(coefValue)
        sumOfCoefficient += coefValue
    
    for invalidMovieNum in zeroRatingList:
        finalValue = 0
        for trainUser in coefficientMap.keys():
            param1 = trainUserRatings[trainUser][invalidMovieNum - 1]

            if param1 !=0:
                param1 -= trainRatingMeans[trainUser]
                param1 *= coefficientMap[trainUser]
                finalValue += param1
        if sumOfCoefficient != 0:
            predictValue = myMeanCurrUser +  finalValue / sumOfCoefficient
        else:
            predictValue = myMeanCurrUser

        myRatingMap[invalidMovieNum] = predictValue

    return myRatingMap


def getVectorSimilarityCustomValue(validMovieIdRatingMap, myMeanRating, blockSize, currUser):
    simValue = {}
    returnKSimValue = {}
    denominator = sum(i*i for i in validMovieIdRatingMap.values())
    denominator = math.sqrt(denominator)

    for userIndex in range(0, numTrainUsers):
        finalValue = 0
        for key in validMovieIdRatingMap.keys():
            if trainUserRatingSquare[userIndex] != 0:
                param1 = validMovieIdRatingMap[key] / denominator
                param2 = trainUserRatings[userIndex][key - 1] / trainUserRatingSquare[userIndex]
                param = param1 * param2
                finalValue += param
        simValue[userIndex] = finalValue

    for keyValue in sorted(simValue.iteritems(), key = operator.itemgetter(1), reverse=True)[:k]:
        returnKSimValue[keyValue[0]] = keyValue[1]
    return returnKSimValue

def getCustomSimilarityValue(validMovieIdRatingMap, myMeanRating, blockSize, currUser):
    simValue = []
    threshold = 2.5

    for userIndex in range(0, numTrainUsers):
        finalValue = 0
        for key in validMovieIdRatingMap.keys():
            param1 = abs(trainUserRatings[userIndex][key - 1] - validMovieIdRatingMap[key])

            if param1 <= threshold:
                finalValue = 1.0
            else:
                finalValue = 0.0
        simValue.append(finalValue)

    return simValue

def getVectorSimilarityValue(validMovieIdRatingMap, myMeanRating, blockSize, currUser):
    simValue = []
    denominator = sum(i*i for i in validMovieIdRatingMap.values())
    denominator = math.sqrt(denominator)

    for userIndex in range(0, numTrainUsers):
        finalValue = 0
        for key in validMovieIdRatingMap.keys():
            if trainUserRatingSquare[userIndex] != 0:
                param1 = validMovieIdRatingMap[key] / denominator
                param2 = trainUserRatings[userIndex][key - 1] / trainUserRatingSquare[userIndex]
                param = param1 * param2
                finalValue += param
        simValue.append(finalValue)
    return simValue


def calculateTrainUserRatingSquare(validMovieIdRatingMap):
    for trainUser in range(0, numTrainUsers):
        ratingSquare = 0
        movieRated = 0
        for key in validMovieIdRatingMap.keys():
            ratingSquare += trainUserRatings[trainUser][key - 1] ** 2
        trainUserRatingSquare[trainUser] = math.sqrt(ratingSquare)
            
        '''
            if trainUserRatings[trainUser][key - 1] != 0:
                movieRated += 1
        
        if movieRated <= 2:
            trainUserRatingSquare[trainUser] = 0
        else:
            trainUserRatingSquare[trainUser] = math.sqrt(ratingSquare)
        
        if ratingSquare == 0 :
            print trainUser
        '''


def getPearsonSimilarityValue(validMovieIdRatingMap, myMeanRating, blockSize, currUser):
    simValue = []
    
    for userIndex in range(0, numTrainUsers):
        currTrainUserMeanRating = trainRatingMeans[userIndex]
        numParam = 0
        denParam1 = 0
        denParam2 = 0
        param1 = 0
        param2 = 0
        param1Square = 0
        param2Square = 0
        
        for key in validMovieIdRatingMap.iterkeys():
            
            if trainUserRatings[userIndex][key - 1] != 0:
                param1 = validMovieIdRatingMap[key] - myMeanRating
                param1Square = param1 * param1

                param2 = trainUserRatings[userIndex][key - 1] - currTrainUserMeanRating
                param2Square = param2 * param2
            
                numParam += (param1 * param2)
                denParam1 += param1Square
                denParam2 += param2Square

        if numParam == 0 or denParam1 == 0 or denParam2 == 0:
            simValue.append(0.0)
            '''
            print "test user: " + str(currUser) + " trainUser: " + str(userIndex + 1) + "\n"
            print "numParam: " + str(numParam) + " param1: " + str(param1) + " param2: " + str(param2) + "\n"
            print "denPAram1: " + str(denParam1) + " denParam2: " + str(denParam2) + "\n"
            '''
        else:
            simValue.append(numParam / (1.0 * math.sqrt(denParam1 * denParam2)))

    return simValue
'''
    if currUser == 265:
        print "simValue for testUser: " + str(currUser) + " - "
        print simValue
        print "\n"
'''


def predictVote(coefficientList, myMeanCurrUser, zeroRatingList, currUser):
    sumOfCoefficient = 0
    myRatingMap = {}
    for coefValue in coefficientList:
        if coefValue < 0:
            coefValue = abs(coefValue)
        sumOfCoefficient += coefValue
    
    for invalidMovieNum in zeroRatingList:
        finalValue = 0
        for trainUser in range(0, numTrainUsers):
            param1 = trainUserRatings[trainUser][invalidMovieNum - 1]

            if param1 !=0:
                param1 -= trainRatingMeans[trainUser]
                param1 *= coefficientList[trainUser]
                finalValue += param1
        if sumOfCoefficient != 0:
            predictValue = myMeanCurrUser +  finalValue / sumOfCoefficient
        else:
            predictValue = myMeanCurrUser

        myRatingMap[invalidMovieNum] = predictValue

    return myRatingMap


def doJob(jobFileName, userId, blockSize):
    fileTest = open(jobFileName, 'r')
    fileLinesTest = []

    # Store the test file into a list
    fileLinesList = fileTest.readlines()
    fileTest.close()
   
    numElements = len(fileLinesList)
#   print "Num of lines in test file is: " + str(numElements) + "\n"
    '''
    fout = open("pearsonResult_" + str(blockSize) + ".txt", "w")
    dataCalculatedPearson = []
    
    customFile = open("CustomResult_" + str(blockSize) + ".txt", "w")
    dataCalculatedCustom = []
    
    
    customKFile = open("CustomKResult_" + str(blockSize) + ".txt", "w")
    dataCalculatedCustomK = []
    
    vectorFile = open("vectorResult_" + str(blockSize) + ".txt", "w")
    dataCalculatedVector = []
    '''
    itemItemFile = open("ItemItemResult_" + str(blockSize) + ".txt", "w")
    dataCalculatedItemCF = []
    
    count = 0
    while count < numElements:
        # Read first blockSize number of lines 
        index = 0 
        ratingSumCurrUser = 0
        nonZeroRatingInfo = {}
        zeroRatingInfo = [] 
        ratingMeanCurrUser = 0 
        similarityListPearson = []
        similarityListVector = []
        similarityListCustom = []
        similarityListCustomK = {}
        predictedRatingMapPearson = {}
        predictedRatingMapVector = {}
        predictedRatingMapCustom = {}
        predictedRatingMapCustomK = {}

        predictedRatingMapItemCF = {}
        movieMeans = {}

        while index < blockSize:
            fileLinesTest = fileLinesList[index + count].split()

            # Calculate Mean for each user and store in the dictionary ratinMean
            localUserID = int(fileLinesTest[0])
            localMovieID = int(fileLinesTest[1])
            localRating = int(fileLinesTest[2])
            ratingSumCurrUser += localRating

            # current selected user. Populate the movieID's for non-zero, zero rating
            # and a dictionary for userID and its mean
            nonZeroRatingInfo[localMovieID] = localRating
            index += 1
       
        ratingMeanCurrUser = ratingSumCurrUser / (1.0 * blockSize)
        
        count += blockSize
        index = count
    #print nonZeroRatingInfo


        while index < numElements:
            fileLinesTest = fileLinesList[index].split()
            currentUserID = int(fileLinesTest[0])
            
            if(currentUserID != localUserID):
                break
            # Current user record with zero rating
            zeroRatingInfo.append(int(fileLinesTest[1]))
            index += 1
        
        # Get the similarity of current user with all the train users
        # For PEARSON Method
        #similarityListPearson = getPearsonSimilarityValue(nonZeroRatingInfo, ratingMeanCurrUser, blockSize, localUserID)

        # For Vector Method
        #calculateTrainUserRatingSquare(nonZeroRatingInfo)
        #similarityListVector = getVectorSimilarityValue(nonZeroRatingInfo, ratingMeanCurrUser, blockSize, localUserID)

        # For CUSTOM Method
        #similarityListCustom = getCustomSimilarityValue(nonZeroRatingInfo, ratingMeanCurrUser, blockSize, localUserID)

      
        #similarityListCustomK = getVectorSimilarityCustomValue(nonZeroRatingInfo, ratingMeanCurrUser, blockSize, localUserID)

        # Get the predicted value of zero rating movie Id
        # For PEARSON Method
        #predictedRatingMapPearson = predictVote(similarityListPearson, ratingMeanCurrUser, zeroRatingInfo, localUserID)

        # For Vector Method
        #predictedRatingMapVector = predictVote(similarityListVector, ratingMeanCurrUser, zeroRatingInfo, localUserID)

        # For CUSTOM Method
        #predictedRatingMapCustom = predictVote(similarityListCustom, ratingMeanCurrUser, zeroRatingInfo, localUserID)

        # For CUSTOM K METHOD
        #predictedRatingMapCustomK = predictVoteCustomK(similarityListCustomK, ratingMeanCurrUser, zeroRatingInfo, localUserID)

        # For Item-Item rating
        
        movieMeans = calculateMovieMeans(nonZeroRatingInfo)
        for invalidMovie in zeroRatingInfo:
            predictedRatingMapItemCF[invalidMovie] = predictVoteItemCF(invalidMovie, nonZeroRatingInfo, movieMeans, ratingMeanCurrUser, blockSize) 
        

        # Write the pearson algorithm result
        '''
        for key in sorted(predictedRatingMapPearson.iterkeys()):
            movieRating = round(predictedRatingMapPearson[key])
            if movieRating > 5.0:
                movieRating = 5.0
            dataCalculatedPearson.append(str(localUserID) + " " + str(key) + " " + str(movieRating) + "\n")
        
        # Write the vector algorihtm result
        for key in sorted(predictedRatingMapVector.iterkeys()):
            movieRating = int(round(predictedRatingMapVector[key]))
            if movieRating > 5:
                movieRating = 5
            if movieRating < 1:
                movieRating = 1

            dataCalculatedVector.append(str(localUserID) + " " + str(key) + " " + str(movieRating) + "\n")
                    
        # Write the Custom Algorithm result
        for key in sorted(predictedRatingMapCustom.iterkeys()):
            movieRating = round(predictedRatingMapCustom[key])

            if movieRating > 5.0:
                movieRating = 5.0
            
            dataCalculatedCustom.append(str(localUserID) + " " + str(key) + " " + str(movieRating) + "\n")
        
        # Write the CustomK Algorithm result
        for key in sorted(predictedRatingMapCustomK.iterkeys()):
            movieRating = int(round(predictedRatingMapCustomK[key]))

            if movieRating > 5:
                movieRating = 5
            
            if movieRating < 1:
                movieRating = 1
            dataCalculatedCustomK.append(str(localUserID) + " " + str(key) + " " + str(movieRating) + "\n")
        '''
        for key in sorted(predictedRatingMapItemCF.keys()):
            movieRating = int(round(predictedRatingMapItemCF[key]))

            if movieRating > 5:
                movieRating = 5

            if movieRating < 1:
                movieRating = 1
            dataCalculatedItemCF.append(str(localUserID) + " " + str(key) + " " + str(movieRating) + "\n")
         

#        print predictedRatingMap
        
        count += len(zeroRatingInfo)
    '''   
    for item in dataCalculatedPearson:
        fout.write(item) 
    fout.close()
        
    for item in dataCalculatedVector:
        vectorFile.write(item)
    vectorFile.close()
        
    for item in dataCalculatedCustom:
        customFile.write(item)
    customFile.close()
    
    for item in dataCalculatedCustomK:
        customKFile.write(item)
    customKFile.close()
    '''
    for item in dataCalculatedItemCF:
        itemItemFile.write(item)
    itemItemFile.close()
    
    

def myWorkFunction(blockSize):
    if blockSize == 5:
        userId = 201
        doJob("test5.txt", userId, blockSize)
    elif blockSize == 10:
        userId = 301
        doJob("test10.txt", userId, blockSize)
    else:
        userId = 401
        doJob("test20.txt", userId, blockSize)


if __name__=="__main__":
    #store the train data from train.txt
    numTrainUsers = 200
    numOfMovies = 1000
    #blockSize = BLOCKSIZE
    trainUserRatings = getDataFromFile("train.txt", numTrainUsers, numOfMovies)
    #print trainUserRatings
    trainRatingMeans = []
    for userRatings in trainUserRatings:
        numOfValidMovies = len(filter(lambda movieNum: movieNum > 0, userRatings))
        trainRatingMeans.append(sum(userRatings)/(1.0 * numOfValidMovies))
    
    calculateItemToItemSimilarity()
    #print "Done Matrix compute\n"
    #print trainUserRatings[200]
    for blockSize in [5, 10, 20]:
        myWorkFunction(blockSize)

