'''
Created on 03.02.2013

@author: hm
'''
import os.path, re, logging

from util.configurationbuilder import ConfigurationBuilder
from util.sqlitedb import SqLiteDb
from webbasic.page import PageResult

logger = logging.getLogger(__name__)

class SessionBase(object):
    '''
    Manages session specific data and services.
    Live time: request
    '''

    @staticmethod
    def isHomeDir(path):
        if not path.endswith(os.sep):
            path += os.sep
        rc = path if os.path.exists (path + 'data/config.db') else None
        # logger.debug('isHomeDir({:s}: {:s}'.format(path, '' if rc else rc))
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
        @param globalPage: the page holding global (= page independent) fields
        '''
        self._request = request
        self._application = application
        self._pageAndBookmark = None
        self._metaDynamic = ''
        self._supportedLanguages = languages
        self._logMessages = []
        self._errorMessages = []
        self._globalPage = None
        
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
        logger.debug('SessionBase(): lang: {:s} home: {:s} db: {:s}'.format(
            self._language if self._language else '',
            self._homeDir if self._homeDir else '',
            self._configDbName if self._configDbName else ''))


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
            rc = record['value']
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
   
    def getConfigOrNoneWithoutLanguage(self, key):
        '''Returns a value from the configuration db.
        The value is language independent.
        @param key: the key of the wanted value
        @return: None: the key is not in the configuration db
                otherwise: the value from the database
        '''
        record = self._configDb.selectByKey(self._configInfo, 'key', key)
        value = None if record == None else record['value']
        return value

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
        if specialVars != None and name in specialVars:
            rc = specialVars[name]
        elif name == '!language':
            rc = self._language
        else:
            rc = self.getConfigOrNone(name)
        return rc
    
    def replaceVars(self, source, specialVars = None):
        '''Replaces placeholders by its values.
        @param source: the text containing placeholders
        @param dict: a dictionary for special variables
        @return: the source with replaced placeholders 
        '''
        end = 0
        rc = ''
        while True:
            start = source.find('{{', end)
            if start < 0:
                if end == 0:
                    rc = source
                else:
                    rc += source[end:]
                break
            else:
                rc += source[end:start]
                start += 2
                end = source.find('}}', start)
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
                        rc += value
                
        return rc
    
    def buildAbsUrl(self, relativeUrl):
        '''Redirects to another location (URL).
        @param relativeUrl: the target url (without domain and port)
        @return: an absolute url
        '''
        absUrl = 'http://' + self._request.META['SERVER_NAME'];
        if ('SERVER_PORT' in self._request.META 
                and self._request.META['SERVER_PORT'] != 80):
            absUrl += ':' + str(self._request.META['SERVER_PORT'])
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
        