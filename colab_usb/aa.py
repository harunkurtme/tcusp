import usb

aa=usb.SerialProvider(socket_adress="localhost",socket_port=12351,auth_token= "1sjU8qmyzCygwbJpF7Xgy1dtIkx_3cuCG6P29GUkVUk9hRntt",usb_port=["/dev/ttyUSB0"],usb_baudrate=[9600],usb_timeout=[1])
aa.start()
try:
    while True:
        pass
except KeyboardInterrupt:
    aa.running=False
