'''
Created on 04.03.2013

@author: hm
'''
import unittest, os.path

from aux import Aux
from webbasic.menu import MenuItem, Menu
from util.util import Util
from webbasic.htmlsnippets import HTMLSnippets

class Test(unittest.TestCase):


    def setUp(self):
        self._session = Aux.getSession()
        self._session._homeDir = Aux.buildDummyHome()
        self._menuName = 'tmenu'
        


    def tearDown(self):
        pass


    def buildSnippet(self):
        fn = self._session._homeDir + 'config/' + self._menuName + '.snippet.html'
        if not os.path.exists(fn):
            Util.writeFile(fn, '''
LEVEL_0:
 <ul>
 ###ENTRIES###
 </ul>
ENTRY_0:
<li{{class_current}}><a href="{{link}}">{{title}}</a>###SUBMENUS###</li>
LEVEL_1:
 <ul {{id}}>
###ENTRIES###
 </ul>
ENTRY_1:
  <li{{class_current}}><a href="{{link}}">{{title}}</a>
###SUBMENUS###
  </li>
LEVEL_2:
   <ul class="sub2-menu"{{id}}>
###ENTRIES###
   </ul>
ENTRY_2:
   <li{{class_current}}><a href="{{link}}">{{title}}</a></li>
CLASS_CURRENT:
 class="current-item"
ID:
 id="{{id}}"
'''             )
            
    def buildMenuDef(self):
        fn = self._session._homeDir + 'config/' + self._menuName + '_de.conf'
        if not os.path.exists(fn):
            Util.writeFile(fn, '''
*   main home Startseite
**  -    impressum  Impressum und Kontakt
*   help help Hilfe
**  -    help#about Ueber uns
**  -    help#authors Autoren
*   Bye  bye  Auf Wiedersehen   
'''             )   

    def testBasic(self):
        self._session._pageAndBookmark = 'home'
        self.buildSnippet()
        self.buildMenuDef()
        menu = Menu(self._session, self._menuName, True)
        menu.read()
        snippets = HTMLSnippets(self._session)
        snippets.read(self._menuName)
        html = menu.buildHtml(snippets) 
        diff = Aux.compareText(''' <ul>
 <li class="current-item"><a href="home">Startseite</a> <ul  id="main">
  <li><a href="impressum">Impressum und Kontakt</a>

  </li>

 </ul>
</li>
<li><a href="help">Hilfe</a> <ul  id="help">
  <li><a href="help#about">Ueber uns</a>

  </li>
  <li><a href="help#authors">Autoren</a>

  </li>

 </ul>
</li>
<li><a href="bye">Auf Wiedersehen</a></li>

 </ul>
''',
            html)
        if diff != None:
            self.fail(diff)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()