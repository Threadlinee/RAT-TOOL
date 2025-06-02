import subprocess

def build_exe(py_path):
    try:
        result = subprocess.run(
            ["pyinstaller", "--onefile", "--noconsole", py_path],
            capture_output=True,
            text=True,
            check=True
        )
        print("[+] Build succeeded.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("[!] Build failed.")
        print(e.stdout)
        print(e.stderr)
