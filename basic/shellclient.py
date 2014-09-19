'''
Created on 28.04.2013

@author: hm
'''
import os.path, time, math

SVOPT_BACKGROUND = "background"
SVOPT_SOURCE = "source"
SVOPT_DEFAULT = "std"

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
        self._dirTask = session.getConfigOrNoneWithoutLanguage(".dir.tasks")
        if self._dirTask == None:
            self._dirTask = "/var/cache/sidu-base/shellserver-tasks" 
        # session info
        self._session = session
        # current number for unique filenames
        self._fileNo = 0
        
    def execute(self, answer, options, command, params, timeout = 3600,
                deleteAnswer = True):
        '''Executes a command.
         @param answer:     the name of the answer file
         @param options:    the options for the shell server
         @param command:   the command to execute, e.g. SVOPT_DEFAULT
         @param params:   NULL or a string or an array of strings
         @param timeout:    the maximum count of seconds
         @return: true: answer file exists. false: timeout reached
        '''
        self._fileNo += 1
        self._lastCommandFile = filename = self.buildFileName("", 
            "." + str(self._fileNo) + ".cmd", None)
        trueAnswer = answer if answer != None else self.buildFileName("answer_", ".txt")
        tmpName = filename + ".tmp"
        if deleteAnswer:
            self._session.deleteFile(trueAnswer)
        if options == None:
            options = ""
        cmd = "\n".join((trueAnswer, options, command, ""))
        lang = ""
        if params != None:
            if type(params) == list:
                cmd += "\n".join(params)
            else:
                cmd += self._session.toUnicode(params);
            if cmd.find("{{lang}}") >= 0:
                lang = self._session._language
                if len(lang) == 2:
                    lang = lang.lower() + '_' + lang.upper() + '.UTF8'
                elif len(lang) == 5:
                    lang = lang[0:1].lower() + lang[3:4].upper() + '.UTF8'
                cmd = cmd.replace("{{lang}}", lang)
        with open(tmpName, "w") as fp:
            fp.write(cmd)
        fp.close()
        os.rename(tmpName, filename);
        for ii in xrange(timeout):
            time.sleep(1)
            if os.path.exists(trueAnswer):
                break
        if trueAnswer != answer and trueAnswer.endswith(".answer"):
            self._session.deleteFile(trueAnswer)
        return os.path.exists(trueAnswer)
     
    def buildFileName(self, prefix = "f", suffix = ".answer", subdir = None):
        '''Builds the name of an answer file.
        @param prefix: the prefix of the node name
        @param suffix: the suffix of the node name
        @return the nameo of a file which does not exist
        '''
        fn = None
        if subdir == None:
            subdir = ""
            
        while True:
            base = self._session.getConfigWithoutLanguage(".dir.tasks")
            if not base.endswith(os.sep):
                base += os.sep
            time1 = int(time.time()) % 0x100
            time2 = int(math.fmod(time.time(), 1) * 0x10000)
            fn = "{:s}{:s}{:s}{:s}.{:02x}{:04x}{:s}".format(
                base, subdir, prefix, self._session._id, time1, time2, suffix)
            if not os.path.exists(fn):
                break
        return fn

    def escShell(self, text):
        '''Makes a string "shell proof".
        @param text: the text to encode
        @return: the text with escaped meta characters
        ''' 
        rc = text.replace("$", r'\$')
        return rc

