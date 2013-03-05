'''
Created on 31.01.2013

@author: hm
'''
from sqldb import SqlDb
import sqlite3, logging

class SqLiteDb(SqlDb):
    def __init__(self, filename):
        '''Constructor.
        @param filename: the full path of the SqLite database
        '''
        SqlDb.__init__(self)
        self._dbName = filename
        self._conn = None
        self._cursor = None
        self._insertCount = 0
        self._maxCommit = 50
 
    def dropTable(self, tableInfo):
        '''Deletes a table from the database.
        @param tableInfo: the info about the table to delete
        '''
        try:
            sql = self.buildDropTable(tableInfo)
            cursor = self.getCursor()
            cursor.execute(sql)
        except Exception, e:
            logging.error('dropTable: ' + repr(e))
            raise(e)
         
    def createTable(self, tableInfo):
        '''Creates a table.
        @param tableInfo: the description of the table
        '''
        try:
            sql = self.buildCreateTable(tableInfo)
            cursor = self.getCursor()
            cursor.execute(sql)
        except Exception, e:
            logging.error('createTable: ' + repr(e))
            raise(e)
            
        
    def createTables(self):
        '''Creates the tables defined in self._tables
        '''
        for info in self._tables.itervalues():
            self.createTable(info)
        
    def getCursor(self):
        '''Returns the cached cursor.
        @return the current db cursor
        '''
        if self._conn is None:
            self._conn = sqlite3.connect(self._dbName)

        if self._cursor is None:
            self._cursor = self._conn.cursor()
        return self._cursor
        
    def commit(self, force = False):
        'Performs a commit.'
        self._insertCount += 1
        if (self._conn != None
            and (force or self._insertCount % self._maxCommit == 0)):
            self._conn.commit()
 
    def close(self):
        'Frees the resources.'
        if self._conn != None:
            self.commit(True)
        if self._cursor != None:
            self._cursor.close()
            self._cursor = None
        if self._conn != None:
            self._conn.close()
            self._conn = None

    def flush(self):
        '''Writes the current state to the database file.
        '''
        self.commit(True)
        self.close()
        
    def insert(self, record, tableInfo):
        '''Inserts a record into the database.
        @param record: a dictionary with column : value
        @param tableInfo: the info of the table where the insert will be done
                            or the table name (if it is a string)
        '''
        (sql, values) = self.buildInsert(record, tableInfo)
        cursor = self.getCursor()
        try:
            cursor.execute(sql, values)
            self.commit()
        except Exception as e:
            logging.error('insert(%s): %s' % (tableInfo._tablename, repr(e)))
            raise(e)

    def selectByKey(self, tableInfo, key, value, mustExist = True):
        '''Selects a record from a table.
        @param tableInfo: the table' info
        @param key: the name of the column for searching
        @param value: the value of the record to find
        @return: None: not found<br>
               a dictionary of the found record (column : value)
        '''
        record = None
        try:
            sql = self.buildSelectByKey(tableInfo, key, value)
            cursor = self.getCursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            if row == None:
                record = None
            else:
                record = {}
                for ii in xrange(len(row)):
                    key = cursor.description[ii][0]
                    record[key] = row[ii];
        except Exception, e:
            if mustExist:
                logging.error('selectByKey(%s, %s): %s' % (tableInfo._tablename, 
                    repr(value), repr(e)))
                raise(e)
            
        return record
       
    def selectByValues(self, tableInfo, values, mustExist=True):
        '''Finds a value given by some (key, value) pairs.
        @param tableInfo: the table' info
        @param values:  a sequence of (key, value) pairs 
        @param mustExist: True: the record must be found<br>
                            False: the record must not exist
        @return None: not found<br>
                otherwise: the wanted record
        '''
        record = None
        try:
            (sql, vals) = self.buildSelectByValues(tableInfo, values)
            cursor = self.getCursor()
            cursor.execute(sql, vals)
            row = cursor.fetchone()
            if row == None:
                record = None
            else:
                record = {}
                for ii in xrange(len(row)):
                    key = cursor.description[ii][0]
                    record[key] = row[ii];
        except Exception, e:
            if mustExist:
                logging.error('selectByValues(%s, %s): %s' % (tableInfo._tablename, 
                    repr(values), repr(e)))
                raise(e)
            
        return record
