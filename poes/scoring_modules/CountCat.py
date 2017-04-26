import poes_scorable
import poes_wordlist

modname = "CountCat"

def recscore(sc, wlist):
    """
    Score the scorable heirarchy below sc
    using the CountCat scoring method. 
    """

    uniqueKeys = set(sc.getKeyCounts().keys())
    values = set()
    for key in uniqueKeys:
        values.add(wlist.getValue(key))
    score = len(values)
    sc.appendScoreTable(modname, score)
            
    nextLvl = sc.getSubScorables()
    if nextLvl is not None:
        for subsc in nextLvl.values():
            recscore(subsc, wlist)

def score(batch, wlist):
#    batchScore = 0
#    for subj in batch.getSubScorables().values():
#        subjScore = 0
#        for item in subj.getSubScorables().values():
#            itemScore = 0
#            for subp in item.getSubScorables().values():
#                uniqueKeys = set(subp.getKeyCounts().keys())
#                values = set()
#                for key in uniqueKeys:
#                    values.add(wlist.getValue(key))
#                subpScore = len(values)
#                subp.appendScoreTable(modname, subpScore)
#                itemScore += subpScore
#                subjScore += subpScore
#                batchScore += subpScore
#            item.appendScoreTable(modname, itemScore)
#        subj.appendScoreTable(modname, subjScore)
#    batch.appendScoreTable(modname, batchScore)
    recscore(batch, wlist)

