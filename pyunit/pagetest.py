'''
Created on 11.03.2013

@author: hm
'''
import unittest

from webbasic.page import Page, PageResult
from aux import Aux

class MiniPage(Page):
    def __init__(self, session):
        Page.__init__(self, 'mpage', session)
        
    def defineFields(self):
        self.addField('f1', 'xxx')
        self.addField('d2', 4711, 'd')
        self.addField('f3')
    
    def handleButton(self, button):
        pass
        
    def changeContent(self, body):
        body = body.replace('h1', 'h2')
        return body
        
class TestPage(unittest.TestCase):


    def setUp(self):
        home = Aux.buildDummyHome()
        self._session = Aux.getSession()
        self._session._homeDir = home
        Aux.buildPageFrame()
        self._template = Aux.buildPageTemplate('mpage')
        self._page = MiniPage(self._session)

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
        self.assertEqual('xxx', page._data.get('x4'))

    def testBasicError(self):
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
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()