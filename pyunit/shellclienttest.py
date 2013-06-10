'''
Created on 28.04.2013

@author: hm
'''
import unittest, os.path

from basic.shellclient import ShellClient
from aux import Aux
from util.util import Util 

class ShellClientTest(unittest.TestCase):


    def setUp(self):
        self._session = Aux.getSession('testappl')
        self._tempDir = Util.getTempDir("shellserver")
        self._session.addConfig(".dir.temp", self._tempDir)
        self._session.addConfig(".task.dir", self._tempDir)


    def tearDown(self):
        pass


    def testBasic(self):
        client = ShellClient(self._session)
        answer = client.buildFileName()
        options = "-v --help"
        command =  "test"
        params = ["1", "abc"]  
        timeout = 1
        client.execute(answer, options, command, params, timeout)
        content = Util.readFileAsList(client._lastCommandFile)
        self.assertTrue(content[0].startswith("/tmp/shellserver/f"))
        content = "".join(content[1:])
        self.assertMultiLineEqual('''-v --help
test
1
abc''',     content)

    def testBuildAnswerFile(self):
        client = ShellClient(self._session)
        answer = client.buildFileName()
        self.assertTrue(answer.endswith(".answer"))
        self.assertTrue(answer.find(os.sep + "f") > 0)
        self.assertFalse(os.path.exists(answer))
        Util.writeFile(answer)
        self.assertTrue(os.path.exists(answer))
        os.unlink(answer)
        
    def testRemote(self):
        if Aux.isRunningProgram("shellserver.sh"):
            pass
        pass
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()