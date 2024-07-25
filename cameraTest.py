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

initbytes = b"\x81\x01\x04\x19\x01\xFF"
defaultzoombytes = b"\x81\x01\x04\x47\x00\x00\x00\x00\xFF"
fullzoombytes = b"\x81\x01\x04\x47\x04\x00\x00\x00\xFF"

ser.write(fullzoombytes)
curTime = time.time()
ReceivedData = b""
while ser.inWaiting() < 6:
    time.sleep(0.01) # Read bytes from the device until finished
ReceivedData += ser.read(6)
if ReceivedData == b"\x90\x42\xFF\x90\x52\xFF":
    print("elapsed: " , time.time() - curTime)
