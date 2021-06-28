from socket import socket
import socket as socket_confg
from threading import Thread
import json

# !pip3 install pyserail

from serial import Serial
from pyngrok import ngrok,conf

class SerialJson:

    def __init__(self,usb_port=None,usb_baudrate=None,usb_timeout=None):
        
        try:
            assert usb_port!=None,"You must choose USB Port from portputer for examples, port* or ttyACM*"
            self.usb_port=usb_port
            assert usb_baudrate !=None,"You have to give a BaudRate like 9600" 
            self.usb_baudrate=usb_baudrate
            # assert len(usb_port) != len(baudrate) | len(timeout) != len(baudrate) | len(usb_port) != len(timeout), "Your parametres have to same length"
            self.usb_timeout=usb_timeout
        except AssertionError as msg:
            print(msg)
            exit(1)
        finally:
            self.serialjson={}
            self.usb_data={}
            self.serial_data={}

    def clean_serialJson(self):
        self.serialjson={}
    
    def clean_data(self):
        self.serial_data=[]

    def create_dictionary(self):
        self.clean_serialJson()

        try:
            for i in range(len(self.usb_port)):
                self.usb_data={
                    "usb_port":str(self.usb_port[i]),
                    "baudrate":self.usb_baudrate[i],
                    "timeout":self.usb_timeout[i],
                    "serial_data":self.serial_data[str(i)]

                }

                self.serialjson.update({
                    self.usb_port[i]:self.usb_data
                })
        except IndexError :
            import time
            time.sleep(0.01)
        except KeyError :
            import time
            time.sleep(0.01)

    def encode_json(self):
        
        self.serialjson=json.dumps(self.serialjson)
        return self.serialjson

    def decode_json(self,jsonObject):
        self.decodejson= json.loads(jsonObject)
        return self.decode_json

class SerialUSBConnection(SerialJson,Thread):
    def __init__(self, *args,**kwargs):
        SerialJson.__init__(self=self,*args,**kwargs)
        Thread.__init__(self=self)

        self.ser=Serial()
    def func_serial_port(self,serial_port):
        self.serial_port=serial_port

    def func_serial_baudrate(self,serial_baudrate):
        self.serial_baudrate=serial_baudrate

    def func_serial_timeout(self,serial_timeout):
        self.serial_timeout=serial_timeout
    
    def func_serial_connection(self):
        
        for i in range(len(self.usb_port)):

            self.ser.port= self.usb_port[i]#self.serial_port
            self.ser.baudrate= self.usb_baudrate[i] #9600 #self.serial_baudrate
            self.ser.timeout= self.usb_timeout[i]  #1 #self.timeout

            self.ser.open()

            if self.ser.is_open==True:
                # print(self.encode_json())
                self.ser.write(b'1')
                self.data= self.ser.readline().decode("utf-8").replace("\r","").replace("\n","")
                if self.data!=None and self.data!="":
                    
                    # print(self.data)
                    self.serial_data = {str(i):self.data}
                    # print(self.serial_data)
                    # print(i)

                self.ser.flush()
                
            else :
                print("not open")

            self.ser.close()

        self.create_dictionary()



class SerialConnection(SerialUSBConnection, socket):
    
    def __init__(self,socket_adress,socket_port, *args, **kwargs):
        SerialUSBConnection.__init__(self=self,*args, **kwargs)
        socket.__init__(self=self)

        try:
            assert socket_adress!=None, "You must give adress"
            assert socket_port!=None, "You must give port"
            # Thread(target=self.run).start()
            self.socket_adress=socket_adress
            self.socket_port=socket_port
            self.read_data=None
            self.running=True
        except AssertionError as msg:
            print(msg)
    
    def func_read_data(self):
        return self.read_data
    
    def func_serial_read(self):
        return self.serial_data
    
    def run(self):
        self.connect((self.socket_adress,self.socket_port))
        
        try:
            while self.running!=False:
                self.func_serial_connection()
                self.send(self.encode_json().encode("utf-8"))
                self.read_data = self.recv(1024).decode("utf-8")
                if not self.read_data: break
                print(self.read_data)
        except KeyboardInterrupt:
            self.is_alive=False
            self.running=False

    def __exit__(self):
        self.close()

class SerialProvider(socket,SerialJson,Thread):

    def __init__(self, socket_adress, socket_port,auth_token, *args, **kwargs):
        socket.__init__(self=self,family=socket_confg.AF_INET, type= socket_confg.SOCK_STREAM)
        SerialJson.__init__(self=self,*args,**kwargs)
        Thread.__init__(self=self)
        self.send_data=""
        self.jsonObject=""
        self.running=True
        
        try:
            assert auth_token!=None, "You must your auth token from you must get ngrok website"
        
            self.bind((socket_adress,socket_port))
            self.listen(5)

            self.pyngrok_config = conf.PyngrokConfig(log_event_callback=self.log_event_callback,
                                                max_logs=10)
            conf.set_default(self.pyngrok_config)
            ngrok.set_auth_token(auth_token)
            #remote_addr="{}:{}".format(socket_adress,socket_port)
            public_url=ngrok.connect(socket_port,"tcp").public_url


        except OSError as msg:
            print(msg)
        except ngrok.PyngrokNgrokHTTPError as msg:
            print(msg)
        except AssertionError as error:
            print(error)
        
    
    def func_send_data(self,send_data):
        self.send_data=send_data

    def log_event_callback(self,log):
        print(str(log))

    def run(self) :
        
            self.conn, self.addr = self.accept()
            with self.conn:
                    print('Connected by', self.addr)
                    while self.running==True:
                        try:
                            print("hello")
                            self.jsonObject = self.conn.recv(1024).decode("utf-8")

                            if not self.jsonObject: break

                            print(self.jsonObject)
                            # print(data.decode("utf-8"))
                            if self.send_data==None:
                                self.conn.sendall(''.encode("utf-8"))
                            else:    
                                self.conn.sendall(self.send_data.encode("utf-8"))
                        except KeyboardInterrupt:
                            self.is_alive=False
                            

                            tunnels=ngrok.get_tunnels(pyngrok_config=self.pyngrok_config)
                            # print(tunnels.)
                            for xtunel in tunnels:
                                ngrok.disconnect(xtunel.public_url)
                            exit(1)


        # return super().run()

    def __exit__(self):
        self.close()
        tunnels=ngrok.get_tunnels(pyngrok_config=self.pyngrok_config)



if __name__ == '__main__':

    # serialJson=SerialJson(usb_port=1,baudrate=9600)
    # serialUSB=SerialUSB(usb_port=["1","2","3"],baudrate=[5,5,5],timeout=[0,0,0])
    # serialUSB.run()
    #4.tcp.ngrok.io:10768
    serial_Con=SerialConnection(socket_adress="4.tcp.ngrok.io",socket_port=10768,usb_port=["/dev/ttyUSB0"],usb_baudrate=[9600],usb_timeout=[1])
    serial_Con.start()
    # serial_pro=SerialProvider(socket_adress="localhost",socket_port=12345,usb_port=["/dev/ttyUSB0"],usb_baudrate=[9600],usb_timeout=[1])
    # serial_pro.start()
    

    
    while serial_Con.running!=False:
        # try:
        print(serial_Con.func_read_data())
        print(serial_Con.func_serial_read())

        #     pass
        # except KeyboardInterrupt:
        #     serial_Con.running=False
        #     break
    # print(serialUSB.encode_json())
    # print(serialJson.encode_json(SerialJson(usb_port=2,baudrate=115200)))
