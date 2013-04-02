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
        self._session = Aux.getSession(homeDir = Aux.buildDummyHome())
        self._menuName = 'tmenu'
        


    def tearDown(self):
        pass


    def buildSnippet(self):
        fn = self._session._homeDir + 'templates/' + self._menuName + '.snippets'
        if not os.path.exists(fn):
            Util.writeFile(fn, '''
LEVEL_0:
 <ul id="treeMenu">
###ENTRIES###
 </ul>

ENTRY_0:
 <li{{current_item}}><a href="{{link}}">{{title}}</a></li>

ENTRY_SUBMENU_0:
 <li{{current_item}}> <label for="{{menulabel}}" class="open"> </label>
     <input name="tree" {{checked}} id="{{menulabel}}" type="checkbox" />
###SUBMENUS###
 </li>

LEVEL_1:
  <ul>
###ENTRIES###
  </ul>

ENTRY_1:
    <li class="file"><a href="{{link}}">{{title}}</a></li>
    
ENTRY_SUBMENU_1:
 <li{{current_item}}> <label for="{{menulabel}}" class="open"> </label>
     <input name="tree" {{checked}} id="{{menulabel}}" type="checkbox" />
###SUBMENUS###
    </li>

LEVEL_2:
     <ul>
###ENTRIES###
     </ul>

ENTRY_2:
       <li{{current_item}}><a href="{{link}}">{{title}}</a></li>

CLASS_CURRENT:
 class="current_item"

ID:

MENU_LABEL:
M{{menuid}}
'''             )
            
    def buildMenuDef(self):
        fn = self._session._homeDir + 'config/' + self._menuName + '_de.conf'
        if not os.path.exists(fn):
            Util.writeFile(fn, '''
*    welcome    Willkommen
*   - siduction-Handbuch
**    welcome#welcome-gen    Grunds&auml;tzliches
**    credits#cred-team    Das siduction-Team
*   - Festplatte partitionieren
**  - Festplatte partitionieren
***    part-gparted    Partitionierung der Festplatte - traditionell, GPT und LVM
'''             )   

    def buildMenuDefError(self):
        fn = self._session._homeDir + 'config/menu_error_en.conf'
        if not os.path.exists(fn):
            Util.writeFile(fn, '''
* home Startseite
** home2 Home2
*** home3 Home3
**** home4 Home4
* home5 Home5
*** home6 Home6
'''             )   

    def testBasic(self):
        self._session._pageAndBookmark = 'home'
        self.buildSnippet()
        self.buildMenuDef()
        fields = { 'M2' : 'checked' }
        menu = Menu(self._session, self._menuName, True, fields)
        menu.read()
        snippets = HTMLSnippets(self._session)
        snippets.read(self._menuName)
        html = '\n' + menu.buildHtml(snippets)
        diff = Aux.compareText('''
 <ul id="treeMenu">
 <li><a href="welcome">Willkommen</a></li>
 <li> <label for="M2" class="open"> </label>
     <input name="tree" checked="checked" id="M2" type="checkbox" />
  <ul>
    <li class="file"><a href="welcome#welcome-gen">Grunds&auml;tzliches</a></li>
    
    <li class="file"><a href="credits#cred-team">Das</a></li>
    

  </ul>

 </li>
 <li> <label for="M3" class="open"> </label>
     <input name="tree"  id="M3" type="checkbox" />
  <ul>
 <li> <label for="M3_1" class="open"> </label>
     <input name="tree"  id="M3_1" type="checkbox" />
     <ul>
       <li><a href="part-gparted">Partitionierung</a></li>

     </ul>

    </li>

  </ul>

 </li>

 </ul>
''',
            html)
        if diff != None:
            self.fail(diff)
    
    def testFindLink(self):
        menu = Menu(self._session, self._menuName, True)
        menu.read()
        item = menu._topLevelItems[1]._subMenus[0]
        self.assertTrue(item == item.findLink('welcome#welcome-gen'))
     
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