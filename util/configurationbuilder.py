'''
Created on 27.02.2013

@author: hm
'''

import os.path, re
from xml.sax.saxutils import escape

from sqlitedb import SqLiteDb
from sqldb import TableInfo

from util import Util

class ConfigurationBuilder(object):
    '''
    Builds a configuration database and populates it with text files.
    '''


    def __init__(self, db = None):
        '''
        Constructor.
        @param db: the configuration DB
        '''
        self._confDb = db
     
    
    @staticmethod
    def getTableInfo():
        '''Returns the table info of the configuration.
        @return the table info
        '''
        tableInfo = TableInfo('configuration',
            { 'key' : 'varchar(255)', 
             'value' : 'text', 
             'language' : 'varchar(6)',
             'kind' : 'varchar(8)'
             })
        return tableInfo

    def buildSqLiteDb(self, dbName, filesAndLanguages):
        '''Builds a configuration database using textfiles.
        @param dbName: the database's filename with path
        @param filesAndLanguages: a list of tuples containing filename
                                and language
        '''
        if not os.path.exists(dbName) or os.path.getsize(dbName) == 0:
            db = SqLiteConfigurationDb(dbName, 
                ConfigurationBuilder.getTableInfo())
            db.buildConfig()
            self._confDb = db
            for pair in filesAndLanguages:
                self.addFile(pair[0], pair[1])
        
       
    def addFile(self, name, language = None):
        '''Appends the content of a file into the database.
        @param name: the filename (with path)
        @param language: the language of the content
        '''
        record = { 'key' : None,
                'value' : None,
                'kind' : None,
                'language' : language }
        db = self._confDb._db
        tableInfo = db.getTableInfo('configuration')
        self._tableInfo = tableInfo
        parser = re.compile(r'^([a-zA-Z.][a-zA-Z0-9_.]*)%?=([<]xml[>])?(.*)')
        with open(name, "r") as fp:
            for line in fp:
                matcher = parser.match(line)
                if matcher:
                    kind = matcher.group(2)
                    kind = 'text' if kind == None else 'xml'
                    record['kind'] = kind
                    record['key'] = matcher.group(1)
                    value = matcher.group(3)
                    record['value'] = value if kind == 'text' else escape(value)
                    db.insert(record, tableInfo)  
        fp.close()
        db.flush()
    
    def addDirectory(self, directory, prefix, suffix):
        '''Adds all configuration files from a directory.
        @param directory: the directory to search
        @param prefix: the configuration files must start with this prefix
        @param suffix: the configuration files must end with this suffix
        '''
        files = os.listdir(directory)
        if not directory.endswith(os.sep):
            directory += os.sep
        rexpr = re.compile(r'_([a-zA-Z]{2}(-[a-zA-Z]{2})?)[.]')
        for node in files:
            if node.startswith(prefix) and node.endswith(suffix):
                language = None
                matcher = rexpr.search(node)
                if matcher != None:
                    language = matcher.group(1) 
                self.addFile(directory + node, language)
                          
    def getValue(self, key, language = None):
        '''Gets a value from the configuraton database.
        @param key: the key of the (key, value) pair
        @param language: None or the language
        @return: None: not found.<br>
                otherwise: the configuration value
        '''
        db = self._confDb._db
        if language == None:
            value = db.selectByKey(self._tableInfo, 'key', key, )
        else:
            values = (('key', key), ('language', language))
            value = db.selectByValues(self._confDb._tableInfo, values)
        return value

class SqLiteConfigurationDb:
    '''Administrates a SQLite configuration database.
    '''
    
    def __init__(self, name):
        '''Constructor.
        @param name: name of the database with path
        '''
        self._tableInfo = ConfigurationBuilder.getTableInfo()
        self._db = SqLiteDb(name)
        self._db.addTableInfo(self._tableInfo)
        
    def buildConfig(self):
        '''Builds a configuration database.
        '''
        self._db.createTable(self._tableInfo)
    
    def getDb(self):
        '''Returns the database.
        @return: the database
        '''
        return self._db
                