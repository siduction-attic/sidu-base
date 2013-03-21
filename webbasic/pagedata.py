'''
Created on 10.03.2013

@author: hm
'''
import re
from Cookie import SimpleCookie
from gi.overrides.keysyms import currency

SEPARATOR = '~|^'

class PageData:
    '''Stores the page specific data, e.g. the field values of a form.
    '''
    
    # static member! There is only one cookie for all pages!
    _cookie = None
    
    def __init__(self, session):
        '''Constructor.
        @param session: sessinfo info
        '''
        self._session = session
        # String --> FieldData
        self._dict = {}
        self._list = []
        # the name of the page specific entry in the cookie:
        self._cookieName = None
        
        
    def add(self, field):
        '''Adds a field to the fieldlist.
        @param field: the field to add
        '''
        field._no = len(self._list)
        self._list.append(field)
        self._dict[field._name] = field

    def get(self, name):
        '''Gets a value from a field.
        @param key: the name of the field
        @return: None: unknown field<br>
                otherwise: the field's value
        '''
        rc = None
        if name in self._dict:
            rc = self._dict[name]._value
        else:
            self._session.error('PageData.put: Unknown field: ' + name)
        return rc
    
    def put(self, name, value):
        '''Puts a value to a field.
        @param key: the name of the field
        @param value: the new value
        '''
        if name in self._dict:
            self._dict[name]._value = value
        else:
            self._session.error('PageData.put: Unknown field: ' + name)
            
    def putError(self, name, errorKey):
        '''Puts an error message (exactly its key) to a field.
        @param name: the field's name
        @param errorKey: the key of the error message
        @param value: the new value
        @return: True
        '''
        if name in self._dict:
            self._dict[name]._errorKey = errorKey
        else:
            self._session.error('PageData.putError: Unknown field: ' + name)
        return True
       
    def getFromHTTP(self, environ):
        '''Gets the field values from the HTTP data, e.g. request.GET.
        @param environ: the dictionary with the name value pairs
        '''
        for field in self._list:
            name = field._name
            if name in environ:
                field._value = environ[name]
    
    def getFromCookie(self, name, cookieData):
        '''Gets the values from the client's cookie.
        @param name: the name of the cookie part. 
        @param cookieData: the cookie dictionary
        '''
        if PageData._cookie == None:
            PageData._cookie = cookieData
        cookie = PageData._cookie
        self._cookieName = name
        values = ''
        key = 'D_' + name
        if key in cookie:
            version = cookie['V_' + name]
            values = cookie[key]
        currentVersion = self.getDataVersion()
        if values != None and values != '' and version == currentVersion:
            values = values.split(SEPARATOR)
            for ix in xrange(len(values)):
                field = self._list[ix]
                val = values[ix]
                if field._type == 'd':
                    val = int(val)
                field._value = val
  
    def putToCookie(self):
        '''Puts the data to the Cookies
        '''
        value = None
        for field in self._list:
            val = str(field._value) if field._value != None else ''
            if value == None:
                value = val
            else:
                value += SEPARATOR + val
        PageData._cookie['D_' + self._cookieName] = value
        PageData._cookie['V_' + self._cookieName] = self.getDataVersion()
        
    
    def replaceValues(self, body, errorPrefix, errorSuffix):
        '''Replaces the placeholders for field values and field errors
        by their values.
        @param body: the string which will be changed
        @return: the body with expanded placeholders
        ''' 
        for field in self._list:
            value = '' if field._value == None else str(field._value)
            body = body.replace('{{val_' + field._name + '}}', value)
            if field._errorKey == None:
                value = ''
            else:
                key = field._errorKey
                value = '' if errorPrefix == None else errorPrefix
                value += self._session.getConfig(key)
                if errorPrefix != None:
                    value += errorSuffix
            body = body.replace('{{err_' + field._name + '}}', value)
        return body
            
    def getDataVersion(self):
        '''Returns a string which represents the structure of the data.
        This can signal the validity of external stored data.
        @return: a structure specific string
        '''
        rc = ''
        for field in self._list:
            rc += field._type 
        return rc

    def importData(self, name, fieldValues, cookieData):
        '''Builds a PageData instance for a given page.
        @param name: the name of the container, e.g. the page name
        @param fieldValues: the GET or POST dictionary with the current field values
        @param cookieData: the cookie data from the client
        '''
        self.getFromCookie(name, cookieData)
        if fieldValues != None:
            self.getFromHTTP(fieldValues)

        
        
class FieldData:
    '''Stores a field of a page.
    '''
    def __init__(self, name, defaultValue = None, dataType = "s"):
        '''Constructor.
        @param name: the field name
        @param defaultValue: the start value
        @param dataType: "s": string "d": integer "p": password
        '''
        self._no = None
        self._name = name
        self._value = defaultValue
        self._type = dataType
        self._errorKey = None
    
    