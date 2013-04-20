'''
Created on 20.04.2013

@author: hm
'''
import unittest, os.path, sys, shutil, time

from util.util import say, sayError, Util, exceptionString
from util.config import Config

class Test(unittest.TestCase):

    def setUp(self):
        self._temp = Util.getTempDir(None, None, True)
        self._subdir = 'utiltest'
        pass
    
    def tearDown(self):
        pass

    def testBase(self):
        say("Testing the module util.util:", False)
        say(" method say...")
        sayError("Test of the", False)
        sayError(" method sayError...")
        
    def testExceptionString(self):
        try:
            raise Exception("missing any")
        except Exception:
            self.assertEquals("missing any", exceptionString(sys.exc_info()))
        
        try:
            raise Exception("missing any file")
        except Exception:
            self.assertEquals("missing any file", exceptionString(None, "file"))

        try:
            raise Exception("missing any file")
        except Exception:
            self.assertEquals("missing any file: a.txt", 
                exceptionString(sys.exc_info(), "a.txt"))

    def testwriteFile(self):
        fn = Util.getTempFile('f.txt', 'utiltest')
        Util.ensureMissing(fn)
        Util.writeFile(fn)
        self.assertTrue(os.path.exists(fn))
        
    
    def testReadFileAsString(self):
        fn = Util.getTempFile('f2.txt', 'utiltest')
        Util.ensureMissing(fn)
        content = "abc\ndef"
        Util.writeFile(fn, content)
        self.assertEquals(content, Util.readFileAsString(fn))
        
        self.assertEquals(None, Util.readFileAsString(fn + '$!-'))
    
    def testReadFileAsList(self):
        fn = Util.getTempFile('f3.txt', 'utiltest')
        Util.ensureMissing(fn)
        content = "abc\ndef"
        Util.writeFile(fn, content)
        self.assertEquals(["abc\n", "def"], Util.readFileAsList(fn))
        self.assertEquals(["abc", "def"], Util.readFileAsList(fn, True))
    
    def testMkDir(self):
        subdir = Util.getTempFile('subdir', 'utiltest')
        Util.ensureMissing(subdir)
        Util.mkDir(subdir)
        self.assertTrue(os.path.isdir(subdir))
        os.rmdir(subdir)
        subdir += os.sep + 'subdir2'
        Util.mkDir(subdir)
        self.assertTrue(os.path.isdir(subdir))
        
    def testGetTempDir(self):
        base = Util.getTempDir('utiltest')
        self.assertTrue(base.endswith('utiltest'))
        if os.path.exists(base):
            shutil.rmtree(base, True)
        subdir = Util.getTempDir('utiltest', 'subdir3')
        self.assertTrue(subdir.endswith('subdir3'))
        self.assertTrue(subdir.find('utiltest') > 0)
        self.assertTrue(os.path.isdir(subdir))
        
        self.assertEquals(os.sep, Util.getTempDir('utiltest', True)[-1])
        
        
    def testGetTempFile(self):
        fn = Util.getTempFile('x2.txt', 'utiltest')
        Util.writeFile(fn, None)
        self.assertTrue(os.path.exists(fn))
    
    def testDeleteIfOlder(self):
        fn = Util.getTempFile('x2.txt', 'utiltest')
        Util.writeFile(fn, None)
        Util.deleteIfOlder(fn)
        self.assertTrue(os.path.exists(fn))
        Util.writeFile(fn, None)
        time.sleep(2)
        Util.deleteIfOlder(fn, 1)
        self.assertFalse(os.path.exists(fn))
    
    def testEnsureMissing(self):
        fn = Util.getTempFile('y1.txt', 'utiltest')
        Util.ensureMissing(fn)
        self.assertFalse(Util.ensureMissing(fn))
        self.assertFalse(os.path.exists(fn))
        Util.writeFile(fn)
        self.assertTrue(Util.ensureMissing(fn))

    def testMkDir2(self):
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
        
    def testExceptionString2(self):
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
        

    def testGetTempDir2(self):
        base = Util.getTempDir(None, True)
        name = Util.getTempDir('!test!')
        self.assertEquals(True, name.startswith(base))
        self.assertEqual(True, os.path.exists(name))
        os.rmdir(name)
     
    def testGetTempFile2(self):
        subdir = self._subdir
        base = Util.getTempDir(subdir, True)
        shutil.rmtree(base, True)
        name = Util.getTempFile('test', subdir)
        self.assertTrue(name.startswith(base))
        os.rmdir(base)
       
    def testDeleteIfOlder2(self):
        fn = Util.getTempFile('delOlder.tst', self._subdir)
        Util.writeFile(fn, '')
        self.assertTrue(os.path.exists(fn))
        Util.deleteIfOlder(fn)
        self.assertTrue(os.path.exists(fn))
        time.sleep(1)
        Util.deleteIfOlder(fn, 1)
        self.assertFalse(os.path.exists(fn))
        
    def testReadFileAsList2(self):
        fn = Util.getTempFile('file1.txt', self._subdir)
        Util.writeFile(fn, '''Line 1
This is line2
and line3'''         )
        lines = Util.readFileAsList(fn, True)
        self.assertEqual('Line 1', lines[0])
        self.assertEqual('This is line2', lines[1])
        self.assertEqual('and line3', lines[2])
        
        lines = Util.readFileAsList(fn, False)
        self.assertEqual('Line 1\n', lines[0])
        self.assertEqual('This is line2\n', lines[1])
        self.assertEqual('and line3', lines[2])

    def testEnsureMissing2(self):
        fn = Util.getTempFile('ensure_test.dat')
        Util.writeFile(fn, '')
        self.assertTrue(Util.ensureMissing(fn))
        self.assertFalse(Util.ensureMissing(fn))
        self.assertFalse(os.path.exists(fn))
       
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()