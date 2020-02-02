'''
Created on 2020-02-01

@author: wf
'''
import unittest
import socket
import time
from Vertx.eventbus import Eventbus
from Vertx.eventbus import State

class Handler(object):
    result=None
    
    def __init__(self,debug=False):
        self.debug=debug
    
    def handle(self, message):
        if message != None:
            self.result = message['body']
            if self.debug:
                print("handler received "+str(self.result))

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
        Eventbus.DEFAULT_TIMEOUT=1.0
    
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
        handler.handle(message)
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
        body1 = {'msg': 'testpublish 1', }  
        eb.wait(State.OPEN)
        # publish without headers
        eb.publish('echo', body1)
        # wait for the message to arrive
        time.sleep(RECEIVE_WAIT)
        eb.close()
        assert handler.result == body1
       
    def test_publishWithHeader(self):   
        eb = Eventbus(port=7001,debug=True)
        handler=Handler()
        eb.registerHandler("echo", handler.handle)   
        body2 = {'msg': 'testpublish with headers', }   
        eb.addHeader('type', 'text')
        eb.addHeader('size', 'small')
        # publish with headers
        eb.publish('echo', body2)
        # wait for the message to arrive
        time.sleep(RECEIVE_WAIT)
        eb.close()    
        assert handler.result == body2
        
    def test_send(self):
        eb = Eventbus(port=7001,debug=True)
        handler=Handler()
        eb.registerHandler("echo", handler.handle)    
        #jsonObject -body
        body1 = {'msg': 'test send', }  
        eb.wait(State.OPEN)
        # send without headers
        # FIXME - this needs to be a send ... 
        eb.publish('echo', body1)
        # wait for the message to arrive
        time.sleep(RECEIVE_WAIT)
        eb.close()  
        assert handler.result == body1
          
        
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
    #        #s.settimeout(3.0)
    #        #s.setblocking(0)
    #        body = {'msg': 'test socket5' }
    #        message = json.dumps({'type': 'send', 'address': 'echo', 'body': body, })
    #        Eventbus.sendFrameViaSocket(s, message,True)
    #        #socket_list=[s]
    #         #timeout=2.0
    #        #read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [],timeout)
    #        #for sock in read_sockets:
    #        #    #incoming message from remote server
    #        #    if sock is s:
    #        data=s.recv(4)
    #        #s.close()

if __name__ == "__main__":
    unittest.main()