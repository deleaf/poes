import os 

import poes_scorable
import poes_wordlist

from poes_loadconf import loadLineSepFile

modname = "UniqueMaximums"

def score(batch, wlist):
    cfgLoc = os.path.join(os.getcwd(),"scoring_modules",modname + ".cfg")
    try:
        params = loadLineSepFile(cfgLoc)
        if params is not None:
            keyMax = int(params["KeyMax"])
            subpMax = int(params["SubpartMax"])
            itemMax = int(params["ItemMax"])
            subjMax = int(params["SubjectMax"])
            batchMax = int(params["BatchMax"])
        else: return
    except IOError:
        print "Error: " + modname + " scoring module could not open configuration file " + cfgLoc
        return

    batchScore = 0
    maxSubjScore = None
    nGEsubjMax = 0
    for subj in batch.getSubScorables().values():
        subjScore = 0
        maxItemScore = None
        nGEitemMax = 0
        for item in subj.getSubScorables().values():
            itemScore = 0
            maxSubpScore = None
            nGEsubpMax = 0
            for subp in item.getSubScorables().values():
                subpScore = 0
                # find min(keyMax, max(key value))
                maxVal = None
                nGEkeyMax = 0
                for key in subp.getKeyCounts():
                    val = wlist.getValue(key)
                    maxVal = max(val, maxVal)
                    if val >= keyMax:
                        nGEkeyMax = nGEkeyMax + 1
                if maxVal is not None:
                    subpScore = min(maxVal, keyMax)
                    if maxVal >= keyMax:
                        subpScore = subpScore + nGEkeyMax - 1
                    if subpScore >= subpMax:
                        subpScore = subpMax
                        nGEsubpMax = nGEsubpMax + 1
                subp.appendScoreTable(modname, subpScore)
                maxSubpScore = max(subpScore, maxSubpScore) 

            itemScore = maxSubpScore
            if maxSubpScore >= subpMax:
                itemScore = itemScore + nGEsubpMax - 1
            if itemScore >= itemMax:
                itemScore = itemMax
                nGEitemMax = nGEitemMax + 1
            item.appendScoreTable(modname, itemScore)
            maxItemScore = max(itemScore, maxItemScore)

        subjScore = maxItemScore
        if maxItemScore >= itemMax:
            subjScore = subjScore + nGEitemMax - 1
        if subjScore >= subjMax:
            subjScore = subjMax
            nGEsubjMax = nGEsubjMax + 1
        subj.appendScoreTable(modname, subjScore)
        maxSubjScore = max(subjScore, maxSubjScore)

    batchScore = maxSubjScore
    if maxSubjScore >= subjMax:
        batchScore = batchScore + nGEsubjMax - 1
    batchScore = max(batchScore, batchMax)
    batch.appendScoreTable(modname, batchScore)
