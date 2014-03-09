'''
Created on 19.03.2014

@author: hm
'''
import unittest, os, tempfile

from executor import Executor

class Test(unittest.TestCase):

    def setUp(self):
        self._dir = tempfile.gettempdir()
        fnProgress = self._dir + os.sep + "progress.txt"
        self._executor = Executor(fnProgress, False)
    
    def readFile(self, fn):
        fp = open(fn, "r")
        rc = fp.readlines()
        fp.close()
        return rc
        
    def tearDown(self):
        pass
        
    def testGetVars(self):
        (x, y) = self._executor.getVars()
        self.assertTrue(type(x) == list)
        self.assertTrue(type(y) == list)
        
    def testExecute(self):
        self._executor.execute("/usr/bin/expr 2 + 1", True)
        (e, log) = self._executor.getVars()
        self.assertEquals(1, len(e))
        self.assertEquals(1, len(log))
        self.assertEquals("/usr/bin/expr 2 + 1", e[0])
        self.assertEquals("=== /usr/bin/expr 2 + 1\n", log[0])
 
    def testError(self):
        self._executor.error("test error")
        (e, log) = self._executor.getVars()
        self.assertEquals(0, len(e))
        self.assertEquals(1, len(log))
        self.assertEquals("===+++ test error\n", log[0])
        self.assertEquals(1, self._executor.getErrorCount())
       
    def testProgress(self):
        self._executor.progress("task1", False)
        lines = self.readFile(self._executor._fnProgress)
        self.assertEquals(["PERC=5\n", 
                           "CURRENT=<b>task1 ...</b>\n", 
                           "COMPLETE=completed 1 of 5\n"], lines)
      
    def coverTest(self, src):
        x = self._executor.cover(src)
        y = self._executor.uncover(x)
        self.assertEquals(src, y)  

    def testCover(self):
        self.coverTest("abc")
        self.coverTest(" 1234567890abcdefghijklmnopqrstuvewyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()