'''
Created on 11.03.2013

@author: hm
'''
import unittest, os.path

from webbasic.page import Page, PageResult, PageException
from aux import Aux
from util.util import Util, say
from util.configurationbuilder import ConfigurationBuilder
from webbasic.globalbasepage import GlobalBasePage
import logging

logger = logging.getLogger("pywwetha")

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
        self.addField('disk', None, 0, "v")
        self.addField('id')
    
    def handleButton(self, button):
        pass
        
    def changeContent(self, body):
        body = body.replace('h1', 'h2')
        return body

class GlobalPage(GlobalBasePage):
    def __init__(self, session):
        GlobalBasePage.__init__(self, session, {})

    def defineFields(self):
        self.addField('global_disk')
        self.addField('.pages')
               
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
        self._page._globalPage = GlobalPage(self._session)
        self._session.addConfig(".gui.pages", ";home;edit;help")
        self._session.addConfig(".gui.button.next", "next_button")
        self._session.addConfig(".gui.button.prev", "prev")
        self._page.defineFields()
        logging.basicConfig(filename="/tmp/test.log", level=logging.INFO)
        
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
.dir.tasks=/tmp/tasks
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
        say('Expected: Missing template, defineFields() and handleButtons() for epage:')
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
        page._redirect = "Hi"
        self.assertEqual("Hi", page.handle('MyMenu', fields, cookies))
        page._redirect = None
        
       
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
                rc = (1, '<xml>adam')
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
        
        self.assertEquals([], self._page.autoSplit("", True))
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
        self.assertEquals("10239By", self._page.humanReadableSize(10*1024-1))
        self.assertEquals("10KiB", self._page.humanReadableSize(10*1024+1))
        self.assertEquals("10239KiB", self._page.humanReadableSize(10*1024*1024-1))
        self.assertEquals("10MiB", self._page.humanReadableSize(10*1024*1024+1))
        self.assertEquals("10239MiB", self._page.humanReadableSize(10*1024*1024*1024-1))
        self.assertEquals("10GiB", self._page.humanReadableSize(10*1024*1024*1024+1))
        self.assertEquals("-10GiB", self._page.humanReadableSize(-10*1024*1024*1024-1))

        self.assertEquals("4M", self._page.humanReadableSize(4*1024*1024, 1))
        self.assertEquals("4Mi", self._page.humanReadableSize(4*1024*1024, 2))
        self.assertEquals("4MiB", self._page.humanReadableSize(4*1024*1024, 3))

        self.assertEquals("4KiB", self._page.humanReadableSize(4*1024, 3))
        self.assertEquals("5MiB", self._page.humanReadableSize(5*1024*1024, 3))
        self.assertEquals("6GiB", self._page.humanReadableSize(6*1024*1024*1024, 3))
        self.assertEquals("10TiB", self._page.humanReadableSize(10*1024*1024*1024*1024, 3))

    def testSizeAndUnitToByte(self):
        page = self._page
        self.assertEqual(0, page.sizeAndUnitToByte("0"))
        self.assertEqual(567, page.sizeAndUnitToByte("567B"))
        self.assertEqual(567, page.sizeAndUnitToByte("567By"))
        self.assertEqual(567, page.sizeAndUnitToByte("567Byte"))
        
        self.assertEqual(24*1024, page.sizeAndUnitToByte("24k"))
        self.assertEqual(24*1024, page.sizeAndUnitToByte("24Ki"))
        self.assertEqual(24*1024, page.sizeAndUnitToByte("24kibyte"))
        self.assertEqual(24*1000, page.sizeAndUnitToByte("24kbyte"))
        
        self.assertEqual(123*1024*1024, page.sizeAndUnitToByte("123m"))
        self.assertEqual(123*1024*1024, page.sizeAndUnitToByte("123Mi"))
        self.assertEqual(123*1024*1024, page.sizeAndUnitToByte("123MiByte"))
        self.assertEqual(123*1000*1000, page.sizeAndUnitToByte("123MByte"))

        self.assertEqual(47*1024*1024*1024, page.sizeAndUnitToByte("47G"))
        self.assertEqual(47*1024*1024*1024, page.sizeAndUnitToByte("47gi"))
        self.assertEqual(47*1024*1024*1024, page.sizeAndUnitToByte("47gibyte"))
        self.assertEqual(47*1000*1000*1000, page.sizeAndUnitToByte("47gbyte"))
        
        self.assertEqual(29*1024*1024*1024*1024, page.sizeAndUnitToByte("29T"))
        self.assertEqual(29*1024*1024*1024*1024, page.sizeAndUnitToByte("29Ti"))
        self.assertEqual(29*1024*1024*1024*1024, page.sizeAndUnitToByte("29Tibyte"))
        self.assertEqual(29*1000*1000*1000*1000, page.sizeAndUnitToByte("29Tbyte"))
        
        self.assertEqual(-1, page.sizeAndUnitToByte("29x"))

       
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
    def putError(self):
        self.assertTrue(self._page.putError("i", "key"))
        
    def putErrorText(self):
        self.assertTrue(self._page.putErrorText("i", "text"))
   
    def testFindIndexOfOptions(self):
        self.assertEqual(-1, self._page.findIndexOfOptions("disk"))
        
    def testStoreAsGlobal(self):
        self._page.storeAsGlobal("disk", "disk")
        
    def testSetRefresh(self):
        self._page.setRefresh()
        self.assertEqual('<meta http-equiv="refresh" content="3" />', self._page._dynMeta)
        self._page.setRefresh(2)
        self.assertEqual('<meta http-equiv="refresh" content="2" />', self._page._dynMeta)
        
    def testGetButton(self):
        html = self._page.getButton("next")
        self.assertEqual("next_button", html)
    
    def testBuildNavigationButtons(self):
        html = self._page.buildNavigationButtons(self._page._name, '''
{{.gui.button.prev}}
{{.gui.button.next}}''')
        self.assertEqual("\n\n", html)
        
    def testBuildInfo(self):
        self._session.error("E1")
        self._session.error("e2")
        self._session.log("L1")
        self._session.log("L2")
        html = self._page.buildInfo("{{INFO}}")
        self.assertEqual('<p class="error">E1<br/>e2</p><p class="log">L1<br/>L2</p>', html)
    
    def testReplaceInPageFrame(self):
        html = '''
'''
        html = self._page.replaceInPageFrame(html)
        
    def testNeighbourOf(self):
        self.assertEquals("home", self._page.neighbourOf("edit", True))
        self.assertEquals("help", self._page.neighbourOf("edit", False))
        
    def testIsValidContent(self):
        self.assertFalse(self._page.isValidContent("f", "A-F", "A-Z", True, True))
        self._page.putField("id", "Hans_7")
        self.assertTrue(self._page.isValidContent("id", "A-Z_", "A-Za-z_0-9", True, True))
        self.assertTrue(self._page.isValidContent("id", "A-Z_", "A-Za-z_0-9", True, False))

        self._page.putField("id", None)
        self.assertTrue(self._page.isValidContent("id", "A-Z_", "A-Za-z_0-9", False, False))
        self.assertFalse(self._page.isValidContent("id", "A-Z_", "A-Za-z_0-9", True, False))
        
        self._page.putField("id", "_Hans7")
        self.assertFalse(self._page.isValidContent("id", "A-F0-9", "A-Z_0-9", True, True))
       
        self._page.putField("id", "H-7")
        self.assertFalse(self._page.isValidContent("id", "A-Z", "0-9", True, True))
       
    def testGetPages(self):
        self.assertEquals(";home;edit;help", self._page.getPages())
        
    def testAddPage(self):
        pages = self._page.getPages()
        self.assertEquals(";home;edit;help", pages)
        self._page.addPage("abc", "home")
        pages = self._page.getPages()
        self.assertEquals(";abc;home;edit;help", pages)
        self._page.addPage("end", None)
        pages = self._page.getPages()
        self.assertEquals(";abc;home;edit;help;end", pages)
        
 
    def testDelPage(self):
        pages = self._page.getPages()
        self.assertEquals(";home;edit;help", pages)
        self._page.delPage("edit")
        pages = self._page.getPages()
        self.assertEquals(";home;help", pages)
       
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()