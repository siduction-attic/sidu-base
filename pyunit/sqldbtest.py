'''
Created on 13.03.2013

@author: hm
'''
import unittest
from util.sqldb import TableInfo, SqlDb
from aux import Aux


class TestSqlDb(unittest.TestCase):


    def setUp(self):
        self._tableInfo = TableInfo('person', 
            { 'id' : 'integer', 
             'name' : 'varchar(255)',
             'amount' : 'float', 
             'checked' : 'bool'})
        self._sql = SqlDb()
        self._sql.addTableInfo(self._tableInfo)

    def tearDown(self):
        pass


    def testTableInfo(self):
        info = self._tableInfo
        self.assertTrue(info.isNumber('id'))
        self.assertTrue(info.isNumber('amount'))
        self.assertFalse(info.isNumber('name'))
        self.assertFalse(info.isNumber('checked'))
        self.assertFalse(info.isBoolean('id'))
        self.assertFalse(info.isBoolean('amount'))
        self.assertFalse(info.isBoolean('name'))
        self.assertTrue(info.isBoolean('checked'))

    def testAddTableInfo(self):
        sql = self._sql
        info = TableInfo('keys', { 'key' : 'varchar(64)'})
        sql.addTableInfo(info)
        self.assertEquals(sql._tables['keys'], info)
      
    def testGetTableInfo(self):
        self.assertEquals(self._tableInfo, self._sql.getTableInfo('person'))
    
    def testBuildDropTable(self):
        # sql = 'drop table ' + tableInfo._tablename
        self.assertEquals('drop table person',
            self._sql.buildDropTable(self._tableInfo))
    
    def testBuildCreateTable(self):
        sql = self._sql.buildCreateTable(self._tableInfo)
        self.assertEquals(
            "create table person(amount float,checked bool,id integer,name varchar(255))",
            sql)
            
    def testBuildInsert(self):
        record = { 'id' : 1, 'name' : 'Miller', 'checked' : 1}
        sql, values = self._sql.buildInsert(record, self._tableInfo)
        self.assertEquals(
            "insert into person(checked,id,name)values(:1,:2,:3)",
            sql)
        self.assertEqual(1, values[0])
        self.assertEqual('Miller', values[2])
        self.assertEqual(1, values[1])
            
    def testBuildSelectByKey(self):
        sql = self._sql.buildSelectByKey(self._tableInfo, 'id', 99)
        self.assertEquals(
            "select * from person where id=99",
            sql)
    
    def testBuildSelectByValues(self):
        sql, values = self._sql.buildSelectByValues(self._tableInfo,
            (('id', 44), ('name', 'Jonny')))
        self.assertEquals(
            "select * from person where id=:1 and name=:2",
            sql)
        self.assertTrue(44, values[0])
        self.assertTrue('Jonny', values[1])

#if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()