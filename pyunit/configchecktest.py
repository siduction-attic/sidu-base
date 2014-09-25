'''
Created on 23.03.2013

@author: hm
'''
import unittest, os.path


from webbasic.configchecker import ConfigChecker
from util.util import Util
from aux import Aux

class Test(unittest.TestCase):

    def setUp(self):
        self._appl = 'testconfigcheck'
        self._fnDe = Util.getTempFile('conf_de.conf', self._appl)
        self._fnEn = Util.getTempFile('conf_en.conf', self._appl)
    
    def buildDe(self):
        Util.writeFile(self._fnDe, '''
std.key.common=Gemeinsam
std.key.de.only.1=Nur in de
std.key.de.only.2=Nur in de2
'''           )
        
    def buildEn(self):
        Util.writeFile(self._fnEn, '''
std.key.common=Common
std.key.en.only.1=Only in en
std.key.en.only.2=Only in en2
'''             )
    def buildSession(self):
        fn = Util.getTempFile('config.db', self._appl, 'data')
        if os.path.exists(fn):
            os.unlink(fn)
        self._session = Aux.getSession(self._appl, None,
            Util.getTempDir(self._appl),
            ((self._fnDe, 'de'), (self._fnEn, 'en')))

    def testBase(self):
        self.buildDe()
        self.buildEn()
        self.buildSession()
        checker = ConfigChecker(self._session)
        msg = checker.checkConfig('de', '\n<p>\n{{message}}</p>', '<br>\n')
        diff = Aux.compareText('''
<p>
.error.config.keys.superflousstd.key.de.only.1<br>
std.key.de.only.2</p>
<p>
.error.config.keys.missingstd.key.en.only.1<br>
std.key.en.only.2</p>'''         , msg)
        self.assertEqual(None, diff)
        
    def testMoreInEn(self):
        Util.writeFile(self._fnDe, '')
        self.buildEn()
        self.buildSession()
        checker = ConfigChecker(self._session)
        msg = checker.checkConfig('de', '\n<p>\n{{message}}\n</p>', '<br>\n')
        diff = Aux.compareText('''
<p>
.error.config.keys.missingstd.key.common<br>
std.key.en.only.1<br>
std.key.en.only.2
</p>'''         , msg)
        self.assertEqual(None, diff)

    def testMoreInDe(self):
        Util.writeFile(self._fnEn, '')
        self.buildDe()
        self.buildSession()
        checker = ConfigChecker(self._session)
        msg = checker.checkConfig('de', '\n<p>\n{{message}}\n</p>', '<br>\n')
        diff = Aux.compareText('''
<p>
.error.config.keys.superflousstd.key.common<br>
std.key.de.only.1<br>
std.key.de.only.2
</p>'''         , msg)
        self.assertEqual(None, diff)
     
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testBase']
    unittest.main()