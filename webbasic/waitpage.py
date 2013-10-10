'''
Created on 01.05.2013

@author: hm
'''

import re, os.path
from webbasic.page import Page

class WaitPage(Page):
    '''
    A page displayed while waiting for an given event.
    '''


    def __init__(self, session):
        '''
        Constructor.
        @param session: the session info
        '''
        Page.__init__(self, 'wait', session)
        
        
    def afterInit(self):
        '''Will be called after all initializations are done.
        Note: self._globalPage will be set after the constructor.
        This method can be overridden.
        '''
        fileStop = self._globalPage.getField('wait.file.stop')
        if fileStop != None and os.path.exists(fileStop):
            follower = self._globalPage.getField('wait.page')
            self._session.trace("wait: found: {:s} goto {:s}".format(fileStop, follower))
            self._redirect = self._session.redirect(follower, "wait-" + follower)
        else:
            self.setRefresh()

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
        argsIntro = self._globalPage.getField("wait.intro.args")
        if argsIntro == "":
            argsIntro = None
        argsDescr = self._globalPage.getField("wait.descr.args")
        translationKey = self._globalPage.getField("wait.translation")
        if argsDescr == "":
            argsDescr = None
        body = self.replaceGlobalField("wait.intro.key", "wait.intro", 
            argsIntro, None, "{{intro}}", body)
        body = self.replaceGlobalField("wait.descr.key", "wait.descr", 
            argsDescr, "DESCRIPTION", "{{txt_description}}", body)
        fnProgress = self._globalPage.getField("wait.file.progress")
        progressBody = ""
        if fnProgress != None and fnProgress != "":
            progressBody = self._snippets.get("PROGRESS")
            (percentage, task, no, count) = self._session.readProgress(fnProgress)
            if task == None:
                task = ""
            if task != "" and translationKey != None:
                task = self._session.translateTask(translationKey, task)
            progressBody = progressBody.replace("{{percentage}}", unicode(percentage))
            progressBody = progressBody.replace("{{width}}", unicode(percentage))
            progressBody = progressBody.replace("{{task}}", task)
            progressBody = progressBody.replace("{{no}}", unicode(no))
            progressBody = progressBody.replace("{{count}}", unicode(count))
            demo = ""
            progressBody = progressBody.replace("{{DEMO_TEXT}}", demo)
        body = body.replace("{{PROGRESS}}", progressBody)
        return body
    
    def handleButton(self, button):
        '''Do the actions after a button has been pushed.
        @param button: the name of the pushed button
        @return: None: OK<br>
                otherwise: a redirect info (PageResult)
        '''
        pageResult = None
        if button == 'button_cancel':
            page = self._globalPage.getField("wait.page")
            pageResult = self._session.redirect(page, "waitpage.handleButton")
        else:
            self.buttonError(button)
            
        return pageResult
    
    @staticmethod
    def defineGlobalFields(globalPage):
        '''Defines the fields used in the global page.
        Should be called from GlobalPage.defineFields()
        @param globalPage    the instance of the global page
        '''
        globalPage.addField("wait.intro.args")
        globalPage.addField("wait.descr.args")
        globalPage.addField("wait.intro.key")
        globalPage.addField("wait.descr.key")
        globalPage.addField("wait.page")
        globalPage.addField("wait.file.stop")
        globalPage.addField("wait.file.progress")
