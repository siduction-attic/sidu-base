#!/usr/local/bin/python2.7
# encoding: utf-8
'''
config_import -- importing the configuration

config_import reads a text file and put the information into the database

@author:     hamatoma
        
@copyright:  2013 Hamatoma
        
@license:    GPL

@contact:    hama@siduction.net
'''

import sys, os, re, time

from sqlitedb import SqLiteDb
from sqldb import TableInfo
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2013.01.01'
__updated__ = '2013.01.30'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

        
         

class Import:
    def __init__(self, dbName):
        '''Constructor.
        @param filename: the text file containing the configuration info
        @param language: the language of the text file, e.g. 'de-CH'
        @param dbName: thei import will be done into this database
        ''' 
        self._dbName = dbName
        self._db = SqLiteDb(dbName)
        columns = { 'id' : 'integer NOT NULL PRIMARY KEY', 
            'key' : 'varchar(64) NOT NULL', 
            'value' : 'text NOT NULL', 
            'kind' : 'varchar(8) NOT NULL', 
            'language' : 'varchar(8)' }
        tablename = 'config_config'
        self._configInfo = TableInfo(tablename, columns)
        if not os.path.exists(dbName):
            self.createTables()
    
    def createTables(self):
        '''Creates the tables for the db.
        '''
        self._db.createTable(self._configInfo)
        
    def dropTables(self):
        '''Drops the database table config_config
        '''  
        self._db.dropTable(self._configInfo)
            
    def getLanguage(self, filename):
        '''Extracts the language from a file name.
        @param filename: the filename to inspect
        @return: None: no language found<br>
                otherwise: the ISO code of the language
        '''
        parser = re.compile(r'_([A-Za-z]{2})([-_]([a-zA-Z]{2}))?[.][^.]+$')
        matcher = parser.search(filename)
        rc = None
        if matcher:
            rc = matcher.group(1).lower()
            if (matcher.group(2)):
                rc += '-' +  matcher.group(3).lower()
        return rc
        
    def read(self, filename, language = None):
        '''Reads the textfile and imports the info into the DB.
        '''
        if language == None:
            language = self.getLanguage(filename)
        if language == 'en':
            language = None
        self._db.getCursor()
        parser = re.compile(r'^([a-zA-Z.][a-zA-Z0-9_.]*)%?=([<]xml[>])?(.*)')
        self._db.addTableInfo(self._configInfo)
        with open(filename, "r") as fp:
            for line in fp:
                matcher = parser.match(line)
                if matcher:
                    kind = matcher.group(2)
                    kind = 'text' if kind == None else 'xml'
                    record = { 'key' : matcher.group(1), 'kind' :  kind,
                              'value' : matcher.group(3), 'language' : language}
                    self._db.insert(record, self._configInfo)  
        fp.close()
        self._db.commit(True)    
          
class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg


def main(argv=None): # IGNORE:C0111
    '''Command line options.
    '''
    start = time.time()
    if argv is None:
        argv = sys.argv

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
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('dbName', help='the database file name (full path)')
        parser.add_argument('textfile', nargs='+', help='the textfile containing the configuration variables')
        # Process arguments
        args = parser.parse_args(argv)
        
        if not os.path.exists(args.textfile[0]):
            return help("+++ textfile does not exist: " + args.textfile, parser)
        
        exists = os.path.exists(args.dbName)
        importer = Import(args.dbName)
        if exists and args.dropTables:
            if os.path.getsize(args.dbName) > 0:
                importer.dropTables()
            importer.createTables()
        
        for textfile in args.textfile:
            if not os.path.exists(textfile):
                print "not a file (ignored): \n"
            else:
                importer.read(textfile)
            
        if args.verbose:
            print "runtime: " + str(time.time() - start) + "\n"  
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
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