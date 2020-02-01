#!/usr/bin/python
# Authors:
# 2016: Jayamine Alupotha https://github.com/jaymine
# 2020: Wolfgang Fahl https://github.com/WolfgangFahl

import socket
import json
import struct
import time
import threading
import traceback
from enum import IntEnum

class DeliveryOption:
    """

    """
    def __init__(self,replyAddress=None,timeInterval=10.0):
        """
        construct me

        Args:
           replyAddress(str): the address to potentialy reply to - default: None
           timeInterval(float):
        """
        self.replyAddress = replyAddress
        self.headers = {}
        self.timeInterval = timeInterval

    def addHeader(self, header, value):
        """
        add a header with the given header key and value

        Args:
           header(str):  the key of the header value to add
           value(object): the value of the header value to add
        """
        self.headers[header] = value

    def deleteHeader(self, header):
        """
        delete the given header

        Args:
           header(str):  the key of the header value to be deleted
        """
        del self.headers[header]

    def addReplyAddress(self, replyAddress):
        """
        add a the given reply address

        Args:
           replyAddress(str):  the address to reply to
        """
        self.replyAddress = replyAddress

    def deleteReplyAddress(self):
        self.replyAddress = None

    def setTimeInterval(self, time):
        self.timeInterval = time

class State(IntEnum):
    """ Eventbus state see https://github.com/vert-x3/vertx-bus-bower/blob/master/vertx-eventbus.js"""
    CONNECTING=0
    OPEN=1
    CLOSING=2
    CLOSED=3

class Eventbus:
    """
    Vert.x TCP eventbus client for python
    """

    def __init__(self, instance, host='localhost', port=7000, timeOut=0.1, timeInterval=10.0,debug=False):
        """
        constructor

        Args:
            host(str): the host to connect to - default: 'localhost'
            port(int): the port to use - default: 7000
            timeOut(float): time in secs to be used as the socket timeout - default: 100 msecs
            timeInterval(float): time in secs - default: 10 secs
            debug(bool): True if debugging should be enabled - default: False

        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.handlers = {}
        self.ReplyHandler = {}
        self.host = host
        self.port = port
        self.this = instance
        self.debug=debug
        self.writable=True
        if timeOut < 0.01:
            self.timeOut = 0.01
        else:
            self.timeOut = timeOut

        self.timeInterval = timeInterval
        # connect
        try:
            self.state = State.CONNECTING
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(self.timeOut)
            t1 = threading.Thread(target=self.__receivingThread)
            t1.start()
            self.state = State.OPEN
        except IOError as e:
            self.printErr(1, 'SEVERE', str(e))
        except Exception as e:
            self.printErr('Undefined Error', 'SEVERE', str(e))

    def isOpen(self):
        """
        Checks if the eventbus state is OPEN.

        Returns:
           bool: True if State is OPEN else False
        """
        if self.state is State.OPEN:
            return True
        return False

    def __sendFrame(self, message_s):
        """
        send the given message

        Args:
           message_s (str): the message to be sent.

        """
        message = message_s.encode('utf-8')
        frame = struct.pack('!I', len(message)) + message
        self.sock.sendall(frame)

    def __receive(self):
        try:
            if self.state < State.CLOSING:  # closing socket
                len_str = self.sock.recv(4)
            else:
                return False
            len1 = struct.unpack("!i", len_str)[0]
            if self.state < State.CLOSING:  # closing socket
                payload = self.sock.recv(len1)
            else:
                return False
            json_message = payload.decode('utf-8')
            message = json.loads(json_message)
            # check
            # print(message)
            if message['type'] == 'message':
                # failure message
                if 'address' not in message.keys():
                    self.printErr('message failure', 'SEVERE', message)
                else:
                    try:
                        # handlers
                        if self.handlers[message['address']] != None:
                            for handler in self.handlers[message['address']]:
                                handler(self.this, message)
                            self.ReplyHandler = None

                    except KeyError:
                        # replyHandler
                        try:
                            if self.ReplyHandler['address'] == message['address']:
                                self.ReplyHandler['replyHandler'](
                                    self.this, None, message)
                                self.ReplyHandler = None
                        except KeyError:
                            print('no handlers for ' + message['address'])

            elif message['type'] == 'err':
                try:
                    self.ReplyHandler['replyHandler'](self.this, message, None)
                    self.ReplyHandler = None
                except:
                    pass
            else:
                self.printErr(2, 'SEVERE', 'Unknown type')
            return True
        except socket.timeout:
            return True
        except Exception as e:
            # 1) close socket while thread is running
            # 2) function error in the client code
            self.printErr('Undefined Error', 'SEVERE', str(e))
            return False
            # send error message

    def __receivingThread(self):
        """
        receive loop to be started in separate Thread
        """
        while self.state < State.CLOSING:  # 0,1,2
            if self.writable == False:
                if self.__receive() == False:
                    break

    def close(self, timeInterval=30):
        """
        close the eventbus connection after staying in the CLOSING state
        for the given timeInterval

        Args:
            timeInterval(float): the number of seconds to sleep before actually closing the eventbus - default: 30 seconds

        """
        if self.state == State.CONNECTING:
            self.sock.close()
            return
        self.state = State.CLOSING
        time.sleep(timeInterval)
        try:
            self.sock.close()
        except Exception as e:
            self.printErr('Undefined Error', 'SEVERE', str(e))
        self.state = State.CLOSED

    def send(self, address, body=None, deliveryOption=None, replyHandler=None):
        """
        Args:
            address(str): the target address to send the message to
            body(str): the body of the message e.g. a JSON object- default: None
            deliveryOption(DeliveryOption): delivery options to be set - default: None
            replyHandler(function): callback for replies - if deliveryOption is callable it will be used as a replyHandler
        """
        if self.isOpen():
            message = None

            if callable(deliveryOption) == True:
                replyHandler = deliveryOption
                deliveryOption = None

            if deliveryOption != None:
                headers = deliveryOption.headers
                replyAddress = deliveryOption.replyAddress
                timeInterval = deliveryOption.timeInterval
            else:
                headers = None
                replyAddress = None
                timeInterval = self.timeInterval

            message = json.dumps({'type': 'send', 'address': address,
                                  'replyAddress': replyAddress, 'headers': headers, 'body': body, })
            # print('sent'+message)

            self.writable = True
            self.__sendFrame(message)

            # replyHandler
            if replyAddress != None and replyHandler != None:
                self.ReplyHandler = {}
                self.ReplyHandler['address'] = replyAddress
                self.ReplyHandler['replyHandler'] = replyHandler
            self.writable = False
            # time.sleep(timeInterval)
            i = 0.0
            while timeInterval / self.timeOut >= i:
                time.sleep(self.timeOut)
                if self.ReplyHandler == None:
                    break
                if timeInterval / self.timeOut == i and self.ReplyHandler != None:
                    try:
                        self.ReplyHandler['replyHandler'](
                            self.this, 'Time Out Error', None)
                        self.ReplyHandler = None
                        break
                    except:
                        break
                i += 1.0
        else:
            self.printErr(3, 'SEVERE', 'INVALID_STATE_ERR')

    def publish(self, address, body, deliveryOption=None):
        """
        publish

        Args:
            address(str): the target address to send the message to
            body(str): the body of the message e.g. a JSON object- default: None
            deliveryOption(DeliveryOption): delivery options to be set - default: None

        """
        if self.isOpen():
            if deliveryOption != None:
                headers = deliveryOption.headers
                replyAddress = deliveryOption.replyAddress
            else:
                headers = None
                replyAddress = None

            if replyAddress == None:
                message = json.dumps(
                    {'type': 'send', 'address': address, 'headers': headers, 'body': body, })
            else:
                message = json.dumps(
                    {'type': 'send', 'address': address, 'headers': headers, 'body': body, })

            self.writable = True
            self.__sendFrame(message)
            self.writable = False

        else:
            self.printErr(3, 'SEVERE', 'INVALID_STATE_ERR')

    def registerHandler(self, address, handler):
        """
        register a handler

        Args:
            address(str): the target address to send the message to
            handler(function): a handler for the address
        """
        if self.isOpen():
            message = None
            if callable(handler) == True:
                try:
                    if (address not in self.handlers.keys()) or (self.handlers[address] == None):
                        self.handlers[address] = []
                        message = json.dumps(
                            {'type': 'register', 'address': address, })
                        self.writable = True
                        self.__sendFrame(message)
                        self.writable = False
                        time.sleep(self.timeOut)
                except KeyError:
                    self.handlers[address] = []

                try:
                    self.handlers[address].append(handler)
                except Exception as e:
                    self.printErr(
                        4, 'SEVERE', 'Registration failed\n' + str(e))
            else:
                self.printErr(
                    4, 'SEVERE', 'Registration failed. Function is not callable\n')
        else:
            self.printErr(3, 'SEVERE', 'INVALID_STATE_ERR')

    def unregisterHandler(self, address):
        """
        unregister a handler

        Args:
            address(str): the target address to send the message to
        """
        if self.isOpen():
            message = None
            try:
                if self.handlers[address] != None:
                    if len(self.handlers) == 1:
                        message = json.dumps(
                            {'type': 'unregister', 'address': address, })
                        self.__sendFrame(message)
                    del self.handlers[address]
            except:
                self.printErr(5, 'SEVERE', 'Unknown address:' + address)

        else:
            print('error occured: INVALID_STATE_ERR')

    # print Error
    # 1 - connection errors
    # 2 - unknown type of the received message
    # 3 - invalid state errors
    # 4 - registration failed error
    # 5 - unknown address of un-registeration
    def printErr(self, No, Category, error):
        print(No)
        print(Category)
        print (error)
        if self.debug:
            traceback.print_exc()
