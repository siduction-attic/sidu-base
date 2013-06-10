'''
Created on 04.03.2013

@author: hm
'''

import re, os.path

from webbasic.sessionbase import SessionBase
from util.util import Util
from util.configurationbuilder import ConfigurationBuilder
from webbasic.page import Page

class Aux(object):
    '''
    Implements service around the PUnit tests.
    '''


    def __init__(self):
        '''
        Constructor.
        '''
        self._init = True

    
    @staticmethod
    def getRequestApplication():
        rc = DummyRequest()
        return rc
 
    @staticmethod
    def getRequest():
        rc = DummyRequest()
        return rc

    @staticmethod
    def getSession(application = None, request = None, homeDir = None, 
            filesAndLanguages = None):
        request = Aux.getRequest() if request == None else request
        Aux.buildConfigDb(application, filesAndLanguages)
        session = SessionBase(request, ['de', 'en', 'pt-br'], application, homeDir)
        return session

    @staticmethod
    def getSessionWithStdConfig(application = None, request = None, 
            filesAndLanguages = None):
        request = Aux.getRequest() if request == None else request
        homeDir = os.path.realpath(".")
        if os.path.exists(homeDir + "/../data/config.db"):
            homeDir = os.path.dirname(homeDir)
        session = SessionBase(request, ['de', 'en', 'pt-br'], application, homeDir)
        return session
    
    @staticmethod
    def buildDummyHome(application = None):
        if application == None:
            application = 'testappl'
        subdir = Util.getTempDir(application, True)
        Util.getTempDir('testappl/config', True)
        Util.getTempDir('testappl/templates', True)
        return subdir
    @staticmethod
    def getConfigFilename(lang):
        if lang == None:
            fn = Util.getTempFile('testappl.conf', 'testappl')
        else:
            fn = Util.getTempFile(
                'testappl_' + lang + '.conf', 'testappl')
        return fn
     
    @staticmethod
    def buildConfigDb(application = None, filesAndLanguages = None):
        if application == None:
            application = 'testappl'
        if filesAndLanguages == None:
            fn = Aux.getConfigFilename(None)
            if not os.path.exists(fn):
                Util.writeFile(fn, '''
# Test config file
test.language=de
data.string.long=123456789 123456789 123456789 123456789 123456789 123456789
data.int=34777
data.bool=True
'''
                    )
            fnDe = Aux.getConfigFilename('de')
            if not os.path.exists(fnDe):
                Util.writeFile(fnDe, '''
# Test config file for German
title=Modultest
'''
                )
            fnEn = Aux.getConfigFilename('en')
            if not os.path.exists(fnEn):
                Util.writeFile(fnEn, '''
# Test config file for English
title=Module Test
'''
                )
            filesAndLanguages = ((fn, None), (fnDe, 'de'), (fnEn, 'en'))
        builder = ConfigurationBuilder()
        Util.getTempDir(application + os.sep + 'data', True)
        fnDb = Util.getTempFile('config.db', application, 'data')
        builder.buildSqLiteDb(fnDb, filesAndLanguages)

    @staticmethod
    def getMetaData(additionalVars):
        vvars = {
            'HTTP_ACCEPT_LANGUAGE' : 'de,pt-BR,de; abc',
            'SERVER_NAME' : 'testappl',
            'SERVER_PORT' : '8086',
            }
        for key in additionalVars:
            vvars[key] = additionalVars[key]
        return vvars
      
    @staticmethod 
    def buildPageTemplate(application, pageName):
        fn = Util.getTempFile(pageName + '.snippets', 
            application + os.sep + 'templates')
        if not os.path.exists(fn):
            Util.writeFile(fn, '''
MAIN:
<h1>{{title}}</h2>
<form>
<input type="text" name="f1" value="{{val_f1}}" />
</form>
'''             )
        return fn
         
    @staticmethod 
    def buildPageFrame(application = None):
        fn = Util.getTempFile('pageframe.html', 
            application + os.sep + 'templates')
        if not os.path.exists(fn):
            Util.writeFile(fn, '''
<html>
<head>
{{META_DYNAMIC}}
</head>
<body>
{{MENU}}
{{CONTENT}}
</body>
</html>
'''             )
        return fn
         
            
    @staticmethod
    def compareText(source1, source2):
        if source1 == None:
            rc = 'arg1 == None'
        elif source2 == None:
            rc = 'arg2 == None'
        else:
            list1 = re.split("\n", source1)
            list2 = re.split("\n", source2)
            rc = Aux.compareLines(list1, list2)
        return rc
    
    @staticmethod    
    def compareLines(list1, list2):
        rc = None
        lineNo = 0
        for line1 in list1:
            lineNo += 1
            if len(list2) < lineNo:
                rc = 'more lines in source1! Line {:d}: {:s}'.format(lineNo, line1)
                break 
            line2 = list2[lineNo-1]
            if line2 != line1:
                maxIx = min(len(line1), len(line2))
                diff = 0
                for ix in xrange(maxIx):
                    if line1[ix] != line2[ix]:
                        diff = ix
                        break
                reason = 'case different' if line2.lower() == line1.lower() else 'different' 
                diff2 = diff + 5 if maxIx <= diff + 5 else maxIx
                rc = ('line: {:d} col: {:d}: {:s} "{:s}..." / "{:s}...":\n{:s}\n{:s}'
                        .format(lineNo, diff, reason, 
                            line1[diff:diff2], line2[diff:diff2], line1, line2))
                break
        return rc

    @staticmethod    
    def buildPage(name = None, session = None):
        '''Builds a page and returns a page
        @param session: None or the session info
        @return: a page
        '''
        if name == None:
            name = 'Page'
        if session == None:
            session = Aux.getSession('testappl')
        page = Page(name, session)
        return page
        
    @staticmethod    
    def writeFile(name, content = None):
        '''Writes a string into a file.
        @param name        the filename
        @param content    the file's content. If None the file will be empty
        '''
        with open(name, "w") as fp:
            if content != None:
                fp.write(content)
        fp.close

    @staticmethod    
    def isRunningProgram(name):
        '''Checks whether a given program is running.
        @param name: the name of the program to test
        @return: True: the program is running.
                 False: otherwise
        '''
        rc = False
        dirs = os.listdir("/proc")
        rexprDir = re.compile(r'\d+$')
        rexprName = re.compile(r'Name:\s+(.*)')
        for node in dirs:
            stat = "/proc/" + node + "/status"
            if rexprDir.match(node) and os.path.exists(stat):
                with open(stat, "r") as fp:
                    line = fp.readline()
                    matcher = rexprName.match(line)
                    if matcher != None and matcher.group(1) == name:
                        rc = True
                        break
                fp.close
        return rc
                
                  
class DummyRequest:
    def __init__(self):
        self.META = { 
            "HTTP_HOST" : "testappl:8087",
            "HTTP_ACCEPT_LANGUAGE" : "de; any many",
            "SERVER_NAME" : "localhost",
            "SERVER_PORT" : "8000",
            "PATH_INFO" : "/home/dummy",
            "REMOTE_ADDR" : "127.0.0.1",
            "HTTP_USER_AGENT" : "testbrowser 1.0"
            }

    