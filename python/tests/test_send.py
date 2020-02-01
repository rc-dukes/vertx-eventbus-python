import unittest

from Vertx.eventbus import DeliveryOption
from Vertx.eventbus import Eventbus


#replyHandler (self,error,message)
#handlers (self,message)
class Client(unittest.TestCase):
    ('System Testing')
    result = {'msg': 'test', }

    # Handler
    def Handler(self, message):
        if message != None:
            Client.result = message['body']

    # replyHandler
    def replyHandler(self, error, message):
        pass

    def test_send(self):
        c = Client()
        eb = Eventbus(c, 'localhost', 7001,debug=True)

        #jsonObject -body
        body = {'msg': 'test1', }

        # DeliveryOption
        do = DeliveryOption()
        do.addHeader('type', 'text')
        do.addHeader('size', 'small')
        do.addReplyAddress('echo')
        do.setTimeInterval(5)

        # register handler
        eb.registerHandler('echo', Client.Handler)
        # send
        eb.send('echo', body, do)

        # without deliveryoption
        eb.send('echo', body, Client.replyHandler)
        assert(Client.result == {'msg': 'test1', })

        # without replyHandler
        body = {'msg': 'test2', }

        eb.send('echo', body, do)

        # close after 1 seconds
        eb.close(1)
        assert(Client.result == {'msg': 'test2', })

if __name__ == '__main__':
    unittest.main()
