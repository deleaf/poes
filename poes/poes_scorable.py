# POES puts input data into a heirarchy of class objects.  Scoring methods can assign scores at any level
# of the heirarchy.  For example, individual subjects are represented at one level of the heirarchy;
# scoring methods can assign scores to individual subjects.  Individual subjects have one or more 
# responses, which are represented below subjects in the heirarchy.  Scoring methods can also assign
# scores at the response level.  The Scorable class defines general data structures and methods that are
# common to each level of the heirarchy.

import re
import os

from poes_str2wkey import str2wkey
from poes_wordlist import Wordlist

class Scorable(object):
    
    # If there is a lower level in the heirarchy, then its container (dictionary)  must already be instantiated 
    # and its alias MUST be given here. nextLevelAlias is a pointer to the dictionary containing the next level 
    # (it could be an empty dictionary).  nextLevelType is a type object for a child class of Scorable which 
    # corresponds to the type of the objects pointed to by nextLevelAlias.  The optional dataLine is parsed to 
    # update this Scorable (and its subScorables).  NextLevelOrder is a list used to store an ordering of the
    # objects stored in the dictionary at nextLevelAlias, where nestLevelAlias[nextLevelOrder[0]] is the first
    # element, etc.
    def __init__(self, nextLevelAlias = None, nextLevelOrder = None, nextLevelType = None, dataLine = None):
        self.__keyCounts = None
        self.__scoreTable = {}
        self.__scoreMethOrder = []
        self.__subScorables = nextLevelAlias
        self.__subType = nextLevelType

        if nextLevelAlias is not None:
            if nextLevelOrder is not None:
                self.__subIDorder = nextLevelOrder
            else:
                self.__subIDorder = nextLevelAlias.keys()

        if dataLine is not None:
            self.updateData(dataLine)


        
    def getSubIDOrder(self):
        """
        Returns a list of ID's in the order in which they were added to the subScorables
        This will typically used to write output in the same order as they were input.
        """
        return self.__subIDorder


    # On each line of POES input data file, commas separate the ID strings corresponding to successively deeper levels of the heirarchy.
    # dataLine is a string of text where the start of the string to the first comma specifies the ID for this level of the 
    # heirarchy.  The remainder of the string, after the first comma, is data for lower levels of the heirarchy.
    # If this is the bottom of the heirarchy, the string is processed and stored in self.data
    def updateData(self, dataLine):
        if self.__subScorables is not None:  # strip ID and pass the remaining data down the heirarchy
            sepLoc = dataLine.index(',')
            ID = dataLine[:sepLoc]
            subDataLine = dataLine[sepLoc+1:]
        
            if ID in self.__subScorables:
                self.__subScorables[ID].updateData(subDataLine)
            else:
                self.__subScorables[ID] = self.__subType(subDataLine)
                self.__subIDorder.append(ID)

        else:  # this is the bottom of the heirarchy
            self.data = str2wkey(dataLine)


    # First, the keycounts are updated in all lower levels of the heirarchy.  Then, the key counts
    # are updated at this level.
    def updateKeyCounts(self, wordlist):
        self.__keyCounts = {}

        if self.__subScorables is not None:
            for ID in self.__subScorables:
                # update key counts at the next lower level
                self.__subScorables[ID].updateKeyCounts(wordlist)

                for wKey in self.__subScorables[ID].getKeyCounts():
                    if wKey in self.__keyCounts: # I already have this key and need to update the count
                        self.__keyCounts[wKey] += self.__subScorables[ID].getKeyCounts()[wKey]
                    else: # I don't have this key and need to start counting it
                        self.__keyCounts[wKey] = self.__subScorables[ID].getKeyCounts()[wKey]

        else: # this is the bottom of the heirarchy
            try:
                self.__keyCounts = wordlist.getSeqLongestMatchCounts(self. data)
            except:
                print "Error: Failed matching wordlist keys to subject response."
            return

    # Returns a dictionary of keys from the wordlist and number of times they occur in the subScorables
    def getKeyCounts(self):
        if self.__keyCounts is not None:
            return self.__keyCounts
        else:
            raise Exception("Error: attempted to get wordlist key counts without first updating key counts.")
     

    # Appends a score to the scoring table.  This function should be used be scoring 
    # methods to store their output. 
    # methodName is the name of the scoring method.
    # methodScore is the score computed by the method.
    def appendScoreTable(self, methodName, methodScore):
        if methodName in self.__scoreTable:
            raise Exception("Warning: Attempted to update score table with a scoring method name that was already used.")
        else:
            self.__scoreTable[methodName] = methodScore
        self.__scoreMethOrder += [methodName]

    # Returns a dictionary with scoring method names as keys and their assigned scores as values.
    def getScoreTable(self):
        return self.__scoreTable

    # Returns an ordering for the scoring methods.
    def getScoreMethOrder(self):
        return self.__scoreMethOrder

    # Returns next lowest level of heirarchy as a dictionary with IDs as keys and self.subType instances as values
    def getSubScorables(self):
        return self.__subScorables
