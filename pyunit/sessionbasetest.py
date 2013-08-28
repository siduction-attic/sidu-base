# coding=utf-8
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
        fnDb = Util.getTempFile('config.db', 'testappl', 'data')
        if TestSessionBase._deleteConfig:
            if os.path.exists(fnDb):
                os.unlink(fnDb)
            TestSessionBase._deleteConfig = False
        if not os.path.exists(fnDb) or os.path.getsize(fnDb) == 0:
            config = ConfigurationBuilder(None)
            fnConfig = Util.getTempFile('config.conf', 'testappl')
            Util.writeFile(fnConfig, '''
.home.dir=/home/ws/py/disk_help/website
.tempdir=/var/cache/sidu-base
.dir2=${.tempdir}/any
.exec=ls ${.tempdir}
.
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
        self._session = Aux.getSession('testappl', self._request)
            
    def tearDown(self):
        if self._session._configDb != None:
            self._session._configDb.close()

    def test01IsHomeDir(self):
        self.assertEqual(None, SessionBase.isHomeDir('/dummyDir'))
        fn = Util.getTempFile('config.db', 'sessionbasetest', 'data')
        if not os.path.exists(fn):
            Util.writeFile(fn, '')
        self.assertEqual('/tmp/sessionbasetest/', 
            SessionBase.isHomeDir('/tmp/sessionbasetest'))
        self.assertEqual('/tmp/sessionbasetest/', 
            SessionBase.isHomeDir('/tmp/sessionbasetest/'))
           
    
    def test05FindHomeDir(self):
        application = 'testappl'
        fn = Util.getTempFile('config.db', application, 'data')
        if not os.path.exists(fn):
            Util.writeFile(fn, '')
        #self.assertEquals('/usr/share/sidu-manual/',
        #    SessionBase.findHomeDir('sidu-manual', None))
        self.assertEquals('/tmp/testappl/',
            SessionBase.findHomeDir(application, None))
        request = Aux.getRequest()
        request.META['SCRIPT_PATH'] = '/tmp/testappl/dummy1/dummy2.txt'
        self.assertEquals('/tmp/testappl/',
            SessionBase.findHomeDir('xxx', request))
        del request.META['SCRIPT_PATH']
        request.META['SCRIPT_FILENAME'] = '/tmp/testappl/dummy1/dummy2.txt'
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
        session = SessionBase(self._request, ['en'], None, '/tmp/test')   
        self.assertTrue(None != session)
        session._configDb = None
        session.error('unknown.key')

        
    def testPlaceholder(self):
        aDict = { "var" : "value" }
        self.assertEquals("value",
            self._session.valueOfPlaceholder('var', aDict))
        self.assertEquals("Testanwendung",
            self._session.valueOfPlaceholder('home.title', aDict))
        self.assertEquals("de",
            self._session.valueOfPlaceholder('!language', aDict))
        self._session.addConfig(".intro_menu2", "Intro")
        self.assertEquals("Intro",
            self._session.valueOfPlaceholder('.intro_menu', aDict))

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
        
    def testConfigReplacement(self):
        session = self._session
        self.assertEqual("/var/cache/sidu-base", 
            session.getConfigOrNoneWithoutLanguage('.tempdir'))
        self.assertEqual("/var/cache/sidu-base/any", 
            session.getConfigOrNoneWithoutLanguage('.dir2'))
        self.assertEqual("ls /var/cache/sidu-base", 
            session.getConfigOrNoneWithoutLanguage('.exec'))
    
    def testAdditionConfig(self):
        session = self._session
        session.addConfig('TestVar', '123')
        self.assertEqual("123", 
            session.getConfigOrNoneWithoutLanguage('TestVar'))
        self.assertEqual("123", 
            session.getConfigOrNone('TestVar'))
        
    def testDeleteFile(self):
        fn = Util.getTempFile('test01.dat', 'testappl', "sessionbase")
        if os.path.exists(fn):
            os.unlink(fn)
        self.assertFalse(os.path.exists(fn))
        self._session.deleteFile(fn)
        Util.writeFile(fn, "x")
        self.assertTrue(os.path.exists(fn))
        self._session.deleteFile(fn)
        self.assertFalse(os.path.exists(fn))
        
    def testNextPowerOf2(self):
        session = self._session
        self.assertEqual(0, session.nextPowerOf2(-11))
        self.assertEqual(0, session.nextPowerOf2(0))
        self.assertEqual(1, session.nextPowerOf2(1))
        self.assertEqual(4, session.nextPowerOf2(4))
        self.assertEqual(4, session.nextPowerOf2(5))
        self.assertEqual(4, session.nextPowerOf2(7))
        self.assertEqual(8, session.nextPowerOf2(8))
        self.assertEqual(0x100000, session.nextPowerOf2(0x1abcde))
     
    def testReadFile(self):
        fn = Util.getTempFile('test01.dat', 'testappl', "sessionbase")
        Util.writeFile(fn, "xxxx")
        self.assertEqual("xxxx", self._session.readFile(fn))
        content = '''Line1
line2
'''
        Util.writeFile(fn, content)
        self.assertEqual(content, self._session.readFile(fn))
        
    def testUnicodeToAscii(self):
        self.assertEquals("%e4%f6%fc%c4%d6%dc%df", self._session.unicodeToAscii(u"äöüÄÖÜß"))
        self.assertEquals("abc", self._session.unicodeToAscii(u"abc"))
        self.assertEquals("abc", self._session.unicodeToAscii("abc"))
        self.assertEquals(None, self._session.unicodeToAscii(None))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSessionBase']
    unittest.main()