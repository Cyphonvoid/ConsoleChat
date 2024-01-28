import threading
import socket
from Utility import *


ERROR_CODE_SE = '--sender error--'
ERROR_CODE_RE = '--reciever error--'
SUCCESS_CODE_SE = '--sender active--'
SUCCESS_CODE_RE = '--reciever active--'
CLOSE_CONNECTION = '--Close Connection--'

class ERROR():

    SENDER = '--sender error--'
    RECIEVER = '--reciever error--'

class SUCCESS():
    SENDER = '--sender active--'
    RECIEVER = '--reciever active--'


class Message():

    def __init__(self, content, owner):
        self.content = content
        self.owner = owner
        if(owner == None):
            self.owner = "someone"

    def read(self):
        return (self.content, self.owner)
    
    def write(self, content):
        self.content = content

    def delete(self):
        self.content = None
        self.owner = None


class Storage():

    def __init__(self):
        self.outgoing = []
        self.incoming = []
    
    def get_handle(self):
        return self
    
    def push_to_outgoing(self, message):
        self.outgoing.append(Message(message, None))
    
    def push_to_incoming(self, message):
        self.incoming.append(Message(message, None))
    
    def pop_outgoing(self, num=-1):
        if(num == -1): return self.outgoing.pop()
        else:return self.outgoing.pop(num)
    
    def pop_incoming(self, num=-1):
        if(num == -1):return self.incoming.pop()
        else:return self.incoming.pop(num)
    
    def read_sent(self, at=-1):
        if(at == -1):return self.outgoing[-1]
        else:return self.outgoing[at]

    def read_recieved(self, at):
        if(at == -1):return self.incoming[-1]
        else:return self.incoming[at]


class Reciever():

    def __init__(self, socket, parent):
        self.socket = socket
        self.status = Status(True)
        self.reciever_thread = None
        self.reciever_thread = threading.Thread(target=self.thread)
        self.reciever_thread.setDaemon(True)
        self.reciever_status = Status(True)
        self.parent_component = parent
        self.socket_local_address = self.socket.getsockname()
        self.socket_remote_address = self.socket.getpeername()
        self.display_messages = True
     
    def display_incoming(self, val):
        self.display_messages = val

    def thread(self):
        #print(self.socket_remote_address, " reciever thread started")
        while(self.status.get() == True and self.reciever_status.get() == True):
            message = self.recieve()
            if(message == ERROR.RECIEVER):
                #print("thread error caught", message)
                return
            self.parent_component.storage.push_to_incoming(message)


    def recieve(self):
        #Need to detech the offline socket state on other side or when it closes it in general 
        if(self.status.get() == False): 
            return ERROR.RECIEVER
        
        Message = None
        try:
            message = self.socket.recv(1024).decode('utf-8')

            if(message == None or message == CLOSE_CONNECTION):
                self.status.set_false()
                self.parent_component.status.set_false()
                return ERROR.RECIEVER
            if(self.display_messages == True): print("Recieved From:",str(self.socket_remote_address) + ">", message)
            return message
        except Exception as error:
            return ERROR.RECIEVER
            
        return message

   

    def activate(self):
        self.status.set_true()
        self.reciever_status.set_true()
        self.reciever_thread.start()
    
    def deactivate(self):
        self.status.set_false()
        self.reciever_status.set_false()

    def shutdown(self):
        self.status.set_false()
        self.reciever_status.set_false()
        self.socket = None
        self.parent_component = None
    
    def reboot(self, socket, parent):
        self.status.set_true()
        self.reciever_status.set_true()
        self.socket = socket
        self.parent_component = parent


class Sender():

    def __init__(self, socket, parent):
        self.socket = socket
        self.status = Status(True)
        self.parent_component = parent
        self.display_message = True
        self.socket_local_address = self.socket.getsockname()
        self.socket_remote_address = self.socket.getpeername()
    
    def display_outgoing(self, val):
        self.display_message = val

    def __check_ready__(self):
        if(self.socket == None):
            self.status.set_false()
        else:
            self.status.set_true()

    def send(self, message):
        if(self.status.get() == False):
            return ERROR.SENDER
        
        try:
            self.socket.send(message.encode('utf-8'))
            if(self.display_message == True):print("Sent To:" + str(self.socket_remote_address) + ">", message)
            return SUCCESS.SENDER
        except Exception as error:
            print("Error in Sender Object", error)
            self.parent_component.status.set_false()
            return ERROR.SENDER
    
    
    def activate(self):
        #print("in sencer activate")
        self.status.set_true()
        self.__check_ready__()

    def deactivate(self):
        self.status.set_false()

    def shutdown(self):
        self.status.set_false()
        self.socket = None
        self.parent_component = None
    
    def reboot(self, socket, parent):
        self.status.set_true()
        self.socket = socket
        self.parent_component = parent

    
class ClientHandle():
    #Client socket object which needs the a socket to be oassed in as constructor
    def __init__(self, socket):
        self.socket = socket
        self._local_address = socket.getsockname()
        self._remote_address = socket.getpeername()
        self.status = Status(True)
        self.storage = Storage()
        self.sender = Sender(socket, self)
        self.reciever = Reciever(socket, self)
        self._display_messages = True
        self.callback = None

        
    def attach_callback(self, callback):
        self.callback = callback

    def send_message(self, message):
        if(self.status.get() == False):
            self.callback(self)
            return ERROR.SENDER
        
        success = self.sender.send(message)

        if(success == ERROR.SENDER):
            self.callback(self)
            self.status.set_false()
        
        return SUCCESS.SENDER

    def storage(self):
        return self.storage
    
    def recieve_message(self):
        if(self.status.get() == False):
            self.callback(self)
            return ERROR.RECIEVER
        
        #self.recieve_event_callback(self)
        value = self.storage.read_recieved()
        return value


    def print(self):
        print("Socket Information:", " Remote: ", self.remote_address())
        pass

    def local_address(self):
        return self._local_address
    
    def remote_address(self):
        return self._remote_address

    def shutdown(self):
        self.sender.shutdown()
        self.reciever.shutdown()
       
    def reboot(self):
        self.sender.reboot(self.socket, self)
        self.reciever.reboot(self.socket, self)

    def open(self):
        #print("in handle open()")
        self.status.set_true()
        self.reciever.activate()
        self.sender.activate()
        
    def close(self):
        self.status.set_false()
        self.sender.shutdown()
        self.reciever.shutdown()
        self.socket.close()
    
    def display_messages(self, val):
        self._display_messages = val

        if(val == True):
            self.sender.display_outgoing(True)
            self.reciever.display_incoming(True)
        else:
            self.sender.display_outgoing(False)
            self.sender.display_outgoing(False)


    def state(self):
        return self.status.get()

#Listener Sockets will listen to incoming calls and produce client sockets
class Listener():

    def __init__(self):
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._local_address = None
        self.client_socket = []
        self.limit = None
        self.listening_thread = None
        self.status = Status(False)
        self.connection_state = Status(False)
        self.callback = None
        self.callback_arg = None

    def __produce_sockets__(self):

        try:
            self.listener_socket.listen()
            client_socket, address = self.listener_socket.accept()
            new_socket = ClientHandle(client_socket)
            new_socket.open()
            if(self.callback != None): self.callback(new_socket)
            self.client_socket.append(new_socket)
        except Exception as error:
            pass
      
    def __listen__(self):
        if(self.status.get() == False):
            return
        
        if(self.limit != None):
            for i in range(0, self.limit+1):
               if(self.status.get() == False or self.connection_state.get() == False):
                   return
               self.__produce_sockets__()

        elif(self.limit == None):
            while True:
               if(self.status.get() == False or self.connection_state.get() == False):
                   return
               self.__produce_sockets__()

    def set_limit(self, num):
        self.limit = num

    def host_with(self, IP, PORT):
        try:
            self.listener_socket.bind((IP, PORT))
            self.connection_state.set_true()
            self._local_address = self.listener_socket.getsockname()
            print("Listerned socket successfully connected...")
        except Exception as error:
            self.connection_state.set_false()
            print("[Error hosting]:", error)
            raise error

    def __run__(self):
        self.listening_thread = threading.Thread(target=self.__listen__)
        self.listening_thread.start()

    def attach_event_handler(self, callback):
        self.callback = callback

    def local_address(self):
        return self._local_address
    
    def open(self):
        if(self.connection_state.get() == False):
            self.status.set_false()
        elif(self.connection_state.get() == True): 
            self.status.set_true()
            print("Listener socket is open and ready.....")
            self.__run__()
       
    def close(self):
        self.status.set_false()
        self.connection_state.set_false()
        self.listener_socket.close()
