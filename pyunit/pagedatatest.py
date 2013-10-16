'''
Created on 11.03.2013

@author: hm
'''
import unittest, logging

from webbasic.pagedata import PageData, FieldData
from aux import Aux

logger = logging.getLogger("pywwetha")
class TestPage(unittest.TestCase):


    def setUp(self):
        self._session = Aux.getSession(homeDir = Aux.buildDummyHome())
        self._pageData = PageData(self._session)
        logging.basicConfig(filename="/tmp/test.log", level=logging.INFO)

    def tearDown(self):
        pass


    def testBasic(self):
        data = self._pageData
        self.assertTrue(None == data._cookieName)
        data.add(FieldData("f1"))
        data.add(FieldData("f2", "abc"))
        data.add(FieldData("i3", 4711, "d"))
        self.assertEquals(None, data.get("f1"))
        self.assertEquals("abc", data.get("f2"))
        self.assertEquals(4711, data.get("i3"))
        
        data.put("f2", "xxx")
        self.assertEquals("xxx", data.get("f2"))
        
        data.putError("i3", "error.format")
        self.assertEquals("\ferror.format", data._dict["i3"]._error)
        
    def testVField(self):
        data = self._pageData
        self.assertTrue(None == data._cookieName)
        data.add(FieldData("v1", "xxx", "v"))
        data.put("v1", "")
        self.assertEquals("xxx", data.get("v1"))
        
    def testPutErrorTextTest(self):
        data = self._pageData
        data.putErrorText(None, "zzz")
        self.assertEquals("zzz", data._generalErrors)
        
    def testClearFields(self):
        data = self._pageData
        self.assertTrue(None == data._cookieName)
        data.add(FieldData("f1"))
        data.add(FieldData("f2", "abc"))
        data.add(FieldData("i3", 4711, "d"))
        self.assertEquals(None, data.get("f1"))
        self.assertEquals("abc", data.get("f2"))
        self.assertEquals(4711, data.get("i3"))

        data.put("f1", "xxx")
        self.assertEquals("xxx", data.get("f1"))
        
        data.clearFields()
        self.assertEqual(None, data.get("f1"))
        self.assertEqual(None, data.get("f2"))
        
    def testBasicError(self):
        data = self._pageData
        self.assertEquals(None, data.get("unknown_field"))
        data.put("unknown_field", 4712)
        data.putError("unknown_field", "E99")
        
    def testFromHtml(self):
        data = self._pageData
        data.add(FieldData("x1"))
        data.add(FieldData("x2"))
        env = { "x1" : "xyz", "x2" : ""}
        data.getFromHTTP(env)
        self.assertEquals("xyz", data.get("x1"))
        self.assertEquals("", data.get("x2"))
      
    def testReplaceValues(self):
        data = PageData(self._session)
        data.add(FieldData("d1", "xxx"))
        data.putError("d1", "E1")
        data.add(FieldData("d2", 33, "d"))
        data.add(FieldData("d3"))
        self.assertTrue("xxx33 err: E1", 
            data.replaceValues(
                "{{val_d1}}{{val_d2}}{{val_d3}} err: {{err_d1}}{{err_d2}}",
                None, None))
        self.assertTrue("xxx33 err: !!!E1$$", 
            data.replaceValues(
                "{{val_d1}}{{val_d2}}{{val_d3}} err: {{err_d1}}{{err_d2}}",
                "!!!", "$$"))
     
    def testImportData(self):
        data = PageData(self._session)
        self._pageData.importData("test", {})
      
    def testGetDataVersion(self):
        data = PageData(self._session)
        self.assertEqual("", data.getDataVersion())
        data.add(FieldData("d1", "xxx"))
        data.add(FieldData("d2", 33, "d"))
        data.add(FieldData("d3"))
        self.assertEqual("sds", data.getDataVersion())

if __name__ == "__main__":
    #import sys;sys.argv = ["", "Test.testName"]
    unittest.main()