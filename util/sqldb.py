'''
Created on 31.01.2013

@author: hm
'''

class TableInfo:
    ''' Implements an info about a table.
    '''
    def __init__(self, tablename, columns):
        '''Constructor.
        @param tablename: the table's name
        @param columns: a dictionary colName : dataType
        '''
        self._tablename = tablename
        self._columns = columns
    
    def isNumber(self, colName):
        '''Tests whether a column is numeric.
        @param colName: the column's name to test
        @return: True: the column is numeric<br>
                False: otherwise
        '''
        aType = self._columns[colName]
        rc = aType.startswith('int') or aType.startswith('float')
        return rc

    def isBoolean(self, colName):
        '''Tests whether a column is boolean.
        @param colName: the column's name to test
        @return: True: the column is boolean<br>
                False: otherwise
        '''
        aType = self._columns[colName]
        rc = aType.startswith('bool')
        return rc

class SqlDb:
    '''Represents a base class for all SQL databases.
    '''
    def __init__(self):
        '''Constructor
        '''
        self._tables = {}
        
    def addTableInfo(self, tableInfo):
        '''Adds a table info to the database.
        @param tableInfo: an info about the columns of a table
        '''
        self._tables[tableInfo._tablename] = tableInfo
        if tableInfo._tablename != 'configuration':
            pass
      
    def getTableInfo(self, tablename):
        '''Returns the table info given by a table name
        @param tablename: the table's name
        @return: the table info
        '''
        return self._tables[tablename]
    
    def buildDropTable(self, tableInfo):
        '''Builds a SQL statement for deleting a table.
        @param tableInfo: the info about the table to delete
        '''
        sql = 'drop table ' + tableInfo._tablename
        return sql
    
    def buildCreateTable(self, tableInfo):
        '''Builds a SQL statement for creating a table.
        @param tableInfo: the description of the table
        @return: the SQL statement
        '''
        sql = 'create table ' + tableInfo._tablename
        sep = '('
        
        for column in tableInfo._columns.iterkeys():
            sql += sep + column + ' ' + tableInfo._columns[column]
            sep = ','
        sql += ')'
        return sql
            
    def buildInsert(self, record, tableInfo):
        '''Builds a SQL statement for inserting a record.
        @param record: a dictionary colName : value
        @param tableInfo: the table's info or the table's name
        @return a tuple (sql, values)
        '''
        sql = 'insert into ' + tableInfo._tablename;
        sep = '('
        for item in record.iterkeys():
            if record[item] != None:
                sql += sep + item
                sep = ','
        sql += ')values'
        sep = '('
        values = []
        argNo = 1
        for key in record.iterkeys():
            value = record[key]
            if record[key] != None:
                if tableInfo.isBoolean(key):
                    value = 1 if value else 0
                values.append(value)
                sql += sep + ':' + unicode(argNo)
                argNo += 1
                sep = ','
        sql += ')'
        return (sql, values)
    
    def buildSelectByKey(self, tableInfo, key, value):
        '''Builds a SQL statement for searching a record from a table.
        @param tableInfo: the table's info
        @param key: the name of the column for searching
        @param value: the value of the record to find
        @return: the sql statement
        '''
        if not tableInfo.isNumber(key):
            value = "'" + value + "'"
        sql = 'select * from ' + tableInfo._tablename + ' where ' + key + '=' + unicode(value)
        return sql
    
    def buildSelectByValues(self, tableInfo, pairs):
        '''Builds a SQL statement for searching a record from a table.
        @param tableInfo: the table's info
        @param pairs: a sequence of (key, value) pairs 
        @return a tuple (sql, values)
        '''
        sql = 'select * from ' + tableInfo._tablename;
        sep = ' where '
        no = 0
        vals = []
        for pair in pairs:
            no += 1
            sql += sep + pair[0] + '=:' + unicode(no)
            #sql += sep + pair[0] + '=?'
            sep= ' and '
            vals.append(pair[1])
        return (sql, vals)
        