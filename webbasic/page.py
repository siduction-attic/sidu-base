'''
Created on 09.03.2013

@author: hm
'''
import xml.sax.saxutils
import operator

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
        If not an error message must be displayed.
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
        @param name: the field's name
        @param errorKey: the key of the error message
        @return: True
        '''
        return self._pageData.putError(name, errorKey)
    
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
                    .format(unicode(rowCount), repr(type(rowCount))))
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
                if not (type(col) is unicode or type(col) is unicode):
                    val = unicode(col)
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
        rc = '''
<h1>{{page.error.txt_header}}</h1>
<p class="error">+++ {:s}</p>
'''         .format(message)
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
        selection = self.getField(field)
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
            
        self.defineFields()
        self._pageData.importData(self._name, fieldValues, cookies)
        self.afterInit()
        if self._redirect != None:
            rc = self._redirect
        else:
            self._pageData.correctCheckBoxes(fieldValues);
    
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
            title = self._session.getConfig(self._name + '.title')
            env = { 'CONTENT' : content, 
                'MENU' : htmlMenu,
                'META_DYNAMIC' : self._dynMeta,
                'STATIC_URL' : '',
                'DYNAMIC_URL' : '',
                '!title' : title
                }
            frame = self._session.replaceVars(frame, env)
            rc = PageResult(frame)
            
        self._pageData.putToCookie()
        globalPage = self._globalPage
        if globalPage != None:
            globalPage._pageData.putToCookie()
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
   
    def autoSplit(self, listAsString):
        '''Splits a string into a list with an automatic separator:
        @param listAsString: the list as string. The first char is the separator
        @return the list built from the string
        '''
        if listAsString == None or listAsString == "":
            raise PageException(self, "autosplit(''): too short")
        sep = listAsString[0]
        rc = listAsString[1:].split(sep)
        return rc
    
    def humanReadableSize(self, size):
        '''Builds a human readable size with max. 3 digits and a matching unit.
        @param size: the size in kByte (type: int)
        @return: a string with the size and unit, e.g. 213 MByte
        '''
        if size < 10*1000:
            size = '{:d}By'.format(size)
        elif size < 10*1000*1000:
            size = '{:d}KB'.format(size / 1000)
        elif size < 10*1000*1000*1000:
            size = '{:d}MB'.format(size / 1000 / 1000)
        else:
            size = '{:d}GB'.format(size / 1000 / 1000 / 1000)
        return size

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
        self._globalPage.putField("wait.intro.arg", argsIntro)
        self._globalPage.putField("wait.descr.key", keyDescr)
        if argsDescr != None:
            argsDescr = ";" + ";".join(argsDescr)
        self._globalPage.putField("wait.descr.arg", argsDescr)
        self._globalPage.putField("wait.file.stop", fileStop)
        self._globalPage.putField("wait.file.progress", fileProgress)
        self._globalPage.putField("wait.page", follower)
        self._globalPage.putField("wait.translation", translation)
        
        rc = self._session.redirect("wait", "gotoWait-" + self._name)
        return rc

    def execute(self, answer, options, command, params, timeout = 3600):
        '''Executes a command. Delegates to the object _session._shellClient
         @param answer:     the name of the answer file
         @param options:    the options for the shell server
         @param command:   the command to execute, e.g. SVOPT_DEFAULT
         @param params:   NULL or a string or an array of strings
         @param timeout:    the maximum count of seconds
         @return: true: answer file exists. false: timeout reached
        '''
        return self._session._shellClient.execute(answer, options, command, 
            params, timeout)

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
        pages = self._session.getConfigWithoutLanguage('.gui.pages')
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
        pages = self._session.getConfigWithoutLanguage('.gui.pages')
        pages = pages[1:].split(pages[0])
        ix = operator.indexOf(pages, page)
        if prev:
            rc = None if ix <= 0 else pages[ix - 1]
        else:
            rc = None if ix >= len(pages) - 1 else pages[ix + 1]
        return rc
      
