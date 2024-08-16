import subprocess
import sys

# List of required libraries
required_libraries = ['pynput', 'pyautogui', 'pillow']

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"'{package}' has been installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install '{package}'. Error: {str(e)}")

def main():
    for library in required_libraries:
        try:
            __import__(library)
            print(f"'{library}' is already installed.")
        except ImportError:
            print(f"'{library}' is not installed. Installing now...")
            install_package(library)

if __name__ == "__main__":
    main()
