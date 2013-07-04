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
            self._redirect = self._session.redirect(follower, "wait-" + follower)
        else:
            self.setRefresh(3)

    def defineFields(self):
        '''Must be overwritten!
        '''
        # hidden fields:
        pass
        
    def translateTask(self, keyPrefix, message):
        '''Translate the English message into the current.
        @param message: the English message to translate
        @return: message: no translation available.
                otherwise: the translation
        '''
        keyPrefix += "."
        count = self._session.getConfigOrNone(keyPrefix + "count")
        if count != None and count != "":
            for no in xrange(int(count)):
                msg = self._session.getConfigOrNone(keyPrefix + str(no+1))
                if msg != None and msg.startswith(message):
                    message = msg[len(message) + 1:]
                    break
        return message
        
    def changeContent(self, body):
        '''Changes the template in a customized way.
        @param body: the HTML code of the page
        @return: the modified body
        '''
        argsIntro = self._globalPage.getField("wait.intro.arg")
        if argsIntro == "":
            argsIntro = None
        argsDescr = self._globalPage.getField("wait.descr.arg")
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
            (percentage, task, no, count) = self.readProgress(fnProgress)
            if task == None:
                task = ""
            if task != "":
                task = self.translateTask(translationKey, task)
            progressBody = progressBody.replace("{{percentage}}", str(percentage))
            progressBody = progressBody.replace("{{width}}", str(percentage))
            progressBody = progressBody.replace("{{task}}", task)
            progressBody = progressBody.replace("{{no}}", str(no))
            progressBody = progressBody.replace("{{count}}", str(count))
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
        percentage = currNoOfTask = countOfTasks = None
        if os.path.exists(filename):
            with open(filename, "r") as fp:
                line = fp.readline()
                if line != None:
                    matcher = re.match(r'PERC=(\d+)', line)
                    if matcher != None:
                        percentage = int(matcher.group(1))
                line = fp.readline()
                if line != None:
                    if line.startswith("CURRENT="):
                        task = line[8:-1]
                line = fp.readline()
                if line != None:
                    matcher = re.match(r'COMPLETE=completed (\d+) of (\d+)', line)
                    if matcher != None:
                        currNoOfTask = int(matcher.group(1))
                        countOfTasks = int(matcher.group(2))
            fp.close() 
        msg = ""
        if task == None:
            msg += " taskname"
            task = "?"
        if percentage == None:
            msg += " percentage"
            percentage = 0
        if currNoOfTask == None or countOfTasks == None:
            msg += " taskno"
            currNoOfTask = 0 if currNoOfTask == None else currNoOfTask
            countOfTasks = 0 if countOfTasks == None else countOfTasks
        if msg != "":
            msg = "invalid progress file: " + filename + msg
            self._session.error(msg)
        return (percentage, task, currNoOfTask, countOfTasks)               

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
