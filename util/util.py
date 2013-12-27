import sys, os.path, time, codecs, tempfile, random, operator

FILENAMECHARS = "U^Qy9gSH#%a-pW_K2MTc!P.@r4ALEIm16RNo5Cv&dJbfnYeGD0t8l+iB~XxhF7w3=jOV$Zksuzq"
INVERS_FILENAMECHARS = [ 20, -1, 8, 68, 9, 39, -1, -1, -1, -1, 53, -1, 11, 22,
     -1, 49, 31, 16, 63, 25, 36, 32, 61, 51, 4, -1, -1, -1, 64, -1, -1, 23, 26,
     55, 37, 48, 28, 60, 47, 7, 29, 41, 15, 27, 17, 34, 66, 21, 2, 33, 6, 18,
     0, 67, 13, 57, 45, 69, -1, -1, -1, 1, 14, -1, 10, 42, 19, 40, 46, 43, 5,
     59, 54, 65, 70, 52, 30, 44, 35, 12, 74, 24, 71, 50, 72, 38, 62, 58, 3, 73,
     -1, -1, -1, 56, -1]
INVALID_FILENAMECHARS = "\"'()*,/:;<>?[\\]`{|}"
ALGO_REVERS = "0"
ALGO_XOR = "1"
ALGO_ADD = "2"
ALGO_DEFAULT = ALGO_ADD
CHARS10 = "9147253806"
CHARS16 = "fadceb" + CHARS10
CHARS26 = "zfsoeiurglhqnmwtbvpxyjakcd"
CHARS38 = "_." + CHARS10 + CHARS26
CHARS64 = "QASDFGHJKLWERTZUIOPYXCVBNM" + CHARS38
CHARS76 = "!@$%&#;,/+=?" + CHARS64
CHARS93 = "^`(>~[{<*)\" |}]-:" + CHARS76
CHARS95 = "'\\" + CHARS93
CHARS96 = "" + CHARS95
TAG_CHARS10 = "9"
TAG_CHARS16 = "f"
TAG_CHARS26 = "z"
TAG_CHARS38 = "_"
TAG_CHARS64 = "Q"
TAG_CHARS76 = "!"
TAG_CHARS93 = "^"
TAG_CHARS95 = "<"
TAG_CHARS96 = ">"
TAG_TO_CHARS = { 
    TAG_CHARS10 : CHARS10, 
    TAG_CHARS16 : CHARS16, 
    TAG_CHARS26 : CHARS26, 
    TAG_CHARS38 : CHARS38, 
    TAG_CHARS64 : CHARS64, 
    TAG_CHARS76 : CHARS76, 
    TAG_CHARS93 : CHARS93, 
    TAG_CHARS95 : CHARS95, 
    TAG_CHARS96 : CHARS96, 
    }
ALL_TAGS = (TAG_CHARS10, TAG_CHARS16, TAG_CHARS26, TAG_CHARS38, TAG_CHARS64,
            TAG_CHARS76, TAG_CHARS93, TAG_CHARS95, TAG_CHARS96)
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
    
    @staticmethod
    def hideText(text, algorithm = ALGO_DEFAULT):
        '''disquises the passphrase.
        @param text         clear text
        @param algorithm    method for hiding: ALGO_...
        @return:    the disguised text
        '''
        seed = int(random.randint(0, 0xffff))
        #seed = 0x1234
        head = "{:02x}{:02x}".format(seed % 256, seed / 256) + algorithm
        rc = "" 
        #msg = ""
        for cc in text:
            seed = (seed * 7 + 0x1234321) & 0x8fffffff
            if algorithm == ALGO_XOR:
                val = operator.xor(ord(cc), seed) % 256
            elif algorithm == ALGO_ADD:
                val = (ord(cc) + seed % 256) % 256
            else:
                val = ord(cc)
            # reverse string:
            rc = "{:x}{:x}".format(val % 16, val / 16) + rc
            #msg += "\ncc: {:s} seed: {:d} val: {:d}/{:x}".format(cc, seed, val, val)
        return head + rc
    
    @staticmethod
    def unhideText(text):
        '''Unhide the text disguised with hide().
        @param text    encrypted text
        @return:       clear text
        '''
        rc = ""
        pos = 0
        algorithm = text[4:5]
        seed = int(text[pos:pos+2], 16) + 256 * int(text[pos+2:pos+4], 16)
        pos += 5
        pos = len(text) - 2
        while pos >= 5:
            seed = (seed * 7 + 0x1234321) & 0x8fffffff
            val = int(text[pos:pos+1], 16) + 16*int(text[pos+1:pos+2], 16)
            if algorithm == ALGO_XOR:
                val2 = operator.xor(val, seed) % 256
            elif algorithm == ALGO_ADD:
                val2 = val - seed % 256
                if val2 < 0:
                    val2 += 256
            else:
                val2 = val
            # reverse string:
            rc += chr(val2)
            pos -= 2
        return rc

    @staticmethod
    def getCharset(tag):
        '''Returns the charset given by its tag.
        @param tag:    TAG_CHAR...
        @return:      a string containing the given charset
        '''
        if tag in TAG_TO_CHARS:
            rc = TAG_TO_CHARS[tag]
        else:
            msg = "unknown charset: " + ("None" if tag == None else tag)
            raise Exception(msg)
        return rc

    @staticmethod
    def matchCharset(text, charset):
        '''Tests whether a text has only chars from a given charset.
        @param text:    text to inspect
        @param charset: a string containing all allowed chars
        @return:        True: all chars of <code>text</code> are in <code>charset</code>
                        False: otherwise
        '''
        rc = True
        for cc in text:
            if charset.find(cc) < 0:
                rc = False
                break
        return rc

    @staticmethod
    def nextTag():
        '''Returns a generator function of all charset tags.
        @return:    the next tag
        '''
        for tag in ALL_TAGS:
            yield tag

    @staticmethod
    def findCharsetTag(text):
        '''Finds the tag of an charset containing all chars of the given text.
        @param text:    text to inspect
        @return:        None: no charset found
                        otherwise: the tag of th smallest charset possible 
        '''
        rc = None
        for tag in ALL_TAGS:
            charset = TAG_TO_CHARS[tag]
            if Util.matchCharset(text, charset):
                rc = tag
                break
        return rc
        

    @staticmethod
    def scrambleText(text, tagCharset = None):
        '''Disquises a text.
        @param text         clear text
        @param tagCharset   an id for the charset: TAG_CHARS...
                            if None the charset will be found automatically
        @return:            the disguised text
        '''
        if tagCharset == None:
            tagCharset = Util.findCharsetTag(text)
        seed2 = random.randint(0, 0x7fff0000)
        charset = Util.getCharset(tagCharset) 
        size = len(charset)
        head = ""
        seed = 0
        for ii in xrange(3):
            seedX = seed2 % size
            seed = seed * size + seedX
            seed2 = int(seed2 / size)
            head += charset[seedX:seedX+1]
        head += tagCharset
        rc = "" 
        msg = "seed: {:d}\n".format(seed)
        for cc in text:
            seed = (seed * 7 + 0x1234321) & 0x8fffffff
            delta = 1 + seed % (size - 1)
            ix = charset.find(cc)
            if ix < 0:
                raise Exception(u"scrambleText: unknown char {:s} allowed: {:s}"
                        .format(cc, charset))
            ix = (ix + delta) % size
            rc += charset[ix:ix+1]
            msg += u"\ncc: {:s} seed: {:d} ix: {:d} delta: {:d} val: {:s}".format(cc, seed, ix, delta, charset[ix:ix+1])
        return head + rc
    
    @staticmethod
    def unscrambleText(text):
        '''Unhide the text disguised with hide().
        @param text    encrypted text
        @return:       clear text
        '''
        tagCharset = text[3:4]
        charset = Util.getCharset(tagCharset)
        size = len(charset)
        seed = 0
        for ii in xrange(3):
            cc = text[ii:ii+1]
            seed = seed * size + charset.index(cc)
        pos = 4
        rc = ""
        while pos < len(text):
            seed = (seed * 7 + 0x1234321) & 0x8fffffff
            cc = text[pos:pos+1]
            # delta = 1 + seed % (size - 1)
            # ix = (charset.index(cc) + delta) % size
            delta = 1 + seed % (size - 1)
            ix = charset.index(cc) - delta
            if ix < 0:
                ix += size
            rc += charset[ix:ix+1]
            pos += 1
        return rc

    @staticmethod
    def toAscii(value):
        '''Converts an non ascii string to ascii.
        @param value:   string to convert
        @return:        a string with special characters converted to %HH syntax
        '''
        if value == None:
            rc = None
        else:
            hasNoAscii = True
            for cc in value:
                if ord(cc) <= 0 or ord(cc) > 127:
                    hasNoAscii = False
                    break
            if hasNoAscii:
                rc = str(value)
            else:
                rc = ""
                for cc in value:
                    if ord(cc) <= 127:
                        rc += cc
                    else:
                        rc += "%{:02x}".format(ord(cc))
        return rc

    @staticmethod
    def toUnicode(value):
        '''Converts a string to unicode.
        Handles conversion errors.
        @param value:    string to convert
        @return:         converted unicode 
        '''
        rc = value
        if type(value) != unicode:
            if type(value) == str:
                try:
                    rc = unicode(value, "UTF-8")
                except UnicodeDecodeError:
                    try:
                        rc = unicode(value, "iso8859-1")
                    except:
                        rc = unicode(Util.toAscii(value))
            else:
                rc = str(value)
        return rc
        
        