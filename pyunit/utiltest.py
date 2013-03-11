# Project: https://github.com/republib/republib/wiki
# Licence: Public domain: http://www.wtfpl.net
import os, sys, time

from unittest import TestCase, main
from util.config import Config
from util.util import Util, exceptionString, say, sayError

class Test(TestCase):


    def setUp(self):
        self._temp = '/tmp/' if os.sep == '/' else 'c:\\temp\\'
        self._subdir = 'utiltest'
        pass
    
    def tearDown(self):
        pass
    
    def testMkDir(self):
        subdir = self._temp + "reutil.tst"
        Util.mkDir(subdir)
        self.assertEquals(True, os.path.exists(subdir))
        Util.mkDir(subdir)
        os.rmdir(subdir)
        self.assertEquals(False, os.path.exists(subdir))
        
    def testWriteFile(self):
        name = self._temp + "reutil.tst.txt"
        content = '''Line 1
line2'''

        Util.writeFile(name, content)
        self.assertEquals(content, Util.readFileAsString(name))
        os.unlink(name)
        
    def testConfig(self):
        conf1 = self._temp + "reutil1.conf"
        conf2 = self._temp + "reutil2.conf"
        Util.writeFile(conf1, '''
include "%s"
value.conf1=True
'''         % conf2)
        Util.writeFile(conf2, '''
value.conf2=4711
'''         )
        conf = Config(conf1)
        self.assertEquals(None, conf.get('NotExistingKey'))
        self.assertEquals('True', conf.get('value.conf1'))
        self.assertEquals('4711', conf.get('value.conf2'))
        os.unlink(conf1)
        os.unlink(conf2)
 
    def testConfigMissingInclude(self):
        conf1 = self._temp + "reutil1.conf"
        conf2 = self._temp + "reutil2.conf"
        Util.writeFile(conf1, '''
include "%s"
value.conf1=True
'''         % conf2)
        say('We expect a missing include file: ' + conf2)
        conf = Config(conf1)
        self.assertTrue(conf != None)
        os.unlink(conf1)
        
    def testExceptionString(self):
        name = Util.getTempDir(None, True) + 'reutiltest.exceptiontest.txt'
        try:
            open(name, "r")
            self.fail('impossible filename found: ' + name)
        except Exception:
            expected = "addInfoString"
            msg = exceptionString(sys.exc_info(), expected)
            self.assertEquals(True, msg != None)
            self.assertEquals(True, msg.endswith(expected))

    def testBasic(self):
        say('This should be exactly one line! ', False)
        say('We expect an error:')
        sayError('this is the expected ', False)
        sayError(' Error')
        

    def testGetTempDir(self):
        base = Util.getTempDir(None, True)
        name = Util.getTempDir('!test!')
        self.assertEquals(True, name.startswith(base))
        self.assertEqual(True, os.path.exists(name))
        os.rmdir(name)
     
    def testGetTempDir2(self):
        subdir = '/tmp/tmp1'
        if not os.path.exists(subdir):
            os.mkdir(subdir)
        os.environ['TEMP'] = subdir
        self.assertEquals(subdir, Util.getTempDir(None, False))
        del os.environ['TEMP']
        subdir = '/tmp/tmp2/'
        if not os.path.exists(subdir):
            os.mkdir(subdir)
        os.environ['TMP'] = subdir
        self.assertEquals(subdir, Util.getTempDir(None, True))
        del os.environ['TMP']

    def testGetTempFile(self):
        subdir = self._subdir
        base = Util.getTempDir(subdir, True)
        os.rmdir(base)
        name = Util.getTempFile('test', subdir)
        self.assertTrue(name.startswith(base))
        os.rmdir(base)
       
    def testDeleteIfOlder(self):
        fn = Util.getTempFile('delOlder.tst', self._subdir)
        Util.writeFile(fn, '')
        self.assertTrue(os.path.exists(fn))
        Util.deleteIfOlder(fn)
        self.assertTrue(os.path.exists(fn))
        time.sleep(1)
        Util.deleteIfOlder(fn, 1)
        self.assertFalse(os.path.exists(fn))
        
        
         
if __name__ == "__main__":
    import sys;sys.argv = ['', 'Test.testName']
    main()
    
