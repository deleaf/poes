# This function "tokenizes" text into words (instead of individual characters).  
# It is used for storing both wordlist entries and response text

import re

def str2wkey(s):
    # remove whitespace at ends
    s = str.strip(s)

    # convert to lower case
    s = str.lower(s)

    # remove extra spaces
    #s = re.sub(" +", ' ', s)

    # convert slashes into space
    s = re.sub("[/|\\\]",' ', s)

    # split words around whitespace
    s = re.split("\s+", s)

    # remove numeric characters

    #s2 = re.sub("[\d]", '', s1)

    # remove non-alphabetical characters 
    # TO DO: make this work for international alphabets
    s = tuple(map(lambda t: re.sub("[\W|\d]", '', t), s))

    return s

