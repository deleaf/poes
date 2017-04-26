import poes_scorable
import poes_wordlist

modname = "CountWords"

def score(batch, wlist):
    batchNWords = 0
    for subj in batch.getSubScorables().values():
        subjNWords = 0
        for item in subj.getSubScorables().values():
            itemNWords = 0
            for subp in item.getSubScorables().values():
                subpNWords = sum(map(lambda x: int(len(x) > 0), subp.data))
                subp.appendScoreTable(modname, subpNWords)
                itemNWords += subpNWords
                subjNWords += subpNWords
                batchNWords += subpNWords
            item.appendScoreTable(modname, itemNWords)
        subj.appendScoreTable(modname, subjNWords)
    batch.appendScoreTable(modname, batchNWords)
 
 
