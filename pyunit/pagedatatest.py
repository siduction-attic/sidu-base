'''
Created on 11.03.2013

@author: hm
'''
import unittest

from webbasic.pagedata import PageData, FieldData
from aux import Aux

class TestPage(unittest.TestCase):


    def setUp(self):
        self._session = Aux.getSession()
        self._data = PageData(self._session)


    def tearDown(self):
        pass


    def testBasic(self):
        data = self._data
        self.assertTrue(None == data._cookieName)
        data.add(FieldData('f1'))
        data.add(FieldData('f2', 'abc'))
        data.add(FieldData('i3', 4711, 'd'))
        self.assertEquals(None, data.get('f1'))
        self.assertEquals('abc', data.get('f2'))
        self.assertEquals(4711, data.get('i3'))
        
        data.put('f2', 'xxx')
        self.assertEquals('xxx', data.get('f2'))
        
        data.putError('i3', 'error.format')
        self.assertEquals('error.format', data._data['i3']._errorKey)
        
    def testBasicError(self):
        data = self._data
        self.assertEquals(None, data.get('unknown_field'))
        data.put('unknown_field', 4712)
        data.putError('unknown_field', 'E99')
        
    def testFromHtml(self):
        data = self._data
        data.add(FieldData('x1'))
        data.add(FieldData('x2'))
        env = { 'x1' : 'xyz', 'x2' : ''}
        data.getFromHTTP(env)
        self.assertEquals('xyz', data.get('x1'))
        self.assertEquals('', data.get('x2'))

    def testCookie(self):
        data = self._data
        data.add(FieldData('d1'))
        data.add(FieldData('d2', 33, 'd'))
        data.getFromCookie('tpage', {})
        data.put('d1', 'data1')
        data.put('d2', 44)
        data.putToCookie()
        self.assertEqual('data1~|^44', PageData._cookie['D_tpage'])
        
        PageData._cookie['D_page2'] = '4711~|^99'
        PageData._cookie['V_page2'] =  PageData._cookie['V_tpage']
        data2 = PageData(self._session)
        data2.add(FieldData('w1'))
        data2.add(FieldData('w2', None, 'd'))
        data2.getFromCookie('page2', None)
        self.assertEquals('4711', data2.get('w1'))
        self.assertEquals(99, data2.get('w2'))
       
    def testReplaceValues(self):
        data = PageData(self._session)
        data.add(FieldData('d1', 'xxx'))
        data.putError('d1', 'E1')
        data.add(FieldData('d2', 33, 'd'))
        data.add(FieldData('d3'))
        self.assertTrue('xxx33 err: E1', 
            data.replaceValues(
                '{{val_d1}}{{val_d2}}{{val_d3}} err: {{err_d1}}{{err_d2}}'))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()