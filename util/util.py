import sys, os.path, time, codecs, tempfile

def exceptionString(excInfo = None, additionalInfo = None):
    '''Extracts the info as string from an exception info.
    @param excInfo:    the info given by sys.exc_info
    @return the info string
    '''
    if excInfo == None:
        excInfo = sys.exc_info()
    exc = excInfo[1]
    rc = str(exc)
        
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
                