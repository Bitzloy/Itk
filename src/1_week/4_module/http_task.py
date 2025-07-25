import socket

host = "www.google.com"
port = 80

request = "GET / HTTP/1.1\r\nHost: www.google.com\r\nConnection: close\r\n\r\n"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(request.encode())
    response = s.recv(4096)

print(response.decode(errors="ignore"))
