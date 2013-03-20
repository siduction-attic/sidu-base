'''
Created on 02.03.2013

@author: hm
'''
import unittest, os.path

from util.util import Util
from aux import Aux  
from util.configurationbuilder import ConfigurationBuilder
from webbasic.sessionbase import SessionBase

class TestSessionBase(unittest.TestCase):
    _deleteConfig = True

    def setUp(self):
        fnDb = Util.getTempFile('config.db', 'testappl')
        if TestSessionBase._deleteConfig:
            if os.path.exists(fnDb):
                os.unlink(fnDb)
            TestSessionBase._deleteConfig = False
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
            fnConfigEn = Util.getTempFile('config_en.conf', 'testappl')
            Util.writeFile(fnConfigEn, '''
home.title=Test application
home.en_only=only English
'''             )
            config.buildSqLiteDb(fnDb, ((fnConfig, None), 
                (fnConfigDe, 'de'), (fnConfigEn, 'en')))
        self._request = Aux.getRequest()
        self._session = Aux.getSession('testappl', self._request, '/tmp/testappl')
            
    def tearDown(self):
        if self._session._configDb != None:
            self._session._configDb.close()

    def test01IsHomeDir(self):
        self.assertEqual(None, SessionBase.isHomeDir('/dummyDir'))
        fn = Util.getTempFile('config.db', 'sessionbasetest')
        if not os.path.exists(fn):
            Util.writeFile(fn, '')
        self.assertEqual('/tmp/sessionbasetest/', 
            SessionBase.isHomeDir('/tmp/sessionbasetest'))   
    
    def test05FindHomeDir(self):
        application = 'testappl'
        fn = Util.getTempFile('config.db', application)
        if not os.path.exists(fn):
            Util.writeFile(fn, '')
        self.assertEquals('/usr/share/sidu-manual/',
            SessionBase.findHomeDir('sidu-manual', None))
        self.assertEquals('/tmp/testappl/',
            SessionBase.findHomeDir(application, None))
        request = Aux.getRequest()
        request.META['SCRIPT_PATH'] = '/tmp/testappl/dummy1/dummy2.txt'
        self.assertEquals('/tmp/testappl/',
            SessionBase.findHomeDir('xxx', request))
            
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
        if session._configDb != None:
            session._configDb.close()
    
    def testGetConfig(self):
        self.assertEquals('Testanwendung',
            self._session.getConfig('home.title'))
        self.assertEquals('Testanwendung',
            self._session.getConfig('home.title'))
        self.assertEquals('only English',
            self._session.getConfig('home.en_only'))
        self.assertEquals('not_existing', 
            self._session.getConfig('not_existing'))

        self.assertEquals(None, 
            self._session.getConfigOrNone('not_existing'))
        self.assertEquals('Testanwendung',
            self._session.getConfigOrNone('home.title'))
        self.assertEquals('only English',
            self._session.getConfigOrNone('home.en_only'))
       
    def testGetConfigWithoutLanguage(self):
        self.assertEquals('/home/ws/py/disk_help/website',
            self._session.getConfigWithoutLanguage('.home.dir'))
        self.assertEquals('/home/ws/py/disk_help/website',
            self._session.getConfigOrNoneWithoutLanguage('.home.dir'))

        self.assertEquals('not_existing_key',
            self._session.getConfigWithoutLanguage('not_existing_key'))
        self.assertEquals(None,
            self._session.getConfigOrNoneWithoutLanguage('not_existing_key'))

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
            self._session.valueOfPlaceholder('!language', aDict))
     
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
        session = Aux.getSession('testappl', None)
        self.assertTrue(None == session.getMetaVar('MISSING_VAR'))

    def testAbsUrl(self):
        self.assertEquals('http://localhost:8000/home/help', 
            self._session.buildAbsUrl('home/help'))
    
    def testBuildLanguage(self):
        session = self._session
        session._supportedLanguages = ['de', 'en', 'pt-br']
        self.assertEquals('en', session.correctLanguage('en'))
        self.assertEquals('de', session.correctLanguage('de-de,de-AT'))
        self.assertEquals('pt-br', session.correctLanguage('pt-BR; ANY'))
        self.assertEquals('pt-br', session.correctLanguage('pt;pt-XX'))
        self.assertEquals('pt-br', session.correctLanguage('pt-pt;pt-XX'))
        self.assertEquals('pt-br', session.correctLanguage('pt'))
        self.assertEquals('en', session.correctLanguage('ru'))
        self.assertEquals('en', session.correctLanguage(None))
              
    def testRedirect(self):
        rc = self._session.redirect('xyz', 'ThatsMe')
        self.assertEqual('ThatsMe', rc._caller)
        self.assertEqual('xyz', rc._url)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSessionBase']
    unittest.main()