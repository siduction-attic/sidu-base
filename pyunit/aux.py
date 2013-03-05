'''
Created on 04.03.2013

@author: hm
'''

import re

from webbasic.sessionbase import SessionBase
from util.util import Util

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
    def getRequest():
        rc = DummyRequest()
        return rc

    @staticmethod
    def getSession(application = None, request = None):
        request = Aux.getRequest() if request == None else request
        session = SessionBase(request, application, False)
        return session
    
    @staticmethod
    def buildDummyHome(application = None):
        if application == None:
            application = 'testappl'
        subdir = Util.getTempDir(application, True)
        Util.getTempDir('testappl/config', True)
        return subdir
        
    @staticmethod
    def compareText(source1, source2):
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
                rc = ('line: {:d} col: {:d}: {:s} "{:s}" / "{:s}":\n{:s}\n{:s}'
                        .format(lineNo, diff, reason, 
                            line1[diff:diff2], line2[diff:diff2], line1, line2))
                break
        return rc
             
        
class DummyRequest:
    def __init__(self):
        self.META = { 
            "HTTP_HOST" : "testappl:8087",
            "HTTP_ACCEPT_LANGUAGE" : "de; any many"
            }

    