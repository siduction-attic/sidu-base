'''
Created on 22.03.2013

@author: hm
'''

import os.path, logging, re
from util.util import Util
logger = logging.getLogger(__name__)

class FileChecker:
    '''
    Checks whether 2 directories have the same files.
    '''


    def __init__(self, session):
        '''
        Constructor.
        '''
        self._session = session
    
    def normFilename(self, name, dir1NotDir2):
        return name
       
    def buildList(self, base, rexpr):
        '''Returns a list of filenames of a directory matching a pattern.
        @param base: the directory
        @param rexpr: a compiled regular expression
        @return: a sorted list of filenames (without path)
        '''
        rc = []
        if os.path.exists(base) and os.path.isdir(base):
            files = os.listdir(base)
            for item in files:
                if rexpr.match(item):
                    rc.append(item)
        rc = sorted(rc)
        return rc   
    
    def compareDirs(self, dir1, dir2, pattern):
        '''Compares the menu of the given language with the English menu.
        @param dir1: first directory to inspect
        @param dir2: second directory to inspect
        @param pattern: a regular expression for the files to compare
        @return: tuple (mising1, missing2) missingX is None or a list not in dirX
        '''
        rexpr = re.compile(pattern)
        list1 = self.buildList(dir1, rexpr)
        list2 = self.buildList(dir2, rexpr)
        
        missing1 = []
        missing2 = []
        while len(list1) > 0 and len(list2) > 0:
            if self.normFilename(list1[0], True) == self.normFilename(list2[0], False):
                del list1[0]
                del list2[0]
                continue
            if self.normFilename(list1[0], True) < self.normFilename(list2[0], False):
                missing2.append(list1[0])
                del list1[0]
                continue
            if self.normFilename(list2[0], False) < self.normFilename(list1[0], True):
                missing1.append(list2[0])
                del list2[0]
        if len(list1) > 0:
            missing2.extend(list1)
        elif len(list2) > 0:
            missing1.extend(list2)
        if len(missing1) == 0:
            missing1 = None
        if len(missing2) == 0:
            missing2 = None
        return (missing1, missing2)
                    
        