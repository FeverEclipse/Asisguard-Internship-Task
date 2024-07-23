import requests
import socket
import select

UDP_IP = "10.10.10.54"
UDP_LATLON_PORT = 11453
UDP_ELE_PORT = 1453

lat = 0
lon = 0

def elevation():
    global lat
    global lon
    if lat == "":
        lat = 0
    if lon == "":
        lon = 0
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    r = requests.get(url=url)
    data = r.json()
    return data['results'][0]['elevation']

# Create and bind the socket once
latlon_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
latlon_socket.bind((UDP_IP, UDP_LATLON_PORT))

# Create the socket for sending elevation data
elevation_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # Use select to wait for data with a timeout
    ready_sockets, _, _ = select.select([latlon_socket], [], [], 1)
    if ready_sockets:
        msg, address = latlon_socket.recvfrom(1024)
        print("Received Message!")
        msg = msg.decode("utf-8")
        lat, lon = msg.split(",")
        ele = elevation()
        elevation_socket.sendto(str(ele).encode("utf-8"), (UDP_IP, UDP_ELE_PORT))
