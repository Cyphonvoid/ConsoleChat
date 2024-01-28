import threading
from Utility import *
from Sockets import *
import time


CLOSE_CONNECTION = '--Close Connection--'

class Input():

    def __init__(self, status):
        self.state = Status(status)

    def user_input(self):
        if(self.state.get() == True):
            return input()
        elif(self.state.get() == False):
            return None

    def open(self):
        self.state.set_true()

    def close(self):
        self.state.set_false()


class MultiClientServer():

    def __init__(self):
        self.clients = []
        self.client_listener = Listener()
        self.client_listener.attach_event_handler(self.push_new_client)
        self.client_listener.set_limit(10)
        self.current_client = None
        self.status = Status(False)
        self.input = Input(True)
        self.reciever_thread = threading.Thread(target=self.__thread__, daemon=True)
        self.send_all_flag = False
    
    def push_new_client(self, client):
        self.clients.append(client)
        client.attach_callback(self.server_callback)
        print(client.remote_address(), " Connected...")
    
    def server_callback(self, client):
        address = client.remote_address()
        self.filter_clients(client)
        print(str(address) + " got disconnected....")
        self.current_client = None

    def __thread__(self):
        #This thread needs to be synchronized with the main thread when deleting stuff like current client
        while self.status.get() == True:
            value = self.recieve_message()
            if(value == ERROR.RECIEVER):
                self.filter_clients(self.current_client)
                self.current_client = None
            
            if(self.current_client == None):
                time.sleep(1)
                
            
    def select_client(self, num):

        try:
            num = int(num)
            if(num > len(self.clients)-1 or num < 0):
                return
            self.current_client = self.clients[num]
        except Exception as error:
            pass

    def close_client(self):
        self.current_client.close()

        counter = 0; 
        for client in self.clients:
            if(client == self.current_client):
                self.clients.pop(counter)
            
            counter+=1

    def display(self):
        print("         MultiClientServer")
        print("____________________________________")
        print("Hosted On:", self.client_listener.local_address())  

        
    def send_message(self, message):
        if(len(self.clients) == 0):
            print("[No Clients Available")
            return None
        
        if(self.current_client == None):
            print("[Current client is None and not selected..]")
            return None
        
        if(message == 'exit'):
            self.input.close()
            self.close()
            return None
        try:
            if(self.current_client.state() == True):
                success = self.current_client.send_message(message)
                if(success == ERROR.SENDER):
                    print("[Error recieved in send:", ERROR.SENDER)
                    return False
                #print(self.current_client.remote_address(), "> sent:", message)
                return True
            else:
                return False
        except Exception as error:
            print("[Error recieved in send:", error)
            return False
        

    def recieve_message(self):
        if(len(self.clients) == 0):
            print("[No Clients Available")
            return None
        
        if(self.current_client == None):
            print("[Current client is None and not selected..]")
            return None
        
        message = None
        try:
            if(self.current_client.state() == True):
                message = self.current_client.recieve_messae()
                if(message == ERROR.RECIEVER):
                    print("[Error recieved]:", ERROR.RECIEVER)
                    return False
                print(self.current_client.remote_address(),"> recieved:", message)
                return message
            else:
                return False
        except Exception as error:
            print("[Error recieved]:", error)
            return False
    
    def __clients(self):

        #Display clients
        counter = 0; 
        for client in self.clients:
            print("client [" + str(counter) + "]")
            client.print()
            counter += 1
        
        print("Select >>", end="")
        val = input()
        self.select_client(val)

    def __disconnect_client(self, num):

        #Display clients
        counter = 0; 
        for client in self.clients:
            print("client [" + str(counter) + "]")
            client.print()
            counter += 1
        
        print("Select to disconnect >>", end="")
        val = input()
        temp = ""
        for i in range(0, len(self.clients)):
            if(i == int(val)):
                temp = self.clients.pop(i)
                break
        
        print("client dropped", temp.remote_address())


    def run(self, IP, PORT):
        self.status.set_true()
        self.input.open()
        self.client_listener.host_with(IP, PORT)
        self.client_listener.open()
        self.display()
        #self.reciever_thread.start()
        
        while True:
            val = input()

            if(val == '-exit'):
                print("_______________Closed__________________")
                self.send_close_header()
                self.close_all_clients()
                self.close()
                break

            if(val == '-select'):
                self.send_all_flag = False
                self.__clients()
                continue
            elif(val == 'close'):
                self.__disconnect_client()
                pass
            if(val == '-select all'):
                self.send_all_flag = True
    
            success = None
            if(self.send_all_flag == False):success = self.send_message(val)
            else: 
                for client in self.clients:
                    success = client.send_message(val)
            if(success == ERROR.SENDER):
                self.filter_clients(self.current_client)
                self.current_client = None


    def filter_clients(self, _client):
        counter = 0
        for client in self.clients:
            if(client == _client):
                self.clients.pop(counter)
            counter += 1

        pass
    def send_close_header(self):
        for client in self.clients:
            client.send_message(CLOSE_CONNECTION)

    def close_all_clients(self):
        for client in self.clients:
            client.close()
        
    def close(self):
        self.client_listener.close()
        self.input.close()
    


server = MultiClientServer()
server.run('192.168.1.222', 9999)
server.close()
