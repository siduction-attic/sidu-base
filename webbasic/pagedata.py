'''
Created on 10.03.2013

@author: hm
'''
SEPARATOR = '~|^'
PREFIX_ERROR_KEY = "\f"

class PageData:
    '''Stores the page specific data, e.g. the field values of a form.
    One cookie stores two (key,value) pairs:
    ("D_<page_name>", data)
    ("V_<page_name>", dataTypes) 
    <data> and <versions> are constructed strings separated by "~|^"
    dataType: "s": string "d": integer "p": password "b": boolean "v": vocabulary
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
        self._generalErrors = ""
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
        if rc == "" and self._dict[name]._type == 'v':
            rc = self._dict[name]._defaultValue
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
        @param name: the field's name. If None a standard field will be taken
        @param errorKey: the key of the error message
        @return: True
        '''
        text = PREFIX_ERROR_KEY + self._session.getConfig(errorKey)
        rc = self.putErrorText(name, text)
        return rc
       
    def putErrorText(self, name, text):
        '''Puts an error message (exactly its key) to a field.
        @param name: the field's name. If None a standard field will be taken
        @param text: the key of the error message
        @return: True
        '''
        if name == None:
            if self._generalErrors == None:
                self._generalErrors = text
            else:
                self._generalErrors = "<br/>\n" + text
        elif name in self._dict:
            self._dict[name]._error = text
        else:
            self._session.error('PageData.putErrorText: Unknown field: ' + name)
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
            count = min(len(values), len(self._list))
            for ix in xrange(count):
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
            val = unicode(field._value) if field._value != None else ''
            if value == None:
                value = val
            else:
                value += SEPARATOR + val
        PageData._cookie['D_' + self._cookieName] = value
        PageData._cookie['V_' + self._cookieName] = self.getDataVersion()
        
    def clearCookies(self):
        '''Resets all values in the cookies.
        '''
        for entry in PageData._cookie:
            PageData._cookie[entry] = ""
    
    def replaceValues(self, body, errorPrefix, errorSuffix):
        '''Replaces the placeholders for field values and field errors
        by their values.
        @param body: the string which will be changed
        @param errorPrefix: None or a phrase put in front of the error message
        @param errorSuffix: None or a phrase put behind the error message
        @return: the body with expanded placeholders
        ''' 
        for field in self._list:
            value = '' if field._value == None else unicode(field._value)
            if (field._type != "b"):
                body = body.replace('{{val_' + field._name + '}}', value)
            else:
                content = "" if field._value == "F" else 'checked="checked"'
                body = body.replace("{{checked_" + field._name + "}}", content)
            if field._error == None:
                value = ""
            else:
                text = field._error
                value = '' if errorPrefix == None else errorPrefix
                if text.startswith(PREFIX_ERROR_KEY):
                    text = self._session.getConfig(text[1:])
                value += text
                if errorPrefix != None:
                    value += errorSuffix
            body = body.replace('{{err_' + field._name + '}}', value)
        body = body.replace("{{error_message}}", self._generalErrors)
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

    def correctCheckBoxes(self, fieldValues):
        '''Corrects the value of the checkboxes.
        
        A checkboxes has a silly behaviour: If it is not checked the field
        does not appear in the fieldvalues.
        Without special handling the field cannot reset, because the value
        is defined by the cookie value.
        Solution: If the field is not in the fieldValues, the value is set
        to 'F'
        @param fieldValues: the field values given from HttpRequest
        '''
        # at least there must be one field, e.g. a button:
        if fieldValues != None and len(fieldValues) > 0:
            # for all checkboxes:
            for field in self._list:
                if field._type == 'b':
                    if field._name not in fieldValues:
                        field._value = 'F'
        
        
class FieldData:
    '''Stores a field of a page.
        @param name: the field's name
        @param defaultValue: the value for the first time
        @param dataType: "s": string "d": integer "p": password "b": boolean 'v': vocabulary
    '''
    def __init__(self, name, defaultValue = None, dataType = "s"):
        '''Constructor.
        @param name: the field name
        @param defaultValue: the start value
        @param dataType: "s": string "d": integer "p": password 
                        "b": boolean "v": vocabulary
        '''
        self._no = None
        self._name = name
        self._value = defaultValue
        self._type = dataType
        # if starting with "\f" this is an error text, otherwise an error key
        self._error = None
        self._defaultValue = defaultValue
    
    