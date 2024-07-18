import msvcrt
import serial
import time
import os
import numpy as np
import serial.tools.list_ports
import tkinter
import threading

CRC16_XMODEM_POLY = 0x1021
CRC16_XMODEM_INITIAL_VALUE = 0x0000

PANTILT_SYNC_BYTE = 0x55
MASTER_STM = 0x01
SLAVE_PANTILIT = 0x02
AXIS_MOVEMENT = 0x20
GO_TO_START = 0x1A

TILT_AXIS = 20

availablePorts = serial.tools.list_ports.comports()
portsList = []
for port in availablePorts:
    portsList.append(port.name)


frequency = 1
amplitude = 30000
start_time = time.time()
bPanTilt_Transmitter_Buffer = bytearray(100)
gui = tkinter.Tk()
selectedPort = tkinter.StringVar(value=availablePorts[0].name)
gui.title("Pan/Tilt UI")
frequencyEntry = tkinter.Entry(gui, width=5)
frequencyEntry.insert(0, "0")
amplitudeEntry = tkinter.Entry(gui, width=5)
amplitudeEntry.insert(0, "0")
frequencyLabel = tkinter.Label(gui, text='Enter frequency: ')
frequencyLabel.grid(row=1,column=1, sticky="W", padx=15, pady=15)
portLabel = tkinter.Label(gui, text="Enter Port: ")
connectionStatusLabel = tkinter.Label(gui, text="Not Connected", background="#f00")
connectionStatusLabel.grid(row=0, column=3)
portLabel.grid(row=0, column=1, padx= 5, pady= 5)
portEntry = tkinter.OptionMenu(gui, selectedPort, *portsList)
portEntry.grid(row=0, column=2, padx=5, pady=5)
frequencyEntry.grid(row=1, column=2, padx=5, pady=5)
amplitudeLabel = tkinter.Label(gui, text='Enter amplitude: ')
amplitudeLabel.grid(row=2,column=1, sticky="W", padx=15, pady=15)
amplitudeEntry.grid(row=2, column=2, padx=5, pady=5)
ser= None
file = "config.txt"

def connectSerial():
    global ser
    global connectionStatusLabel
    ser = serial.Serial(selectedPort.get(),
            baudrate=57600,
            write_timeout=100,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE)
    connectionStatusLabel.config(text="Connected", background="#0f0")
    portEntry.config(state=tkinter.DISABLED)

global stop_flag
stop_flag = threading.Event()
task_thread = None

def calculateCRC16(data, length):
    
    crc = CRC16_XMODEM_INITIAL_VALUE

    for pos in range(length):
        crc ^= data[pos] << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ CRC16_XMODEM_POLY
            else:
                crc <<= 1
            
    return crc

def PanTilt_Go_TO_Home():

    with open(file, "w") as f:
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK,1)
            f.write("0\n0")
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK,1)
            f.close()
    bPanTilt_Transmitter_Buffer = bytearray(50)

    bPanTilt_Transmitter_Buffer[0] = PANTILT_SYNC_BYTE
    bPanTilt_Transmitter_Buffer[1] = MASTER_STM
    bPanTilt_Transmitter_Buffer[2] = SLAVE_PANTILIT
    bPanTilt_Transmitter_Buffer[3] = GO_TO_START
    bPanTilt_Transmitter_Buffer[4] = 0

    CRCValue = calculateCRC16(bPanTilt_Transmitter_Buffer,5) 
    bPanTilt_Transmitter_Buffer[5] = (CRCValue >> 8) & 0x00FF
    bPanTilt_Transmitter_Buffer[6] = CRCValue & 0x00FF

    ser.write(bPanTilt_Transmitter_Buffer)

def sendData():
    while True:
        if stop_flag.is_set():
            break
        elapsed = (time.time() - start_time)
        new_y = np.cos(2 * np.pi * frequency * elapsed) * amplitude

        bPanTilt_Transmitter_Buffer[0] = PANTILT_SYNC_BYTE
        bPanTilt_Transmitter_Buffer[1] = MASTER_STM
        bPanTilt_Transmitter_Buffer[2] = SLAVE_PANTILIT
        bPanTilt_Transmitter_Buffer[3] = AXIS_MOVEMENT
        bPanTilt_Transmitter_Buffer[4] = 4 # Data Lengt
        bPanTilt_Transmitter_Buffer[5] = TILT_AXIS
        bPanTilt_Transmitter_Buffer[6] = (int(new_y) >> 16) & 0xFF
        bPanTilt_Transmitter_Buffer[7] = (int(new_y) >> 8) & 0xFF
        bPanTilt_Transmitter_Buffer[8] = int(new_y) & 0xFF
        CRCValue = calculateCRC16 (bPanTilt_Transmitter_Buffer,9)

        bPanTilt_Transmitter_Buffer[9] = (CRCValue >> 8) & 0x00FF
        bPanTilt_Transmitter_Buffer[10] = (CRCValue >> 0) & 0x00FF


        ser.write(bPanTilt_Transmitter_Buffer)
        print(new_y)
        time.sleep(1/60)

def startSending():
    global task_thread
    global stop_flag
    global start_time
    global frequency
    global amplitude
    frequency = int(frequencyEntry.get())
    amplitude = int(amplitudeEntry.get())
    with open(file, "w") as f:
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK,os.path.getsize(f.name))
        f.write(str(frequency) + "\n" + str(amplitude))
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK,os.path.getsize(f.name))
        f.close()
    stop_flag.clear()
    start_time = time.time()
    task_thread = threading.Thread(target=sendData)
    task_thread.start()
def stopSending():
    global stop_flag
    global task_thread
    stop_flag.set()
    time.sleep(0.1)
    task_thread.join()
    print("stopped")
startButton = tkinter.Button(gui, text="Start Sending", command=startSending)
startButton.grid(row=4, column=1, pady=10, sticky="W")
stopButton = tkinter.Button(gui, text="Stop Sending", command=stopSending)
stopButton.grid(row=4, column=2, pady=10, sticky="W")
homeButton = tkinter.Button(gui, text="Go to Home", command=PanTilt_Go_TO_Home, bg="#f00", fg="#fff")
homeButton.grid(row=4, column=3, pady=10, sticky="W")
connectButton = tkinter.Button(gui, text="Connect to device", command=connectSerial)
connectButton.grid(row=0, column=4)
gui.mainloop()