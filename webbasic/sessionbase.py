'''
Created on 03.02.2013

@author: hm
'''
import os.path, re, logging, codecs, time, math
from util.util import Util
from util.configurationbuilder import ConfigurationBuilder
from util.sqlitedb import SqLiteDb
from webbasic.page import PageResult
from basic.shellclient import ShellClient

logger = logging.getLogger("pywwetha")

class SessionBase(object):
    '''
    Manages session specific data and services.
    Live time: request
    There is only one instance of SessionBase()
    '''

    @staticmethod
    def isHomeDir(path):
        if not path.endswith(os.sep):
            path += os.sep
        rc = path if os.path.exists (path + 'data/config.db') else None
        logger.debug('isHomeDir({:s}: {:s}'.format(path, '' if rc else rc))
        return rc
    
    @staticmethod
    def findHomeDir(application, request = None):
        curDir = os.path.realpath('.')
        subdir = SessionBase.isHomeDir(curDir)
        if subdir == None:
            subdir = SessionBase.isHomeDir(os.path.dirname(curDir))
        subdir = subdir if subdir != None else SessionBase.isHomeDir('/etc/' + application + '/home')
        if subdir == None:
            subdir = SessionBase.isHomeDir('/tmp/' + application)
        if subdir == None:
            subdir = SessionBase.isHomeDir('/usr/share/' + application)
        script = ''
        if request != None and hasattr(request, 'META'):
            if 'SCRIPT_FILENAME' in request.META:
                script = request.META['SCRIPT_FILENAME']
            elif 'SCRIPT_PATH' in request.META:
                script = request.META['SCRIPT_PATH']
        if subdir == None and script != '':
            while subdir == None and len(script) > 1:
                subdir = SessionBase.isHomeDir(script)
                script = os.path.dirname(script)
        logger.debug('findHomeDir({:s}): curDir={:s} script: {:s} rc: {:s}'.format(application, 
            curDir, script, subdir))
        return subdir
    
    def __init__(self, request, languages, application, homeDir = None):
        '''
        Constructor
        @param request: the HTTP request info
        @param languages: the languages which are supported by the application
        @param application: None of the name of the application
        @param homeDir: None or the base directory (containing data/config.db)
        '''
        if "DEBUG" in os.environ:
            # Note: Nothing is done if the logger is already initialized 
            logging.basicConfig(filename='/tmp/sidu-base.log',level=logging.DEBUG)
        self._id = None
        self._localVars = dict()
        self._request = request
        self._application = application
        self._pageAndBookmark = None
        self._metaDynamic = ''
        self._supportedLanguages = languages
        self._logMessages = []
        self._errorMessages = []
        self._configAdditional = None
        self._userAgent = ''
        # a list of lines containing the field data for all pages
        # format: <page>.<var>=<value>
        # lines end with '\n'
        self._userData = None
        self._urlStatic = "../static/"
        hasAgent = 'HTTP_USER_AGENT' in request.META
        if request != None and hasAgent:
            self._userAgent = request.META['HTTP_USER_AGENT']
        self._expandNeedsRightMove = not re.search(
            'iceweasel|firefox|opera', 
            self._userAgent, re.IGNORECASE);
        self.handleMetaVar()
        if application == None:
            application = self.getApplicationName(request)
        self._application = application
        if homeDir != None: 
            self._homeDir = homeDir 
        else:
            self._homeDir = SessionBase.findHomeDir(application, request)
        if self._homeDir and not self._homeDir.endswith('/'):
            self._homeDir += '/'
        self._configDb = None
        self._configDbName = None
        if self._homeDir != None:
            self._configDbName = self._homeDir + 'data/config.db'
            self._configInfo = ConfigurationBuilder.getTableInfo()
            if os.path.exists(self._configDbName):
                self._configDb = SqLiteDb(self._configDbName)
                self._configDb.addTableInfo(self._configInfo)
        
        self._language = self.correctLanguage(self.getMetaVar('HTTP_ACCEPT_LANGUAGE'))
        self.trace('SessionBase(): lang: {:s} home: {:s} db: {:s}'.format(
            self._language if self._language else '',
            self._homeDir if self._homeDir else '',
            self._configDbName if self._configDbName else ''))
        self._shellClient = ShellClient(self)

    def addConfig(self, key, value):
        '''Adds a (key, value) pair to the configuration.
        @param key: the key to store
        @param value: the value to store
        '''
        if self._configAdditional == None:
            self._configAdditional = {}
        self._configAdditional[key] = value;
        
    def correctLanguage(self, language):
        '''Search for a matching language.
        @param language: a string starting with the language (ISO, e.g. en-US
        @return: the best matching supported language
        '''
        if language == None:
            rc = 'en'
        else:
            matcher = re.match(r'([a-z]{2}(-[a-zA-Z]{2})?)', language)
            rc = language = 'en' if matcher == None else matcher.group(1).lower()
            if language not in self._supportedLanguages:
                ll = language[0:2]
                rc = None
                for lang in self._supportedLanguages:
                    if ll.startswith(lang):
                        # de-de matches de:
                        rc = lang
                        break
                    elif ll == lang[0:2]:
                        # pt-pt matches pt-br
                        rc = lang
                        break
                if rc == None:
                    rc = 'en'
        return rc 
         
    def deleteFile(self, name):
        '''Deletes a file if it exists.
        @param name: the file's name
        '''
        if name == None:
            pass
        elif os.path.exists(name):
            self.trace("deleted: " + name)
            os.unlink(name)
        
    def handleMetaVar(self):
        value = self.getMetaVar('PATH_INFO')
        if value != None:
            ix = value.rfind('/')
            if ix >= 0:
                value = value[ix+1:]
            # /help?label=help-gen -> help#help-gen
            #
            #query = self.getMetaVar('QUERY_STRING')
            #if query.startswith('label='):
            #    value += '?label=' + query[6:] + '#' + query[6:]
            self._pageAndBookmark = value
            
        if self._application == None:
            value = self.getMetaVar('HTTP_HOST')
            if value != None:
                ix = value.find(':')
                if ix > 0:
                    value = value[0:ix]
            self._application = value
        
    def getMetaVar(self, name):
        '''Returns the value of a meta variable.
        @param name: the variable's name
        @param return: None: unknown variable<br>
                otherwise: the value of the variable
        '''
        if not hasattr(self._request, 'META') or name not in self._request.META:
            rc = None
        else:
            rc = self._request.META[name]
        return rc
    
    def getApplicationName(self, request):
        '''Gets the application name from the request.
        The domain name of the URL will be used as application name.
        @param request: the HTTP request info
        @return None: the application cannot retrieved.<br>
                otherwise: the application name
        '''
        application = request.META['SERVER_NAME']
        return application

    def getConfigOrNone(self, key, language = None):
        '''Returns a value from the configuration db.
        The value can be language dependent.
        @param key: the key of the wanted value
        @param language: None: the browser defined language will be tested first<br>
                        otherwise: the wanted language
        @return: None: the key is not stored in the configuration db
                otherwise: the value from the database
        '''
        lang = language if language != None else self._language
        record = self._configDb.selectByValues(self._configInfo,
            (('key', key), ('language', lang)), False)
        if record == None and lang != 'en' and language == None:
            record = self._configDb.selectByValues(self._configInfo,
                (('key', key), ('language', 'en')), False)
        if record == None:
            rc = None
        else:  
            rc = unicode(record['value'])
        if (rc == None and self._configAdditional != None 
                and key in self._configAdditional):
            rc = self._configAdditional[key]
        if rc != None:
            rc = self._replaceVar(rc, True)
        return rc
 
    def getConfig(self, key):
        '''Returns a value from the configuration db.
        The value can be language dependent.
        @param key: the key of the wanted value
        @return: if none is found: the parameter <code>key</code><br>
                otherwise: the value from the database
        '''
        rc = self.getConfigOrNone(key)
        if rc == None:
            rc = key
        return rc
   
    def _replaceVar(self, text, withLanguage):
        end = 0
        while end >= 0:
            start = text.find('${', end)
            if start < 0:
                end = -1
            else:
                end = text.find('}', start + 2)
                if end > 0:
                    name = text[start + 2:end]
                    value = None
                    if withLanguage:
                        value = self.getConfigOrNone(name)
                    if value == None:
                        value = self.getConfigOrNoneWithoutLanguage(name)
                    if value != None:
                        head = '' if start == 0 else text[0:start]
                        text = head + value + text[end+1:]
                        # try it again:
                        end = start
        return text
    
    def getConfigOrNoneWithoutLanguage(self, key):
        '''Returns a value from the configuration db.
        The value is language independent.
        @param key: the key of the wanted value
        @return: None: the key is not in the configuration db
                otherwise: the value from the database
        '''
        # None is possible in test suites
        if self._configDb == None:
            rc = None
        else :
            record = self._configDb.selectByKey(self._configInfo, 'key', key)
            rc = None if record == None else record['value']
            if (rc == None and self._configAdditional != None 
                    and key in self._configAdditional):
                rc = self._configAdditional[key]
            if rc != None:
                rc = self._replaceVar(rc, False)
        return rc

    def getConfigWithoutLanguage(self, key):
        '''Returns a value from the configuration db.
        The value is language independent.
        @param key: the key of the wanted value
        @return: if none is found: the parameter <code>key</code><br>
                otherwise: the value from the database
        '''
        rc = self.getConfigOrNoneWithoutLanguage(key)
        if rc == None:
            rc = key
        return rc

    def getTemplateDir(self):
        '''Returnts the directory with the templates.
        @return the name of the directory containing the templates
        '''
        rc = self._homeDir + 'templates/'
        return rc
    
    def log(self, msg):
        '''Logs a message.
        @param msg: the message
        '''
        logger.info(msg)
        self._logMessages.append(msg)
        
    def trace(self, msg):
        '''Logs a message.
        @param msg: the message
        '''
        logger.debug(msg)
        
    def error(self, key, msg = None):
        '''Logs an error message.
        @param key: None of the key of the message (in configuration db)
        @param msg: the message. Only relevant if key == None
        '''
        if key != None:
            if self._configDb == None:
                msg = key
            else:
                msg = self.getConfig(key)
        logger.error(msg)
        self._errorMessages.append(msg)
   
    def valueOfPlaceholder(self, name, specialVars = None):
        '''Gets the value of a placeholder.
        @param name: the placeholder
        @param specialVars: a dictionary of placeholder value pairs
        @return None: unknown placeholder.<br>
                otherwise: the value of the placeholder
        '''
        rc = None
        if name in self._localVars:
            rc = self._localVars[name]
        elif specialVars != None and name in specialVars:
            rc = specialVars[name]
        elif name == '!language':
            rc = self._language
        elif name == '!piwik':
            if os.path.exists("/etc/sidu-base/piwik.html"):
                rc = self.readFile("/etc/sidu-base/piwik.html")
        elif name == '.intro_menu' and self._expandNeedsRightMove:
            rc = self.getConfigOrNone('.intro_menu2')
        else:
            rc = self.getConfigOrNone(name)
        return rc
    
    def setLocalVar(self, name, value):
        '''Sets a placeholder for the snippet.
        @param name     name of the placeholder
        @param value    value of the placeholder. Can be a placeholder to:
                        Then the value will be catched from the configuration db
        '''
        self._localVars[name] = value
        
    def replaceVars(self, source, specialVars = None):
        '''Replaces placeholders by its values.
        Note: Because the values of placeholders can contain placeholders
        the method is recursive.
        @param source: the text containing placeholders
        @param dict: a dictionary for special variables
        @return: the source with replaced placeholders 
        '''
        end = 0
        rc = ''
        while source != None:
            start = source.find("{{", end)
            if start < 0:
                if end == 0:
                    rc = source
                else:
                    rc += source[end:]
                break
            else:
                rc += source[end:start]
                start += 2
                end = source.find("}}", start)
                if end < 0:
                    rc += source[start-2:]
                    break
                else:
                    name = source[start:end]
                    end += 2
                    value = self.valueOfPlaceholder(name, specialVars)
                    if value == None:
                        rc += source[start - 2:end]
                    else:
                        if value.find("{{") >= 0:
                            value = self.replaceVars(value, specialVars)
                        rc += value
                
        return rc
    
    def buildAbsUrl(self, relativeUrl):
        '''Redirects to another location (URL).
        @param relativeUrl: the target url (without domain and port)
        @return: an absolute url
        '''
        absUrl = 'http://' + self._request.META['SERVER_NAME']
        if ('SERVER_PORT' in self._request.META 
                and self._request.META['SERVER_PORT'] != 80):
            absUrl += ':' + unicode(self._request.META['SERVER_PORT'])
        if not relativeUrl.startswith('/'):
            absUrl += '/'
        absUrl += relativeUrl
        return absUrl
        
    def redirect(self, relativeUrl, caller):
        '''Builds a redirection info.
        @param relativeUrl: the target url (without domain and port)
        @return: a PageResult instance
        '''
        rc = PageResult(None, relativeUrl, caller)
        return rc
        
    def nextPowerOf2(self, value):
        '''Returns the maximum of a 2**n where value > 2**n
        @return: max(2**n) where 2**n <= value
        '''
        if value <= 0:
            rc = 0
        else:
            n = 0
            val = value
            while val > 0:
                n += 1
                val /= 2
            rc = 1
            while n > 1:
                rc *= 2
                n -= 1
            assert(rc <= value)
            assert(rc*2 >= value)
        return rc
    '''Reads a file and returns the content as a string.
    @param name        the file's name
    @param marker      None or: only lines starting with this marker will be returned
                       (without marker)
    @param toXml       True: result can be uses as XML content ('<' '>' and '&'
                       will be replaced by entities) 
    @return:       the content of the file as a unicode string
    '''
    def readFile(self, name, marker = None, toXml = False):
        rc = ""
        if os.path.exists(name):
            with codecs.open(name, "r", encoding="utf-8") as fp:
                for line in fp:
                    if marker == None or line.startswith(marker):
                        if marker != None:
                            line = line[len(marker):]
                        if toXml:
                            line = line.replace("&", "&amp;") 
                            line = line.replace("<", "&lt;") 
                            line = line.replace(">", "&gt;") 
                        rc += line
            fp.close()
        return rc
    
    def unicodeToAscii(self, value):
        '''Converts an unicode to ascii.
        @param value:   unicode string to convert
        @return:        a string with special characters converted to %HH syntax
        '''
        if value == None:
            rc = None
        else:
            value = unicode(value)
            hasNoAscii = True
            for cc in value:
                if ord(cc) > 127:
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
    
    def setId(self, cookies):
        '''Sets a session specific id if that does not exist yet.
        @param cookies: the dictionary with the cookies
        '''
        if self._id == None:
            if "id" in cookies:
                self._id = cookies["id"]
                self.trace("ID found: " + self._id)
            else:
                prefix = self._application
                if prefix.startswith("sidu-"):
                    prefix = prefix[5:]
                never = False
                if never:
                    self._id = prefix + Util.encodeFilenameChar(
                        int(math.fmod(time.time()*0x100, 0x100000000)))
                    self._id += Util.encodeFilenameChar(os.getpid())
                self._id = prefix + "." + self._request.META["REMOTE_ADDR"]
                fixId = False
                if fixId:
                    self._id = prefix +".fixid"
                self.trace("new id: {:s} cookies contains {:d}"
                    .format(self._id, len(cookies)))
                cookies["id"] = self._id
                
        
    def readUserData(self):
        '''Reads the user data into a list.
        User data are the field values of all pages.
        '''
        if self._userData == None:
            base = self.getConfigOrNoneWithoutLanguage(".dir.tasks")
            self._userData = []
            if base == None:
                self.error("readUserData(): no .dir.tasks")
                base = "/var/cache/sidu-base/shellserver-tasks/"
            fn = base + self._id + ".data"
            if os.path.exists(fn):
                with codecs.open(fn, "r", "utf-8") as fp:
                    for line in fp:
                        self._userData.append(line)
                fp.close()

    def writeUserData(self):
        '''writes the user data into a file
        User data are the field values of all pages.
        '''
        base = self.getConfigOrNoneWithoutLanguage(".dir.tasks")
        if base == None:
            self.error("writeUserData(): .dir.tasks")
            base = "/var/cache/sidu-base/shellserver-tasks/"
        fn = base + self._id + ".data"
        with codecs.open(fn, "w", "utf-8") as fp:
            for line in self._userData:
                if not line.endswith("\n"):
                    line += "\n"
                fp.write(line)
        fp.close()
        
    def putUserData(self, page, name, value):
        '''Puts a field value of another page.
        @param page:    name of the page
        @param name:    name of the field
        @param value    field value to store
        '''
        prefix = page + "." + name + "="
        newLine = prefix if value == None else prefix + value + "\n"
        found = False
        for ix in xrange(len(self._userData)):
            line = self._userData[ix]
            if line.startswith(prefix):
                self._userData[ix] = newLine
                found = True
                break
        if not found:
            self._userData.append(newLine)
            
    def clearUserData(self):
        '''Delete all field values in the data store.
        '''
        self._userData = []

    def readProgress(self, filename):
        '''Reads the progress file.
        Format of the file: 3 lines:
        
        PERC=30
        CURRENT=<b>Partition created</b>
        COMPLETE=completed 3 of 20
         
        @param filename    name of the progress file
        @return a tuple (percentage, name_of_task, cur_no_of_task, count_of_tasks)
        '''
        task = None
        percentage = None
        currNoOfTask = countOfTasks = None
        hasInfo = False
        if os.path.exists(filename):
            with open(filename, "r") as fp:
                line = fp.readline()
                hasInfo = line != None and line != ""
                if line != None:
                    matcher = re.match(r'PERC=([\d.]+)', line)
                    if matcher != None:
                        percentage = float(matcher.group(1))
                        if percentage < 1:
                            percentage *= 100
                        percentage = int(percentage)
                line = fp.readline()
                if line != None:
                    if line.startswith("CURRENT="):
                        task = line[8:-1]
                line = fp.readline()
                if line != None:
                    matcher = re.match(r'COMPLETE=completed\s+(\d+)\s+of\s+(\d+)', line)
                    if matcher != None:
                        currNoOfTask = int(matcher.group(1))
                        countOfTasks = int(matcher.group(2))
            fp.close() 
            msg = ""
            if task == None:
                msg += " taskname"
                task = "initialization"
            if percentage == None:
                msg += " percentage"
                percentage = 0
            if currNoOfTask == None or countOfTasks == None:
                msg += " taskno"
                currNoOfTask = 0 if currNoOfTask == None else currNoOfTask
                countOfTasks = 0 if countOfTasks == None else countOfTasks
            if hasInfo and msg != "":
                msg = "invalid progress file: " + filename + msg
                self.error(msg)
        if percentage == None:
            percentage = 0
        return (percentage, task, currNoOfTask, countOfTasks)               

    def translateTask(self, keyPrefix, message):
        '''Translate the English message into the current.
        @param message: the English message to translate
        @return: message: no translation available.
                otherwise: the translation
        '''
        keyPrefix += "."
        count = self.getConfigOrNone(keyPrefix + "count")
        if count != None and count != "":
            for no in xrange(int(count)):
                msg = self.getConfigOrNone(keyPrefix + str(no+1))
                if msg != None and msg.startswith(message):
                    message = msg[len(message) + 1:]
                    break
        return message
