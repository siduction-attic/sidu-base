"""
This module contains the tests for the package webbasic. These will pass
when you run "manage.py test".
"""

#from django.test import TestCase
from unittest import TestCase
import unittest, os.path

from aux import Aux  

from sessionbase import SessionBase
class HttpRequest:
    def __init__(self):
        self.META = Aux.getMetaData(None)
        
class WebbasicTest(TestCase):
    def init(self):
        if '_testAppl' not in self.__dict__:
            self._testAppl = 'test-app'
            self._applPath = '/tmp/' + self._testAppl
            self._dbName =  self._applPath + '/config.db'
            if not os.path.exists(self._dbName):
                fnText = self._applPath + '/config.txt'
                if not os.path.exists(self._applPath):
                    os.mkdir(self._applPath)
                fp = open(fnText, "w")
                fp.write('''
.home.dir=/tmp/%s
''' 
                    % (self._testAppl))
                importer = Import(self._dbName)
                importer.read(fnText)
                importer._db.close() 
        
        
        
    def test0SessionBase(self):
        self.init()
        request = HttpRequest()
        session = SessionBase(request, self._testAppl)
        self.assertEquals('de', session._language)
        self.assertEquals(self._testAppl, session._application)
     
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()        
