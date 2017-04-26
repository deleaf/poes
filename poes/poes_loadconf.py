# Function for loading configuration information from a file
# where parameter names and values are delimited by newlines

def loadLineSepFile(fileLoc):
    cf = open(fileLoc,'r')   
    try:
        lines = cf.readlines()
        i = 0
        for l in lines:
            if len(l.strip()) == 0 or l.strip()[0] == '#':
                i += 1
            else:
                break

        names = map(lambda s: str.strip(s), lines[i::3])
        values = map(lambda s: int(str.strip(s)), lines[(i+1)::3])
        params = dict(map(None,names,values))
        
        return params

    except IOError:
        print "Error: Could not open configuration file: " + fileLoc
    except:
        print "Error: Could not read contents of configuration file: " + fileLoc
    finally:
        cf.close()

