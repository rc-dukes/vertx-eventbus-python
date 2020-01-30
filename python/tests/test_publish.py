import unittest

import Vertx.DeliveryOption as DeliveryOption
import Vertx.Eventbus as Eventbus


#handlers (self,message)
class Client(unittest.TestCase):
    ('System Testing')
    result = {'msg': 'test', }

    def test_publish(self):
        c = Client()
        eb = Eventbus.Eventbus(self, 'localhost', 7001,debug=True)


        #jsonObject -body
        body = {'msg': 'test1', }

        # DeliveryOption
        do = DeliveryOption.DeliveryOption()
        do.addHeader('type', 'text')
        do.addHeader('size', 'small')
        do.addReplyAddress('echo')
        do.setTimeInterval(5)

        # publish
        eb.publish('echo', body, do)

        # publish without do
        eb.publish('echo', body)

        # close after 2 seconds
        eb.closeConnection(2)


if __name__ == '__main__':
    unittest.main()
