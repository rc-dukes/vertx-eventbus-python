# DeliveryOption constructor
#	inside parameters
#		1) replyAddress
#		2) headers
#		3) timeInterval for reply


class DeliveryOption:
    ('deliveryOption class describe headers and replyAddress')
    def __init__(self,timeInterval=10.0):
        """ construct me 
        Args:
           timeInterval(float):  
        """
        self.replyAddress = None
        self.headers = {}
        self.timeInterval = timeInterval

    def addHeader(self, header, value):
        """
        add a header with the given header kery and value
        Args:
           header(str):  the key of the header value to add
           value(object): the value of the header value to add
        """
        self.headers[header] = value

    def deleteHeader(self, header):
        """
        Args:
           header(str):  the key of the header value to be deleted
        """
        del self.headers[header]

    def addReplyAddress(self, replyAddress):
        self.replyAddress = replyAddress

    def deleteReplyAddress(self):
        self.replyAddress = None

    def setTimeInterval(self, time):
        self.timeInterval = time
