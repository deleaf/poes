"""This module defines a class for storage of and lookups in the POES wordlist."""

import os
import re

from poes_str2wkey import str2wkey

# trieNode used to implement trie structure for storing wordlist keys and
# their values
class trieNode:
    def __init__(self, v = None):
        self.children = {}
        self.value = v
        self.order = None


class Wordlist(object):
    def __init__(self, fileLoc):
        self.__wlist = {}
        self.descTxt = "WORDLIST DESCRIPTION TEXT NOT DEFINED"
        self.refTxt = "WORDLIST REFERENCE TEXT NOT DEFINED"

        if fileLoc is not None:
            self.loadFromFile(fileLoc)

        
    def getKeys(self):
        return self.__wlist.keys()

    def getValue(self, key):
        return self.__wlist[key]

    def getValues(self):
        return self.__wlist.values()
    
    def getSeqLongestMatchCounts(self, t):
        """
        Input: t is a sequence of token objects.
        getSeqLongestMatches moves through the tokens in t sequentially.  Starting at a
        single token in t, it finds the longest consecutive sequence of tokens that matches
        an entry in the wordlist.  Once a match is found, it starts searching for a new matching
        sequence starting from the token following the end of the previously matched sequence.  
        If no match is found, the search resumes from the word immediately after the wordt that
        first matched a wordlist key.  The matches are returned as a dictionary with the sequences 
        of tokens as tuple keys each indexing the number of occurrences of the key in t.
        """
        matches = {}
        
        value = None
        currentNode = self.__trie
        seqStart = seqEnd = 0
        i = 0   
        while i < len(t):
            # check if t[i] can be appended so that the token sequence still matches (the prefix of) a wordlist key
            if t[i] in currentNode.children:
                currentNode = currentNode.children[t[i]]
                # find the value (if any) for the token sequence t[seqStart] ... t[i]
                if currentNode.value is not None:
                    value = currentNode.value
                    seqEnd = i
                i += 1
            else: # dead end
                # if t[seqStart] ... t[i-1] is a wordlist key (has a value), append it to matches
                if value is not None:
                    wkey = tuple(t[seqStart:seqEnd+1])
                    if wkey in matches:
                        matches[wkey] += 1
                    else:
                        matches[wkey] = 1
                else:
                    i = seqStart + 1

                # use i as the starting point for a new sequence
                seqStart = seqEnd = i
                value = None
                currentNode = self.__trie
                                    
        if value is not None:
            wkey = tuple(t[seqStart:seqEnd+1])
            if wkey in matches:
                matches[wkey] += 1
            else:
                matches[wkey] = 1

        return matches
            

    
    # buildTrie builds a trie structure from self.wlist and stores it in self.trie.  If 
    #self.wlist is empty then so will be self.__trie.
    def buildTrie(self):
        self.__trie = trieNode()
        for key in self.__wlist:
            currentNode = self.__trie
            for word in key:
                if word not in currentNode.children:
                    currentNode.children[word] = trieNode()
                currentNode = currentNode.children[word]
            # Store the value
            currentNode.value = self.__wlist[key]
        
            
    def loadFromFile(self, fileLoc):
        try:
            wf = open(fileLoc,'r')
            self.descTxt = wf.readline().strip() 
            self.refTxt = wf.readline().strip()
            entries = wf.readlines()
            # remove newlines and whitespace at end of wordlist file
            while entries[-1].strip() == "":
                entries = entries[0:-1]
            keys = map(str2wkey, entries[0::3])
            values = map(int, entries[1::3])
            self.__wlist = dict(map(None,keys,values))
            self.buildTrie()
        except IOError:
            raise Exception("Error: Could not open wordlist file: " + fileLoc)
        except:
            raise Exception("Error: Could not load wordlist file: " + fileLoc)
        finally:
            wf.close()
