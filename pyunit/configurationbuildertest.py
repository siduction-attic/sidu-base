'''
Created on 27.02.2013

@author: hm
'''
import unittest, os.path
from util.configurationbuilder import ConfigurationBuilder
from util.configurationbuilder import SqLiteConfigurationDb, main
from util.util import Util

class Test(unittest.TestCase):

    def setUp(self):
        self._subdir = Util.getTempDir('sidu-base')
        self._dbName = Util.getTempFile('config.db', 'sidu-base')
        self._configFile = Util.getTempFile('test.conf', 'sidu-base')
        self._configFileDe = Util.getTempFile('test_de.conf', 'sidu-base')
        self._configFileEn = Util.getTempFile('test_en.conf', 'sidu-base')
        
        if not os.path.exists(self._configFile):
            Util.writeFile(self._configFile, '''
# Test config file
test.language=de
data.string.long=123456789 123456789 123456789 123456789 123456789 123456789
data.int=34777
data.bool=True
'''
                )
        if not os.path.exists(self._configFileDe):
            Util.writeFile(self._configFileDe, '''
# Test config file for German
title=Modultest
'''
                )
        if not os.path.exists(self._configFileEn):
            Util.writeFile(self._configFileEn, '''
# Test config file for German
title=Module Test
'''
                )
        
    def test0SqLite(self):
        dbName = self._dbName
        if os.path.exists(dbName):
            os.unlink(dbName)
        db = SqLiteConfigurationDb(dbName)
        db.buildConfig()
        self.assertTrue(os.path.exists(dbName))
        self.assertTrue(db.getDb() != None)
        
    def testGetLanguage(self):
        config = ConfigurationBuilder()
        self.assertEqual('de', config.getLanguage('abc_de.conf'))
        self.assertEqual('de', config.getLanguage('ABC_DE.CONF'))
        self.assertEqual('pt-br', config.getLanguage('abc_pt-BR.conf'))
        self.assertEqual(None, config.getLanguage('abc_de.x/y.conf'))
        
    def test1Config(self):
        db = SqLiteConfigurationDb(self._dbName)
        config = ConfigurationBuilder(db)
        config.addFile(self._configFile)
        config.addFile(self._configFileDe, 'de')
        config.addFile(self._configFileEn, 'en')
        self.assertEquals('Modultest', config.getValue('title', 'de')['value'])
        self.assertEquals('de', config.getValue('test.language')['value'])
        self.assertEquals('123456789 123456789 123456789 123456789 123456789 123456789', 
            config.getValue('data.string.long')['value'])
        self.assertEquals('Module Test', config.getValue('title', 'en')['value'])
        
    def test2addDirectory(self):
        dbName = self._dbName
        if os.path.exists(dbName):
            os.unlink(dbName)
        db = SqLiteConfigurationDb(dbName)
        db.buildConfig()
        config = ConfigurationBuilder(db)
        config.addDirectory(self._subdir, 'test', '.conf');
        self.assertEquals('Modultest', config.getValue('title', 'de')['value'])
        self.assertEquals('de', config.getValue('test.language')['value'])
        self.assertEquals('123456789 123456789 123456789 123456789 123456789 123456789', 
            config.getValue('data.string.long')['value'])
        self.assertEquals('Module Test', config.getValue('title', 'en')['value'])
       
    def testMain(self):
        dbName = Util.getTempFile('dummy.db', 'conftest')
        if os.path.exists(dbName):
            os.unlink(dbName)
        textFile = Util.getTempFile('dummy_de.conf', 'conftest')
        Util.writeFile(textFile, '''
myKey.first=abcde
'''         )
        args = ["--drop-tables", 
            "--create-tables",
            "--prefix=NeverEver",
            "--suffix=.never",
            "--verbose",
            "--summary",
            dbName,
            textFile]
        main(args)
        self.assertTrue(os.path.exists(dbName))
        
    def testMain2(self):
        dbName = Util.getTempFile('dummy.db', 'conftest')
        if os.path.exists(dbName):
            os.unlink(dbName)
        textFile = Util.getTempFile('dummy_de.conf', 'conftest')
        Util.writeFile(textFile, '''
myKey.first=abcde
'''         )
        args = ["-d", 
            "-c",
            "-p", "dummy",
            "--suffix=.conf",
            "-v",
            "-y",
            dbName,
            textFile]
        main(args)
        self.assertTrue(os.path.exists(dbName))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()