'''
Created on 23.03.2013

@author: hm
'''
import unittest, os.path


from webbasic.menucheck import MenuChecker
from util.util import Util
from aux import Aux

class Test(unittest.TestCase):

    def setUp(self):
        self._appl = 'sidu-manual'
        self._fnDe = Util.getTempFile('menu_de.conf', self._appl, 'config')
        self._fnEn = Util.getTempFile('menu_en.conf', self._appl, 'config')
        self._dir = Util.getTempDir(self._appl, None, True)
    
    def buildDe(self):
        Util.writeFile(self._fnDe, '''* unvollstaendig
* home Die Startseite
** help Allgemeine Hilfe
** about Ueber uns
*** authors Authoren
*   onlygerman Nur in Deutsch
'''           )
        
    def buildEn(self):
        Util.writeFile(self._fnEn, '''* invalid
* home Die Startseite

** about About us
** help General Help
** authors Authors  
* content Content
'''           )
    def buildSession(self):
        self._session = Aux.getSession(self._appl)
        self._session._language = 'en'

    def testBase(self):
        self.buildDe()
        self.buildEn()
        self.buildSession()
        checker = MenuChecker(self._session, self._dir)
        msg = checker.checkMenu('de', '\n<p>\n{{message}}</p>')
        diff = Aux.compareText('''
<p>
/tmp/sidu-manual/config/menu_de.conf-1: Too few columns: * unvollstaendig</p>
<p>
/tmp/sidu-manual/config/menu_de.conf-3: the link help is moved in /tmp/sidu-manual/config/menu_en.conf to line 5</p>
<p>
/tmp/sidu-manual/config/menu_de.conf-4: the link about is moved in /tmp/sidu-manual/config/menu_en.conf to line 4</p>
<p>
/tmp/sidu-manual/config/menu_de.conf-5: Indention is different: *** / ** [authors]</p>
<p>
/tmp/sidu-manual/config/menu_de.conf-6: the link onlygerman is not available in /tmp/sidu-manual/config/menu_en.conf</p>'''         , msg)
        if diff != None:
            self.assertEqual(None, diff)
        
    def testMoreInEn(self):
        Util.writeFile(self._fnDe, '')
        self.buildEn()
        self.buildSession()
        checker = MenuChecker(self._session, self._dir)
        msg = checker.checkMenu('de', '\n<p>\n{{message}}\n</p>')
        diff = Aux.compareText('''
<p>
/tmp/sidu-manual/config/menu_de.conf has 6 fewer lines than /tmp/sidu-manual/config/menu_en.conf
</p>'''         , msg)
        self.assertEqual(None, diff)

    def testMoreInDe(self):
        Util.writeFile(self._fnEn, '')
        self.buildDe()
        self.buildSession()
        checker = MenuChecker(self._session, self._dir)
        msg = checker.checkMenu('de', '\n<p>\n{{message}}\n</p>')
        diff = Aux.compareText('''
<p>
/tmp/sidu-manual/config/menu_de.conf has 6 more lines than /tmp/sidu-manual/config/menu_en.conf
</p>'''         , msg)
        self.assertEqual(None, diff)
        
    def testMissingFileDe(self):
        Util.ensureMissing(self._fnDe)
        self.buildSession()
        checker = MenuChecker(self._session, self._dir)
        msg = checker.checkMenu('de', '\n<p>\n{{message}}\n</p>')
        diff = Aux.compareText('''
<p>
File does not exist: /tmp/sidu-manual/config/menu_de.conf
</p>'''         , msg)
        self.assertEqual(None, diff)

    def testMissingFileEn(self):
        Util.ensureMissing(self._fnEn)
        Util.writeFile(self._fnDe, '')
        self.buildSession()
        checker = MenuChecker(self._session, self._dir)
        msg = checker.checkMenu('de', '\n<p>\n{{message}}\n</p>')
        diff = Aux.compareText('''
<p>
File does not exist: /tmp/sidu-manual/config/menu_en.conf
</p>'''         , msg)
        self.assertEqual(None, diff)
    
    def testBuildTable(self):
        Util.writeFile(self._fnDe, '* main Startseite 1')
        Util.writeFile(self._fnEn, '* main Homepage 2')
        self.buildSession()
        checker = MenuChecker(self._session, self._dir)
        html = '\n' + checker.buildTable('de')
        diff = Aux.compareText('''
<table border="1">
<tr><td>main</td><td>Startseite 1</td><td>Homepage 2</td><td>main</td>
</tr></table>'''         , html)
        self.assertEqual(None, diff)
        
    def testTooFewCols(self):
        Util.writeFile(self._fnDe, '''* main Startseite
* correct Guter Link''')
        Util.writeFile(self._fnEn, '''* main Homepage
* tofew''')
        self.buildSession()
        checker = MenuChecker(self._session, self._dir)
        html = '\n' + checker.buildTable('de')
        diff = Aux.compareText('''
<table border="1">
<tr><td>main</td><td>Startseite</td><td>Homepage</td><td>main</td>
</tr></table>'''         , html)
        self.assertEqual(None, diff)
        
    def testBuildTableError(self):
        Util.ensureMissing(self._fnDe)
        Util.writeFile(self._fnEn, '')
        self.buildSession()
        checker = MenuChecker(self._session, self._dir)
        msg = '\n' + checker.buildTable('de')
        diff = Aux.compareText('''
<p>File does not exist: /tmp/sidu-manual/config/menu_de.conf</p>''', msg)
        self.assertEqual(None, diff)

        Util.writeFile(self._fnDe, '')
        Util.ensureMissing(self._fnEn)
        self.buildSession()
        checker = MenuChecker(self._session, self._dir)
        msg = '\n' + checker.buildTable('de')
        diff = Aux.compareText('''
<p>File does not exist: /tmp/sidu-manual/config/menu_en.conf</p>''', msg)
        self.assertEqual(None, diff)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testBase']
    unittest.main()