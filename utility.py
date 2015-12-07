#!/usr/bin/python

from numpy import fromfile

def getDataFromFile(filename, numOfRows, numOfColumns):
    return fromfile(filename, dtype=int, sep='\n').reshape(numOfRows, numOfColumns)


#if __name__ == "__main__":
#    print getDataFromFile("train.txt",200,1000)



