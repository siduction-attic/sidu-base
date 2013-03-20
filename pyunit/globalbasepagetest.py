'''
Created on 14.03.2013

@author: hm
'''
import unittest, time

from aux import Aux
from webbasic.globalbasepage import GlobalBasePage
from util.util import Util, say


class Test(unittest.TestCase):


    def setUp(self):
        self._session = Aux.getSession('testappl')
        cookies = {
            "V_global" : 'sss', 
            "D_global" : "~|^it~|^0"}
        self._page = TestGlobalPage(self._session, cookies)


    def tearDown(self):
        pass

    def testBasic(self):
        say('expected: not overwritten defineFields()')
        page = GlobalBasePage(self._session, {})
        self.assertTrue(None != page)

    def testSessionKey(self):
        key1 = self._page.getSessionKey()
        self.assertEqual(4+8, len(key1))
        time.sleep(1)
        key2 = self._page.getSessionKey()
        self.assertEqual(key1, key2)
    
    def testTempFile(self):
        fn = self._page.getTempFile('x_')
        self.assertTrue(fn.find('testappl') >= 0)    
        self.assertTrue(fn.find('x_') >= 0)    


class TestGlobalPage(GlobalBasePage):
    def __init__(self, session, cookies):
        GlobalBasePage.__init__(self, session, cookies)
    
    def defineFields(self):
        self.addField('init')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()