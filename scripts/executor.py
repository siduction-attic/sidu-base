'''
Created on 19.03.2014

@author: hm
'''

import os.path, random

LOG_PREFIX_IMPORTANT = "=== ";
LOG_PREFIX = "";
STDOUT_PREFIX_IMPORTANT = "";
PREFIX_ERROR = "+++";

class Executor:
    '''Executes and logs sytem commands.
    '''
    def __init__(self, fnProgress, testRun):
        self._fnProgress = fnProgress
        self._testRun = testRun
        self._execLines = []
        self._logLines = []
        self._logStdOut = True
        self._logList = True
        self._execList = True
        self._countErrors = 0
        self._currentTask = 0
        self._maxTask = 5

    def getVars(self):
        '''
        Returns the important static variables.
        @return: (<refExecLines>, <reflogLines>)
        ''' 
        return (self._execLines, self._logLines)

    def execute(self, command, important):
        '''
        Executes a command.
        @param cmd:          the command to execute
        @param important:    true: the logging will be prefixed
        '''
        if self._execList:
            self._execLines.append(command)
        if not self._testRun:
            self.log(command, important)
            os.system(command)

    def log(self, msg, important = False):
        '''
        Logs a message.
        @param msg:          message
        @param important:    true: a prefix will be added
        '''
        if type(msg) == list:
            sep = "\n" if not msg[0].endswith("\n") else ""
            msg = sep.join(msg)
        if important:
            msg = LOG_PREFIX_IMPORTANT + msg
        if self._logStdOut:
            print(msg)
        if self._logList:
            self._logLines.append(msg + "\n")    

    def error(self, msg):
        '''
        Handles an error message.
        @param msg:    error message
        '''
        self.log("===+++ " + msg)
        self._countErrors += 1

    def getErrorCount(self):
        '''
        Return the number of errors.
        @return:   the count of calls of the subroutine error()
        '''
        return self._countErrors
        
    def progress(self, task, isLast):
        '''
        Writes the progress file.
        @param task:      name of the current task
        @param isLast:    the step is the last step
        '''
        task += " ..."
        self._currentTask += 1
        if isLast:
            self._maxTask = self._currentTask
        if self._currentTask >= self._maxTask:
            self._currentTask = self._currentTask + 5

        temp = self._fnProgress + ".tmp"
        fp = open(temp, "w")
        percent = int(100 * (self._currentTask - 1) / self._maxTask)
        if percent < 5:
            percent = 5
        fp.write('''PERC={:d}
CURRENT=<b>{:s}</b>
COMPLETE=completed {:d} of {:d}
'''.format(percent, task, self._currentTask, self._maxTask)) 
        fp.close()
        if os.path.exists(self._fnProgress):
            os.unlink(self._fnProgress)
        os.rename(temp, self._fnProgress)
    
    def cover(self, text):
        '''
        Disquises the passphrase.
        @param text: clear text
        @return:     the disguised text
        '''
        seed = random.randint(0, 0xffff)
        rc = "{:02x}{:02x}".format(seed % 256, seed / 256)
        for cc in text:
            seed = (seed * 7 + 0x1234321) & 0x8fffffff
            val = ((ord(cc) ^ seed) & 0xff)
            rc += "{:02x}".format(val)
        return rc
    
    def hexToBin(self, x):
        '''
        Converts a 2 digit hex number into a number.
        @param x:      2 digit hex number, e.g. "a9"
        @return:       the value of x, 0..255
        '''
        rc = int(x, 16)
        return rc

    def uncover(self, text):
        '''
        Uncovers the text disguised with cover().
        @param text:    encrypted text
        @return:        clear text
        '''
        rc = ""
        s1 = self.hexToBin(text[0:2])
        s2 = self.hexToBin(text[2:4])
        seed = s1 + s2*256
        ix = 4
        while ix < len(text):
            seed = int((seed * 7 + 0x1234321) & 0x8fffffff)
            val = self.hexToBin(text[ix:ix+2])
            val2 = ((val ^ seed) & 0xff)
            rc += chr(val2)
            ix += 2
        return rc
        