'''
Created on 22.03.2013

@author: hm
'''

from util.sqlitedb import ResultSet

class ConfigChecker:
    '''
    Checks the consisty of the configuration database.
    '''


    def __init__(self, session):
        '''
        Constructor.
        '''
        self._session = session
        
    def checkConfigOfAPair(self, lang1, lang2, separator):
        '''Checks whether each key of lang1 has an  key of lang2
        @param lang1:  first language
        @param lang2:  second language
        @param separator: the separator between the missed keys
        '''
        db = self._session._configDb
        sql = 'select key from configuration where language=:1 order by key'
        rs = ResultSet(db, sql, [lang1])
        missing = None
        while True:
            key = rs.next()
            if key == None:
                break
            value = key['key']
            if self._session.getConfigOrNone(value, lang2) == None:
                if missing == None:
                    missing = value
                else:
                    missing += separator + value
        return missing
            
    def checkConfig(self, language, template, separator):
        '''Checks whether each key of the language has an English key
        and vice versa.
        @param language: language to test
        @param template: a HTML code with placeholder {{message}}
        @param separator: the separator between the missed keys
        '''
        # Does each language key have an English version?
        missing = self.checkConfigOfAPair(language, 'en', separator)
        msg = None
        if missing != None:
            msg = template.replace('{{message}}', 
                self._session.getConfig('.error.config.keys.superflous') 
                    + missing)
        # Does each language key have an English version?
        missing = self.checkConfigOfAPair('en', language, '<br>\n')
        if missing != None:
            if msg == None:
                msg = ''
            msg += template.replace('{{message}}',
               self._session.getConfig('.error.config.keys.missing') + missing)                      
        return msg
        
        
        