# POES puts input data into a heirarchy of class objects.  Scoring methods can assign scores at any level
# of the heirarchy.  The poes_scorable module defines a general Scorable class to represent any level of the 
# heirarchy. This file defines specific classes for each level of the heirarchy.  Each heirarchy class is 
# a child of Scorable.

from poes_scorable import Scorable

class Subpart(Scorable):
    def __init__(self, dataLine):
        Scorable.__init__(self, None, None, None, dataLine)

    def getData(self):
        """
        Returns Subpart response data as a tuple
        """
        return self.data
       

class Item(Scorable):
    def __init__(self, dataLine):
        self.subparts = {}
        Scorable.__init__(self, self.subparts, None, Subpart, dataLine)


class Subject(Scorable):
    def __init__(self, dataLine):
        self.items = {}
        Scorable.__init__(self, self.items, None, Item, dataLine)


class Batch(Scorable):
    def __init__(self, dataFileLoc=None):
        self.subjects = {}
        Scorable.__init__(self, self.subjects, None, Subject)

        if dataFileLoc is not None:
            self.loadFromFile(dataFileLoc)

    def loadFromFile(self, dataFileLoc):
        """
        Load subject data from file.  For backward compatibility, the first line of the file
        *should* be an integer specifying the number of subjects in the file.  loadFromFile
        returns a two-tuple.  The first element is the number of subjects specified
        on the first line of the file.  The second element is the integer number of subjects
        actually found in the file.
        """
        ifile = open(dataFileLoc)
        try:
            dataLines = ifile.readlines()
            nSubjects = int(dataLines[0])
            for line in dataLines[1:]:
                self.updateData(line.strip())
        finally:
            ifile.close()

        return (nSubjects, len(self.subjects))


