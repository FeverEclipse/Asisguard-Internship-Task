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

curTime = time.time()
ser.write(fullzoombytes)
time.sleep(0.05) # Wait a little to guarentee that a response has received
ReceivedData = b""
while ser.inWaiting() > 0:
    ReceivedData += ser.read(1) # Read bytes from the device until finished
# decoded = ''.join(f'{byte:02X}' for byte in ReceivedData) # Decode the received bytecode to string
received2 = b""
count = 0
if ReceivedData == b"\x90\x42\xFF":
    while ser.in_waiting() > 0:
        received2 += ser.read(1)
    if received2 == b"\x90\x52\xFF":
        print("elapsed: " , time.time() - curTime - 0.05)
else:
    print(received2.hex())