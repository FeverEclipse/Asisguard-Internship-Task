import serial
import time
import os
import fastcrc
import tkinter
import glob
import threading

# Enter port here. COM Port on windows and '/dev/tty.~your-device-name' on macOS/Linux.
os.environ['PORT'] = '/dev/tty.usbmodem103'


gui = tkinter.Tk()
gui.title("STM32 Modbus")
serial_ports = glob.glob('/dev/tty.*')
selected_port = tkinter.StringVar()
selected_port.set(serial_ports[0] if serial_ports else "No Ports Available")
ser = None


def initSerial():
    global ser
    ser = serial.Serial(
    port=selected_port.get(),
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=100,
    xonxoff=0,
    rtscts=0)
    connectionLabel.config(bg='#0f0', text="Connected")
    connectionButton.config(state=tkinter.DISABLED)
    option_menu.config(state=tkinter.DISABLED)
    baudEntry.config(state=tkinter.DISABLED)
def readValues(startIndex, numPoints):
    ser = initSerial()
    slaveIdb = int(os.environ['SLAVE_ID']).to_bytes(1,'big') # Take the Slave ID from environment variable.
    functionIdb = b"\x03" # 0x03 is the function code for reading values.
    startAddressb = startIndex.to_bytes(2, 'big') # Take Start Address as function parameter.
    numPointsb = numPoints.to_bytes(2, 'big') # Take the requested amount of elements to read from function parameter.
    bytesWithoutCrc = slaveIdb + functionIdb + startAddressb + numPointsb
    crcBytes = fastcrc.crc16.modbus(bytesWithoutCrc).to_bytes(2, 'big') # Calculate the crc
    bytesWithCrc = bytesWithoutCrc + crcBytes
    ser.write(bytesWithCrc) # Send request to device
    time.sleep(0.05) # Wait a little to guarentee that a response has received
    ReceivedData = b""
    while ser.inWaiting() > 0:
        ReceivedData += ser.read(1) # Read bytes from the device until finished
    decoded = ''.join(f'{byte:02X}' for byte in ReceivedData) # Decode the received bytecode to string
    # Extract values from received bytes
    slaveId = decoded[0:2]
    functionId = decoded[2:4]
    numOfValuesRequested = int(int(decoded[4:6],16) / 2)
    values = []
    index = 6
    for x in range(numOfValuesRequested):
        values.append(int(decoded[index:index+4], 16))
        index += 4

    print("The Slave ID is: " + slaveId)
    print("The function ID is: " + functionId)
    print("You requested " + str(numOfValuesRequested) + " value(s).")
    print("The values are:")

    for value in values:
        print(value)
    
    ser.close()
    

stop_flag = threading.Event()
task_thread = None
slaveList = []
tempLabelList = []
def readTemp():
    while(not stop_flag.is_set()):
        for i in range(10):
            slaveIdb = int(slaveList[i].get()).to_bytes(1,'big') # Take the Slave ID from environment variable.
            functionIdb = b"\x04" # 0x04 is the function code for reading temperature.
            startingAddrb = b"\x00\x00"
            numOfRegsb = b"\x00\x01"
            bytesWithoutCrc = slaveIdb + functionIdb + startingAddrb + numOfRegsb
            crcBytes = fastcrc.crc16.modbus(bytesWithoutCrc).to_bytes(2, 'big') # Calculate the crc
            bytesWithCrc = bytesWithoutCrc + crcBytes
            ser.write(bytesWithCrc) # Send request to device    
            time.sleep(0.05) # Wait a little to guarentee that a response has received
            ReceivedData = b""
            while ser.inWaiting() > 0:
                ReceivedData += ser.read(1) # Read bytes from the device until finished
            decoded = ''.join(f'{byte:02X}' for byte in ReceivedData) # Decode the received bytecode to string
            # Extract values from received bytes
            if(decoded[2:3] == "1" or decoded[0:1] == ""):
                tempLabelList[i].config(text="ERROR")
                print("An error occurred. Please check the configuration and try again.")
                continue
            temperature = int(decoded[6:10], 16)
            tempLabelList[i].config(text=(str(temperature) + "°C"))
        time.sleep(int(selected_interval_second.get()))

        # Uncomment this and change the for loop above's range from 10 to 8 to see the last two slave ID's register values in the UI.
        '''slaveIdb = int(slaveList[8].get()).to_bytes(1,'big')
        functionIdb = b"\x07"
        startingAddrb = b"\x00\x00"
        bytesWithoutCrc = slaveIdb + functionIdb + startingAddrb
        crcBytes = fastcrc.crc16.modbus(bytesWithoutCrc).to_bytes(2, 'big')
        bytesWithCrc = bytesWithoutCrc + crcBytes
        ser.write(bytesWithCrc) # Send request to device    
        time.sleep(0.05) # Wait a little to guarentee that a response has received
        ReceivedData = b""
        while ser.inWaiting() > 0:
            ReceivedData += ser.read(1) # Read bytes from the device until finished
        decoded = ''.join(f'{byte:02X}' for byte in ReceivedData) # Decode the received bytecode to string
        if(decoded[2:3] == "1" or decoded[0:1] == ""):
            tempLabelList[8].config(text="ERROR")
            print("An error occurred. Please check the configuration and try again.")
            continue
        value = int(decoded[8:12], 16)
        tempLabelList[8].config(text=("Reg. value: " + str(value)))

        slaveIdb = int(slaveList[9].get()).to_bytes(1,'big')
        functionIdb = b"\x09"
        startingAddrb = b"\x00\x01"
        bytesWithoutCrc = slaveIdb + functionIdb + startingAddrb
        crcBytes = fastcrc.crc16.modbus(bytesWithoutCrc).to_bytes(2, 'big')
        bytesWithCrc = bytesWithoutCrc + crcBytes
        ser.write(bytesWithCrc) # Send request to device    
        time.sleep(0.05) # Wait a little to guarentee that a response has received
        ReceivedData = b""
        while ser.inWaiting() > 0:
            ReceivedData += ser.read(1) # Read bytes from the device until finished
        decoded = ''.join(f'{byte:02X}' for byte in ReceivedData) # Decode the received bytecode to string
        if(decoded[2:3] == "1" or decoded[0:1] == ""):
            tempLabelList[8].config(text="ERROR")
            print("An error occurred. Please check the configuration and try again.")
            continue
        value = int(decoded[8:12], 16)
        tempLabelList[9].config(text=("Reg. value: " + str(value)))'''
        

def on_select(selected_port):
    os.environ['PORT'] = selected_port
def startReadingTemp():
    tempButton.config(state=tkinter.DISABLED)
    tempButtonStop.config(state=tkinter.NORMAL)
    global task_thread
    global stop_flag
    stop_flag.clear()
    task_thread = threading.Thread(target=readTemp)
    task_thread.start()
def stopReadingTemp():
    tempButton.config(state=tkinter.NORMAL)
    tempButtonStop.config(state=tkinter.DISABLED)
    global stop_flag, task_thread
    stop_flag.set()

selected_interval = tkinter.StringVar()
selected_interval_second = tkinter.StringVar()
selected_interval_second.set("5")
selected_interval.set("5")
intervals= ["1","2","5","10"]

connectionButton = tkinter.Button(gui, text="Create Connection", command=initSerial)
connectionButton.grid(row=0, column=4, padx=5, pady=5)

connectionLabel = tkinter.Label(gui, text="Not Connected", bg='#f00')
connectionLabel.grid(row=0, column=5, padx=5, pady=5)

serialLabel = tkinter.Label(gui, text='Select a serial port:')
serialLabel.grid(row=0, column=0, padx=(30,0), pady=10)

option_menu = tkinter.OptionMenu(gui, selected_port, *serial_ports, command=lambda port: on_select(port))
option_menu.grid(row=0, column=1, padx=(0,5), pady=10)

baudLabel = tkinter.Label(gui, text='Baud Rate:')
baudLabel.grid(row=0, column=2, padx=(30,0), pady=10)

baudEntry = tkinter.Entry(gui)
baudEntry.insert(0, "115200")
baudEntry.grid(row=0, column=3, padx=5, pady=5)

# Start of first group
slaveLabel1 = tkinter.Label(gui, text='Slave ID')
slaveLabel1.grid(row=1,column=0, sticky="E", padx=15)

slaveLabel2 = tkinter.Label(gui, text='Slave ID')
slaveLabel2.grid(row=2,column=0, sticky="E", padx=15)

slaveLabel3 = tkinter.Label(gui, text='Slave ID')
slaveLabel3.grid(row=3,column=0, sticky="E", padx=15)

slaveLabel4 = tkinter.Label(gui, text='Slave ID')
slaveLabel4.grid(row=4,column=0, sticky="E", padx=15)

slaveLabel5 = tkinter.Label(gui, text='Slave ID')
slaveLabel5.grid(row=5,column=0, sticky="E", padx=15)

e1 = tkinter.Entry(gui, width=2)
e1.insert(0, "0")
e1.grid(row=1, column=1, padx=5, pady=5, sticky="W")
slaveList.append(e1)

e2 = tkinter.Entry(gui, width=2)
e2.insert(0, "0")
e2.grid(row=2, column=1, padx=5, pady=5, sticky="W")
slaveList.append(e2)

e3 = tkinter.Entry(gui, width=2)
e3.insert(0, "0")
e3.grid(row=3, column=1, padx=5, pady=5, sticky="W")
slaveList.append(e3)

e4 = tkinter.Entry(gui, width=2)
e4.insert(0, "0")
e4.grid(row=4, column=1, padx=5, pady=5, sticky="W")
slaveList.append(e4)

e5 = tkinter.Entry(gui, width=2)
e5.insert(0, "0")
e5.grid(row=5, column=1, padx=5, pady=5, sticky="W")
slaveList.append(e5)


tempLabel1 = tkinter.Label(gui, text='-°C')
tempLabel1.grid(row=1, column=1, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel1)

tempLabel2 = tkinter.Label(gui, text='-°C')
tempLabel2.grid(row=2, column=1, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel2)

tempLabel3 = tkinter.Label(gui, text='-°C')
tempLabel3.grid(row=3, column=1, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel3)

tempLabel4 = tkinter.Label(gui, text='-°C')
tempLabel4.grid(row=4, column=1, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel4)

tempLabel5 = tkinter.Label(gui, text='-°C')
tempLabel5.grid(row=5, column=1, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel5)


slaveLabel6 = tkinter.Label(gui, text='Slave ID')
slaveLabel6.grid(row=1,column=3, sticky="E", padx=15)

slaveLabel7 = tkinter.Label(gui, text='Slave ID')
slaveLabel7.grid(row=2,column=3, sticky="E", padx=15)

slaveLabel8 = tkinter.Label(gui, text='Slave ID')
slaveLabel8.grid(row=3,column=3, sticky="E", padx=15)

slaveLabel9 = tkinter.Label(gui, text='Slave ID')
slaveLabel9.grid(row=4,column=3, sticky="E", padx=15)

slaveLabel10 = tkinter.Label(gui, text='Slave ID')
slaveLabel10.grid(row=5,column=3, sticky="E", padx=15)

e6 = tkinter.Entry(gui, width=2)
e6.insert(0, "0")
e6.grid(row=1, column=4, padx=5, pady=5, sticky="W")
slaveList.append(e6)

e7 = tkinter.Entry(gui, width=2)
e7.insert(0, "0")
e7.grid(row=2, column=4, padx=5, pady=5, sticky="W")
slaveList.append(e7)

e8 = tkinter.Entry(gui, width=2)
e8.insert(0, "0")
e8.grid(row=3, column=4, padx=5, pady=5, sticky="W")
slaveList.append(e8)

e9 = tkinter.Entry(gui, width=2)
e9.insert(0, "0")
e9.grid(row=4, column=4, padx=5, pady=5, sticky="W")
slaveList.append(e9)

e10 = tkinter.Entry(gui, width=2)
e10.insert(0, "0")
e10.grid(row=5, column=4, padx=5, pady=5, sticky="W")
slaveList.append(e10)

tempLabel6 = tkinter.Label(gui, text='-°C')
tempLabel6.grid(row=1, column=4, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel6)

tempLabel7 = tkinter.Label(gui, text='-°C')
tempLabel7.grid(row=2, column=4, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel7)

tempLabel8 = tkinter.Label(gui, text='-°C')
tempLabel8.grid(row=3, column=4, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel8)

tempLabel9 = tkinter.Label(gui, text='-°C')
tempLabel9.grid(row=4, column=4, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel9)

tempLabel10 = tkinter.Label(gui, text='-°C')
tempLabel10.grid(row=5, column=4, sticky="W", padx=(50, 15))
tempLabelList.append(tempLabel10)


tempButton = tkinter.Button(gui, text="Start Reading\nTemperature", command=startReadingTemp)
tempButton.grid(row=6, column=3, pady=10, sticky="W")

tempButtonStop = tkinter.Button(gui, text="Stop Reading\nTemperature", command= stopReadingTemp, state=tkinter.DISABLED)
tempButtonStop.grid(row=6, column=3, pady=10,padx=(120,0))

outputView = tkinter.Text(gui, height=10, width=50)
# outputView.grid(row=3, column=0,columnspan=2, padx=(15,0), pady=0, sticky="W")
outputView.insert(tkinter.END, "OUTPUT:\n\n")
outputView.config(state=tkinter.DISABLED)

intervalLabel = tkinter.Label(gui, text="Interval(s)", padx=15, pady=0)
intervalLabel.grid(row=6, column=2, sticky="W")

interval_menu = tkinter.OptionMenu(gui, selected_interval_second, *intervals)
interval_menu.grid(row=6, column=2, padx=(80,5), pady=(15,10))

gui.mainloop()