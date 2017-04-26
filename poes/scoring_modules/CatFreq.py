import poes_scorable
import poes_wordlist

modname = "CatFreq"

def score(batch, wlist):
    wlValues = list(set(wlist.getValues()))
    wlValues.sort()
    batchValCt = {}
    for subj in batch.getSubScorables().values():
        subjValCt = {}
        for item in subj.getSubScorables().values():
            itemValCt = {}
            for subp in item.getSubScorables().values():
                keyCt = subp.getKeyCounts()
                subpValCt = {}
                for key in keyCt:
                    val = wlist.getValue(key)
                    if(val is None):
                        raise Exception("In CatFreq, key in key count table, but has no value in wordlist.")
                    subpValCt[val] = 1 + (subpValCt[val] if val in subpValCt else 0)
                for val in wlValues:
                    methName = modname + str(val)
                    subpScore = subpValCt[val] if val in subpValCt else 0
                    subp.appendScoreTable(methName, subpScore)
                for val in subpValCt:
                    itemValCt[val] = subpValCt[val] + (itemValCt[val] if val in itemValCt else 0)
                    subjValCt[val] = subpValCt[val] + (subjValCt[val] if val in subjValCt else 0)
                    batchValCt[val] = subpValCt[val] + (batchValCt[val] if val in batchValCt else 0)
            for val in wlValues:
                methName = modname + str(val)
                itemScore = itemValCt[val] if val in itemValCt else 0
                item.appendScoreTable(methName, itemScore)
        for val in wlValues:
            methName = modname + str(val)
            subjScore = subjValCt[val] if val in subjValCt else 0
            subj.appendScoreTable(methName, subjScore)
    for val in wlValues:
        methName = modname + str(val)
        batchScore = batchValCt[val] if val in batchValCt else 0
        batch.appendScoreTable(methName, batchScore)
 
 
