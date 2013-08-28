'''
Created on 26.05.2013

@author: hm
'''
import unittest
from webbasic.waitpage import WaitPage
from aux import Aux
from util.util import Util
from webbasic.globalbasepage import GlobalBasePage

class Test(unittest.TestCase):

    def getConfigFilename(self, lang):
        if lang == None:
            fn = Util.getTempFile("wait.conf", "testappl")
        else:
            fn = Util.getTempFile(
                "wait_" + lang + ".conf", "testappl")
        return fn


    def setUp(self):
        self._appl = "wait"
        request = None
        homeDir = None
        fnConfig = Util.getTempFile("wait.conf", self._appl)
        fnConfigEn = Util.getTempFile("wait_en.conf", self._appl)
        Util.writeFile(fnConfig, '''
''')
        Util.writeFile(fnConfigEn, '''
wait.intro=Shows the sample wait page {{1}} {{2}}
wait.descr=Sample wait page {{1}}
''')
        filesAndLanguages = ((fnConfig, None), (fnConfigEn, "en"))
        self._session = Aux.getSession(self._appl, request, homeDir, filesAndLanguages)
        self._page = WaitPage(self._session)
        self._page._globalPage = TestGlobalPage(self._session)
        self._page._globalPage.putField("wait.intro.key", "wait.intro")
        self._page._globalPage.putField("wait.descr.key", "wait.descr")
        self._page._globalPage.putField("wait.intro.args", ";X1;Y2")
        self._page._globalPage.putField("wait.descr.args", ";z1")
        self._page._globalPage.putField("wait.page", "home")

        self._fileProgress = "/tmp/progress_test.dat"
        Aux.writeFile(self._fileProgress, '''PERC=30
CURRENT=<b>Partition created</b>
COMPLETE=completed 3 of 20
'''         )

    def tearDown(self):
        pass


    def testBasic(self):
        self.assertFalse(self._page == None)
        
    def testChangeContent(self):
        body = "i: {{intro}}\nd: {{txt_description}}"
        body = self._page.changeContent(body)
        self.assertEqual('''i: Shows the sample wait page X1 Y2
d: Sample wait page z1''', body)
        
    def testHandleButton(self):
        result = self._page.handleButton("button_cancel")
        self.assertFalse(result == None)
        self.assertEqual("home", result._url)

        result = self._page.handleButton("button_missing")
        self.assertTrue(result == None)

    def testGotoWait(self):
        result = self._page.gotoWait("home", "fnStop", "fnProgress", "intro", 
            ["i1"], "descr", ["d1"])
        self.assertFalse(result == None)
        self.assertEquals("home", self._page._globalPage.getField("wait.page"))
        self.assertEquals("fnStop", self._page._globalPage.getField("wait.file.stop"))
        self.assertEquals("fnProgress", self._page._globalPage.getField("wait.file.progress"))
        self.assertEquals("intro", self._page._globalPage.getField("wait.intro.key"))
        self.assertEquals(";i1", self._page._globalPage.getField("wait.intro.args"))
        self.assertEquals("descr", self._page._globalPage.getField("wait.descr.key"))
        self.assertEquals(";d1", self._page._globalPage.getField("wait.descr.args"))
        
    def testReadProgress(self):
        progress = self._page.readProgress(self._fileProgress)
        self.assertEquals(progress[0], 30)
        self.assertEquals(progress[1], "<b>Partition created</b>")
        self.assertEquals(progress[2], 3)
        self.assertEquals(progress[3], 20)

    def testReadProgress2(self):
        Aux.writeFile(self._fileProgress, '''PERCx=30
CURRENTy=<b>Partition created</b>
COMPLETEz=completed 3 of 20
'''         )
        progress = self._page.readProgress(self._fileProgress)
        self.assertEquals(progress[0], 0)
        self.assertEquals(progress[1], "?")
        self.assertEquals(progress[2], 0)
        self.assertEquals(progress[3], 0)
        self.assertEquals(2, len(self._session._errorMessages))
        self.assertEquals("invalid progress file: /tmp/progress_test.dat taskname percentage taskno",
            self._session._errorMessages[1])

    def testReadProgressFactor(self):
        Aux.writeFile(self._fileProgress, '''PERC=0.97
CURRENT=<b>Partition created</b>
COMPLETE=completed 3 of 20'''         )
        progress = self._page.readProgress(self._fileProgress)
        self.assertEquals(progress[0], 97)
        self.assertEquals(progress[1], "<b>Partition created</b>")
        self.assertEquals(progress[2], 3)
        self.assertEquals(progress[3], 20)

    def testProgressPage(self):
        self._page._snippets = {}
        self._page._snippets["PROGRESS"] = "progress: {{percentage}}% {{task}} ({{no}} of {{count}})"
        self._page._snippets["DESCRIPTION"] = ""
        body = "{{PROGRESS}}"
        self._page.gotoWait(None, None, self._fileProgress, None, None, None, None) 
        body = self._page.changeContent(body)
        self.assertEquals("progress: 30% <b>Partition created</b> (3 of 20)",
            body)
        
    def testDefineField(self): 
        self._page.defineFields()
        
        
class TestGlobalPage (GlobalBasePage):
    def __init__(self, session):
        cookies = {}
        cookies['V_global'] = ";args~|^key"
        cookies['D_global'] = "s~|^s"
        GlobalBasePage.__init__(self, session, cookies)
    
    def defineFields(self):
        """Must be overwritten!
        """
        WaitPage.defineGlobalFields(self)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()