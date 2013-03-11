'''
Created on 27.02.2013

@author: hm
'''

import os.path, re, time, sys, codecs
from xml.sax.saxutils import escape

from sqlitedb import SqLiteDb
from sqldb import TableInfo

from util import Util, say, sayError

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.2
__date__ = '2013.03.06'
__updated__ = '2013.03.11'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

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
        self._rexpr = None
     
    
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
            db = SqLiteConfigurationDb(dbName)
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
        with codecs.open(name, "r", "UTF-8") as fp:
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
    
    def getLanguage(self, node):
        '''Gets the language from a filename.
        @param node: the filename to inspect
        @return None: no language found.<br>
                otherwise: the language
        '''
        if self._rexpr == None:
            self._rexpr = re.compile(r'_([a-zA-Z]{2}(-[a-zA-Z]{2})?)[.][^.]+$')
        rc = None
        matcher = self._rexpr.search(node)
        if matcher != None:
            rc = matcher.group(1).lower()
        return rc
 
    def addDirectory(self, directory, prefix, suffix):
        '''Adds all configuration files from a directory.
        @param directory: the directory to search
        @param prefix: the configuration files must start with this prefix
        @param suffix: the configuration files must end with this suffix
        '''
        files = os.listdir(directory)
        if not directory.endswith(os.sep):
            directory += os.sep
        
        for node in files:
            if node.startswith(prefix) and node.endswith(suffix):
                language = self.getLanguage(node)
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
 
def showSummary(db):
    sql = 'select language, count(*) from configuration group by language'
    cursor = db.getCursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows == None or len(rows) == 0:
        say("No records found")
    else:
        for row in rows:
            say("{:5s}: {:3d}".format(row[0], row[1]))
    
        
def main(argv=None): # IGNORE:C0111
    '''Command line options.
    '''
    start = time.time()
    if argv is None:
        argv = sys.argv[1:]

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    doc = __import__('__main__').__doc__
    program_shortdesc = doc.split("\n")[1] if doc else "Imports the configuration database"
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2013 organization_name. All rights reserved.
  
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0
  
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))
    program_usage = 'configimport.py [<options>] textfile dbfile'
    program_epilog = '''Example:
configimport.py --drop-tables -v config/sidu-base_de-ch.conf db/sqlite3.db
'''
    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter, 
            usage=program_usage, epilog=program_epilog)
        parser.add_argument("-d", "--drop-tables", dest="dropTables", action="store_true", help="drop tables before import [default: %(default)s]")
        parser.add_argument("-c", "--create-tables", dest="createTables", action="store_true", help="create tables before import [default: %(default)s]")
        parser.add_argument("-p", "--prefix", dest="prefix", default="", help="prefix of the configuration files")
        parser.add_argument("-s", "--suffix", dest="suffix", default=".conf", help="suffix of the configuration files")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument("-y", "--summary", dest="summary", action="store_true", help="shows the record count grouped by language [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('dbName', help='the database file name (full path)')
        parser.add_argument('textfile', nargs='+', help='the textfile containing the configuration variables')
        # Process arguments
        args = parser.parse_args(argv)
        
        if not os.path.exists(args.textfile[0]):
            return help("+++ textfile does not exist: " + args.textfile, parser)
        
        exists = os.path.exists(args.dbName)
        configDb = SqLiteConfigurationDb(args.dbName)
        db = configDb.getDb()
        
        builder = ConfigurationBuilder(configDb)
        if exists and args.dropTables:
            if os.path.getsize(args.dbName) > 0:
                if args.verbose:
                    say("deleting table(s)...")
                db.dropTable(builder.getTableInfo())
        if (not exists or args.dropTables or args.createTables 
                or os.path.getsize(args.dbName) == 0):
            if args.verbose:
                say("creating table(s)...")
            db.createTable(builder.getTableInfo())
        
        for path in args.textfile:
            if not os.path.exists(path):
                sayError("not a file (ignored):")
            elif os.path.isdir(path):
                builder.addDirectory(path, args.prefix, args.suffix)
            else:
                builder.addFile(path, builder.getLanguage(path))
            
        if args.summary:
            showSummary(db)
        if args.verbose:
            say("runtime: " + str(time.time() - start))  
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sayError(program_name + ": " + repr(e))
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'config.import_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())           