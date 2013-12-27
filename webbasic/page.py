'''
Created on 09.03.2013

@author: hm
'''
import xml.sax.saxutils
import operator, re

from util.util import Util
from pagedata import PageData, FieldData
from webbasic.htmlsnippets import HTMLSnippets

class PageException(Exception):
    def __init__(self, page, message):
        if page != None:
            message = page._name + ': ' + message
        super(PageException, self).__init__(message)
        
class PageResult:
    '''Stores the "result" of a page: a HTML code or a redirection URL.
    '''
    def __init__(self, body = None, url = None, caller = None): 
        self._body = body
        self._url = url
        self._caller = caller

class Page(object):
    '''
    classdocs
    '''

    def __init__(self, name, session, readSnippets = True):
        '''Constructor.
        @param name: the name of the page. Defines the template filename
        @param session: the session info
        @param readSnippets: True: the page specific snippets will be read
        '''
        self._name = name
        self._session = session
        self._pageData = PageData(session)
        self._snippets = None
        self._globalPage = None
        self._errorPrefix = None
        self._errorSuffix = None
        self._redirect = None
        if readSnippets:
            self._snippets = HTMLSnippets(session)
            self._snippets.read(name)
        self._dynMeta = ""
        

    def afterInit(self):
        '''Will be called after all initializations are done.
        Note: self._globalPage will be set after the constructor.
        This method can be overridden.
        '''
        pass
    
    def defineFields(self):
        '''This method must be overwritten:
        If not an error message must be displayed.
        '''
        self._session.error('missing defineFields(): ' + self._name)
    
    def handleButton(self, button):
        '''This method must be overwritten:
        If not an error message will be displayed.
        @param button: the pushed button
        '''
        self._session.error('missing handleButton(): ' + self._name)
        
    def addField(self, name, defaultValue = None, defaultIndex = None, dataType = 's'):
        '''Adds a field definition.
        Delegation to PageData.add()
        @param name: the field's name
        @param defaultValue: the value for the first time
        @param dataType: "s": string "d": integer "p": password 
                        "b": boolean "v": vocabulary
        @param defaultIndex: only on selection fields: the default index 
        '''
        if defaultIndex != None:
            (texts, values) = self.getOptValues(name)
            if values == None:
                values = texts
            if defaultIndex < len(values):
                defaultValue = values[defaultIndex]
        self._pageData.add(FieldData(name, defaultValue, dataType))
          
    def getField(self, name):
        '''Returns a value from a (virtual) field.
        Delegation to PageData.get()
        @param name: the field's name
        '''
        rc = self._pageData.get(name)
        return rc

    def putField(self, name, value):
        '''Puts a value to a (virtual) field.
        Delegation to PageData.put()
        @param name: the field's name
        @param value: the value to set
        '''
        self._pageData.put(name, value)

    def putError(self, name, errorKey):
        '''Puts an error message (exactly its key) to a field.
        @param name: the field's name. If None a standard field will be taken
        @param errorKey: the key of the error message
        @return: True
        '''
        return self._pageData.putError(name, errorKey)
    
    def putErrorText(self, name, text):
        '''Puts an error message (exactly its key) to a field.
        @param name: the field's name. If None a standard field will be taken
        @param text: the error text
        @return: True
        '''
        return self._pageData.putErrorText(name, text)
    
    def buildHtml(self, htmlMenu):
        '''Builds the HTML text of the page.
        @param htmlMenu: the HTML code for the menu
        @return: the content part of the page
        '''
        body = self._snippets.get('MAIN')
        if hasattr(self, 'changeContent'):
            body = self.changeContent(body)
        body = self._session.replaceVars(body)    
        return body
    
    def buildTable(self, builder, info):
        '''Builds a table which is a piece of text containing rows.
        A row is a piece of text containing columns.
        A column is a piece of text containing values.
        
        @param builder: an instance with the method buildPartOfTable(info, what, ix)
                        ix is the row index (0..N-1) in the case of what == 'cols'
                        info: see below
                        Description of what:
                        'Table': None or html template of table with '{{ROWS}}'
                        'Row:' None or a template with '{{COLS}}'
                        'Col': None or a template with '{{COL}}'
                        'rows': number of rows. Data type: int
                        'cols': list of column values (data type: Object)
                        If one of the templates is None a standard 
                        HTML template will be used
        @param info:    will be given to the builder. Can be used
                        to build more than one table with one
                        builder
        @return:    the text of the HTML table
        '''            
        table = builder.buildPartOfTable(info, 'Table')
        if table == None:
            table = '<table>{{ROWS}}</table>'
        elif table.find('{{ROWS}}') < 0:
            raise PageException(self, 'missing {{ROWS} in ' + table)
        rowCount = builder.buildPartOfTable(info, 'rows')
        if type(rowCount) != int:
            raise PageException(self, "wrong type for row count: {:s} / {:s}"
                    .format(str(rowCount), repr(type(rowCount))))
        rows = ''
        colTemplate =  builder.buildPartOfTable(info, 'Col')
        if colTemplate == None:
            colTemplate = '<td>{{COL}}</td>'
        elif colTemplate.find('{{COL}}') < 0:
            raise PageException(self, 'missing {{COL} in ' + colTemplate)
        rowTemplate =  builder.buildPartOfTable(info, 'Row')
        if rowTemplate == None:
            rowTemplate = '<tr>{{COLS}}</tr>'
        elif rowTemplate.find('{{COLS}}') < 0:
            raise PageException(self, 'missing {{COLS} in ' + rowTemplate)
        for ixRow in xrange(rowCount):
            cols = builder.buildPartOfTable(info, 'cols', ixRow)
            content = ''
            for col in cols:
                if not (type(col) is str or type(col) is unicode):
                    val = self._session.toUnicode(col)
                else:
                    if col.startswith("<xml>"):
                        val = col[5:]
                    else:
                        val = xml.sax.saxutils.escape(col) 
                content += colTemplate.replace('{{COL}}', val)
            rows += rowTemplate.replace('{{COLS}}', content)
        table = table.replace('{{ROWS}}', rows)
        return table
        
    def errorPage(self, key):
        '''Returns the content of an error message page.
        @param key: the key of the error message
        @return: the content of the error page
        '''
        message =  '' if self._session._configDb == None else self._session.getConfig(key)
        rc = u'''
<h1>{{page.error.txt_header}}</h1>
<p class="error">+++ {:s}</p>
'''         .format(Util.toUnicode(message))
        return rc
    
    def buttonError(self, button):
        '''Generic handling of an unknown button.
        @param button: the button's name
        @return: None
        '''
        self._session.error('unknown button {:s} in page {:s}'.format(button, self._name))
        return None
    
    def findButton(self, fields):
        '''Tests whether a button has been pushed.
        @param fields: a dictionary with the field values
        @param: None: no button has been pushed<br>
            otherwise: the name of the pushed button
        '''
        rc = None
        if fields != None:
            for key in fields:
                if key.startswith('button_'):
                    rc = key
                    self._session.trace(key + " recognized")
                    break
        return rc
    
    def fillOpts(self, field, texts, values, selection, source):
        '''Builds the body of an <select> element.
        The placeholder will be replaced by the values.
        @param field: the name of the field (without page name)
        @param selection: if type(selection) == int: index of the selected. 
                        Otherwise: value of the selected option
        @param source: the HTML code containing the field to change
        @return: the source with expanded placeholder for the field
        '''
        opts = ""
        if type(selection) != int:
            try:
                if values != None:
                    selection = values.index(selection)
                else:
                    selection = texts.index(selection)
            except ValueError:
                selection = -1
        for ix in xrange(len(texts)):
            if opts != "":
                opts += '\n'
            opts += '<option selected="selected"' if ix == selection else '<option'
            if values != None and ix < len(values):
                opts += ' value="' + values[ix] + '"'
            opts += '>' + texts[ix] + '</option>'
        name = '{{body_' + field + '}}'
        source = source.replace(name, opts)
        return source
            
    def getOptValues(self, field):
        '''Gets the texts and (if available) the values of a selection field.
        @param field: the name of the field (without page name)
        @return: a tuple (texts, values)
        '''       
        key = self._name + '.opts_' + field
        values = self._session.getConfigOrNone(key)
        if values == None:
            values = self._session.getConfigOrNoneWithoutLanguage(key)
        texts = values[1:].split(values[0]) if values != None else []
        key = self._name + '.vals_' + field
        values = self._session.getConfigOrNoneWithoutLanguage(key)
        if values != None:
            values = values[1:].split(values[0])
        return (texts, values)
    
    def fillStaticSelected(self, field, body, pageOfField = None):
        '''Fills a selection field with fix options stored in configuration.
        @param field: name of the selection field
        @param body: the html text with the field definition
        @param pageOfField: the page containing the field.
                            If None pageOfField = self
        @return: the body with the supplemented field
        '''
        if pageOfField == None:
            pageOfField = self
        (texts, values) = self.getOptValues(field)
        selection = pageOfField.getField(field)
        body = self.fillOpts(field, texts, values, selection, body)
        return body
                
    def fillDynamicSelected(self, field, texts, values, body, pageOfField = None):
        '''Fills a selection field with fix options stored in configuration.
        @param field: name of the selection field
        @param texts: list of texts of the field option
        @param value: None or list of values of the field option
        @param body: the html text with the field definition
        @param pageOfField: the page containing the field.
                            If None pageOfField = self
        @return: the body with the supplemented field
        '''
        page = self if pageOfField == None else pageOfField
        selection = page.getField(field)
        body = self.fillOpts(field, texts, values, selection, body)
        return body
     
    def findIndexOfOptions(self, field):
        '''Returns the index of current value of a selection field
        in the text or value list.
        @param field: name of the field to test
        @return: -1: not found
                otherwise: the index of the value/text
        '''
        ix = -1
        current = self.getField(field)
        (texts, values) = self.getOptValues(field)
        if values == None:
            values = texts
        for ii in xrange(len(texts)):
            if texts[ii] == current or current == values[ii]:
                ix = ii
                break
        return ix
    
    def handle(self, htmlMenu, fieldValues, cookies):
        '''Generic handling of the page.
        @param fieldValues: the dictionary containing the field values (GET or POST)
        @param cookies: the cookie dictionary
        @return: a PageResult instance
        '''
        self._session.setId(cookies)
        self._session.readUserData()
        self.defineFields()
        self._pageData.importData(self._name, fieldValues)
        self._pageData.correctCheckBoxes(fieldValues);
        self.afterInit()
        if self._redirect != None:
            rc = self._redirect
        else:
    
            # Checks wether a button has been pushed:
            button = self.findButton(fieldValues)
            rc = None
            if button != None:
                rc = self.handleButton(button)
        
        if rc == None:
            fn = self._session.getTemplateDir() + 'pageframe.html'
            frame = Util.readFileAsString(fn)
            
            content = self.buildHtml(htmlMenu)
            content = self._pageData.replaceValues(content, self._errorPrefix,
                    self._errorSuffix)
            content = self._session.replaceVars(content)
            title = self._session.getConfig(self._name + '.txt_title')
            env = { 'CONTENT' : content, 
                'MENU' : htmlMenu,
                'META_DYNAMIC' : self._dynMeta,
                'STATIC_URL' : '',
                'DYNAMIC_URL' : '',
                '!title' : title
                }
            frame = self._session.replaceVars(frame, env)
            rc = PageResult(frame)
            
        self._pageData.exportData()
        if self._globalPage != None:
            self._globalPage._pageData.exportData()
        self._session.writeUserData()
        return rc
    
    def fillCheckBox(self, name, body):
        '''Handles the state of a checkbox.
        @param field: the field's name
        @param body: the html code containing the checkbox
        @return: the body with replaced placeholder for the field 
        '''
        value = self.getField(name)
        checked = '' if value != 'T' else 'checked="checked"'
        body = body.replace('{{chk_' + name + '}}', checked)
        return body
   
    def autoSplit(self, listAsString, mayBeEmpty = False):
        '''Splits a string into a list with an automatic separator:
        @param listAsString: the list as string. The first char is the separator
        @param mayBeEmpty:  True: an empty ListAsString returns []
                            False: an empty ListAsString raise an exception
        @return the list built from the string
        '''
        if mayBeEmpty and listAsString == "":
            rc = []
        else:
            if listAsString == None or listAsString == "":
                raise PageException(self, "autosplit(''): too short")
            sep = listAsString[0]
            rc = listAsString[1:].split(sep)
        return rc
    
    def humanReadableSize(self, size, unitLength = 3):
        '''Builds a human readable size with max. 3 digits and a matching unit.
        Reverse function to sizeAndUnitToKiByte
        @param size:         the size in Byte (type: int)
        @param unitLength:   the length of the unit string: 1, 2 or 3
        @return: a string with the size and unit, e.g. 213MiB
        '''
        sign = "-" if size < 0 else ""
        if sign == "-":
            size = -size
        if size <= 10*1024:
            if size > 0 and size % 1024 == 0:
                rc = '{:d}Ki'.format(size / 1024)
            else: 
                rc = '{:d}By'.format(size)
        elif size <= 10*1024*1024:
            if size % (1024*1024) == 0:
                rc = '{:d}Mi'.format(size / 1024 / 1024)
            else: 
                rc = '{:d}Ki'.format(size / 1024)
        elif size <= 10*1024*1024*1024:
            if size % (1024*1024*1024) == 0:
                rc = '{:d}Gi'.format(size / 1024 / 1024 / 1024)
            else:
                rc = '{:d}Mi'.format(size / 1024 / 1024)
        else:
            if size % (1024*1024*1024*1024) == 0:
                rc = '{:d}Ti'.format(size / 1024 / 1024 / 1024 / 1024)
            else:
                rc = '{:d}Gi'.format(size / 1024 / 1024 / 1024)
        if unitLength == 1:
            rc = rc[0:-1]
        elif unitLength == 3 and rc.endswith("i"):
            rc = rc + "B"
        return sign + rc

    def sizeAndUnitToByte(self, size, defaultUnit = "B"):
        '''Converts a string with size and unit into an integer value
        Rerverse function to humanReadableSize()
        @param size:         the size or the size and optionally a unit.
        @param defaultUnit:  if no unit is given this unit will be taken
        @return:             -1: invalid input<br>
                             otherwise: the size in Byte (int)
        '''
        rexpr = re.compile(r'(\d+)(.*)')
        matcher = rexpr.match(size)
        rc = -1
        if matcher:
            factor = 1
            size = int(matcher.group(1))
            unit = matcher.group(2)
            if unit == "":
                unit = defaultUnit
            unit = unit.lower()
            if unit.startswith("b"):
                factor = 1
            elif unit == "k" or unit.startswith("ki"):
                factor = 1024
            elif unit.startswith("kb"):
                factor = 1000
            elif unit == "m" or unit.startswith("mi"):
                factor = 1024*1024
            elif unit.startswith("mb"):
                factor = 1000*1000
            elif unit == "g" or unit.startswith("gi"):
                factor = 1024*1024*1024
            elif unit.startswith("gb"):
                factor = 1000*1000*1000
            elif unit == "t" or unit.startswith("ti"):
                factor = 1024*1024*1024*1024
            elif unit.startswith("tb"):
                factor = 1000*1000*1000*1000
            else:
                size = -1
            rc = -1 if size < 0 else size * factor 
        return rc
        
    def replaceGlobalField(self, field, defaultKey, args, snippet,
            placeholder, body):
        '''Replace a placeholder in a template with a global field.
        If the key does not exist a default key will be taken.
        @param key:        the field of the global page
        @param defaultKey: this key will be taken if the key has no value
        @param args:       None or a autoseparated list like ";yes;no"), 
                           In the text gotten by key/defaultKey must exist
                           placeholders like {{1}}.... this placeholders
                           will be replaced by the related entry of the list.
        @param snippet:    None or the snippet with the placeholder
        @param placeholder:    a string placed in the body.
        @param body:        the HTML template with the placeholder
        @return:     the body with replaced placeholder
        '''
        key = self._globalPage.getField(field)
        if key == None or key == "":
            key = defaultKey
        text = self._session.getConfigOrNone(key)
        if snippet != None:
            content = "" if text == None else  self._snippets.get(snippet)
            body = body.replace("{{" + snippet + "}}", content)
        if text != None and args != None:
            args = self.autoSplit(args)
            for ix in xrange(len(args)):
                posVar = "{:s}{:d}{:s}".format("{{", ix+1, "}}")
                text = text.replace(posVar, args[ix])
        if text != None:
            body = body.replace(placeholder, text)
        return body
    
    def storeAsGlobal(self, fieldLocal, fieldGlobal):
        '''Stores a local field in the global field.
        @param fieldLocal: the field to store
        @param fieldGlobal: the field in the global page
        '''
        value = self.getField(fieldLocal)
        self._globalPage.putField(fieldGlobal, value)

    def autoJoinArgs(self, args):
        rc = ";".join(args)
        if rc.count(";") == len(args) - 1:
            rc = ";" + rc
        else:
            rc = "|".join(args)
            if rc.count("|") == len(args) - 1:
                rc = "|" + rc
            else:
                rc = "^".join(args)
                if rc.count("^") == len(args) - 1:
                    rc = "^" + rc
                else:
                    rc = "~".join(args)
                    if rc.count("~") == len(args) - 1:
                        rc = "~" + rc
                    else:
                        raise Exception("No separator possible: ;|^~")
        return rc
    def gotoWait(self, follower, fileStop, fileProgress, 
            keyIntro, argsIntro, keyDescr = None, argsDescr = None,
            translation = None):
        '''Prepares the start of the wait page.
        @param session:    session info
        @param follower:    the name of the page (relative url) after the wait page
        @param fileStop:    if this file exists the wait page will be stopped
        @param fileProgress: None of the file containing a progress value
        @param keyIntro:    None or the key of the introduction text
        @param argsIntro:   None or a list of values for the placeholders in intro
        @param keyDescr:    None or the key of the description text
        @param argsIntro:   None or a list of values for the placeholders in descr
        @param translation  None or a key (exactlier: a key prefix) for 
                            translations in the progress message
        @return:            a PageResult instance with a redirection to wait
        '''
        self._globalPage.putField("wait.intro.key", keyIntro)
        if argsIntro != None:
            argsIntro = ";" + ";".join(argsIntro)
        self._globalPage.putField("wait.intro.args", argsIntro)
        self._globalPage.putField("wait.descr.key", keyDescr)
        if argsDescr != None:
            argsDescr = ";" + ";".join(argsDescr)
        self._globalPage.putField("wait.descr.args", argsDescr)
        if fileStop != None and not fileStop.endswith(".txt"):
            self._session.deleteFile(fileStop)
        self._session.deleteFile(self._globalPage.getField("wait.file.stop"))
        self._globalPage.putField("wait.file.stop", fileStop)
        self._globalPage.putField("wait.file.progress", fileProgress)
        self._globalPage.putField("wait.page", follower)
        self._globalPage.putField("wait.translation", translation)
        
        rc = self._session.redirect("wait", "gotoWait-" + self._name)
        return rc

    def execute(self, answer, options, command, params, timeout = 3600, 
                deleteAnswer = True):
        '''Executes a command. Delegates to the object _session._shellClient
         @param answer:     the name of the answer file
         @param options:    the options for the shell server
         @param command:   the command to execute, e.g. SVOPT_DEFAULT
         @param params:   NULL or a string or an array of strings
         @param timeout:    the maximum count of seconds
         @param deleteAnswer True: the answer file will be deleted
         @return: true: answer file exists. false: timeout reached
        '''
        return self._session._shellClient.execute(answer, options, command, 
            params, timeout, deleteAnswer)

    def setRefresh(self, sec = 3):
        '''Takes care that the page will be refreshed in a given time.
        @param sec    the time until the refresh will be done in seconds
        '''
        self._dynMeta = '<meta http-equiv="refresh" content="{:d}" />'.format(sec)
  
    def getButton(self, key):
        '''Returns the HTML code for a navigation key.
        Handles button.next and button.prev.
        @param key: 'prev' or 'next'
        @return: the html code for the button
        '''
        htmlKey = '.gui.button.' + key
        html = self._session.getConfigWithoutLanguage(htmlKey)
        textKey = '.gui.text.' + key
        text = self._session.getConfig(textKey)
        html = html.replace('{{' + textKey + '}}', text)
        return html
        
    def buildNavigationButtons(self, page, source):
        '''Replaces the placeholders for the navigation buttons.
        @param page: name of the current page
        @param source: the text with the placeholders
        @return: the source with replaced placeholders
        '''
        pages = self.getPages()
        pages = pages[1:].split(pages[0:1])
        ix = -1 if page not in pages else  pages.index(page)
        html = '' if ix <= 0 else self.getButton('prev')
        source = source.replace('{{.gui.button.prev}}', html)    
        html = '' if ix < 0 or ix == len(pages) - 1 else self.getButton('next')
        source = source.replace('{{.gui.button.next}}', html)
        return source    
        
    def buildInfo(self, source):
        '''Replaces the placeholder {{INFO}} with the log and error messages.
        @param source: the text with the placeholder
        @return: the source with replaced placeholder
        '''
        html = None
        for msg in self._session._errorMessages:
            if html == None:
                html = '<p class="error">' + msg
            else:
                html += '<br/>' + msg
        if html != None:
            html += '</p>'
        html2 = None
        for msg in self._session._logMessages:
            if html2 == None:
                html2 = '<p class="log">' + msg
            else:
                html2 += '<br/>' + msg
        if html2 != None:
            html2 += '</p>'
        if html == None:
            html = html2
        elif html2 != None:
            html += html2
        if html == None:
            html = ''
        source = source.replace('{{INFO}}', html)
        return source

    def replaceInPageFrame(self, source):
        '''Replace placeholders existing in the page frame (all pages).
        @param page: name of the current page
        @param source: the text with the placeholdes
        @return: the source with replaced placeholders
        '''
        source = self.buildInfo(source)
        source = self.buildNavigationButtons(self._name, source)
        source = source.replace('{{!form.url}}', self._name)
        return source
        
    def neighbourOf(self, page, prev):
        '''Returns the neighbour page.
        @param page: current page
        @param prev: True: the result is the prevous page<br>
                    False: the result is the next page
        @result: None: no neighbour found<br>
                otherwise: the name of the neighbour page
        '''
        pages = self.getPages()
        pages = pages[1:].split(pages[0])
        ix = operator.indexOf(pages, page)
        if prev:
            rc = None if ix <= 0 else pages[ix - 1]
        else:
            rc = None if ix >= len(pages) - 1 else pages[ix + 1]
        return rc
      
    def isValidContent(self, field, firstChars, restChars, mandatory, 
            useStandardErrorMessage = False):
        '''Tests whether a field value contains valid character only.
    
        Tests whether the field is empty. If yes and mandatory an error occurres.
        Tests whether the field matches a regular expression.
        If no error the field will be stored into the user data.
        
        @param field        the name of the field to test
        @param firstChars    the characters which can be the first character of the value
        @param restChars    the characters which can be the not first characters of the value
        @param mandatory    true: an empty field returns an error false: the field may be empty
        '''
        notOk = False
        value = self.getField(field)
        outputField = None if useStandardErrorMessage else field
        if value == None or value == "":
            if mandatory:
                notOk = self.putError(outputField, ".empty_field")
        else:
            pattern = "[" + firstChars + "]"
            found = re.match(pattern, value) != None
            if not found:
                text = (self._session.getConfig(".wrong_first")
                   + ": " + value[0] + " " + self._session.getConfig(
                       ".allowed") + " " + firstChars)
                notOk = self.putErrorText(outputField, text);
            else:
                pattern = u".[{:s}]*([^{:s}]+)".format(
                    Util.toUnicode(restChars), Util.toUnicode(restChars))
                rexpr = re.match(pattern, value)
                if rexpr != None:
                    text = (self._session.getConfig(".wrong_next")
                        + ": " + rexpr.group(1) + " " + self._session.getConfig(
                        ".allowed") + " " + firstChars)
                    notOk = self.putErrorText(outputField, text);
        return not notOk

    def getPages(self):
        '''Gets the list of chained pages.
        The listed pages are chained by "prev" and "next" buttons.
        @return: a auto delimited list of pages, e.g. ";home;info"
        '''
        pages = self._globalPage.getField(".pages")
        if pages == None or pages == "":
            pages = self._session.getConfigWithoutLanguage(".gui.pages")
        return pages

    def addPage(self, page, predecessor):
        '''Adds a page to the list of chained pages.
        @param page: the new page
        @param predecessor: the new page will be inserted in front of this page.
                            If None the new page will be the first
        '''
        pages = self.getPages()
        if predecessor == None:
            pages += pages[0] + page
        else:
            pages = pages.replace(predecessor, page + pages[0] + predecessor)
        self._globalPage.putField(".pages", pages)
        
    def delPage(self, page):
        '''Removes a page from the list of chained pages.
        @param page: the page to delete
        '''
        pages = self.getPages()
        pages = pages.replace(pages[0] + page, "")
        self._globalPage.putField(".pages", pages)

    
        