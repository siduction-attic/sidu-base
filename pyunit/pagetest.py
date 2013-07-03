'''
Created on 11.03.2013

@author: hm
'''
import unittest, os.path

from webbasic.page import Page, PageResult, PageException
from aux import Aux
from util.util import Util, say
from util.configurationbuilder import ConfigurationBuilder

class MiniPage(Page):
    def __init__(self, session):
        Page.__init__(self, 'mpage', session)
        
    def defineFields(self):
        self.addField('f1', 'xxx')
        self.addField('d2', 4711, None, 'd')
        self.addField('f3')
        self.addField('s1')
        self.addField('s2')
        self.addField('c1', 'F', None, 'b')
        self.addField('color', 'green', None, 'b')
        self.addField('os', 'linux')
        self.addField('disk', '-')
    
    def handleButton(self, button):
        pass
        
    def changeContent(self, body):
        body = body.replace('h1', 'h2')
        return body
        
class TestPage(unittest.TestCase):
    _deleteConfig = True

    def setUp(self):
        self._application = 'testpageappl'
        home = Aux.buildDummyHome(self._application)
        self.buildConfig()
        self._session = Aux.getSession(self._application, None, home)
        Aux.buildPageFrame(self._application)
        self._template = Aux.buildPageTemplate(self._application, 'mpage')
        self._page = MiniPage(self._session)
        self._page.defineFields()

    def buildConfig(self):
        fnDb = Util.getTempFile('config.db', self._application, 'data')
        if TestPage._deleteConfig:
            TestPage._deleteConfig = False
            if os.path.exists(fnDb):
                os.unlink(fnDb)
        fnConfig = Util.getTempFile('config.conf', self._application)
        fnConfigDe = Util.getTempFile('config_de.conf', self._application)
        fnConfigEn = Util.getTempFile('config_en.conf', self._application)
        if not os.path.exists(fnDb) or os.path.getsize(fnDb) == 0:
            ConfigurationBuilder(None)
            Util.writeFile(fnConfig, '''
.home.dir=/home/ws/py/disk_help/website
mpage.vals_s1=,de,en,it
mpage.vals_color=;red;green;blue
mpage.opts_os=;windows;linux
mpage.empty=
'''             )
            Util.writeFile(fnConfigDe, '''
mpage.opts_s1=;Deutsch;Englisch;Italienisch
mpage.opts_s2=,Ja,Nein
mpage.opts_color=;rot;gr&uuml;n;blau
mpage.opts_color=;red;green;blue
'''             )
            Util.writeFile(fnConfigEn, '''
mpage.opts_s1=;German;English;Italian
mpage.opts_s2=Yes:No
'''             )
        filesAndLanguages = ((fnConfig, None),
            (fnConfigDe, 'de'), (fnConfigEn, 'en'))
        
        self._session = Aux.getSession(self._application, None, None, filesAndLanguages)
        
    def tearDown(self):
        pass


    def testPageResult(self):
        prc = PageResult('mini')
        self.assertEqual('mini', prc._body)
        
        prc = PageResult(None, 'home', 'foo')
        self.assertEqual('home', prc._url)
        self.assertEqual('foo', prc._caller)
        
    def testBasic(self):
        page = self._page
        page.addField('x4', 'xxx')
        self.assertEqual('xxx', page._pageData.get('x4'))

    def testBasicError(self):
        say('Missing template, defineFields() and handleButtons() for epage:')
        page = Page('epage', self._session)
        page.defineFields()
        page.handleButton(None)
        page.handle('', {}, {})

    def testBuildHtml(self):
        page = self._page
        body = page.buildHtml('MyMenu')
        self.assertTrue(body.find('h2') >= 0)
        
    def testErrorPage(self):
        page = self._page
        self.assertTrue(page.errorPage('missing_key').find('h1') > 0)
        
    def testButtonError(self):
        page = self._page
        self.assertEquals(None, page.buttonError('button_missed'))
        
    def testHandle(self):
        page = self._page
        page._globalPage = page
        fields = {'f1' : '4711', 'button_doit' : 'x'} 
        cookies = {}
        prc = page.handle('MyMenu', fields, cookies)
        self.assertTrue(prc != None)
        self.assertTrue(prc._body.find('MyMenu') > 0)
        self.assertTrue(prc._body.find('name="f1"') > 0)
        self.assertTrue(prc._body.find('4711') > 0)
        
       
    def testFindButton(self):
        page = self._page
        env = { 'f1' : "1", 'f2' : '2', 'button_first' : 'xxx', 'f4' : '4'}
        self.assertEquals('button_first', page.findButton(env))
        
    def testFillOpts(self):
        texts = ['abc', 'def']
        values = [ 'A', 'B']
        html = self._page.fillOpts('s1', texts, values, 1, '\n{{body_s1}}\n')
        diff = Aux.compareText(html, '''
<option value="A">abc</option>
<option selected="selected" value="B">def</option>
'''         )
        self.assertEquals(None, diff)

        self.buildConfig()
        texts = ['ABC', 'DEF']
        values = None
        html = self._page.fillOpts('s2', texts, None, 0, '\n{{body_s2}}')
        diff = Aux.compareText(html, '''
<option selected="selected">ABC</option>
<option>DEF</option>'''
            )
        self.assertEquals(None, diff)

    def testFillOpts2(self):
        texts = ['abc', 'def']
        values = [ 'A', 'B']
        html = self._page.fillOpts('s1', texts, values, "B", '\n{{body_s1}}\n')
        diff = Aux.compareText(html, '''
<option value="A">abc</option>
<option selected="selected" value="B">def</option>
'''         )
        self.assertEquals(None, diff)
        html = self._page.fillOpts('s1', texts, None, "def", '\n{{body_s1}}\n')
        diff = Aux.compareText(html, '''
<option>abc</option>
<option selected="selected">def</option>
'''         )
        self.assertEquals(None, diff)

        
    def testGetOptValues(self):
        self.buildConfig()
        (texts, values) = self._page.getOptValues('s1')
        self.assertEqual('Deutsch', texts[0])
        self.assertEqual('Englisch', texts[1])
        self.assertEqual('Italienisch', texts[2])
        self.assertEqual('de', values[0])
        self.assertEqual('en', values[1])
        self.assertEqual('it', values[2])

        (texts, values) = self._page.getOptValues('s2')
        self.assertEqual('Ja', texts[0])
        self.assertEqual('Nein', texts[1])
        self.assertEqual(None, values)
        
        (texts, values) = self._page.getOptValues("os")
        self.assertEqual(None, values)
        self.assertEqual(["windows", "linux"], texts)
 
    def testFillCheckBox(self):
        templ = '<input type="checkbox" {{chk_c1}} name="c1" value="T" />'
        self._page.putField('c1', 'F')
        body = self._page.fillCheckBox('c1', templ)
        self.assertEqual(
            '<input type="checkbox"  name="c1" value="T" />',
            body)   
        
        self._page.putField('c1', 'T')
        body = self._page.fillCheckBox('c1', templ)
        self.assertEqual(
            '<input type="checkbox" checked="checked" name="c1" value="T" />',
            body)   

    def buildErrorTable(self, info, what, ixRow = None):
        if not hasattr(self, '_errorTrace'):
            self._errorTrace = ''
        if what == info:
            self._errorTrace += " " + info
        if what == 'cols':
            if ixRow == 0:
                rc = (1, 'adam')
            else:
                rc = (2, 'bea')
        elif what == 'rows':
            rc = "a" if info == 'rows' else 1
        elif what == 'Table':
            rc = "{{rows}}" if info == 'Table' else "{{ROWS}}"
        elif what == 'Row':
            rc = "{cols}" if info == 'Row' else '{{COLS}}'
        elif what == 'Col':
            rc = "{col}" if info == 'Col' else '{{COL}} '
        else:
            rc = None
        return rc

    def buildPartOfTable(self, info, what, ixRow = None):
        if info.startswith('error_'):
            return self.buildErrorTable(info[6:], what, ixRow)
        if what == 'cols':
            if ixRow == 0:
                rc = (1, 'adam')
            else:
                rc = (2, 'bea')
        elif what == 'rows':
            rc = 1 if info == 'std' else 2
        elif what == 'Table':
            rc = None if info == 'std' else '''Table of result:
Id: Name:
{{ROWS}}'''
        elif what == 'Row':
            rc = None if info == 'std' else '{{COLS}}\n'
        elif what == 'Col':
            rc = None if info == 'std' else '{{COL}} '
        else:
            rc = None
        return rc
    
    def testBuildTable(self):
        self.assertMultiLineEqual('<table><tr><td>1</td><td>adam</td></tr></table>',
            self._page.buildTable(self, 'std'))
        self.assertEquals('''Table of result:
Id: Name:
1 adam 
2 bea 
''',        self._page.buildTable(self, 'Special'))
 
    def testBuildTableErrors(self):
        try:
            self._page.buildTable(self, 'error_rows')
            self.fail("missing PageException")
        except PageException as exc:
            self.assertEquals("mpage: wrong type for row count: a / <type 'str'>", 
                exc.message)
            
        try:
            self._page.buildTable(self, 'error_Table')
            self.fail("missing PageException")
        except PageException as exc:
            self.assertEquals("mpage: missing {{ROWS} in {{rows}}", exc.message)
            
        try:
            self._page.buildTable(self, 'error_Row')
            self.fail("missing PageException")
        except PageException as exc:
            self.assertEquals("mpage: missing {{COLS} in {cols}", exc.message)
            
        try:
            self._page.buildTable(self, 'error_Col')
            self.fail("missing PageException")
        except PageException as exc:
            self.assertEquals("mpage: missing {{COL} in {col}", exc.message)
                       
        self.assertEquals("1 adam ", self._page.buildTable(self, 'error_none'))

    def testFillStaticSelected(self):
        body = self._page.fillStaticSelected("color", "{{body_color}}")
        self.assertMultiLineEqual('''<option value="red">rot</option>
<option selected="selected" value="green">gr&amp</option>
<option value="blue">uuml</option>
<option>n</option>
<option>blau</option>''', body)
        
    def testFillDynamicSelection(self):
        disks = ["sda1", "sda2"]
        diskValues = ["/dev/sda1", "/dev/sda2"]
        body = self._page.fillDynamicSelected("disk", disks, diskValues, "{{body_disk}}")
        self.assertMultiLineEqual('''<option value="/dev/sda1">sda1</option>
<option value="/dev/sda2">sda2</option>''', body)
        body = self._page.fillDynamicSelected("disk", disks, None, "{{body_disk}}")
        self.assertMultiLineEqual('''<option>sda1</option>
<option>sda2</option>''', body)
        
    def testAutosplit(self):
        colors = self._page.autoSplit(";red;green;blue")
        self.assertEquals(["red", "green", "blue"], colors)
        try:
            self._page.autoSplit("")
            self.fail("no exception")
        except PageException as e:
            self.assertTrue(e.message.startswith("mpage"))
        try:
            self._page.autoSplit(None)
            self.fail("no exception")
        except PageException as e:
            self.assertTrue(e.message.find("autosplit") > 0)
        

    def testHumanReadableSize(self):
        self.assertEquals("0By", self._page.humanReadableSize(0))
        self.assertEquals("9999By", self._page.humanReadableSize(10*1000-1))
        self.assertEquals("10KB", self._page.humanReadableSize(10*1000))
        self.assertEquals("9999KB", self._page.humanReadableSize(10*1000*1000-1))
        self.assertEquals("10MB", self._page.humanReadableSize(10*1000*1000))
        self.assertEquals("9999MB", self._page.humanReadableSize(10*1000*1000*1000-1))
        self.assertEquals("10GB", self._page.humanReadableSize(10*1000*1000*1000))
       
    def testAutoJoinArgs(self):
        self.assertEquals(";1;2", self._page.autoJoinArgs(["1", "2"]))
        self.assertEquals("|;semi|colon", self._page.autoJoinArgs([";semi", "colon"]))
        self.assertEquals("^;+^|", self._page.autoJoinArgs([";+", "|"]))
        self.assertEquals("~;+~|+^", self._page.autoJoinArgs([";+", "|+^"]))

    def testAutoJoinArgsException(self):
        try:
            self._page.autoJoinArgs([";+", "|+^+~"])
            self.fail("no exception")
        except Exception as e:
            pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()