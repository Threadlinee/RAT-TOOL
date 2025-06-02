import base64

def obfuscate_base64(script_code):
    encoded_once = base64.b64encode(script_code.encode())
    encoded_twice = base64.b64encode(encoded_once)
    return f'''import base64
exec(base64.b64decode(base64.b64decode("{encoded_twice.decode()}")))'''
