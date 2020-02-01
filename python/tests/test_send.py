import unittest

from Vertx.eventbus import DeliveryOption
from Vertx.eventbus import Eventbus

class Handler(object):
    result=None
    
    def handle(self, message):
        if message != None:
            self.result = message['body']

class TestSend(unittest.TestCase):
    """
    test sending
    """
    result = None;


    # replyHandler
    def replyHandler(self, error, message):
        pass

    def test_send(self):
        eb = Eventbus('localhost', 7001,debug=True)

        #jsonObject -body
        body = {'msg': 'test1', }

        # DeliveryOption
        do = DeliveryOption()
        do.addHeader('type', 'text')
        do.addHeader('size', 'small')
        do.addReplyAddress('echo')
        do.setTimeInterval(5)
        handler=Handler()
        # register handler
        eb.registerHandler('echo', handler.handle)
        # send
        eb.send('echo', body, do)

        replyHandler=Handler()
        # without deliveryoption
        eb.send('echo', body, replyHandler.handle)
        assert(handler.result == {'msg': 'test1', })

        # without replyHandler
        body = {'msg': 'test2', }

        eb.send('echo', body, do)

        # close after 1 seconds
        eb.close(1)
        assert(handler.result == {'msg': 'test2', })

if __name__ == '__main__':
    unittest.main()
