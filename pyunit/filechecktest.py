'''
Created on 24.03.2013

@author: hm
'''
import unittest

from webbasic.filecheck import FileChecker
from aux import Aux
from util.util import Util

class TestFileChecker(unittest.TestCase):


    def setUp(self):
        self._appl = 'filecheckappl'
        self._dir = Util.getTempDir(self._appl, True)
        self._dirDe = self._dir + 'de/'
        self._dirEn = self._dir + 'en/'
        self._session = Aux.getSession(self._appl, None, self._dir)


    def tearDown(self):
        pass


    def testBase(self):
        checker = FileChecker(self._session)
        Util.writeFile(Util.getTempFile('f1.txt', self._appl, 'de'), '1')
        Util.writeFile(Util.getTempFile('f4.txt', self._appl, 'de'), '4')
        Util.writeFile(Util.getTempFile('f5.txt', self._appl, 'de'), '5')

        Util.writeFile(Util.getTempFile('f1.txt', self._appl, 'en'), '1')
        Util.writeFile(Util.getTempFile('f2.txt', self._appl, 'en'), '2')
        Util.writeFile(Util.getTempFile('f3.txt', self._appl, 'en'), '3')
        Util.writeFile(Util.getTempFile('f4.txt', self._appl, 'en'), '4')
        Util.ensureMissing(Util.getTempFile('f6.txt', self._appl, 'en'))

        (missingDe, missingEn) = checker.compareDirs(self._dirDe, self._dirEn, 
                '.*[.]txt$')
        self.assertEquals(missingDe[0], 'f2.txt')
        self.assertEquals(missingDe[1], 'f3.txt')
        self.assertEquals(missingEn[0], 'f5.txt')

        Util.writeFile(Util.getTempFile('f6.txt', self._appl, 'en'), '6')
        (missingDe, missingEn) = checker.compareDirs(self._dirDe, self._dirEn, 
                '.*[.]txt$')
        self.assertEquals(missingDe[0], 'f2.txt')
        self.assertEquals(missingDe[1], 'f3.txt')
        self.assertEquals(missingDe[2], 'f6.txt')
        self.assertEquals(missingEn[0], 'f5.txt')

    def testEmpty(self):
        checker = FileChecker(self._session)
        Util.writeFile(Util.getTempFile('f1.txt', self._appl, 'd1'),'1')
        Util.writeFile(Util.getTempFile('f1.txt', self._appl, 'd2'),'1')
        (m1, m2)= checker.compareDirs(self._dir + 'd1', self._dir + 'd2',
            '.*[.]txt$')
        self.assertTrue(m1 == None)
        self.assertTrue(m2 == None)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()