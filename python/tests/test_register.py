import unittest
from Vertx.eventbus import Eventbus

class TestRegister(unittest.TestCase):
    """
    test registerHandler 
    """
    result = None

    # Handler
    def Handler(self, message):
        if message != None:
            self.result = message['body']
            print(self.result)

    def test_publish(self):
        eb = Eventbus(self, 'localhost', 7001,debug=True)

        eb.registerHandler('echo', self.Handler)
        assert(eb.Handlers['echo'] != None)

        eb.unregisterHandler('echo')
        if eb.Handlers != None:
            assert(1)

        # close after 2 seconds
        eb.close(2)


if __name__ == '__main__':
    unittest.main()