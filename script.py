import subprocess
import sys

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")

def main():
    libraries = [
        "pyautogui",        # For taking screenshots
        "pynput",           # For keylogging
        "psutil",           # For process listing
        "requests",         # (Optional) For making HTTP requests if needed
        "Pillow",           # For image processing (pyautogui may require it)
    ]

    for lib in libraries:
        print(f"Installing {lib}...")
        install(lib)
        print(f"{lib} installed successfully.")

if __name__ == "__main__":
    main()
