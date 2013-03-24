'''
Created on 03.03.2013

@author: hm
'''

import os.path, re, codecs
from webbasic.htmlsnippets import HTMLSnippets


class MenuItem:
    '''Manages a menu item.
    '''
    
    def __init__(self, level, id, title, link):
        '''Constructor.
        @param level: the indention level: 0..N
        @param id: the value of the 'id' tag
        @param title: the text displayed in the menu
        @param link: the URI of the menu item
        '''
        self._level = level;
        self._id = id;
        self._title = title;
        self._link = link;
        # None or array of MenuItems
        self._subMenus = None;
        self._parent = None;
        self._isActive = False;
        
    def addItem(self, item):
        '''Adds an item to the sub items.
        @param item: the item to add
        '''
        item._parent = self
        if self._subMenus == None:
            self._subMenus = []
        self._subMenus.append(item)
        
    def findLink(self, link):
        '''Search for a given link in the submenus.
        @param link: the link to search
        @return: None: not found.<br>
                otherwise: the menu item containing the link
        '''
        rc = None
        if self._link == link:
            rc = self
        else:
            for item in self._subMenus:
                rc = item.findLink(link)
                if rc != None:
                    break
        return rc

class Menu(object):
    '''
    Manages a menu.
    The format of the menu definition file:
    *    sm1    welcome    siduction-Handbuch
    **    sm1a    welcome#welcome-gen    siduction-Handbuch &#8658;
    ***    -    credits#cred-team    Das siduction-Team
    '''

    def __init__(self, session, name, expanded):
        '''
        Constructor.
        @param session: the session info
        @param name:     the name of the menu. This implies the filename
        @param expanded: true: all members of the menu tree are visible<br>
                        false: only the current members and its siblings are visible.
        '''
        self._name = name
        self._session = session
        self._expanded = expanded
        self._topLevelItems = []
        self._snippets = None
        self._extendedMenu = (session._globalPage != None 
            and session._globalPage.getField('expert') == 'T')
        
    def read(self):
        '''Reads the menu definitions into internal structures.
        '''
        session = self._session
        currentLink = session._pageAndBookmark
        if currentLink != None:
            currentLink = currentLink.lower()
            currentLink2 = currentLink + '#'
        lang = session._language if session._language != None else 'en'
        fn = (session._homeDir + 'config/' + self._name + '_'
              + lang + '.conf')
        if not os.path.exists(fn):
            fn = session._homeDir + 'config/' + self._name + '_en.conf'
        if not os.path.exists(fn):
            session.error('Menu.read(): not found: ' + fn)
        else:
            with codecs.open(fn, "r", "UTF-8") as fp:
                maxLevel = 3
                menuStack = []
                for ii in range(maxLevel):
                    menuStack.append(None);
                lastLevel = 0
                lineNo = 0
                rexpr = re.compile(r'\s+')
                for line in fp:
                    lineNo += 1
                    valid = line.startswith('*')
                    if line.startswith('+'):
                        valid = self._extendedMenu
                    if valid:
                        fields = rexpr.split(line, 3)
                        level = len(fields[0]) - 1
                        mId = fields[1]
                        link = fields[2]
                        ix = link.find('#')
                        # abc#xxx -> abc?label=xxxx#xxx
                        #if ix > 0:
                        #    link =  link[0:ix] + '?label=' + link[ix+1:] + link[ix:]
                        title = fields[3].rstrip().replace('&#8658;', '').rstrip()
                        
                        if level >= maxLevel:
                            self._session.error(
                                '{:s}-{:d}: indent level too large'
                                    .format(fn, lineNo))
                        elif level > lastLevel + 1:
                            self._session.error(
                                '{:s}-{:d}: indent level gap found'
                                    .format(fn, lineNo))
                        else:
                            item = MenuItem(level, mId, title, link)
                            menuStack[level] = item
                            if level == 0:
                                self._topLevelItems.append(item)
                            else:
                                menuStack[level - 1].addItem(item)
                            for ii in xrange(level + 1, maxLevel):
                                menuStack[ii] = None
                            if (currentLink != None 
                                    and (currentLink == link.lower()
                                         or link.lower().startswith(currentLink2))):
                                for ii in xrange(level+1):
                                    menuStack[ii]._isActive = True
                        lastLevel = level
                    
    def buildOneLevel(self, level, items, parentIsActive):
        '''Builds the html construct of a menu item for one level.
        @param level: the indention level: 0..N
        @param items: the items representing the menu at this level
        @param parentIsActive: True: the parent is marked as current menu item
        @return: the HTML code of the menu item
        '''
        rc = ''
        if items != None and len(items) > 0:
            entries = ''
            snippet = 'LEVEL_' + str(level)
            template = self._snippets.get(snippet)
            index = 0
            for item in items:
                index += 1
                name = 'ENTRY_' + str(level)
                templateEntry = self._snippets.get(name)
                templateEntry = templateEntry.replace('{{link}}', item._link)
                templateEntry = templateEntry.replace('{{title}}', item._title)
                templateEntry = templateEntry.replace('{{link}}', item._link)
                templateEntry = templateEntry.replace('{{index}}', str(index))
                
                classCurrent = '' 
                if item._isActive:
                    classCurrent = self._snippets.get('CLASS_CURRENT').rstrip()
                templateEntry = templateEntry.replace('{{class_current}}', 
                    classCurrent)
                
                submenus = ''
                if (parentIsActive 
                    or (item._isActive or self._expanded) 
                        and item._subMenus != None
                        and len(item._subMenus) > 0):
                    submenus = self.buildOneLevel(level + 1, item._subMenus, 
                            item._isActive)
                templateEntry = templateEntry.replace('###SUBMENUS###', submenus)
                
                templateId = ''
                if item._id != '-':
                    templateId = self._snippets.get('ID').rstrip()
                    templateId = templateId.replace('{{id}}', item._id)
                
                entries += templateEntry.replace('{{id}}', templateId)
            rc = template.replace('###ENTRIES###', entries) 
        return rc

    def buildHtml(self, snippets): 
        '''Builds the HTML code for the snippets.
        @param snippets: the HTML definitions
        @return: the HTML code of the menu
        '''
        self._snippets = snippets
        rc = self.buildOneLevel(0, self._topLevelItems, False)
        return rc
