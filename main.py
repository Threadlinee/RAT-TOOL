from modules import reverse_shell, beacon_sim, exfil_sim, obfuscator
import os

def save_payload(name, code):
    with open(f"payloads/{name}.py", "w") as f:
        f.write(code)
    print(f"[+] Saved payload to payloads/{name}.py")

def main():
    print("=== Payload Generator ===")
    print("[1] Reverse Shell (custom IP/port)")
    print("[2] Beacon Simulator")
    print("[3] Fake Data Exfil")

    choice = input("Choose: ")

    if choice == "1":
        ip = input("Enter IP to connect to (default 127.0.0.1): ") or "127.0.0.1"
        port_str = input("Enter port to connect to (default 4444): ") or "4444"
        try:
            port = int(port_str)
        except:
            print("Invalid port, using 4444")
            port = 4444
        code = reverse_shell.generate(ip, port)

    elif choice == "2":
        code = beacon_sim.generate()
    elif choice == "3":
        code = exfil_sim.generate()
    else:
        print("Invalid choice")
        return

    obf = input("Obfuscate with Base64? (y/n): ").lower()
    if obf == "y":
        code = obfuscator.obfuscate_base64(code)

    filename = input("Save as (filename, no .py): ")
    save_payload(filename, code)

if __name__ == "__main__":
    os.makedirs("payloads", exist_ok=True)
    main()
