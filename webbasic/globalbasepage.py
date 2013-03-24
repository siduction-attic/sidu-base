'''
Created on 14.03.2013

@author: hm
'''

import time
from webbasic.page import Page
from webbasic.pagedata import PageData
from util.util import Util

class GlobalBasePage(Page):
    '''
    Container for the global (= page independent) data
    '''


    def __init__(self, session, cookies):
        '''
        Constructor.
        @param session: the session info
        @cookies: the COOKIE dictionary from the request 
        '''
        Page.__init__(self, 'global', session, False)
        
        self.addField('session.key')
        self.addField('language')
        self.addField('browser.lang')
        self.addField('expert')
        self.defineFields()
        
        self._pageData.importData(self._name, None, cookies)
        lang = self.getField('language')
        oldBrowserLanguage = self.getField('browser.lang')
        currentBrowserLang = oldBrowserLanguage
        if hasattr(session._request, 'META'):
            currentBrowserLang = session.correctLanguage(
                session.getMetaVar('HTTP_ACCEPT_LANGUAGE'))
        if currentBrowserLang != oldBrowserLanguage:
            self._session.trace('browser language changed from {:1} to {:s}'
                    .format(oldBrowserLanguage, currentBrowserLang))
            lang =currentBrowserLang
            self.putField('browser.lang', currentBrowserLang)
            self.putField('language', currentBrowserLang)
        if lang != None:
            self._session._language = lang
        
    def defineFields(self):
        '''Must be overwritten!
        '''
        self._session.error('GlobalBasePage: missing defineFields()')
        
    def getSessionKey(self):
        '''Returns a unique (over all clients) string.
        @return a key available while the whole session
        '''
        key = self._pageData.get('session.key')
        if key == None or len(key) < 4+8:
            ip = (127, 0, 0, 2)
            if hasattr(self._session, '_request'):
                ip = self._session._request.META['REMOTE_ADDR'].split('.')
            key = "{:04x}{:02x}{:02x}{:02x}{:02x}".format(int(
                time.time()) & 0xffff, int(ip[0]), int(ip[1]), 
                    int(ip[2]), int(ip[3]))
            self._pageData.put('session.key', key)
        return key
    
    def getTempFile(self, prefix):
        '''Returns a application and session specific filename.
        @param prefix: the first part of the node name
        @return: a unique filename (over all clients) in the temporary directory
        '''
        key = self.getSessionKey()
        rc = Util.getTempFile(prefix + key, self._session._application)
        return rc
            