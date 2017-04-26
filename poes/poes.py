# This file contains the main execution code for POES which parses
# user parameters, loads input data, applies scoring modules and
# reporting modules to generate output

import os
import shutil
import sys
import time

from poes_wordlist import Wordlist
from poes_heirarchy import *


# scoring: Update the keyCounts and run the scoring modules.
# scoreModNames is a list of scoring module names.
# batch is an instance of the Batch class
# wordlist is an instance of the wordlist class
# For each module name in scoreModNames, this function imports
# "modulename" in the scoring_modules subdirectory of the 
# current working directory and then executes 
# modulename.score(batch, wlistTab)
# If scoreModNames is an empty list, every module in the
# scoring_modules subdirectory will be used.
def scoring(scoreModNames, batch, wordlist):
    scoreModDir = os.path.join(os.getcwd(),"scoring_modules")
    sys.path.append(scoreModDir)

    # Update keyCounts in batch using wordlist
    try:
        batch.updateKeyCounts(wordlist)
    except:
        print "Error: POES could not extract wordlist keys from the subject data."
        exit()

    if scoreModNames == []: # no scoring modules specified so use all of them
        dircontents = os.listdir(scoreModDir)
        for cand in dircontents:
            if cand[-3:] == ".py":
                scoreModNames.append(cand[:-3])
        if scoreModNames == []:
            print "Warning: You did not specify any scoring modules and POES did not find any scoring modules in " + scoreModDir

    for mod in scoreModNames:
        try:
            m = __import__(mod)
            m.score(batch, wordlist)
        except ImportError:
            print "Warning: Scoring module " + mod + " did not load properly and will be ignored." 
            

# reporting: Runs the reporting modules. 
# Similar to scoring() function, but loads modules from the report_modules
# subdirectory of the current working directory.
def reporting(reportModNames, batch, wordlist, configInfo, runid):
    reportModDir = os.path.join(os.getcwd(),"report_modules")
    sys.path.append(reportModDir)

    if reportModNames == []: # no reporting modules specified so use all of them
        dircontents = os.listdir(reportModDir)
        for cand in dircontents:
            if cand[-3:] == ".py":
                reportModNames.append(cand[:-3])

    if reportModNames == []:
        print "Warning: POES did not find any report modules in " + reportModDir

    for mod in reportModNames:
        try:
            m = __import__(mod)
            m.report(batch, wordlist, os.path.join(os.getcwd(),"output"), mod, configInfo, runid)
        except ImportError:
            print "Warning: Report module " + mod + " did not load properly and will be ignored."

def loadConfig(fileLoc):
    """
    Loads information about POES such as version number and stores it in a dictionary
    """
    cf = open(fileLoc, "r")
    try:
        #cf = open(fileLoc, "r")
        confData = cf.readlines()
        confData = map(lambda s: str.strip(s), confData)
        return dict(map(lambda s: str.split(s,' ',1) if len(s) > 0 else (None, None), confData))
    except IOError:
        print "Error: Could not open POES configuration file " + fileLoc
        exit()
    finally:
        cf.close()

def printLicense(configInfo):
    print "\n\
--------------------------------------------------------------------------\n\
Program for Open-Ended Scoring (POES) version " + configInfo["POES_VER"] + "\n\
Copyright 2013 Duncan Ermini Leaf and Kimberly A. Barchard\n\
Written by Duncan Ermini Leaf (dleaf /a t/ usc /d o t/ edu)\n\
\n\
This program is free software: you can redistribute it and/or modify\n\
it under the terms of the GNU General Public License as published by\n\
the Free Software Foundation, either version 3 of the License, or\n\
(at your option) any later version.\n\
\n\
This program is distributed in the hope that it will be useful,\n\
but WITHOUT ANY WARRANTY; without even the implied warranty of\n\
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n\
GNU General Public License for more details.\n\
\n\
You should have received a copy of the GNU General Public License\n\
along with this program.  If not, see <http://www.gnu.org/licenses/>.\n\
--------------------------------------------------------------------------\n\
"

### BEGIN MAIN PROGRAM ###
configInfo = loadConfig(os.path.join(os.getcwd(),"poes.cfg"))

printLicense(configInfo)

## Parse command line inputs
userInputs = [ # default value, description, command line flag, required
    ["", 'subject data file location', '-i', True], 
    ["wordlist.txt", 'wordlist file location', '-w', False], 
    ["", 'list of scoring module names', '-m', False], 
    ["", 'list of report module names', '-r', False],
    ["0", 'number of test items', '-n', False],
    ["0", 'number of subparts per item', '-s', False]
    ]

for inp in userInputs:    
    try:
        temp = sys.argv[sys.argv.index(inp[2]) + 1]
    except:
        if inp[3]:
            print "Error: " + inp[1] + " was not properly specified in the command line arguments."
            exit()
    else:        
        inp[0] = temp

# check for -r and -d arguments for backward compatibility
try:
    reqCSV = sys.argv.index("-d")
except:
    pass
else:
    apptxt = (',' if len(inp[3]) > 0 else '') + "score_data_csv"
    inp[3].append(apptxt)
try:
    reqHR = sys.argv.index("-r")
except:
    pass
else:
    apptxt = (',' if len(inp[3]) > 0 else '') + "hr1"
    inp[3].append(apptxt)

 
## Load the wordlist
try:
    w = Wordlist(userInputs[1][0])
except:
    print "Error: POES could not load the wordlist file " + userInputs[1][0]
    exit()

configInfo["WL_INFO"] = w.descTxt
configInfo["WL_REF"] = w.refTxt

## Load the data
try:
    b = Batch()
    subjCount = b.loadFromFile(userInputs[0][0])
    if subjCount[0] != subjCount[1]:
        print "Warning: First line of subject data file " + userInputs[0][0] + " says there should be " + str(subjCount[0]) + " subjects, but the file contained " + str(subjCount[1]) + " unique subject IDs."
    configInfo["SUBJFILELOC"] = userInputs[0][0]
except:
    print "Error: POES could not load the subject data file " + userInputs[0][0]
    exit()

## Check item counts and subpart counts (if they were specified)
nItems = int(userInputs[4][0])
nSubparts = int(userInputs[5][0])
maxnItems = 0
maxnSubp = 0
for subjID in b.subjects.keys():
    actualnItems = len(b.subjects[subjID].items)
    maxnItems = max(maxnItems, actualnItems)
    if nItems > 0 and actualnItems != nItems:
            print "Warning: You specified " + str(nItems) + " items for each subject, but subject " + subjID + " had " + str(len(b.subjects[subjID].items)) + " items."

    for itemID in b.subjects[subjID].items.keys():
        actualnSubp = len(b.subjects[subjID].items[itemID].subparts)
        maxnSubp = max(maxnSubp, actualnSubp)
        if nSubparts > 0 and actualnSubp != nSubparts:
            print "Warning: You specified " + str(nSubparts) + " subparts per item, but subject " + subjID + " had " + str(len(b.subjects[subjID].items[itemID].subparts)) + " subparts for item " + itemID + "."
configInfo["MAXNSUBP"] = str(maxnSubp)
configInfo["MAXNITEMS"] = str(maxnItems)
configInfo["NSUBJ"] = str(len(b.subjects)) 


## Run scoring modules
if userInputs[2][0] == "":
    scoreModNames = []
else:
    scoreModNames = userInputs[2][0].split(',')
scoring(scoreModNames, b, w)

## create time stamp used as an ID associated with every file from this run
tm = time.localtime()
runid = str(tm.tm_year) +  "{0:02d}".format(tm.tm_mon) + "{0:02d}".format(tm.tm_mday) + "_" + "{0:02d}".format(tm.tm_hour) + "{0:02d}".format(tm.tm_min) + "{0:02d}".format(tm.tm_sec) 

## Run reporting modules
if userInputs[3][0] == "":
    reportModNames = []
else:
    reportModNames = userInputs[3][0].split(',')
reporting(reportModNames, b, w, configInfo, runid)

## copy scoring module config files to output appending runid to file name
scoreModDir = os.path.join(os.getcwd(),"scoring_modules")
dircontents = os.listdir(scoreModDir)
for conf in dircontents:
    if conf[-4:] == ".cfg" and (scoreModNames == [] or conf[:-4] in set(scoreModNames)):
        shutil.copyfile(os.path.join(scoreModDir,conf), os.path.join(os.getcwd(), "output" , conf[:-4] + '_' + runid + ".cfg"))

print "POES run " + runid + " finished. Exiting."
