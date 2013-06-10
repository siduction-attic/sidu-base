'''
Created on 28.04.2013

@author: hm
'''
import time, os.path, time, math

class ShellClient(object):
    '''
    External commands will be executed by an external "shell server".
    This server waits for tasks: It polls a directory for files containing the command.
    The answer of the server will be written in a file, which is part of the command.

    Format of the command file:
    <pre>
    answer_file
    command
    param1
    ...
    </pre>
    '''


    def __init__(self, session):
        '''Constructor.
        @param session:    the session info
        '''
        # the directory containing the task files, e.g. /tmp/sidu-base/tasks/
        self._dirTask = session.getConfigOrNoneWithoutLanguage(".task.dir")
        if self._dirTask == None:
            self._dirTask = "/var/cache/sidu-base/shellserver-tasks" 
        # session info
        self._session = session
        # current number for unique filenames
        self._fileNo = 0
        
    def execute(self, answer, options, command, params, timeout = 3600):
        '''Executes a command.
         @param answer:     the name of the answer file
         @param options:    the options for the shell server
         @param command:   the command to execute, e.g. SVOPT_DEFAULT
         @param params:   NULL or a string or an array of strings
         @param timeout:    the maximum count of seconds
         @return: true: answer file exists. false: timeout reached
        '''
        self._fileNo += 1
        self._lastCommandFile = filename = self.buildFileName("prefix", 
            "." + str(self._fileNo) + ".cmd", 
            "shellserver")
        trueAnswer = answer if answer != None else self.buildFileName("answer_", ".txt")
        tmpName = filename + ".tmp"
        if os.path.exists(trueAnswer):
            os.unlink(trueAnswer)
        if options == None:
            options = ""
        cmd = "\n".join((trueAnswer, options, command, ""))
        if params != None:
            if type(params) == list:
                cmd += "\n".join(params)
            else:
                cmd += str(params);
        with open(tmpName, "w") as fp:
            fp.write(cmd)
        fp.close()
        os.rename(tmpName, filename);
        for ii in xrange(timeout):
            time.sleep(1)
            if os.path.exists(trueAnswer):
                break
        rc = os.path.exists(trueAnswer);
        if rc and trueAnswer != answer:
            os.unlink(trueAnswer)
        return rc;
     
    def buildFileName(self, prefix = "f", suffix = ".answer", subdir = None):
        '''Builds the name of an answer file.
        @param prefix: the prefix of the node name
        @param suffix: the suffix of the node name
        @return the nameo of a file which does not exist
        '''
        fn = None
        if subdir == None:
            subdir = ""
        else:
            subdir = "/" + subdir
            
        while True:
            base = self._session.getConfigWithoutLanguage(".dir.temp")
            time1 = int(time.time()) % 0x100
            time2 = int(math.fmod(time.time(), 1) * 0x10000)
            fn = "{:s}/{:s}{:s}{:s}.{:02x}{:04x}{:s}".format(
                base, subdir, prefix, self._session._id, time1, time2, suffix)
            if not os.path.exists(fn):
                break
        return fn
