# -*- coding: utf-8 -*-


def readDictionary(inputFile):
    dictionary = {}
    lines = open(inputFile, "r").readlines()
    for line in lines:
        wordtag = line.strip().split()
        dictionary[wordtag[0]] = wordtag[1]
    return dictionary

