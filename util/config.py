import logging, os.path
import codecs

class Config:
    '''Maintenances a dictionary read from file(s).'
    The format of the file:<br>
    CONFIG ::= LINE*<br>
    LINE ::= INCLUDE | ASSIGNMENT | COMMENT<br>
    INCLUDE ::= 'include' FILE<br>
    ASSIGNMENT ::= VARIABLE '=' VALUE<br>

    Example:<br>
    # Configuration for evironment variables
    include "/etc/global_var.conf"
    global.basedir=/etc
    '''
    def __init__(self, filename = None):
        '''Constructor.
        @param filename: the configuration file
        '''
        self._dict = {}
        self._files = []
        if filename != None:
            self.read(filename)

    def read(self, filename):
        '''Reads a configuration file.
        @param filename: the configuration file
        '''
        fp = codecs.open(filename, "r", "UTF-8")
        lineNo = 0
        for line in fp:
            line = line.rstrip()
            lineNo += 1
            if line == '':
                pass
            elif not line.startswith('include'):
                first = line[0]
                if first.isalpha() or first == '.':
                    ix = line.find('=')
                    if ix > 0:
                        self._dict[line[0:ix]] = line[ix+1:]
            else:
                name = line[7:].strip(" \t\"'")
                if name not in self._files:
                    self._files.append(name) 
                    if os.path.exists(name):
                        self.read(name)
                    else:
                        logging.error(filename + '-' + str(lineNo) 
                            + ': can not include: ' + name)
        fp.close()
        
    def get(self, key):
        '''Returns a configuration value.
        @param key: the key of the value
        @return None: invalid key<br>
                otherwise: the value belonging to the key
        '''
        return self._dict[key] if key in self._dict else None 
        