import os

import poes_scorable
import poes_wordlist

from poes_loadconf import loadLineSepFile

modname = "HighestNUnique"

def recscore(sc, wlist, Nsummed):
    """
    Score the scorable heirarchy below sc
    using the HighestNUnique scoring method with
    Nsummed as the number to be summed. 
    """
    uniqueKeys = set(sc.getKeyCounts().keys())
    values = []
    for key in uniqueKeys:
        values += [wlist.getValue(key)]
    values.sort(reverse=True)
    score = sum(values[0:Nsummed])
    sc.appendScoreTable(modname, score)

    nextLvl = sc.getSubScorables()
    if nextLvl is not None:
        for subsc in nextLvl.values():
            recscore(subsc, wlist, Nsummed)

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

    recscore(batch, wlist, N)

