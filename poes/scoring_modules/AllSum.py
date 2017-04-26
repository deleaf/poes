#import os
#os.chdir("..")
import poes_scorable
import poes_wordlist

modname = "All-Sum"

def score(batch, wlist):
    batchScore = 0
    for subj in batch.getSubScorables().values():
        subjScore = 0
        for item in subj.getSubScorables().values():
            itemScore = 0
            for subp in item.getSubScorables().values():
                subpScore = 0
                keyct = subp.getKeyCounts()
                for key in keyct:
                    subpScore += subp.getKeyCounts()[key] * wlist.getValue(key)
                subp.appendScoreTable(modname, subpScore)
                itemScore += subpScore
                subjScore += subpScore
                batchScore += subpScore
            item.appendScoreTable(modname, itemScore)
        subj.appendScoreTable(modname, subjScore)
    batch.appendScoreTable(modname, batchScore)
