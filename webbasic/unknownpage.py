'''
Created on 14.04.2014

@author: hm
'''
from page import Page

class UnknownPage(Page):
    '''
    A page displayed while waiting for an given event.
    '''


    def __init__(self, session):
        '''
        Constructor.
        @param session: the session info
        '''
        Page.__init__(self, 'unknown', session)
        
        
    def defineFields(self):
        '''Must be overwritten!
        '''
        # hidden fields:
        pass
        
    def changeContent(self, body):
        '''Changes the template in a customized way.
        @param body: the HTML code of the page
        @return: the modified body
        '''
        body = self._snippets.get("PROGRESS")
        return body
    
    def handleButton(self, button):
        '''Do the actions after a button has been pushed.
        @param button: the name of the pushed button
        @return: None: OK<br>
                otherwise: a redirect info (PageResult)
        '''
        pageResult = None
        if button == 'button_home':
            pageResult = self._session.redirect("/home", "waitpage.handleButton")
        else:
            self.buttonError(button)
            
        return pageResult
    
        