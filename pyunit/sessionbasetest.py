'''
Created on 02.03.2013

@author: hm
'''
import unittest, os.path

from util.util import Util
from aux import Aux  
from util.configurationbuilder import ConfigurationBuilder



class Test(unittest.TestCase):


    def setUp(self):
        fnDb = Util.getTempFile('config.db', 'testappl')
        if not os.path.exists(fnDb) or os.path.getsize(fnDb) == 0:
            config = ConfigurationBuilder(None)
            fnConfig = Util.getTempFile('config.conf', 'testappl')
            Util.writeFile(fnConfig, '''
.home.dir=/home/ws/py/disk_help/website
'''             )
            fnConfigDe = Util.getTempFile('config_de.conf', 'testappl')
            Util.writeFile(fnConfigDe, '''
home.title=Testanwendung
'''             )
            config.buildSqLiteDb(fnDb, ((fnConfig, None), (fnConfigDe, 'de')))
        self._request = Aux.getRequest()
        self._session = Aux.getSession('testappl', self._request)
            
    def tearDown(self):
        self._session._configDb.close()


    def testLanguage(self):
        self.assertEquals('de', self._session._language)
        
        request = Aux.getRequest()
        request.META['HTTP_ACCEPT_LANGUAGE'] = 'pt-BR,de; abc'
        session = Aux.getSession(None, request)
        self.assertEquals('pt-br', session._language)
        
        request.META['HTTP_ACCEPT_LANGUAGE'] = 'en'
        session = Aux.getSession(None, request)
        self.assertEquals('en', session._language)
        
    def testGetApplicationName(self):
        self.assertEquals('localhost',
            self._session.getApplicationName(self._request))
        request = Aux.getRequest()
        request.META["SERVER_NAME"] = "public.sidu-manual"
        self._session._configDb.close()
        session = Aux.getSession(None, request)
        self.assertEquals("public.sidu-manual",
            session.getApplicationName(request))
        session._configDb.close()
    
    def testGetConfig(self):
        self.assertEquals('/home/ws/py/disk_help/website',
            self._session.getConfigWithoutLanguage('.home.dir'))
        self.assertEquals('Testanwendung',
            self._session.getConfig('home.title', 'de'))
        self.assertEquals('Testanwendung',
            self._session.getConfig('home.title'))
        
    def testBasic(self):
        self._session.log('a test log message')
        self._session.error('a test error message')
        self._session.trace('a test trace message')
        
    def testPlaceholder(self):
        aDict = { "var" : "value" }
        self.assertEquals("value",
            self._session.valueOfPlaceholder('var', aDict))
        self.assertEquals("Testanwendung",
            self._session.valueOfPlaceholder('home.title', aDict))
        self.assertEquals("de",
            self._session.valueOfPlaceholder('language', aDict))
     
    def testReplaceVars(self):
        aDict = { "a" : 'A', 'b' : 'B' }
        
        self.assertEquals("abc",
            self._session.replaceVars('abc', aDict))
        self.assertEquals("AB",
            self._session.replaceVars('{{a}}{{b}}', aDict))
        self.assertEquals("xAbBc",
            self._session.replaceVars('x{{a}}b{{b}}c', aDict))
        self.assertEquals("x{{u}}{{b{{b}}cA",
            self._session.replaceVars('x{{u}}{{b{{b}}c{{a}}', aDict))
        self.assertEquals("x{{u}}{{b{{bca",
            self._session.replaceVars('x{{u}}{{b{{bca', aDict))
    
    def testBasic2(self):
        Aux.buildConfigDb()
        session = Aux.getSession('testappl', None, True)
        self.assertTrue(None == session.getMetaVar('MISSING_VAR'))

    def testAbsUrl(self):
        self.assertEquals('http://localhost:8000/home/help', 
            self._session.buildAbsUrl('home/help'))
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSessionBase']
    unittest.main()