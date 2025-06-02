def generate():
    code = '''import time

try:
    import requests
    def send_beacon():
        while True:
            try:
                requests.get("http://127.0.0.1:8000/beacon", params={"status": "ok"})
            except:
                pass
            time.sleep(10)  # beacon every 10 seconds
except ImportError:
    import urllib.request
    import urllib.parse
    def send_beacon():
        while True:
            try:
                params = urllib.parse.urlencode({"status": "ok"})
                url = f"http://127.0.0.1:8000/beacon?{params}"
                urllib.request.urlopen(url)
            except:
                pass
            time.sleep(10)

import signal
import sys

def handler(signum, frame):
    print("Beacon stopped gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

send_beacon()
'''
    return code
