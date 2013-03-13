'''
Created on 03.02.2013

@author: hm
'''
import os.path, re, logging

from util.configurationbuilder import ConfigurationBuilder
from util.sqlitedb import SqLiteDb
from util.util import Util

class SessionBase(object):
    '''
    Manages session specific data and services.
    Live time: request
    '''


    def __init__(self, request, languages, application = None, openConfig = True):
        '''
        Constructor
        @param request: the HTTP request info
        @param languages: the languages which are supported by the application
        @param application: None of the name of the application
        @param openConfig: True: the configuration database will be opened
        '''
        self._request = request
        self._application = application
        self._pageAndBookmark = None
        self._metaDynamic = ''
        self._supportedLanguages = languages
        
        self.handleMetaVar()
        if application == None:
            application = self.getApplicationName(request)
        self._application = application
        self._configDbName = '/etc/' + application + '/config.db'
        if not os.path.exists(self._configDbName):
            self._configDbName = '/usr/share/' + application + '/config.db'
        if not os.path.exists(self._configDbName):
            self._configDbName = '/tmp/' + application + '/config.db'
        
        self._configInfo = ConfigurationBuilder.getTableInfo()
        self._configDb = SqLiteDb(self._configDbName)
        self._configDb.addTableInfo(self._configInfo)
        
        if openConfig:
            self._homeDir = self.getConfigWithoutLanguage('.home.dir')
        else:
            self._homeDir = None
        if self._homeDir and not self._homeDir.endswith('/'):
            self._homeDir += '/'
        self._language = self.correctLanguage(self.getMetaVar('HTTP_ACCEPT_LANGUAGE'))

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

    def getConfig(self, key, language = None):
        '''Returns a value from the configuration db.
        The value can be language dependent.
        @param key: the key of the wanted value
        @param language: None: the browser defined language will be tested first<br>
                        otherwise: the wanted language
        @return: if none is found: the parameter <code>key</code><br>
                otherwise: the value from the database
        '''
        if language == None:
            language = self._language
        record = self._configDb.selectByValues(self._configInfo,
            (('key', key), ('language', language)), False)
        if record == None and language != 'en':
            record = self._configDb.selectByValues(self._configInfo,
                (('key', key), ('language', 'en')), False)
        if record != None:  
            value = record['value']
        else:
            value = key
        return value
    
    def getConfigWithoutLanguage(self, key):
        '''Returns a value from the configuration db.
        The value is language independent.
        @param key: the key of the wanted value
        @return: if none is found: the parameter <code>key</code><br>
                otherwise: the value from the database
        '''
        record = self._configDb.selectByKey(self._configInfo, 'key', key)
        value = key if record == None else record['value']
        return value

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
        logging.info(msg)
        
    def trace(self, msg):
        '''Logs a message.
        @param msg: the message
        '''
        logging.debug(msg)
        
    def error(self, key, msg = None):
        '''Logs an error message.
        @param key: None of the key of the message (in configuration db)
        @param msg: the message. Only relevant if key == None
        '''
        if key != None:
            msg = self.getConfig(key)
        logging.error(msg)
   
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
        elif name == 'language':
            rc = self._language
        else:
            rc = self.getConfig(name)
            if rc == name:
                rc = None
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
        
        
        