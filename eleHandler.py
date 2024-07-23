import requests
import socket

UDP_IP = "10.10.10.54"
UDP_LATLON_PORT = 11453
UDP_ELE_PORT = 1453

lat = 0
lon = 0

def elevation():
    global lat
    global lon
    url = "https://api.open-elevation.com/api/v1/lookup?locations=" + str(lat) + "," + str(lon)
    r = requests.get(url=url)
    data = r.json()
    elevation = data['results'][0]['elevation']
    return elevation

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((UDP_IP, UDP_LATLON_PORT))
    msg, address = s.recvfrom(1024)
    print("Received Message!")
    msg = msg.decode("utf-8")
    lat = msg.split(",")[0]
    lon = msg.split(",")[0]
    ele = elevation()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(str(ele).encode("utf-8"), (UDP_IP, UDP_ELE_PORT))
