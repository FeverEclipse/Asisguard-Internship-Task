import time
import requests
import tkinter
import threading
import socket



global stop_flag
global stop_receive
stop_flag = threading.Event()
stop_receive = threading.Event()
task_thread = None
receive_thread = None

UDP_IP = "10.10.10.54"
UDP_LATLON_PORT = 11453
UDP_ELE_PORT = 1453

latitude = "0"
longitude = "0"

gui = tkinter.Tk()

def startRetrieve():
    global stop_flag
    global task_thread
    global latitudeEntry
    global longitudeEntry
    global latitude
    global longitude
    latitude = latitudeEntry.get()
    longitude = longitudeEntry.get()
    stop_flag.clear()
    task_thread = threading.Thread(target=sendLatLon)
    receive_thread = threading.Thread(target=receiveElevation)
    task_thread.start()
    receive_thread.start()

def sendLatLon():
    global stop_flag
    global latitude
    global longitude
    global latitudeEntry
    global longitudeEntry
    while not stop_flag.is_set():
        latitude = latitudeEntry.get()
        longitude = longitudeEntry.get()
        message = str(latitude) + "," + str(longitude)
        message = message.encode("utf-8")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message, (UDP_IP, UDP_LATLON_PORT))
        time.sleep(1)

def receiveElevation():
    global eleLabel
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((UDP_IP, UDP_ELE_PORT))
    while True:
        msg, address = s.recvfrom(1024)
        print(msg.decode("utf-8"))
        eleLabel.config(text="The requested elevation is: " + msg.decode("utf-8"))

'''def elevation():
    global eleLabel
    url = "https://api.open-elevation.com/api/v1/lookup?locations=" + str(latitude) + "," + str(longitude)
    r = requests.get(url=url)
    data = r.json()
    elevation = data['results'][0]['elevation']
    print(data)
    eleLabel.config(text=("The requested elevation is: " + str(elevation)))'''

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