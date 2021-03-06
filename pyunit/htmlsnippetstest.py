'''
Created on 04.03.2013

@author: hm
'''
import unittest, os.path

from webbasic.htmlsnippets import HTMLSnippets
from util.util import Util
from aux import Aux

class Test(unittest.TestCase):


    def setUp(self):
        self._snippetFilename = 'test'
        self._dir = Aux.buildDummyHome()
        fn = self._dir + 'templates/' + self._snippetFilename + '.snippets'
        if not os.path.exists(fn):
            Util.writeFile(fn, '''
PART_1:
<div id="part1">
<!--comment-->

PART-B:
</div>

'''             )


    def tearDown(self):
        pass


    def testBasic(self):
        session = Aux.getSession(homeDir=self._dir)
        snippets = HTMLSnippets(session)
        snippets.read(self._snippetFilename)
        self.assertEquals('<div id="part1">\n<!--comment-->\n',
            snippets.get('PART_1'))
        self.assertEquals('</div>\n', snippets.get('PART-B'))
        self.assertEquals('', snippets.get('NOT_EXISTING_PART'))
        
    def testReadError(self):
        session = Aux.getSession(homeDir=self._dir)
        snippets = HTMLSnippets(session)
        snippets.read('notExistingFile')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testBasic']
    unittest.main()