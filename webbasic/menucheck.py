'''
Created on 22.03.2013

@author: hm
'''

import os.path, logging, re
from util.util import Util
logger = logging.getLogger(__name__)

class MenuChecker:
    '''
    Checks the consisty of the configuration database.
    '''


    def __init__(self, session, baseDir):
        '''
        Constructor.
        '''
        self._session = session
        self._baseDir = baseDir
        self._rexpr = re.compile(r'\s')
        
    def findLinks(self, lines, numbers):
        '''Returns a dictionary containing the links of the menu items.
        @param lines:  the lines of the menu definitions
        @param numbers: the true line numbers (related to lines by index)
        @param: a dictionary of links -> lineNo
        '''
        
        links = {}
        ix = -1
        for line in lines:
            ix += 1
            cols = self._rexpr.split(line, 3)
            if len(cols) > 2:
                link = cols[2]
                links[link] = numbers[ix]
        return links
    
    def isValidLine(self, line):
        '''Checks whether a line is a relevant line for menu definition.
        @param line: line to check
        @return: True: a valid line
        '''
        return line.startswith('+') or line.startswith('*')
    
    def stripMenu(self, fn):
        '''Reads a file and remove the non relevant lines, e.g. comments.
        @param filename: filename with path
        @return: a tuple of two lists (lines, numbers)
        '''
        lines = Util.readFileAsList(fn, True)
        lineNumbers = []
        rc = []
        no = 0
        for line in lines:
            no += 1
            if self.isValidLine(line):
                lineNumbers.append(no)
                rc.append(line)
        return (rc, lineNumbers)
    
    def checkMenu(self, language, template):
        '''Compares the menu of the given language with the English menu.
        @param language: language to test
        @param template: a HTML code with placeholder {{message}}
        @param separator: the separator between the missed keys
        '''
        message = ''
        file1 = self._baseDir + 'config/menu_' + language + '.conf'
        file2 = self._baseDir + 'config/menu_en.conf'
        if not os.path.exists(file1):
            msg = self._session.getConfig('.error.menu.file.missing')
            msg = msg.format(file1)
            message += template.replace('{{message}}', msg)
        elif not os.path.exists(file2):
            msg = self._session.getConfig('.error.menu.file.missing')
            msg = msg.format(file2)
            message += template.replace('{{message}}', msg)
        else:    
            (lines1, no1) = self.stripMenu(file1)
            (lines2, no2) = self.stripMenu(file2)
            links2 = self.findLinks(lines2, no2)
            
            count = min(len(lines1), len(lines2))
            for ix in xrange(count):
                line = lines1[ix]
                cols = self._rexpr.split(line, 4)
                if len(cols) < 4:
                    msg = self._session.getConfig('.error.menu.cols.missing')
                    msg = msg.format(file1, no1[ix], line)
                    message += template.replace('{{message}}', msg)
                    continue
                (indent1, link1) = (cols[0], cols[2])
                 
                line = lines2[ix]
                cols = self._rexpr.split(line, 4)
                if len(cols) < 4:
                    msg = self._session.getConfig('.error.menu.cols.missing')
                    msg = msg.format(file2, no2[ix], line)
                    message += template.replace('{{message}}', msg)
                    continue
                (indent2, link2) = (cols[0], cols[2]) 
                
                if link1 != link2:
                    if link1 not in links2:
                        msg = self._session.getConfig('.error.menu.native.link.missing')
                        msg = msg.format(file1, no1[ix], link1, file2)
                        message += template.replace('{{message}}', msg)
                    else:
                        msg = self._session.getConfig('.error.menu.native.link.moved')
                        msg = msg.format(file1, no1[ix], link1, file2, links2[link1])
                        message += template.replace('{{message}}', msg)
                elif indent1 != indent2:
                    msg = self._session.getConfig('.error.menu.indent.different') 
                    msg = msg.format(file1, no1[ix], indent1, indent2)
                    message += template.replace('{{message}}', msg)
             
            if len(lines1) > count:
                    msg = self._session.getConfig('.error.menu.english.fewer') 
                    msg = msg.format(file1, len(lines1) - count, file2)
                    message += template.replace('{{message}}', msg)
            elif len(lines2) > count:
                    msg = self._session.getConfig('.error.menu.english.more') 
                    msg = msg.format(file1, len(lines2) - count, file2)
                    message += template.replace('{{message}}', msg)
        return message
        
    def buildTable(self, language):
        file1 = self._baseDir + 'config/menu_' + language + '.conf'
        file2 = self._baseDir + 'config/menu_en.conf'
        if not os.path.exists(file1):
            msg = self._session.getConfig('.error.menu.file.missing')
            msg = msg.format(file1)
            html = '<p>' + msg + '</p>\n'
        elif not os.path.exists(file2):
            msg = self._session.getConfig('.error.menu.file.missing')
            msg = msg.format(file2)
            html = '<p>' + msg + '</p>\n'
        else:    
            (lines1, no1) = self.stripMenu(file1)
            (lines2, no2) = self.stripMenu(file2)
            html = '<table border="1">\n'
            count = min(len(lines1), len(lines2))
            for ix in xrange(count):
                line = lines1[ix]
                cols1 = self._rexpr.split(line, 3)
                line = lines2[ix]
                cols2 = self._rexpr.split(line, 3)
                if len(cols1) >= 4 and len(cols2) >= 4:
                    html += ('<tr><td>{:s}</td><td>{:s}</td><td>{:s}</td><td>{:s}</td>\n'
                        .format(cols1[2], cols1[3], cols2[3], cols2[2]))
                    html += '</tr>'
            html += '</table>\n'
        return html
                    
        