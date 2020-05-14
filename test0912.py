import socket

ip = "192.168.43.10"
s = socket.socket()
s.connect((str(ip), 6379))
s.send(b"INFO\r\n")
result = s.recv(1024)
if b"redis_version" in result:
    print("redis a")