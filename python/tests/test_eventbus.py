'''
Created on 2020-02-01

@author: wf
'''
import unittest
import socket
import json
import time
import getpass
from Vertx.eventbus import Eventbus, TcpEventBusBridgeStarter
from Vertx.eventbus import State

class EchoCommand(dict):
    """ an Echo Command object """
    def __init__(self,cmd,msgType,address):
        """ construct me

        Args:
            cmd(str): a command  either "time" or "counter"
            msgType(str): a message type either "send" or "publish"
            address(str): an address to be used for the echo
        """
        dict.__init__(self, cmd=cmd,msgType=msgType,address=address)
        self.cmd=cmd;
        self.msgType=msgType;
        self.address=address;

    def asJson(self):
        """
        return me as a json String

        Returns:
           str: the json representation of the EchoCommand
        """
        return json.dumps(self.__dict__)


class Handler(object):
    """ a Handler for messages"""

    def __init__(self,debug=False):
        """
        construct me

        Args:
           debug(bool): if True show debug messages - default: True
        """
        self.debug=debug
        self.result=None
        self.headers=None

    def handle(self, err, message):
        """
        handle the given vert.x tcp-event bus message

        Args:
           err(dict): potential error message
           message(dict): the message dict to handle
           it may contain a body and headers
        """
        if err !=None:
            self.err = err
        if message != None:
            self.result = message['body']
            if 'headers' in message:
                self.headers= message['headers']
            if self.debug:
                print("handler received "+str(self.result))
                if self.headers:
                    print(" headers: "+str(self.headers))

RECEIVE_WAIT=0.3 # number of seconds to wait for result to be received

class TestEventbus(unittest.TestCase):
    """
    test the Eventbus for the vert.x tcp eventbus bridge
    """
    def __init__(self, *args, **kwargs):
        """ construct me """
        # https://stackoverflow.com/a/19102520/1497139
        super(TestEventbus, self).__init__(*args, **kwargs)
        self.debug=True
        if getpass.getuser()=="travis":
            Eventbus.DEFAULT_TIMEOUT=10.0
        elif getpass.getuser()=="wf":
            # could be as low as 0.1 secs on a quick computer ...
            Eventbus.DEFAULT_TIMEOUT=0.1
        else:
            Eventbus.DEFAULT_TIMEOUT=1.0

    def testCmd(self):
        """ test json encoding of a Cmd"""
        cmd=EchoCommand("time","send","me")
        json=cmd.asJson()
        if self.debug:
            print("echo command as json='%s'" % json)
        assert json=='{"cmd": "time", "msgType": "send", "address": "me"}'

    def testCreateWithInvalidPort(self):
        """
        test creating an event bus for an invalid port
        """
        hasErr=False
        try:
            eb=Eventbus(port=9999,debug=self.debug)
            assert eb is not None
        except Exception as e:
            if self.debug:
                print(e)
            hasErr=e is not None
            pass
        assert hasErr,"There should be an exception that eventbus is not expected at this port"

    def testRegisterWithClosedBus(self):
        """
        try registering an event bus for a closed port
        """
        eb=Eventbus(port=7001,debug=self.debug)
        eb.close();
        handler=Handler(self.debug);
        err=False
        try:
            eb.registerHandler("address1", handler.handle)
        except Exception as e:
            if self.debug:
                print (e)
            err=e is not None
            pass
        assert err, "It should not be possible to register a handler while the eventbus is closed"

    def test_registerHandler(self):
        """ test registering a handler"""
        eb = Eventbus(port=7001,debug=self.debug)
        handler=Handler(self.debug);
        eb.registerHandler('echo', handler.handle)
        assert(eb.handlers['echo'] != None)

        eb.unregisterHandler('echo',handler.handle)
        assert eb.handlers is not None
        assert len(eb.handlers) == 0
        # close
        eb.close()

    def testHandler(self):
        """ test handler """
        handler=Handler(self.debug)
        body = {'msg': 'test Handler' }
        message={}
        message["body"]=body
        handler.handle(None,message)
        assert handler.result==body

    def testRegisterHandler(self):
        """
        test a successful handler registration
        """
        eb=Eventbus(port=7001)
        handler=Handler(self.debug)
        eb.registerHandler("echo", handler.handle)
        assert(eb.handlers['echo'] != None)
        eb.close()

    def testWait(self):
        """
        test waiting for the eventbus to open and close
        """
        eb=Eventbus(port=7001,debug=True)
        eb.wait()
        eb.close()
        eb.wait(State.CLOSED)
        eb=Eventbus(port=7001,debug=True,connect=False)
        timedOut=False
        try:
            eb.wait(State.OPEN,timeOut=0.1)
        except Exception as e:
            print(e)
            timedOut=e is not None
        assert timedOut

    def test_publish(self):
        """ test publishing a message to the echo server """
        eb = Eventbus(port=7001,debug=True)
        handler=Handler(self.debug)
        eb.registerHandler("echo", handler.handle)
        #jsonObject -body
        body1 = {'msg': 'testpublish 1'}
        eb.wait(State.OPEN)
        # publish without headers
        eb.publish('echo', body1)
        # wait for the message to arrive
        time.sleep(RECEIVE_WAIT)
        eb.close()
        assert handler.result == body1

    def testMergeHeaders(self):
        """ test merging headers """
        eb = Eventbus(port=7001,debug=self.debug,connect=False)
        eb.addHeader("dh1", "dv1")
        mh1=eb._mergeHeaders();
        assert mh1=={'dh1': 'dv1'};
        headers={"h1","v1"}
        mh2=eb._mergeHeaders(headers)
        assert mh2=={'dh1': 'dv1', 'h': '1', 'v': '1'}

    def test_publishWithHeader(self):
        """ test publishing a message with headers """
        eb = Eventbus(port=7001,debug=self.debug)
        handler=Handler(self.debug)
        eb.registerHandler("echo", handler.handle)
        body2 = {'msg': 'testpublish with headers' }
        eb.addHeader('type', 'text')
        eb.addHeader('size', 'small')
        # publish with headers
        eb.publish('echo', body2)
        # wait for the message to arrive
        time.sleep(RECEIVE_WAIT)
        eb.close()
        assert handler.result == body2
        assert handler.headers == {'type': 'text', 'size': 'small'}

    def test_publishWithMultipleHandlers(self):
        """ test publishing a message to be handle by multiple handlers"""
        eb = Eventbus(port=7001,debug=self.debug)
        handler1=Handler(self.debug)
        handler2=Handler(self.debug)
        address="echoMe"
        eb.registerHandler(address, handler1.handle)
        eb.registerHandler(address, handler2.handle)
        eb.wait(State.OPEN)
        eb.send('echo',EchoCommand("reset","send",address))
        cmd=EchoCommand("counter","publish",address)
        eb.send('echo',cmd)
        time.sleep(RECEIVE_WAIT)
        eb.close()
        assert 'counter' in handler1.result
        assert handler1.result['counter']==1
        assert 'counter' in handler2.result
        assert handler1.result['counter']==1

    def test_sendInvalidAddress(self):
        """ test trying to send to an invalid address"""
        eb = Eventbus(port=7001,debug=self.debug)
        handler=Handler(self.debug)
        address="unpermitted_address"
        eb.registerHandler(address, handler.handle)
        cmd=EchoCommand("time","send",address)
        eb.send('echo',cmd)
        time.sleep(RECEIVE_WAIT)
        # FIXME - 40 message bytes with payload {'type': 'err', 'message': 'access_denied'} not handled yet ...
        eb.close()

    def test_reply(self):
        """ test sending a message with a reply handler """
        eb = Eventbus(port=7001,debug=self.debug)
        handler=Handler(self.debug)
        body = {'msg': 'test reply' }
        eb.wait(State.OPEN)
        eb.send('echo',body,callback=handler.handle)
        # wait for the message to arrive
        time.sleep(RECEIVE_WAIT)
        eb.close()
        assert handler.result==body


    def test_send(self):
        """ test sending a message"""
        eb = Eventbus(port=7001,debug=self.debug)
        handler=Handler(self.debug)
        address="echoMe"
        eb.registerHandler(address, handler.handle)
        cmd=EchoCommand("time","send",address)
        eb.wait(State.OPEN)
        eb.send('echo',cmd)
        # wait for the message to arrive
        time.sleep(RECEIVE_WAIT)
        eb.close()
        assert 'received_nanotime' in handler.result
        assert 'iso_time' in handler.result

    def test_ping(self):
        """ test sending a ping"""
        eb = Eventbus(port=7001,options={"vertxbus_ping_interval":500},debug=self.debug)
        eb.wait(State.OPEN)
        time.sleep(1.2)
        eb.close()
        assert eb.pongCount==2

    def testSocketDirect(self):
        """ test direct socket communication with echo server"""
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.connect(('localhost',7001))
            s.close()

    def testSocketOfEventBus(self):
        """ send a message using the private function of the event bus"""
        eb = Eventbus(port=7001,debug=True,connect=False)
        eb._connect()
        eb.state=State.OPEN
        body = {'msg': 'test socketOfEventBus' }
        eb._send('publish','echo', body)
        eb.sock.close()

    @classmethod
    def setUpClass(cls):
        cls.starter=TcpEventBusBridgeStarter(7001,debug=True)
        cls.starter.start()
        cls.starter.wait()

    @classmethod
    def tearDownClass(cls):
        cls.starter.stop()

    def testTcpEventBusBridgeStarter(self):
        """ test the TcpEventBusBridgeStarter"""
        starter=TcpEventBusBridgeStarter(7002,debug=True)
        starter.start()
        starter.wait()
        time.sleep(2.0)
        portAvailable=starter.checkPort()
        # kill the process (in any case)
        starter.stop()
        assert portAvailable
        time.sleep(2.0)
        assert not starter.checkPort()

if __name__ == "__main__":
    unittest.main()
