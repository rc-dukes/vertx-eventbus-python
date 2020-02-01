'''
Created on 2020-02-01

@author: wf
'''
import unittest
from Vertx.eventbus import Eventbus

class Handler(object):
    result=None
    
    def handle(self, message):
        if message != None:
            self.result = message['body']

    
class TestEventbus(unittest.TestCase):

    def testCreateWithInvalidPort(self):
        hasErr=False
        try:
            eb=Eventbus(port=9999)
            assert eb is not None
        except Exception as e:
            hasErr=True
            pass
        assert hasErr,"There should be an exception that eventbus is not expected at this port"
        
    def testRegisterWithClosedBus(self):
        eb=Eventbus(port=7001)
        eb.close(0.0);
        handler=Handler();
        err=False
        try:
            eb.registerHandler("address1", handler.handle)
        except Exception:
            err=True
            pass
        assert err, "It should not be possible to register a handler while the eventbus is closed"
   
        
    def testRegisterHandler(self):
        eb=Eventbus(port=7001)
        handler=Handler()
        eb.registerHandler("echo", handler.handle)    
        eb.close(1)
        
    #def testSocket(self):
    #    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    #        s.connect(('localhost',7001))
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
        
    #def test_send(self):
    #    eb = Eventbus(port=7001,debug=True)
    #    body = {'msg': 'test send2' }
    #    handler=Handler()
    #    eb.registerHandler("echo", handler.handle)    
    #    eb.send('echo', body)
    #    # close after 1 seconds
    #    eb.close(2)
    #    assert(handler.result == {'msg': 'test send2' })    


if __name__ == "__main__":
    unittest.main()