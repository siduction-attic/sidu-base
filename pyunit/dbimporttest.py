'''
Created on 30.01.2013

@author: hm
'''
from django.test import TestCase
import os.path, logging

from util.sqlitedb import SqLiteDb
from util.sqldb import SqlDb, TableInfo
from util.configimport import Import, main

class Test(TestCase):

    # Will be called before each test routine
    def setUp(self):
        pass


    # Will be called after  each test routine
    def tearDown(self):
        pass


    def _getStdTableName(self):
        return 'user'
    
    def _getStdColumns(self):
        return  { 'name' : 'varchar(128) NOT NULL', 'id' : 'integer NOT NULL PRIMARY KEY', 
            'isadmin' : 'bool NOT NULL'}
    
    def _getStdTableInfo(self):
        tableInfo = TableInfo(self._getStdTableName(), 
            self._getStdColumns())
        return tableInfo
    
    def testTableInfo(self):
        info = self._getStdTableInfo()
        self.assertEquals(False, info.isBoolean('name'))
        self.assertEquals(False, info.isBoolean('id'))
        self.assertEquals(True, info.isBoolean('isadmin'))
        
        self.assertEquals(False, info.isNumber('name'))
        self.assertEquals(True, info.isNumber('id'))
        self.assertEquals(False, info.isNumber('isadmin'))
      
    def testSqlDb(self):
        db = SqlDb()
        tablename = self._getStdTableName()
        tableInfo = self._getStdTableInfo()
        db.addTableInfo(tableInfo)
        info = db.getTableInfo(tablename)
        self.assertEquals(True, info.isNumber('id'))
        record = { 'name' : 'jonny', 'id' : 1, 'isadmin' : True}
        
        (sql, values) = db.buildInsert(record, tableInfo)
        self.assertEqual(sql, 'insert into ' + tablename + '(isadmin,name,id)values(:1,:2,:3)')
        self.assertEqual([1, 'jonny', 1], values)
        
        self.assertEquals('create table ' + tablename 
                + '(isadmin bool NOT NULL,name varchar(128) NOT NULL,id integer NOT NULL PRIMARY KEY)', 
            db.buildCreateTable(tableInfo))
        
        self.assertEquals('select * from ' + tablename + ' where id=1',
            db.buildSelectByKey(tableInfo, 'id', 1))
        self.assertEquals('select * from ' + tablename + " where name='jonny'",
            db.buildSelectByKey(tableInfo, 'name', 'jonny'))
        self.assertEquals('drop table ' + tablename,
            db.buildDropTable(tableInfo))
        
        
    def testSqLiteDb(self):
        fn = '/tmp/dbimport_test.db'
        if os.path.exists(fn):
            os.remove(fn)
        db = SqLiteDb(fn)
        tableInfo = self._getStdTableInfo()
        db.addTableInfo(tableInfo)
        db.createTables()
        record = { 'id' : 4711, 'name' : 'eve', 'isadmin' : False }
        db.insert(record, tableInfo)
        db.commit(True)
        record2 = db.selectByKey(tableInfo, 'id', 4711)
        self.assertEquals(record, record2)
        
        record2 = db.selectByValues(tableInfo, (('name', 'eve'), ('id', 4711)))
        self.assertEquals(record, record2)
        
        record2 = db.selectByValues(tableInfo, (('name', 'wrong'), ('id', 4711)), False)
        self.assertEquals(None, record2)

        try:
            logging.warning('ignore the following error message')
            db.selectByValues(tableInfo, (('name', 'wrong'), ('xxx', 0)))
            self.fail("missing exception!")
        except Exception:
            pass
        
        db.dropTable(tableInfo)
        try:
            logging.warning('next error message is expected because of dropTable():')
            db.selectByKey(tableInfo, 'id', 4711)
            self.fail("drop user failed!")
        except Exception:
            pass
         
        db.close()
        
        
    def _checkRecord(self, no, key, value, language, kind, record):
        self.assertIsNotNone(record)
        self.assertEquals(no, record['id'])
        self.assertEquals(key, record['key'])
        self.assertEquals(value, record['value'])
        self.assertEquals(language, record['language'])
        self.assertEquals(kind, record['kind'])
        
    def testImport(self):
        fnDb = '/tmp/dbimport_test2.db'
        fnText = '/tmp/dbimport_test_de-CH.conf'
        if os.path.exists(fnDb):
            os.remove(fnDb)
        fp = open(fnText, "w")
        fp.write('''
# comment
name=adam
.id=2

sample.txt_intro1%=<xml><h1>Hi</h1>
        ''')
        fp.close()
        drop = os.path.exists(fnDb)
        importer = Import(fnDb)
        if drop:
            importer.dropTables()
        importer.read(fnText)
        tableInfo = importer._configInfo
        db = importer._db
        record = db.selectByKey(tableInfo, 'id', 1)
        self._checkRecord(1, 'name', 'adam', 'de-ch', 'text', record)
        record = db.selectByKey(tableInfo, 'id', 2)
        self._checkRecord(2, '.id', '2', 'de-ch', 'text', record)
        record = db.selectByKey(tableInfo, 'id', 3)
        self._checkRecord(3, 'sample.txt_intro1', '<h1>Hi</h1>', 'de-ch', 'xml', record)
        
        self.assertEquals(None, importer.getLanguage('abc_de'))
        self.assertEquals(None, importer.getLanguage('abc_d1-ab.txt'))
        self.assertEquals(None, importer.getLanguage('abc_dee-ab.txt'))
        self.assertEquals(None, importer.getLanguage('abc_de-abc.txt'))
        self.assertEquals('de', importer.getLanguage('/abc.en-US.lang/abc_de.conf'))
        self.assertEquals('de-ch', importer.getLanguage('abc_de_ch.conf'))
        self.assertEquals('de-ch', importer.getLanguage('abc_de-ch.conf'))
        self.assertEquals('de-ch', importer.getLanguage('abc_De_Ch.conf'))
        db.close()
        main(['--drop-tables', '-v', fnDb, fnText])
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    # unittest.main()
    pass