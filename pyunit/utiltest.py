# -*- coding: utf-8 -*-
'''
Created on 20.04.2013

@author: hm
'''
import unittest, os.path, sys, shutil, time, random

from util.util import say, sayError, Util, exceptionString, ALGO_ADD,\
    ALGO_REVERS, ALGO_XOR, ALGO_DEFAULT, TAG_CHARS64, CHARS64, \
    CHARS95, TAG_CHARS95, TAG_CHARS10
from util.util import FILENAMECHARS, INVERS_FILENAMECHARS
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
        
    def testEncodeFilenameChar(self):
        fn = Util.encodeFilenameChar(0x12345678)
        self.assertEqual("PjsD%", fn)
        fn = Util.encodeFilenameChar(0x82345678)
        self.assertEqual("WOqQZ", fn)
        fn = Util.encodeFilenameChar(-33)
        self.assertEqual("R", fn)
        
    def testDecodeFilenameChar(self):
        val = 7
        r = 0x12345678
        for ii in xrange(29):
            val = val*2 + 7
            fn = Util.encodeFilenameChar(val)
            val2 = Util.decodeFilenameChar(fn)
            fn2 = Util.encodeFilenameChar(val2)
            self.assertEqual(val2, val)
            self.assertEqual(fn, fn2)
            
            r = r * 7 % 0x10000000
            fn = Util.encodeFilenameChar(r)
            val2 = Util.decodeFilenameChar(fn)
            fn2 = Util.encodeFilenameChar(val2)
            self.assertEqual(val2, r)
            self.assertEqual(fn, fn2)
            
        val1 = Util.decodeFilenameChar("1234567")
        val2 = Util.decodeFilenameChar("12/3\\45<6>7")
        self.assertEquals(val1, val2)
    
    def testData(self):
        # Each char unique?
        for ix in xrange(len(FILENAMECHARS) - 1):
            self.assertEqual(-1, FILENAMECHARS[ix+1:].find(FILENAMECHARS[ix]))

        # Each entry of FILENAMECHARS in INVERS_FILENAMECHARS:    
        for ix in xrange(len(FILENAMECHARS)):
            ii = ord(FILENAMECHARS[ix]) - 33
            self.assertEqual(INVERS_FILENAMECHARS[ii], ix)

        # Each entry of INVERS_FILENAMECHARS in FILENAMECHARS:
        for ix in xrange(len(INVERS_FILENAMECHARS)):
            ii = INVERS_FILENAMECHARS[ix]
            if ii >= 0:
                if FILENAMECHARS[ii] != chr(33+ix):
                    self.assertEquals(FILENAMECHARS[ii], chr(33+ix))

    def testBuildInvers(self):
        x = list(FILENAMECHARS)
        x.sort()
        chars = "".join(x)
        (chars, invers) = Util.buildInvers(chars, 33)
        self.assertTrue(chars != None)
        self.assertTrue(invers != None)
        
    def hide(self, algorithm):
        x = "!x"
        y = Util.hideText(x, algorithm)
        self.assertEqual(x, Util.unhideText(y))
        x = "a"
        y = Util.hideText(x, algorithm)
        self.assertEqual(x, Util.unhideText(y))
        x = "One thing has 2 sides!"
        y = Util.hideText(x, algorithm)
        self.assertEqual(x, Util.unhideText(y))
        x = ""
        for ii in xrange(ord(' '), 128):
            x += chr(ii)
        y = Util.hideText(x, algorithm)
        self.assertEqual(x, Util.unhideText(y))

        x = u"öäüÖÄÜß"
        y = Util.hideText(x, algorithm)
        #z = u'' + Util.unhideText(y)
        #self.assertEqual(x, z)
        
    def testHide(self):
        x = "!0A"
        y = Util.hideText(x, ALGO_DEFAULT)
        self.hide(ALGO_ADD)
        self.hide(ALGO_XOR)
        self.hide(ALGO_REVERS)

    def scramble(self, tag):
        charset = Util.getCharset(tag)
        aSet = list(charset)
        aSet.sort()
        x = "".join(aSet)
        y = Util.scrambleText(x, tag)
        self.assertEqual(Util.unscrambleText(y), x)

    def testScramble(self):
        x = "Ab0"
        y = Util.scrambleText(x, TAG_CHARS64)
        x = "All you n33d is s3cret! "
        y = Util.scrambleText(x, TAG_CHARS95)
        self.assertEqual(x, Util.unscrambleText(y))
        for tag in Util.nextTag():
            self.scramble(tag)
        x = "All you need is secret!"
        y = Util.scrambleText(x)
        self.assertEqual(x, Util.unscrambleText(y))

    def testScrambleException(self):
        with self.assertRaises(Exception):
            Util.scrambleText("!abc", TAG_CHARS10)
 
    def esc(self, text):
        rc = text.replace("\\", "\\\\")
        rc = rc.replace('"', '\\"')
        return rc
        
    def shuffle(self, chars):
        aSet = list(chars)
        random.shuffle(aSet)
        rc = "".join(aSet)
        rc = self.esc(rc)
        return rc
        
    def testShuffle(self):
        msg = ""
        lastSet = ""
        lastSize = 0
        msg2 = ""
        for tag in Util.nextTag():
            charset = Util.getCharset(tag)
            size = len(charset)
            msg += "CHARS{:d} = \"{:s}\"\n".format(size, self.shuffle(charset))
            newSet = ""
            for cc in charset:
                if lastSet.find(cc) < 0:
                    newSet += cc
            msg2 += "CHARS{:d} = \"{:s}\" + CHARS{:d}\n".format(size, 
                self.esc(newSet), 0 if len(newSet) == size else lastSize)   
            lastSize = size
            lastSet = charset
        pass
    
    def testGetCharsetException(self):
        with self.assertRaises(Exception):
            Util.getCharset("unknownTag")
        pass
        
    def testUniqueCharset(self):
        for tag in Util.nextTag():
            charset = Util.getCharset(tag)
            aSet = list(charset)
            aSet.sort()
            last = ""
            for cc in aSet:
                if cc == last:
                    self.assertFalse("doubles in " + charset)
                last = cc
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()