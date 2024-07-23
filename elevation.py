import requests
import tkinter
import threading




global stop_flag
stop_flag = threading.Event()
task_thread = None

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
    task_thread = threading.Thread(target=elevation)
    task_thread.start()

def elevation():
    global eleLabel
    url = "https://api.open-elevation.com/api/v1/lookup?locations=" + str(latitude) + "," + str(longitude)
    r = requests.get(url=url)
    data = r.json()
    elevation = data['results'][0]['elevation']
    print(data)
    eleLabel.config(text=("The requested elevation is: " + str(elevation)))

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