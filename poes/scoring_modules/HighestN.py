import os 

import poes_scorable
import poes_wordlist

from poes_loadconf import loadLineSepFile

modname = "HighestN"

def scoreHighestN(sc, wlist, Nsummed):
    """
    Score the scorable sc
    using the HighestN scoring method where Nsummed
    defines the number to be summed.
    """
    keytab = sc.getKeyCounts()
    keys = keytab.keys()
    values = []
    for key in keys:
        values += [wlist.getValue(key)]*keytab[key]
    values.sort(reverse=True)
    score = sum(values[0:Nsummed])
    return score


def score(batch, wlist):
    cfgLoc = os.path.join(os.getcwd(),"scoring_modules",modname + ".cfg")
    try:
        params = loadLineSepFile(cfgLoc)
        if params is not None:
            N = int(params["N"])
        else: return
    except IOError:
        print "Error: " + modname + " scoring module could not open configuration file " + cfgLoc
        return

    batchScore = scoreHighestN(batch, wlist, N)
    batch.appendScoreTable(modname, batchScore)
    for subj in batch.getSubScorables().values():
        subjScore = scoreHighestN(subj, wlist, N)
        subj.appendScoreTable(modname, subjScore)
        for item in subj.getSubScorables().values():
            itemScore = scoreHighestN(item, wlist, N)
            item.appendScoreTable(modname, itemScore)
            for subp in item.getSubScorables().values():
                subpScore = scoreHighestN(subp, wlist, N)
                subp.appendScoreTable(modname, subpScore)

 
