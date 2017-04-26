import poes_scorable
import poes_wordlist

modname = "AllSumUnique"

def recscore(sc, wlist):
    uniqueKeys = set(sc.getKeyCounts().keys())
    score = 0
    for key in uniqueKeys:
        score += wlist.getValue(key)
    sc.appendScoreTable(modname, score)

    nextLvl = sc.getSubScorables()
    if nextLvl is not None:
        for subsc in nextLvl.values():
            recscore(subsc, wlist)

def score(batch, wlist):
    recscore(batch, wlist)
