import unittest
from Vertx.eventbus import Eventbus

class Handler(object):
    result=None
    
    def handle(self, message):
        if message != None:
            self.result = message['body']
            
class TestRegister(unittest.TestCase):
    """
    test registerHandler 
    """
    result = None

    def test_publish(self):
        eb = Eventbus('localhost', 7001,debug=True)
        handler=Handler();
        eb.registerHandler('echo', handler.handle)
        assert(eb.handlers['echo'] != None)

        eb.unregisterHandler('echo',handler.handle)
        if eb.handlers != None:
            assert(1)

        # close after 2 seconds
        eb.close(2)


if __name__ == '__main__':
    unittest.main()