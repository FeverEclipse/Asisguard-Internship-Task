import datetime
import serial
import numpy as np
import tkinter
import threading
import time
import fcntl

file = "config.txt"

CRC16_XMODEM_POLY = 0x1021
CRC16_XMODEM_INITIAL_VALUE = 0x0000

PANTILT_SYNC_BYTE = 0x55
MASTER_STM = 0x01
SLAVE_PANTILIT = 0x02
AXIS_MOVEMENT = 0x20
GO_TO_START = 0x1A

TILT_AXIS = 20

ser = serial.Serial("/dev/ttys010",
            baudrate=57600,
            write_timeout=100,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE)
global stop_flag
stop_flag = threading.Event()
task_thread = None

bPanTilt_Transmitter_Buffer = bytearray(100)

gui = tkinter.Tk()
gui.title("Pan/Tilt UI")
frequencyEntry = tkinter.Entry(gui, width=2)
frequencyEntry.insert(0, "0")
amplitudeEntry = tkinter.Entry(gui, width=2)
amplitudeEntry.insert(0, "0")
frequencyLabel = tkinter.Label(gui, text='Enter frequency: ')
frequencyLabel.grid(row=1,column=1, sticky="W", padx=15, pady=15)
frequencyEntry.grid(row=1, column=2, padx=5, pady=5)
amplitudeLabel = tkinter.Label(gui, text='Enter amplitude: ')
amplitudeLabel.grid(row=2,column=1, sticky="W", padx=15, pady=15)
amplitudeEntry.grid(row=2, column=2, padx=5, pady=5)


entered_amplitude = tkinter.IntVar()
entered_frequency = tkinter.IntVar()
entered_amplitude.set(1)
entered_frequency.set(1)

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
    with open(file, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write("0" + "\n" + "0")
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()

def Generate_Sine_Wave(frequency , amplitude):
        t = np.linspace(0,1,1000) # 1 Saniye
        y = amplitude * np.sin(2 * np.pi * frequency * t)
        return y

def Pan_Tilt_Movement_With_Velocity_On_One_Axis ():
    global stop_flag
    while True:
        if stop_flag.is_set():
            break
        print(stop_flag)
        sine_values = Generate_Sine_Wave(int(frequencyEntry.get()), int(amplitudeEntry.get()))
        sine_list = sine_values.tolist()
        for Velocity in sine_list:
            if stop_flag.is_set():
                break
            bPanTilt_Transmitter_Buffer[0] = PANTILT_SYNC_BYTE
            bPanTilt_Transmitter_Buffer[1] = MASTER_STM
            bPanTilt_Transmitter_Buffer[2] = SLAVE_PANTILIT
            bPanTilt_Transmitter_Buffer[3] = AXIS_MOVEMENT
            bPanTilt_Transmitter_Buffer[4] = 4 # Data Length

            bPanTilt_Transmitter_Buffer[5] = TILT_AXIS
            bPanTilt_Transmitter_Buffer[6] = (int(Velocity) >> 16) & 0xFF
            bPanTilt_Transmitter_Buffer[7] = (int(Velocity) >> 8) & 0xFF
            bPanTilt_Transmitter_Buffer[8] = int(Velocity) & 0xFF

            CRCValue = calculateCRC16(bPanTilt_Transmitter_Buffer,9)

            bPanTilt_Transmitter_Buffer[9] = (CRCValue >> 8) & 0x00FF
            bPanTilt_Transmitter_Buffer[10] = (CRCValue >> 0) & 0x00FF
            #ser.write(bPanTilt_Transmitter_Buffer)
            print("sent")
            time.sleep(0.05)

def startSending():
    global task_thread
    global stop_flag
    with open(file, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(frequencyEntry.get() + "\n" + amplitudeEntry.get())
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
    stop_flag.clear()
    task_thread = threading.Thread(target=Pan_Tilt_Movement_With_Velocity_On_One_Axis)
    task_thread.start()

def stopSending():
    global stop_flag
    global task_thread
    stop_flag.set()
    time.sleep(1)
    task_thread.join()
    print("stopped")

startButton = tkinter.Button(gui, text="Start Sending", command=startSending)
startButton.grid(row=3, column=1, pady=10, sticky="W")
stopButton = tkinter.Button(gui, text="Stop Sending", command=stopSending)
stopButton.grid(row=3, column=3, pady=10, sticky="W")
homeButton = tkinter.Button(gui, text="Go to Home", command=PanTilt_Go_TO_Home)
homeButton.grid(row=4, column=2, pady=10, sticky="W")
gui.mainloop()
