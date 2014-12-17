'''
Implements a converter from MediaWiki syntax to html.

Created on 02.02.2014

@author: hm
'''

import re

rexprImageExtension = re.compile(r'\.(png|jpg|gif)$', re.IGNORECASE) 
rexprManualPage = re.compile(r'(.*?)-(en|de|pl|pt-br|ro|it)\.htm(#.*)$')
REPL_MARKER = "\x01"

TYPE_UNDEF = 0
TYPE_PARAGRAPH = 1
TYPE_INDENT = 2
# preceeding ' ':
TYPE_PRE = 3
# <pre>:
TYPE_PRE_STRONG = 4
TYPE_LIST = 5
TYPE_TABLE = 6

replStorage = []

def replaceMetaChars(text):
    '''Replace the markup meta characters by their replacements.
    @param text:    text to convert
    @return:        the converted text
    '''
    text = text.replace(u"&", u"&amp;");
    text = text.replace(u"<=", u"&le;");
    text = text.replace(u">=", u"&ge;");
    text = text.replace(u"<", u"&lt;");
    text = text.replace(u">", u"&gt;");
    return text
        

def storeReplacement(text):
    '''Stores a string in replStorage and returns a placeholder.
    @param text:    text to store
    @return:        a placeholder for the storage.
    '''
    global replStorage
    ix = len(replStorage)
    replStorage.append(text)
    rc = u"{:s}{:04d}".format(REPL_MARKER, ix)
    return rc

def externalLinkResolver(matcher):
    '''Handles the replacement of an external link.
    see self._rexprExternalLink for the regular expression
    @param matcher:    the link matcher
    @return:            the HTML string of the link
    '''
    # '\[((ftp|https?):\S+)([ |](.+?))?\](\w*)?', re.IGNORECASE)
    # ---12----------2----13----4---43---5---5
    global rexprImageExtension
    link = matcher.group(1)
    text = matcher.group(4)
    linkTextSuffix = matcher.group(5)
    rc = ""
    if text == None:
        text = link
    if linkTextSuffix != None:
        text += linkTextSuffix
    text = replaceMetaChars(text)
    rc += storeReplacement(u'<a href="{:s}">{:s}</a>'.format(link, text))
    return rc

def buildImage(url, arguments):
    '''Decodes the image options.
    @param url:        URL of the image
    @param arguments:  the mediawiki options of the image construct
    @return: the HTML code of the image
    '''
    link = None
    caption = ""
    opts = ""
    clazz = None
    args = arguments.split(r'|')
    for arg in args:
        matcher = re.search(r'class=(.*)', arg)
        if matcher != None:
            opts += ' class="{:s}"'.format(matcher.group(1))
            clazz = matcher.group(1)
            continue
        matcher = re.search(r'link=(.*)', arg)
        if matcher != None:
            link = matcher.group(1)
            continue
        matcher = re.search(r'(\d+)x(\d)px', arg)
        if matcher != None:
            opts += ' width="{:d}" height="{:d}"'.format(matcher.group(1), matcher.group(2))
            continue
        matcher = re.search(r'(\d+)px', arg)
        if matcher != None:
            opts += ' width="{:d}""'.format(matcher.group(1))
            continue
        matcher = re.search(r'(\d+)px', arg)
        if matcher != None:
            opts += ' height="{:d}""'.format(matcher.group(1))
            continue
        caption += " " + arg
    if caption != "":
        opts += u' title="{:s}"'.format(caption[1:])
    html = u'<img src="{:s}"{:s} />'.format(url, opts)
    if link != None:
        html = u'<a href="{:s}"{:s}>{:s}</a>'.format(url, args, html)
    if clazz != None:
        html = u'<div class="{:s}">{:s}</div>'.format(clazz, html)
    return html

def internalLinkResolver(matcher):
    '''Handles the replacement of an internal link.
    see self._rexprInternalLink for the regular expression
    @param matcher:    the link matcher
    @return:            the HTML string of the link
    '''
    global rexprManualPage, rexprImageExtension
    # r'\[\[([^|]+)\|([^\]]+)\]\]'
    # ------1-----1--2------2
    link = matcher.group(1)
    #r'(.*?)-(en|de|pl|pt-br|ro|it)\.htm(#.*)$
    #--1---1-2--------------------2-----3---3
    matcher2 = rexprImageExtension.search(link)
    if matcher2 != None:
        # image:
        if link.startswith('../'):
            link = '../static/' + link[3:]
        html = buildImage(link, matcher.group(2))
    else:
        matcher2 = rexprManualPage.match(link)
        if matcher2 != None:
            link = matcher2.group(1) + matcher2.group(3)
        text = matcher.group(2)
        html = u'<a href="{:s}">{:s}</a>'.format(link, text)
    rc = storeReplacement(html)
    return rc

def simpleLinkResolver(matcher):
    '''Handles the replacement of a simple link.
    see self._rexprSimpleLink for the regular expression
    @param matcher:    the link matcher
    @return:           the HTML string of the link
    '''
    global rexprImageExtension
    # ((ftp|https?):\S+)
    # 12----------2----1
    link = matcher.group(1)
    imgMatcher = rexprImageExtension.search(link)
    if imgMatcher != None:
        rc = u'<img src="{:s}" />'.format(link)
    else:
        text = replaceMetaChars(link)
        rc = u'<a href="{:s}">{:s}</a>'.format(link, text)
    rc = storeReplacement(rc)
    return rc

def storeUnchanged(matcher):
    '''Replaces the last found pattern with a placeholder of this text.
    The effect: the text remains unchanged.
    '''
    rc = storeReplacement(matcher.group(0))
    return rc
     
def unchangedResolver(matcher):
    '''Handle the elements which will be remain unchanged, e.g. <pre>.
    @param matcher:    the matcher object for the hit.
    @return: the placeholder of the stored nowiki body
    '''
    # '(<nowiki>(.*?)</nowiki>|<!--(.*?)-->|(<pre(\s+(style|class)=".*?")*>)(.*?)</pre>|<nowiki\s*/>|<span(\s+(style|class)=".*?")*>|</span>|</?strike>|</?code>|</?ins>|</?del>|</?blockquote>)')
    # 1--------2---2--------------3---3----4--- 5---6-----------6------5--47---7------
    if matcher.group(7) != None:
        body = matcher.group(7)
        prefix = matcher.group(4)
        text = prefix + replaceMetaChars(body) + "</pre>"
    elif matcher.group(3) != None:
        text = "<!--" + matcher.group(3) + "-->"
    elif matcher.group(2) != None:
        text = replaceMetaChars(matcher.group(2))
    else:
        text = matcher.group(1)
        if text.startswith("<nowiki"):
            # replace <nowiki/> by "":
            text = ""
    rc = storeReplacement(text)
    return rc

def storageResolver(matcher):
    '''Replaces the placeholder with the values stored in replStorage.
    @param matcher:    the matcher object for the hit.
    @return:           the stored value defined by the placeholder
    '''
    global replStorage
    ix = int(matcher.group(1))
    rc = replStorage[ix]
    return rc

class MediaWikiConverter:
    '''Translate a text written for the mediawiki (used by wikipedia) into html.
    '''
    def __init__(self):
        '''Constructor.
        '''
        self._currentType = TYPE_UNDEF
        self._currentBlock = ""
        self._html = ""
        self._currentIndent = 0
        self._listStack = []
        self._rowNo = -1
        self._rexprBoldAndItalic = re.compile(r"'''''(.*?)'''''", re.DOTALL)
        self._rexprBold = re.compile(r"'''(.*?)'''", re.DOTALL)
        self._rexprItalic = re.compile(r"''(.*?)''", re.DOTALL)
        self._rexprExternalLink = re.compile(
            r'\[((ftp|https?):\S+)([ |](.+?))?\](\w*)?', re.IGNORECASE + re.DOTALL)
        # ------12----------2----13----4---43---5---5
        self._rexprSimpleLink = re.compile(
            r'((ftp|https?):\S+)', re.IGNORECASE + re.DOTALL)
        # ----12----------2----1
        self._rexprUnchanged = re.compile(
            r'(<nowiki>(.*?)</nowiki>|<!--(.*?)-->|(<pre(\s+(style|class)=".*?")*>)(.*?)</pre>|<nowiki\s*/>|<span(\s+(style|class)=".*?")*>|</span>|</?strike>|</?code>|</?ins>|</?del>|</?blockquote>|</?tt>|</?small>|</?big>|<br ?/>)',
            re.IGNORECASE + re.DOTALL)
            # 1--------2---2--------------3---3----4--- 5---6-----------6------5--47---7------
        self._rexprPlaceholders = re.compile(REPL_MARKER + r'(\d{4})')
        self._rexprEmptyDiv = re.compile(r'<div[^/]+/>')
        self._rexprUtfConst = re.compile(r'&#\d+')
        self._rexprInternalLink = re.compile(r'\[\[([^|]+)\|([^\]]+)\]\]')
        self._regexprSpanId = re.compile(r'\s*<span id="([^"]+)"></span>')
        self._regexprSpanClass = re.compile(r'\s*<!--class="([^"]+)"-->')
        
    def countPrefix(self, line, prefix, prefix2 = None):
        '''Counts the occurrencies of a char in the top of the line.
        @param line: the line to test
        @param prefix: the character to test
        @param prefix: None or a second possibility of the prefix
        '''
        ix = 0
        length = len(line)
        if prefix2 == None:
            while ix < length and line[ix] == prefix:
                ix += 1
        else:
            while ix < length and line[ix] == prefix or line[ix] == prefix2:
                ix += 1
        return ix
          
    def convertBlock(self, text):
        '''Converts a wiki text block into a HTML text.
        A wiki text block is the text of a paragraph, the text of a enumeration ... 
        @param text:        text to convert
        @return return:    html text
        '''
        global replStorage
        replStorage = []
        text = self._rexprEmptyDiv.sub(storeUnchanged, text)
        text = self._rexprInternalLink.sub(internalLinkResolver, text)
        text = self._rexprUtfConst.sub(storeUnchanged, text)
        text = self._rexprUnchanged.sub(unchangedResolver, text)
        text = self._rexprExternalLink.sub(externalLinkResolver, text)
        text = self._rexprSimpleLink.sub(simpleLinkResolver, text)
        text = replaceMetaChars(text)
        text = self._rexprBoldAndItalic.sub(
            lambda m: "<b><i>" + m.group(1) + "</i></b>" , text)
        text = self._rexprBold.sub(
            lambda m: "<b>" + m.group(1) + "</b>" , text)
        text = self._rexprItalic.sub(
            lambda m: "<i>" + m.group(1) + "</i>" , text)
        
        text = self._rexprPlaceholders.sub(storageResolver, text)
        return text  
    
    def convertPreBlock(self, text):
        '''Converts all meta constructs allowed inside a convertPreBlockted block.
        @param text:    text to convert
        @return: the formatted text
        '''
        text = replaceMetaChars(text)
        text = self._rexprBoldAndItalic.sub(
            lambda m: "<b><i>" + m.group(1) + "</i></b>" , text)
        text = self._rexprBold.sub(
            lambda m: "<b>" + m.group(1) + "</b>" , text)
        text = self._rexprItalic.sub(
            lambda m: "<i>" + m.group(1) + "</i>" , text)
        
        text = self._rexprPlaceholders.sub(storageResolver, text)
        return text
    
    def convertHeadline(self, line):
        '''Translate a headline.
        @param line: wiki line
        @return:     html line
        '''
        indent = self.countPrefix(line, "=")
        prefix = line[0:indent]
        if line.endswith(prefix):
            text = line[indent:-indent]
        else:
            text = line[indent:]
        matcher = self._regexprSpanId.match(text)
        ident = ''
        if matcher != None:
            text = text[matcher.end(0):]
            ident = u' id="{:s}"'.format(matcher.group(1))
        text = self.convertBlock(text)
        rc = u"<h{:d}{:s}>{:s}</h{:d}>\n".format(indent, ident, text, indent)
        return rc
      
    def endOfBlock(self, newType, line = None):
        '''Tests whether an end of block is reached.
        In this case the end marker will be appended.
        @param newType:    the type of the current line
        @param line:        None or line to put into the current block
        '''
        if newType != self._currentType:
            if self._currentType == TYPE_PARAGRAPH:
                found = True
                attr = ''
                while found:
                    found = False
                    matcher = self._regexprSpanId.match(self._currentBlock)
                    if matcher != None:
                        self._currentBlock = self._currentBlock[matcher.end(0):]
                        attr += u' id="{:s}"'.format(matcher.group(1))
                        found = True
                    else:
                        matcher = self._regexprSpanClass.match(self._currentBlock)
                        if matcher != None:
                            self._currentBlock = self._currentBlock[matcher.end(0):]
                            attr += u' class="{:s}"'.format(matcher.group(1))
                            found = True
                block = self.convertBlock(self._currentBlock)
                if self._currentBlock != "":
                    self._html += u"<p{:s}>{:s}</p>\n".format(attr, block)
            elif self._currentType == TYPE_PRE:
                block = self.convertBlock(self._currentBlock)
                self._html += u'<pre class="wiki_pre">{:s}</pre>\n'.format(block)
            elif self._currentType == TYPE_PRE_STRONG:
                # reaches never
                block = u"<pre>{:s}\n</pre>\n".format(self._currentBlock)
                self._html += u'<pre class="wiki_pre">{:s}</pre>\n'.format(block)
            elif self._currentType == TYPE_INDENT:
                while self._currentIndent > 0:
                    self._html += u"</dl>"
                    self._currentIndent -= 1
                self._html += u"\n"    
            elif self._currentType == TYPE_LIST:
                while len(self._listStack) > 0:
                    self.popList()
                self._html += u"\n"
            elif self._currentType == TYPE_UNDEF:
                pass
            else:
                self._html += u"unknown type: " + str(self._currentType)
            self._currentType = newType
            self._currentBlock = ""
        
    def popList(self):
        '''Handles the end of list of the most top item in the list stack.
        '''
        self._html += "</li>\n" + self._listStack.pop() + "\n"
        
    def pushList(self, isOrdered):
        '''Handles the begin of a HTML list.
        @param isOrdered:    True: the list is ordered.
                             False: the list is unordered
        '''
        if isOrdered:
            self._html += "<ol>"
            self._listStack.append("</ol>")
        else:
            self._html += "<ul>"
            self._listStack.append("</ul>")       
        
    def isOrderedOfStack(self, indent):
        '''Tests whether the list at a given indent is ordered or not.
        @param indent: the indent of the current stack to inspect
        @return        True: the list is ordered.
                       False: the list is unordered
        '''
        rc = self._listStack[indent - 1].startswith("</ol>")
        return rc
    
    def convertList(self, line):
        '''Converts a line of a orderd/unorderd list.
        @param line:    the line to convert
        '''
        self.endOfBlock(TYPE_LIST)
        indent = self.countPrefix(line, "*", "#")
        lastIndent = len(self._listStack)
        if indent == lastIndent:
            isOrdered = line[indent - 1] == "#"
            if isOrdered == self.isOrderedOfStack(indent):
                self._html += "</li>\n"
            else:
                self.popList()
                self.pushList(isOrdered)
        if indent != lastIndent:
            while indent < lastIndent:
                self.popList()
                lastIndent -= 1
            while indent > lastIndent:
                isOrdered = line[lastIndent] == '#'
                self.pushList(isOrdered)
                lastIndent += 1
        block = self.convertBlock(line[indent:])
        self._html += "<li>" + block

    def convertIndent(self, line):
        self.endOfBlock(TYPE_INDENT)
        indent = self.countPrefix(line, ":")
        while indent > self._currentIndent:
            self._html += "<dl>"
            self._currentIndent += 1
        while indent < self._currentIndent:
            self._html += "</dl>"
            self._currentIndent -= 1
        block = self.convertBlock(line[indent:])
        self._html += u"<dd>{:s}</dd>\n".format(block)
        
    def convertTable(self, line):
        '''Converts the lines belonging to a table.
        @param line:    line
        '''
        if line.startswith("|-"):
            self._colPrefix = 'td'
            self._rowNo += 1
            self._html += "</tr><tr>\n"
        elif line.startswith("|+"):
            self._colPrefix = 'th'
            self._rowNo += 1
            self._html += "</tr><tr>\n"
        elif line.startswith("|}"):
            self._html += "</tr></table>\n"
            self._rowNo = -1
        elif line.startswith("|"):
            cols = line[1:].split("||")
            for col in cols:
                block = self.convertBlock(col)
                self._html += u"<{:s}>{:s}</{:s}>\n".format(self._colPrefix,
                    block, self._colPrefix) 
        elif line.startswith("!"):
            cols = line[1:].split("|")
            for col in cols:
                block = self.convertBlock(col)
                self._html += u"<th>{:s}</th>\n".format(block) 
        elif line.startswith("{|"):
            self._html += "<table><tr>\n"
            self._rowNo = 0
     
    def convert(self, text):
        '''Translate a wiki text into html.
        @param text: wiki text
        @return:     html text
        '''
        lines = text.split("\n")
        self._html = ""
        linNo = 0
        if len(lines) > 0 and lines[0].startswith("mediawiki"):
            linNo = 1
        self._currentBlock = ""
        openPre = False
        while linNo < len(lines):
            line = lines[linNo]
            linNo += 1
            if openPre:
                ix = line.find("</pre>")
                if ix < 0:
                    self._html += line + "\n"
                else:
                    self._currentType = TYPE_UNDEF
                    openPre = False
                    self._html += line[0:ix]
                    if ix > 0 and line[ix] != "\n":
                        self._html += "\n"
                    self._html += "</pre>\n"
                    if len(line) > ix + 7:
                        self._currentBlock = line[ix+7:]
                        self._currentType = TYPE_PARAGRAPH
            elif line.startswith(":"):
                self.convertIndent(line)
            elif line.startswith(" "):
                self.endOfBlock(TYPE_PRE)
                self._currentBlock += self.convertPreBlock(line[1:])
            elif line.startswith('<pre'):
                self.endOfBlock(TYPE_PRE_STRONG)
                openPre = True
                self._html += line + "\n"
            elif line.startswith("----"):
                self.endOfBlock(TYPE_UNDEF)
                self._html += "<hr />\n"
            elif line.startswith("="):
                self.endOfBlock(TYPE_UNDEF)
                self._html += self.convertHeadline(line)
            elif line.startswith("*") or line.startswith("#"):
                self.convertList(line)
            elif line.startswith("{|"):
                self.convertTable(line)
            elif line.startswith("|") or line.startswith("!"):
                if self._rowNo < 0:
                    # missing table start: handle as part of the paragraph
                    self.endOfBlock(TYPE_PARAGRAPH, line)
                else:
                    self.convertTable(line)
            else:
                self.endOfBlock(TYPE_PARAGRAPH)
                if line != "":
                    self._currentBlock += line + "\n"
                elif self._currentBlock != "":
                    self.endOfBlock(TYPE_UNDEF)
        self.endOfBlock(TYPE_UNDEF)          
        return self._html
                    
if __name__ == '__main__':
    pass