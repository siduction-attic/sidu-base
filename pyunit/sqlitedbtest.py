'''
Created on 13.03.2013

@author: hm
'''
import unittest, os
from util.util import Util, say
from util.sqldb import TableInfo
from util.sqlitedb import SqLiteDb


class TestSqListeDb(unittest.TestCase):


    def setUp(self):
        self._dir = Util.getTempDir('test', True)
        self._dbName = self._dir + 'test01.db'
        self._tableInfo = TableInfo('person', 
            { 'id' : 'integer', 
             'name' : 'varchar(255)',
             'amount' : 'float', 
             'checked' : 'bool'})
        self._tableInfoError = TableInfo('unknownTable', 
            { 'id' : 'integer'})
        self._tableInfoSyntaxError = TableInfo('unknownTable', 
            { '~id' : 'integer'})
        self._db = SqLiteDb(self._dbName)
        self._db.addTableInfo(self._tableInfo)

    def tearDown(self):
        pass


    def test01Basic(self):
        os.unlink(self._dbName)
        self.setUp()
        self.assertTrue(None != self._db.getCursor())
 
    def test10CreateTableError(self):
        tableInfo = TableInfo('~wrongtable', 
            { 'id' : 'notexistingtype' })
        try:
            say('SQL error to enforce an exception...')
            self._db.createTable(tableInfo)
            self.fail('wrong sql statement')
        except AssertionError as e1:
            raise e1
        except:
            pass 
            
        
    def test15CreateTables(self):
        db = self._db
        db.createTables()
        
    def test20Commit(self):
        db = self._db
        db.commit(False)
        db.commit(True)
 
    def test30Flush(self):
        self._db.flush()
        
    def test35Insert(self):
        record = { 'id' : 1, 'name' : 'Miller'}
        self._db.insert(record, self._tableInfo)
        try:
            self._db.insert(record, self._tableInfoError)
            self.fail('insert with unknown table')
        except AssertionError as e1:
            raise e1
        except:
            self._db.flush()

    def test36InsertError(self):
        record = { '~id' : 1, 'name' : 'Miller'}
        try:
            say('insert with wrong syntax enforces an exception...')
            self._db.insert(record, self._tableInfoSyntaxError)
            self.fail('insert with wrong syntax')
        except AssertionError as e1:
            raise e1
        except:
            pass

    def test40SelectByKey(self):
        rec = self._db.selectByKey(self._tableInfo, 'id', 1)
        self.assertTrue(rec != None)
        self.assertEquals(1, rec['id'])
        self.assertEquals('Miller', rec['name'])
        
        self.assertEquals(None, self._db.selectByKey(self._tableInfo, 'id', -99))
    
    def test41SelectByKeyError(self):
        try:
            say('select with wrong syntax enforces an exception...')
            self._db.selectByKey(self._tableInfoSyntaxError, '~id', 1)
            self.fail('select with wrong syntax')
        except AssertionError as e1:
            raise e1
        except:
            pass
        
       
    def test45SelectByValues(self):
        rec = self._db.selectByValues(self._tableInfo, 
            (('id', 1), ('name', 'Miller')))
        self.assertTrue(rec != None)
        self.assertEquals(1, rec['id'])
        self.assertEquals('Miller', rec['name'])

    def test46SelectByValuesError(self):
        try:
            say('select with wrong syntax enforces an exception...')
            self._db.selectByValues(self._tableInfoSyntaxError, 
                (('~id', 1), ('name', 'Miller')))
            self.fail('select with wrong syntax')
        except AssertionError as e1:
            raise e1
        except:
            pass

    def test50Close(self):
        self._db.close()
        self.assertTrue(self._db._cursor == None)
    
    def test55DropTable(self):
        try:
            self._db.dropTable(self._tableInfoError)
            self.fail('not exception on a unknown table')
        except AssertionError as e1:
            raise e1
        except:
            pass
        self._db.dropTable(self._tableInfo)
        try:
            say('Select of a dropped table:')
            self._db.selectByKey(self._tableInfo, 'id', 99, True)
            self.fail('droptable failed')
        except AssertionError as e1:
            raise e1
        except:
            pass
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()