'''
Created on 09.03.2013

@author: hm
'''
import os.path

from util.util import Util
from pagedata import PageData, FieldData
from webbasic.htmlsnippets import HTMLSnippets

class PageResult:
    '''Stores the "result" of a page: a HTML code or a redirection URL.
    '''
    def __init__(self, body = None, url = None, caller = None): 
        self._body = body
        self._url = url
        self._caller = caller

class Page(object):
    '''
    classdocs
    '''

    def __init__(self, name, session, readSnippets = True):
        '''Constructor.
        @param name: the name of the page. Defines the template filename
        @param session: the session info
        @param readSnippets: True: the page specific snippets will be read
        '''
        self._name = name
        self._session = session
        self._pageData = PageData(session)
        self._snippets = None
        self._globalPage = None
        self._errorPrefix = None
        self._errorSuffix = None
        if readSnippets:
            self._snippets = HTMLSnippets(session)
            self._snippets.read(name)
        
    def defineFields(self):
        '''This method must be overwritten:
        If not an error message must be displayed.
        '''
        self._session.error('missing defineFields(): ' + self._name)
        
    def handleButton(self, button):
        '''This method must be overwritten:
        If not an error message must be displayed.
        @param button: the pushed button
        '''
        self._session.error('missing handleButton(): ' + self._name)
        
    def addField(self, name, defaultValue = None, dataType = 's'):
        '''Adds a field definition.
        Delegation to PageData.add()
        @param name: the field's name
        @param defaultValue: the value for the first time
        @param dataType: the field's data type
        '''
        self._pageData.add(FieldData(name, defaultValue, dataType))
          
    def getField(self, name):
        '''Returns a value from a (virtual) field.
        Delegation to PageData.get()
        @param name: the field's name
        '''
        rc = self._pageData.get(name)
        return rc

    def putField(self, name, value):
        '''Puts a value to a (virtual) field.
        Delegation to PageData.put()
        @param name: the field's name
        @param value: the value to set
        '''
        self._pageData.put(name, value)

    def buildHtml(self, htmlMenu):
        '''Builds the HTML text of the page.
        @param htmlMenu: the HTML code for the menu
        @return: the content part of the page
        '''
        body = self._snippets.get('MAIN')
        if hasattr(self, 'changeContent'):
            body = self.changeContent(body)
        body = self._session.replaceVars(body)    
        return body
            
    def errorPage(self, key):
        '''Returns the content of an error message page.
        @param key: the key of the error message
        @return: the content of the error page
        '''
        message =  '' if self._session._configDb == None else self._session.getConfig(key)
        rc = '''
<h1>{{page.error.txt_header}}</h1>
<p class="error">+++ {:s}</p>
'''         .format(message)
        return rc
    
    def buttonError(self, button):
        '''Generic handling of an unknown button.
        @param button: the button's name
        @return: None
        '''
        self._session.error('unknown button {:s} in page {:s}'.format(button, self._name))
        return None
    
    def findButton(self, fields):
        '''Tests whether a button has been pushed.
        @param fields: a dictionary with the field values
        @param: None: no button has been pushed<br>
            otherwise: the name of the pushed button
        '''
        rc = None
        if fields != None:
            for key in fields:
                if key.startswith('button_'):
                    rc = key
                    break
        return rc
    
    def fillOpts(self, field, texts, values, currentIndex, source):
        '''Builds the body of an <select> element.
        The placeholder will be replaced by the values.
        @param field: the name of the field (without page name)
        @param ixCurrent: the index of the selected entry
        @param source: the HTML code containing the field to change
        @return: the source with expanded placeholder for the field
        '''
        opts = None
        for ix in xrange(len(texts)):
            if opts == None:
                opts = ''
            else :
                opts += '\n'
            opts += '<option selected="selected"' if ix == currentIndex else '<option'
            if values != None and ix < len(values):
                opts += ' value="' + values[ix] + '"'
            opts += '>' + texts[ix] + '</option>'
        name = '{{body_' + field + '}}'
        source = source.replace(name, opts)
        return source
            
    def getOptValues(self, field):
        '''Gets the texts and (if available) the values of a selection field.
        @param field: the name of the field (without page name)
        @return: a tuple (texts, values)
        '''       
        key = self._name + '.opts_' + field
        values = self._session.getConfig(key)
        texts = values[1:].split(values[0:1])
        key = self._name + '.vals_' + field
        values = self._session.getConfigOrNoneWithoutLanguage(key)
        if values != None:
            values = values[1:].split(values[0:1])
        return (texts, values)
    
    def indexOfFieldValues(self, field, value):
        '''Returns the index of a value in the option value list.
        @param field: the fieldname (without page)
        @param value: the value to find
        @return: None: not found<br>
                otherwise: the index of the value in the value list
        '''
        key = self._name + '.vals_' + field
        values = self._session.getConfigOrNoneWithoutLanguage(key)
        rc = None
        if values != None:
            items = values[1:].split(values[0:1])
            for ix in xrange(len(items)):
                if items[ix] == value:
                    rc = ix
                    break
            if rc == None:
                self._session.error('{:s}: {:s} not found in {:s}'.format(
                    field, value, values))
        return rc
        
        
    def fillOptionsSelectedByIndex(self, field, ixCurrent, source):
        '''Builds the body of an <select> element.
        @param field: the name of the field (without page name)
        @param ixCurrent: the index of the selected entry
        @param source: the HTML code containing the field to change
        @return: the source with expanded placeholder for the field
        '''
        texts, values = self.getOptValues(field)
        source = self.fillOpts(field, texts, values, ixCurrent, source)
        return source
            
    def handle(self, htmlMenu, fieldValues, cookies):
        '''Generic handling of the page.
        @param fieldValues: the dictionary containing the field values (GET or POST)
        @param cookies: the cookie dictionary
        @return: a PageResult instance
        '''
            
        self.defineFields()
        self._pageData.importData(self._name, fieldValues, cookies)

        self._pageData.correctCheckBoxes(fieldValues);

        # Checks wether a button has been pushed:
        button = self.findButton(fieldValues)
        rc = None
        if button != None:
            rc = self.handleButton(button)
        
        if rc == None:
            fn = self._session.getTemplateDir() + 'pageframe.html'
            frame = Util.readFileAsString(fn)
            
            content = self.buildHtml(htmlMenu)
            content = self._pageData.replaceValues(content, self._errorPrefix,
                    self._errorSuffix)
            content = self._session.replaceVars(content)
            title = self._session.getConfig(self._name + '.title')
            env = { 'CONTENT' : content, 
                'MENU' : htmlMenu,
                'META_DYNAMIC' : self._session._metaDynamic,
                'STATIC_URL' : '',
                '!title' : title
                }
            frame = self._session.replaceVars(frame, env)
            rc = PageResult(frame)
            
        self._pageData.putToCookie()
        globalPage = self._globalPage
        if globalPage != None:
            globalPage._pageData.putToCookie()
        return rc
    
    def fillCheckBox(self, name, body):
        '''Handles the state of a checkbox.
        @param field: the field's name
        @param body: the html code containing the checkbox
        @return: the body with replaced placeholder for the field 
        '''
        value = self.getField(name)
        checked = '' if value != 'T' else 'checked="checked"'
        body = body.replace('{{chk_' + name + '}}', checked)
        return body
    