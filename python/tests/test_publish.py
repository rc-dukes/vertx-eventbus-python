import unittest

from Vertx.eventbus import DeliveryOption
from Vertx.eventbus import Eventbus


#handlers (self,message)
class Client(unittest.TestCase):
    ('System Testing')
    result = {'msg': 'test', }

    def test_publish(self):
        eb = Eventbus('localhost', 7001,debug=True)


        #jsonObject -body
        body = {'msg': 'test1', }

        # DeliveryOption
        do = DeliveryOption()
        do.addHeader('type', 'text')
        do.addHeader('size', 'small')
        do.addReplyAddress('echo')
        do.setTimeInterval(5)

        # publish
        eb.publish('echo', body, do)

        # publish without do
        eb.publish('echo', body)

        # close after 2 seconds
        eb.close(2)


if __name__ == '__main__':
    unittest.main()
