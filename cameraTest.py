import serial
import time

ser = serial.Serial(
    port='COM26',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=100,
    xonxoff=0,
    rtscts=0
)

'''1 -> 0000
   2 -> 1571
   3 -> 1F4A
   4 -> 2543
   5 -> 296C
   6 -> 2C9F
   7 -> 2F2F
   8 -> 315A
   9 -> 333C
   10 -> 34E8
   11 -> 3670
   12 -> 37C9
   13 -> 38FF
   14 -> 3A19
   15 -> 3B0F
   16 -> 3BE0
   17 -> 3C96
   18 -> 3D31
   19 -> 3DB0
   20 -> 3E1E
   21 -> 3E79
   22 -> 3EC1
   23 -> 3F0A
   24 -> 3F41
   25 -> 3F6E
   26 -> 3F93
   27 -> 3FB7
   28 -> 3FD2
   29 -> 3FE5
   30 -> 4000
'''

zoom_values = [
    b"\x00\x00",
    b"\x15\x71",
    b"\x1F\x4A",
    b"\x25\x43",
    b"\x29\x6C",
    b"\x2C\x9F",
    b"\x2F\x2F",
    b"\x31\x5A",
    b"\x33\x3C",
    b"\x34\xE8",
    b"\x36\x70",
    b"\x37\xC9",
    b"\x38\xFF",
    b"\x3A\x19",
    b"\x3B\x0F",
    b"\x3B\xE0",
    b"\x3C\x96",
    b"\x3D\x31",
    b"\x3D\xB0",
    b"\x3E\x1E",
    b"\x3E\x79",
    b"\x3E\xC1",
    b"\x3F\x0A",
    b"\x3F\x41",
    b"\x3F\x6E",
    b"\x3F\x93",
    b"\x3F\xB7",
    b"\x3F\xD2",
    b"\x3F\xE5",
    b"\x40\x00"
]

initbytes = b"\x81\x01\x04\x19\x01\xFF"
defaultzoombytes = b"\x81\x01\x04\x47\x00\x00\x00\x00\xFF"
fullzoombytes = b"\x81\x01\x04\x47\x04\x00\x00\x00\xFF"

for i in range(30):
    cur_zoom_bytes = b"\x81\x01\x04\x47" + zoom_values[i] + b"\xFF"
    ser.write(cur_zoom_bytes)
    curTime = time.time()
    ReceivedData = b""
    while ser.inWaiting() < 6:
        time.sleep(0.01) # Read bytes from the device until finished
    ReceivedData += ser.read(6)
    if ReceivedData == b"\x90\x42\xFF\x90\x52\xFF":
        print("elapsed" , i, "-", i+1 ,time.time() - curTime)
