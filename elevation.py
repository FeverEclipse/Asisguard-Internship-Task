import time
import tkinter
import threading
import socket

UDP_IP = "10.10.10.54"
UDP_LATLON_PORT = 11453
UDP_ELE_PORT = 1453

latitude = "0"
longitude = "0"

stop_flag = threading.Event()
stop_receive = threading.Event()
task_thread = None
receive_thread = None

gui = tkinter.Tk()

def startRetrieve():
    global stop_flag, task_thread, receive_thread, latitudeEntry, longitudeEntry
    latitude = latitudeEntry.get()
    longitude = longitudeEntry.get()
    stop_flag.clear()
    task_thread = threading.Thread(target=sendLatLon)
    receive_thread = threading.Thread(target=receiveElevation)
    task_thread.start()
    receive_thread.start()

def sendLatLon():
    global stop_flag, latitudeEntry, longitudeEntry
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_flag.is_set():
        latitude = latitudeEntry.get()
        longitude = longitudeEntry.get()
        message = f"{latitude},{longitude}".encode("utf-8")
        sock.sendto(message, (UDP_IP, UDP_LATLON_PORT))
        time.sleep(1)

def receiveElevation():
    global eleLabel
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((UDP_IP, UDP_ELE_PORT))
    while not stop_flag.is_set():
        msg, _ = s.recvfrom(1024)
        print(msg.decode("utf-8"))
        eleLabel.config(text="The requested elevation is: " + msg.decode("utf-8"))

latitudeLabel = tkinter.Label(gui, text='Enter latitude: ')
latitudeLabel.grid(row=0,column=0, sticky="W", padx=15, pady=15)

longitudeLabel = tkinter.Label(gui, text='Enter longitude: ')
longitudeLabel.grid(row=1, column=0, sticky="W", padx=15, pady=15)

latitudeEntry = tkinter.Entry(gui, width=15)
latitudeEntry.grid(row=0, column=1, padx=15, pady=15)

longitudeEntry = tkinter.Entry(gui, width=15)
longitudeEntry.grid(row=1, column=1, padx=15, pady=15)

button = tkinter.Button(gui, text="Check elevation", command=startRetrieve)
button.grid(row=2, column=1, padx=15, pady=15)

eleLabel = tkinter.Label(gui, text="")
eleLabel.grid()

gui.mainloop()
