#!/usr/bin/python
# Authors:
# 2016: Jayamine Alupotha https://github.com/jaymine
# 2020: Wolfgang Fahl https://github.com/WolfgangFahl

import socket
import json
import struct
import time
import threading
from enum import IntEnum

class State(IntEnum):
    """ Eventbus state see https://github.com/vert-x3/vertx-bus-bower/blob/master/vertx-eventbus.js"""
    CONNECTING=0
    OPEN=1
    CLOSING=2
    CLOSED=3

class Eventbus(object):
    """
    Vert.x TCP eventbus client for python

    :ivar headers: any headers to be sent as per the vertx-tcp-eventbus-bridge specification 
    
    :ivar state: the state of the the eventbus
    :vartype state: State.CONNECTING: State

    :ivar host: 'localhost' the host the eventbus is connected to
    :vartype host: str

    :ivar port: 7000 : the port to be used for the socket connection
    :vartype port: int

    :ivar timeOut: DEFAULT_TIMEOUT:time in secs to be used as the socket timeout
    :vartype timeOut: float

    :ivar debug: False: True if debugging should be enabled
    :vartype debug: bool
    """
    DEFAULT_TIMEOUT=60.0

    def __init__(self, host='localhost', port=7000, timeOut=None,connect=True,debug=False):
        """
        constructor

        Args:
            host(str): the host to connect to - default: 'localhost'
            port(int): the port to use - default: 7000
            timeOut(float): time in secs to be used as the socket timeout - default: 60 secs - the minimium timeOut is 10 msecs and will be enforced
            connect(bool): True if the eventbus should automatically be opened - default: True
            debug(bool): True if debugging should be enabled - default: False
            
        :raise:
           :IOError: - the socket could not be opened
           :Exception: - some other issue e.g. with starting the listening thread    

        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.handlers = {}
        self.headers = {}
        self.host = host
        self.port = port
        self.debug=debug
        if timeOut is None:
            timeOut=Eventbus.DEFAULT_TIMEOUT
        if timeOut < 0.01:
            self.timeOut = 0.01
        else:
            self.timeOut = timeOut

        self.state = State.CONNECTING
        if connect:
            # connect
            self.open()
            
    def open(self):
        """ 
        open the eventbus by connecting the eventbus socket and starting a listening thread
        by default the connection is opened on construction of an Eventbus instance
        
        :raise:
           :IOError: - the socket could not be opened
           :Exception: - some other issue e.g. with starting the listening thread
        """
        try:
            self._connect()
            t1 = threading.Thread(target=self._receivingThread)
            t1.start()
        except IOError as e:
            self.close()
            raise e
        except Exception as e:
            self.close()
            raise e      
    
    def _connect(self): 
        """ connect my socket """ 
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(self.timeOut)    
            
    def wait(self,state=State.OPEN,timeOut=5.0, timeStep=0.01):
        """ 
        wait for the eventbus to reach the given state
        
        Args:
            state(State): the state to wait for - default: State.OPEN
            timeOut(float): the timeOut in secs after which the wait fails with an Exception
            timeStep(float): the timeStep in secs in which the state should be regularly checked
            
        :raise:
           :Exception: wait timed out  
        """
        timeLeft=timeOut;
        while not self.state is state and timeLeft>0:
            time.sleep(timeStep)
            timeLeft=timeLeft-timeStep
        if timeLeft<=0:
            raise Exception("wait for %s timedOut after %.3f secs" % (state.name,timeOut))
        if self.debug:
            print("wait for %s successful after %.3f secs" % (state.name,timeOut-timeLeft))    

    def addHeader(self, header, value):
        """
        add a header with the given header key and value

        Args:
           header(str):  the key of the header value to add
           value(object): the value of the header value to add
        """
        self.headers[header] = value
    
      
    def isOpen(self):
        """
        Checks if the eventbus state is OPEN.

        Returns:
           bool: True if State is OPEN else False
        """
        if self.state is State.OPEN:
            return True
        return False

    def _sendFrame(self, message_s):
        """
        send the given message

        Args:
           message_s (str): the message to be sent.

        """
        message = message_s.encode('utf-8')
        msgLen=len(message)
        frame = struct.pack('!I', msgLen) + message
        if self.debug:
            print("sending %d bytes '%s'" % (msgLen,message_s))
        self.sock.sendall(frame)

    def _receive(self):
        """
        receive a message as specified in https://vertx.io/docs/vertx-tcp-eventbus-bridge/java/
        <Length: uInt32><{
           type: String,
           address: String,
           (replyAddress: String)?,
           headers: JsonObject,
           body: JsonObject
        }: JsonObject>
        """
        if (self.debug):
            print ("trying to receive a message in state %s" %  self.state.name)
        # this is a blocking call which should run in separate thread
        # receive the first uInt32 4 bytes
        if self.state < State.CLOSING:  # closing socket
            len_str = self.sock.recv(4)
        else:
            raise Exception("eventbus is closed while trying to receive first 4 bytes of message/Length")
        len1 = struct.unpack("!i", len_str)[0]
        if (self.debug):
            print ("trying to receive %d bytes in state %s" %  (len1,self.state.name))
        if self.state < State.CLOSING:  # closing socket
            payload = self.sock.recv(len1)
        else:
            raise Exception("eventbus is closed while trying to receive payload of %d bytes" % (len1))
        json_message = payload.decode('utf-8')
        message = json.loads(json_message)
        debugInfo="%d message bytes with payload %s" % (len1,message)
        # check
        if (self.debug):
            print(debugInfo)
        if not 'type' in message:
            raise Exception("invalid message - type missing in: '%s'" % debugInfo)   
        msgType=message['type'];     
        if 'address' not in message:
            raise Exception("invalid message - address missing in '%s'" % debugInfo)
        address=message['address']
        if not address in self.handlers:
                raise Exception("no handler for address %s" % debugInfo)
        if msgType == 'message' or msgType == 'err' or msgType == 'pong':
            for handler in self.handlers[address]:
                handler(message)
        else:
            raise Exception("invalid message type %s in '%s'" %(msgType,debugInfo) )
       

    def _receivingThread(self):
        """
        receive loop to be started in separate Thread
        """
        self.state = State.OPEN
        if self.debug:
            print ("starting receiving thread")
        while self.state < State.CLOSING:  # CONNECTING=0, OPEN=1
            try:
                self._receive()
            except Exception as e:
                if self.debug:
                    print(e)
        if self.debug:
            print ("receiving thread finished in state %s" % self.state.name)
        self.sock.close()
        self.state = State.CLOSED            

    def close(self):
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
        # wait for the socket timeout
        self.wait(State.CLOSED,timeOut=self.timeOut)
        
    def _mergeHeaders(self,headers=None):
        """ merge the given headers with the default headers 
        Args:
           headers(dict): the headers to merge - default:None
           
        Returns:
           dict: the merged headers dict
        """
        
        if headers is None:
            return self.headers
        else:
            # https://stackoverflow.com/a/26853961/1497139
            mergedHeaders=self.headers.copy()
            mergedHeaders.update(headers)
            return mergedHeaders
            
        
    def _send(self,msgType,address,body=None, headers=None):  
        """
           send a message of the given message type to the given address with the givne body
           
        Args:
           msgType(str): the type of the message publish, send or ping
           address(str): the target address to send the message to
           body(str): the body of the message e.g. a JSON object
           headers(dict): headers to be added - default: None
         
        :raise:
           :Exception: - eventbus is not open
        """
        if not self.isOpen():
            raise Exception("eventbus is not open when trying to %s to  %s" % (msgType,address))
        headers=self._mergeHeaders(headers)
        message = json.dumps(
            {'type': msgType, 'address': address, 'headers': headers, 'body': body, })

        self._sendFrame(message)
        
    def send(self, address, body=None, headers=None):
        """
        Args:
            address(str): the target address to send the message to
            body(str): the body of the message e.g. a JSON object- default: None
            headers(dict): headers to be added - default: None
            
        :raise:
           :Exception: - eventbus is not open    
        """
        self._send('send',address,body,headers=headers)

    def publish(self, address, body=None,headers=None):
        """
        publish

        Args:
            address(str): the target address to send the message to
            body(str): the body of the message e.g. a JSON object
            headers(dict): headers to be added - default: None
         
        :raise:
           :Exception: - eventbus is not open
        """
        self._send('publish',address,body)
    
    def registerHandler(self, address, callback, headers=None):
        """
        register a handler

        Args:
            address(str): the address to register a handler for
            callback(function): a callback for the address
            headers(dict): headers to be added - default: None
            
        :raise:
           :Exception: 
              - eventbus is not open
              - callback not callable  
        """
        if not self.isOpen():
            raise Exception("eventbus is not open when trying to register Handler for %s" % address)
        if not callable(callback):
            raise Exception("callback for registerHandler must be callable")
        if not address in self.handlers:
            self.handlers[address]=[]
            self._send('register', address, headers=headers)
        self.handlers[address].append(callback)   

    def unregisterHandler(self, address,callback,headers=None):
        """
        unregister a callback for a given address
        if there is more than one callback for the address it will be remove from the handler list
        if there is only one callback left an unregister message will be sent over the bus and then
        the address is fully removed

        Args:
            address(str): the address to unregister the handler for
            callback(function): the callback to unregister
            headers(dict): headers to be added - default: None
            
        :raise:
           :Exception: 
              - eventbus is not open
              - address not registered
              - callback not registered 
        """
        if not self.isOpen():
            raise Exception("eventbus is not open when trying to unregister handler for %s" % (address))
        if address not in self.handlers:
            raise Exception("can't unregister address %s - address not registered" % (address))
        callbacks=self.handlers[address]
        if callback not in callbacks:
            raise Exception("can't unregister callback for %s - callback not registered" % (address))    
        callbacks.remove(callback)
        if len(callbacks) == 0:
            self._send('unregister', address, body=None, headers=headers)
            del self.handlers[address]
