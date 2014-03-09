'''
Created on 19.03.2014

@author: hm
'''

import re, os.path, subprocess

MODE_NONE = 0
MODE_RECORDING = 1
MODE_REPLAYING = 2

class Recorder:
    '''
    recorder -- implements a recorder for regression tests
    and the infrastructure to replay this recording
    Allows the recording of a real session. This recording can be
    replayed in a regression test.
    '''


    def __init__(self, application, mode, fnRecorder = "/tmp/autopart.recorder.txt"):
        '''
        Constructor
        Initializes the session.
        @param application:  a prefix for temporary files
        @param mode:         0: no recording/replaying 1: recording 2: replaying
        @param file:         recorder storage file
        '''
        self._mode = mode
        self._fnRecorder = fnRecorder
        self._application = application
        self._outputStreamLines = []
        self._currentFileNo = 0
        self._currNoIds = {}
        if mode == MODE_REPLAYING:
            self.readRecordedInfo(self._fnRecorder)
 
    def storeArgs(self, args):
        '''
        Stores the program arguments into the recorder file.
        @param args:       all names and values of the variables
        '''
        if self._mode == MODE_RECORDING:
            # find the values:
            defs = []
            defs.append("###recorder progArgs:")
            name = True
            for item in args.keys:
                if name:
                    defs.append("{:s}={:s}".format())
        self.writeFile("\n".join(defs) + "\n", "", self._fnRecorder);

    def writeFile(self, content, suffix, name, append, aDir):
        '''
        Writes a given content to a temporary file.
        @param content:    content to write
        @param suffix:     suffix of the generated filename
        @param name:       "" or name of the file
        @param append:     if true the content will be appended
        @param aDir:       "" or the target directory
        @return            filename
        '''
        fn = name
        if fn == "":
            if aDir == "":
                aDir = "/tmp"
            fn = "{:s}/tmp.{:s}".format(aDir, self._application)

        fp = open(fn, "a" if append else "w")
        if content != "":
            fp.write(content)
        fp.close()
        return fn
    
    def finish(self, args):
        '''
        Do the last things for the recorder.
        @param varargs    <name1> <content1> <name2> <content2>...
                          <contentX> is a string or a reference of an array of lines
        '''
        for key in args.keys():
            self.put(key, args[key])
            

    def storeBlock(self, header, lines):
        '''
        Stores the content of one stream
        @param header:     identifies the block
        @param lines:      line array
        '''
        matcher = re.search(r'readStream id: (\w+): no: (\d+) device: (.+)', header)
        if matcher != None:
            id = matcher.group(1)
            no = matcher.group(2)
            dev = matcher.group(3)
            key = "{:s}-{:s}:{:s}".format(id, no, dev)
            self._recorderStorage[key] = lines
        else:
            matcher = re.search(r'recorder (\w+):', header)
            if matcher != None:
                key = matcher.group(1)
                self._recorderStorage[key] = lines
            else:
                matcher = re.search(r'FileExists id: (\w+): mode: (\S+) no: (\d+) file: (\S+) rc: (.)', header)
                if matcher != None:
                    id = matcher.group(1)
                    mode = matcher.group(2)
                    callNo = matcher.group(3)
                    aFile = matcher.group(4)
                    val = matcher.group(5)
                    key = "{:s}-{:s}{:s}{:s:{:s}".format(id, callNo, mode, aFile)
                    self._recorderStorage[key] = lines
                else:
                    print("unknown header: " + header)

    def readRecordedInfo(self, fn):
        '''
        Reads the file created by the recorder.
        @param fn:    the file's name
        '''
        fp = open(fn, "r")
        rexpr = re.compile(r'^###(readStream|FileExists|recorder \w+:)')
        lastHeader = None
        lines = []
        for line in fp:
            matcher = rexpr.match(line)
            if matcher != None:
                if lastHeader != None:
                    self.storeBlock(lastHeader, lines)
                lines.clear()
                lastHeader = line
            else:
                lines.append(line)
        self.storeBlock(lastHeader, lines)
        fp.close()

    
    def firstOfLine(self, name, prefix = None):
        '''
        Gets the first line of a file
        @param name:    the filename, e.g. /etc/siduction-version
        @param prefix:  this string will be put in front of the result
        @return:        "\t<prefix>:<first_line>"
        '''
        rc = ""
        if os.path.exists(name):
            lines = self.readStream("firstOfLine", name)
            if prefix == None:
                prefix = ""
            elif not prefix.isEmpty():
                prefix = "\t{:s}:".format(prefix)
            rc = prefix + lines[0]
        return rc

    def put(self, name, content):
        '''
        Puts an entry of the recorder storage.
        @param name:       name of the entry
        @param content:    a string or a reference of an array of lines
        '''
        if type(name) == list:
            sep = "\n" if content[0].endswith("\n") else ""
            content = sep.join(content)
        self.writeFile("###recorder $name:\n" . content, "", 
                       self._fnRecorder, True)
        
    def writeStream(self, id, device, content):
        '''
        Writes to a stream.
        A stream can be a file or the input of an external command.
        For tests this can be a file.
        @param id:        identifies the caller
        @param device:    a filename or a external command, 
                          e.g. "|fdisk /dev/sdb"
        @param content    this content will be written
        '''
        
        if self._mode == MODE_RECORDING:
            header = "### writeStream id: {:s} device: {:s}\n".format(id, device)
            self.writeFile(header . content, "", self._fnRecorder)
        if self._mode != MODE_REPLAYING:
            if device.startswith("|"):
                pass
            else:
                mode = "a" if device.startswith(">>") else "w"
                if mode == "a":
                    device = device[2:]
                fp = open(device, mode)
                if type(content) == list:
                    fp.writelines(content)
                else:
                    fp.write(content)
                fp.close()
        else:
            self._outputStreamLines.append("== id: {:s} device: {:s}",
                                           id, device)
            if type(content) == list:
                self._outputStreamLines += content
            else:
                self._outputStreamLines.append(content)

    def execute(self, id, cmd, important):
        '''
        Execute a command.
        @param id:         identifies the caller
        @param cmd:        command to execute
        @param important:  true: the logging will be prefixed
        @return           the output of the command
        '''
        rc = self.readStream(id, cmd + " |")
        return rc

    def nextCallNo(self, aId):
        '''Returns the next id specific call number.
        @return: a number to make an "event" unique
        '''
        if aId not in self._currNoIds:
            self._currNoIds[aId] = -1
        self._currNoIds[aId] += 1
        return self._currNoIds[aId]
        
    def fileExists(self, aId, mode, aFile):
        '''
        # Tests the existence of a file.
        # @param aId:    id of the caller
        # @param mode:   "-e", "-d", "-f" ...
        # @param aFile:  file to test
        # @return:       False: does not exist. 
        #                True: exists
        '''
        callNo = self.nextCallNo(aId)
        rc = False
        if self._mode == MODE_REPLAYING:
            key = "{:s}-{:d}{:s}:{:s}".format(aId, callNo)
            entry = self.getFromStorage(key)
            if entry == None:
                raise Exception("unknown storage key: " + key)
            else:
                rc = entry != "f"
        else:
            if mode == "-e":
                rc = os.path.exists(aFile)
            elif mode == "-d":
                rc = os.path.isdir(aFile)
            elif mode == "-f":
                rc = os.path.isfile(aFile)
            elif mode == "-l":
                rc = os.path.islink(aFile)
            else:
                raise Exception("unknown mode: " + mode)
            if mode == MODE_RECORDING:
                callNo = self.nextCallNo()
                content = "###FileExists id: {:s}: mode: {:s} no: {:d} file: {:s} rc: {:s}".format(
                                aId, mode, callNo, "T" if rc else "F")
                self.writeFile(content, "", self._fnRecorder, True)
                
        return rc 

    def getFromStorage(self, key):                    
        '''
        Gets an entry of the recorder storage.
        @param name: name of the entry
        @return:     an array of lines
        '''
        if key not in self._storage:
            rc = None
        else:
            rc = self._storage[key]
        return rc

    def readStream(self, aId, device, input = None):
        '''
        Reads a stream into an array of lines.
        A stream can be a file or the output of an extern command.
        For tests this can be a file.
        @param aId:     defines the stream to open
        @param device:  a filename, a directory, an external command 
                        e.g. "partprobe -s |"
                        "gdisk -l /dev/$disk|"
        @param input:   only if device is an external command:
                        a string or a list of strings used as
                        input for stdin of the command
        @return:        a list of lines:
                        file: content
                        dir: list of nodes
                        ext.command: output of the command
        '''
        rc = "<!None>"
        callNo = self.nextCallNo(aId)
        if self._mode != MODE_REPLAYING:
            if os.path.isdir(device):
                rc = self.listdir(device)
            elif os.path.exists(device):
                fp = open(device, "r")
                rc = fp.readlines()
                fp.close()
            elif device.endswith("|"):
                device = device[0:-1].strip()
                if input == None:
                    rc = subprocess.check_output(device)
                else:
                    raise Exception("not implemented: ext. cmd with input")
            else:
                raise Exception("unknown device: " + device)
        return rc
'''
      if ($s_mode != $MODE_REPLAYING){
        # 
        # call of an external program with input and output:
        } elsif ($device =~ /^</){
            my $file = WriteFile("", ".exc");
            my $cmd = substr($device, 1) . " >$file";
            system($cmd);
            open my $INP, "<", $file;
            @rc = <$INP>;
            close $INP;
            unlink $file;
        } elsif ($device =~ /[<]/){
            system($device);
            if ($device =~ /[>]\s*(\S+)/){
                my $file = $1;
                open my $INP, "<", $file;
                @rc = <$INP>;
                close $INP;
            } else {
                die "no output file found: $device";
            }    
        } elsif (open my $INP, $device){
            @rc = <$INP>;
            close $INP;
        } else {
            print "+++ $device: $!";
        }
    } elsif (scalar keys %s_recorderStorage > 0){
        my $key = "$id-$callNo:$device";
        my $refArray = $s_recorderStorage{$key};
        if ($refArray){
            @rc = @$refArray;
        } else {
            my $msg = "+++ stream content not found: $key\nStored blocks:\n";
            foreach(keys %s_recorderStorage){
                $msg .= "$_\n" if /^$id/;
            }
            die $msg;
        }
    } else {
        die "not implemented: $id ($device)";
    }
    @rc = split(/\n/, $content) unless $content eq "<!None>";
    if ($s_mode == $MODE_RECORDING){
        my $sep = $rc[0] =~ /\n/ ? "" : "\n";
        $content = "###readStream id: $id: no: $callNo device: $device\n";
        $content .= join($sep, @rc);
        $content .= "\n" unless substr($content, -1) eq "\n"; 
        &WriteFile($content, "", $s_recorderFile, 1);
    }
    return @rc;
}    


return 1;'''        