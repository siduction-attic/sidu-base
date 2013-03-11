'''
Created on 04.03.2013

@author: hm
'''
import unittest, os.path

from aux import Aux
from webbasic.menu import MenuItem, Menu
from util.util import Util, say
from webbasic.htmlsnippets import HTMLSnippets

class Test(unittest.TestCase):


    def setUp(self):
        self._session = Aux.getSession()
        self._session._homeDir = Aux.buildDummyHome()
        self._menuName = 'tmenu'
        


    def tearDown(self):
        pass


    def buildSnippet(self):
        fn = self._session._homeDir + 'templates/' + self._menuName + '.snippets'
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

    def buildMenuDefError(self):
        fn = self._session._homeDir + 'config/menu_error_en.conf'
        if not os.path.exists(fn):
            Util.writeFile(fn, '''
* - home Startseite
** - home2 Home2
*** - home3 Home3
**** - home4 Home4
* - home5 Home5
*** - home6 Home6

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
    
    def testFindLink(self):
        menu = Menu(self._session, self._menuName, True)
        menu.read()
        item = menu._topLevelItems[0]
        self.assertTrue(item == item.findLink('home'))
        item2 = item.findLink('impressum')        
        self.assertTrue(item2 != None and item2._link == 'impressum')
     
    def testReadError(self):
        self._session._pageAndBookmark = 'home'
        self.buildSnippet()
        self.buildMenuDef()
        menu = Menu(self._session, 'missing_menu', True)
        menu.read()
        self.assertEquals(0, len(menu._topLevelItems))
                 
    def testReadError2(self):
        self._session._pageAndBookmark = 'home'
        self.buildSnippet()
        self.buildMenuDefError()
        menu = Menu(self._session, 'menu_error', True)
        say('expected: level too large and gap detected:')
        menu.read()
        self.assertEquals(2, len(menu._topLevelItems))
                 
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()