import sys, os.path, time, codecs, tempfile, random

FILENAMECHARS = "U^Qy9gSH#%a-pW_K2MTc!P.@r4ALEIm16RNo5Cv&dJbfnYeGD0t8l+iB~XxhF7w3=jOV$Zksuzq"
INVERS_FILENAMECHARS = [ 20, -1, 8, 68, 9, 39, -1, -1, -1, -1, 53, -1, 11, 22,
     -1, 49, 31, 16, 63, 25, 36, 32, 61, 51, 4, -1, -1, -1, 64, -1, -1, 23, 26,
     55, 37, 48, 28, 60, 47, 7, 29, 41, 15, 27, 17, 34, 66, 21, 2, 33, 6, 18,
     0, 67, 13, 57, 45, 69, -1, -1, -1, 1, 14, -1, 10, 42, 19, 40, 46, 43, 5,
     59, 54, 65, 70, 52, 30, 44, 35, 12, 74, 24, 71, 50, 72, 38, 62, 58, 3, 73,
     -1, -1, -1, 56, -1]
INVALID_FILENAMECHARS = "\"'()*,/:;<>?[\\]`{|}"

def exceptionString(excInfo = None, additionalInfo = None):
    '''Extracts the info as string from an exception info.
    @param excInfo:    the info given by sys.exc_info
    @return the info string
    '''
    if excInfo == None:
        excInfo = sys.exc_info()
    exc = excInfo[1]
    rc = unicode(exc)
        
    if additionalInfo != None and rc.find(additionalInfo) < 0:
        rc += ': ' + additionalInfo
    return rc
        
def say(msg, newline=True):
    if newline:
        msg += "\n"
    sys.stdout.write(msg)
    
def sayError(msg, newline=True):
    if newline:
        msg += "\n"
    sys.stdout.write(msg)

class Util:
    '''Only static methods for some useful actions.
    '''
    @staticmethod
    def writeFile(path, content=None):
        '''Creates a regular file.
        @param path: the file's name (with path)
        @param content: None or the file's content
        '''
        fp = codecs.open(path, "w", "UTF-8")
        if content != None:
            fp.write(content);
        fp.close()
    
    @staticmethod
    def readFileAsString(path):
        '''Reads a file into a string.
        @param path: the file's name (with path)
        @return: None: file not readable.<br>
                otherwise: the file's content
        '''
        rc = None
        fp = None
        try:
            fp = codecs.open(path, "r", "UTF-8")
            if fp != None:
                rc = fp.read()
        except Exception:
            pass
        if fp != None:
            fp.close()
        return rc
    
    @staticmethod
    def readFileAsList(path, removeEndOfLine = False):
        '''Reads a file into a line list.
        @param path: the file's name (with path)
        @param removeEndOfLine: True: the '\n' will be removed
        @return: None: file not readable.<br>
                otherwise: the file's content as list
        '''
        rc = None
        fp = codecs.open(path, "r", "UTF-8")
        if fp != None:
            rc = []
            for line in fp:
                if removeEndOfLine:
                    line = line.rstrip()
                rc.append(line)
        fp.close()
        return rc
    
    @staticmethod
    def mkDir(name):
        '''Ensures that a subdirectory exists.
        If not it will be created.
        @param name: the subdirectory's name
        '''
        if not os.path.exists(name):
            os.makedirs(name)
    
    @staticmethod
    def getTempDir(base = None, subdir = None, endsWithSeparator=False):
        '''Returns a temporary directory.
        @param base: None or the parent of <code>node>/code>
        @param node: None of the subdirectory in the temporary directory
        @param endsWithSeparator: True: the result ends with the separator
        @return: the name of an existing temporary directory
        '''
        rc = tempfile.gettempdir()
        # for compatibility only:
        if type(subdir) == bool:
            endsWithSeparator = subdir
            subdir = None
        if base != None:
            rc += os.sep + base
        if subdir != None:
            rc += os.sep + subdir
        if not os.path.exists(rc):
            os.makedirs(rc)
        if endsWithSeparator and not rc.endswith(os.sep):
            rc += os.sep
        return rc
    
    @staticmethod
    def getTempFile(node, subdir = None, subdir2 = None):
        '''Returns a file name in a temporary directory.
        @param node: name of the file without path
        @param subdir: None of the subdirectory where the file is laying
        @return: the name of a file in the temporary directory
        '''
        if subdir2 != None:
            subdir += os.sep + subdir2
        rc = Util.getTempDir(subdir, True) + node
        Util.deleteIfOlder(rc)
        return rc

    @staticmethod
    def deleteIfOlder(filename, maxAge = 24*3600):
        '''Deletes a file if it is older than a given amount of seconds.
        @param filename: the file to test with path
        @param maxAge: the maximum age in seconds
        '''
        if os.path.exists(filename):
            mdate = os.stat(filename).st_mtime
            now = time.time()
            if now - mdate >= maxAge:
                os.unlink(filename)

    @staticmethod
    def ensureMissing(filename):
        '''Deletes a file if it exists.
        @param filename:
        @return: True: the file has been deleted.<br>
                False: Deletion was not necessary
        '''
        exists = os.path.exists(filename)
        if exists:
            os.unlink(filename)
        return exists
      
    @staticmethod
    def encodeFilenameChar(intVal): 
        '''Converts a integer into a string with characters allowed in filenames.
        @param intVal: the integer value to convert
        @return a filename
        '''
        maxChar = len(FILENAMECHARS)
        rc = ""
        if intVal < 0:
            intVal = -intVal
        while intVal > 0:
            rc += FILENAMECHARS[intVal % maxChar]
            intVal /= maxChar
        return rc
    
    @staticmethod
    def decodeFilenameChar(name):
        '''Converts a string with characters allowed in filenames into an integer.
        @param name: the string to convert
        @return: an integer representing the string
        '''
        maxChar = len(FILENAMECHARS)
        rc = 0
        length = len(name)
        for ii in xrange(length):
            cc = name[length - 1 - ii]
            ix = ord(cc) - 33
            if ix >= 0 and ix < len(INVERS_FILENAMECHARS):
                n = INVERS_FILENAMECHARS[ix]
                if n >= 0:
                    rc = rc * maxChar + INVERS_FILENAMECHARS[ix]
        return rc
    @staticmethod
    def buildInvers(chars, offset):
        '''Builds an inverse table of a encoder string.
        @param chars:   a string with the allowed characters. 
                        Each char must be unique
        @param offset:  the ord() value of the lowest char
        @return:        a tuple (chars, invers) char is a permutated sequence of 
                        the input, invers is a list for finding the index in chars
        '''
        aList = []
        for cc in chars:
            aList.append(cc)
        for ii in xrange(5):
            random.shuffle(aList)
        chars = "".join(aList)
        invers = []
        for ii in xrange(128-offset):
            invers.append(-1)
        for ii in xrange(128-offset):
            cc = chr(offset + ii)
            if ii == 126-offset or cc == '~':
                pass
            invers[ii] = chars.find(cc)
        say('FILENAMECHARS = "' + chars + '"')
        out = "INVERS_FILENAMECHARS = ["
        for x in invers:
            out2 = " " + unicode(x) + ","
            if len(out) + len(out2) >= 80:
                say(out)
                out = "    "
            out += out2
        say(out[0:-1] + "]")
        invalid = ""
        for ii in xrange(128-offset):
            cc = chr(offset + ii)
            if chars.find(cc) < 0:
                if cc == '\\' or cc == '"':
                    invalid += "\\"
                invalid += cc
        say('INVALID_FILENAMECHARS = "' + invalid + '"')
        return (chars, invers)            