import subprocess
import sys

def install_packages():
    # List of required packages
    packages = ["pyautogui", "pynput"]

    # Install each package
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install_packages()
