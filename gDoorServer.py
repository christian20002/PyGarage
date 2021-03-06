#!/usr/bin/python3
import socketserver
import time
import _thread
import subprocess

LIB = False
LOCKED = False

WAIT_TIME = 240



try:
    import RPi.GPIO as gp
    LIB = True
    print("Loaded GPIO library")
    gp.cleanup()
    gp.setmode(gp.BOARD)
    gp.setup(16,gp.OUT)
    gp.output(16,1)
    
    gp.setup(8,gp.IN, pull_up_down=gp.PUD_UP)
    gp.setup(10,gp.IN, pull_up_down=gp.PUD_UP)
    gp.setup(12,gp.OUT)
except Exception:
    LIB = False
    print("Could not load GPIO library")

def doorSens():
    return gp.input(8)
def lockSens():
    return gp.input(10)
def lockLight(val):
    gp.output(12,val)
def updateLight():
    if LIB:
        while True:
            if lockSens():
                lockLight(False)
            else:
                lockLight(True)
        time.sleep(1)



def checkDoor():
    while True:
        #print("Starting door check...")
        time.sleep(1)
        if LIB:
            if lockSens():
                #lockLight(False)
                global LOCKED; LOCKED = False
                print("Checking door...")
                if doorSens():
                    print("Door open, waiting "+str(WAIT_TIME)+" seconds for close")
                    time.sleep(WAIT_TIME)
                    if doorSens() and lockSens():
                        print("Door still open, activating lift")
                        lift()
                    else:
                        print("Door shut, probably by driver")
              
                else:
                    print("Door closed.")
            else:
                if LOCKED == False:
                    print("Door Locked")
                global LOCKED; LOCKED = True
                #lockLight(True)
        else:
                print("Simulating door check...")
                time.sleep(20)
    

def lift():
    for x in range (0,2): subprocess.Popen(['mpg123','-q','alarm.mp3']).wait()
    time.sleep(3)
    print("Lifting...")
    if LIB:
        gp.output(16,0)
        time.sleep(0.5)
        gp.output(16,1)
    else:
        print("No GPIO, simulating lift...")

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data.decode())
        lift()
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

if __name__ == "__main__":
    HOST, PORT = "192.168.2.70", 31415

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    _thread.start_new_thread(checkDoor,())
    _thread.start_new_thread(updateLight,())
    server.serve_forever()
    print("Starting server")
    for x in range (0,9):
        print(x)
