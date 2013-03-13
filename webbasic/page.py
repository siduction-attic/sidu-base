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
        self._data = PageData(session)
        self._snippets = None
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
        self._data.add(FieldData(name, defaultValue, dataType))
          
    def buildHtml(self, htmlMenu):
        '''Builds the HTML text of the page.
        @param htmlMenu: the HTML code for the menu
        @return: the content part of the page
        '''
        body = self._snippets.get('MAIN')
        if hasattr(self, 'changeContent'):
            body = self.changeContent(body)
            
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
        for key in fields:
            if key.startswith('button_'):
                rc = key
                break
        return rc
    
    def handle(self, htmlMenu, fieldValues, cookies):
        '''Generic handling of the page.
        @param fieldValues: the dictionary containing the field values (GET or POST)
        @param cookies: the cookie dictionary
        @return: a PageResult instance
        '''
        self.defineFields()
        
        self._data.getFromCookie(self._name, cookies)
        self._data.getFromHTTP(fieldValues)
        
        # Checks wether a button has been pushed:
        button = self.findButton(fieldValues)
        rc = None
        if button != None:
            rc = self.handleButton(button)
        
        if rc == None:
            fn = self._session.getTemplateDir() + 'pageframe.html'
            frame = Util.readFileAsString(fn)
            
            content = self.buildHtml(htmlMenu)
            content = self._data.replaceValues(content)
            content = self._session.replaceVars(content)
            env = { 'CONTENT' : content, 
                'MENU' : htmlMenu,
                'META_DYNAMIC' : self._session._metaDynamic,
                'STATIC_URL' : ''
                }
            frame = self._session.replaceVars(frame, env)
            rc = PageResult(frame)
            
        self._data.putToCookie()
        return rc