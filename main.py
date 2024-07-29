import cv2
from pynput import mouse, keyboard
import subprocess
import os
import threading
from datetime import datetime
import pygetwindow as gw

# Flag to ensure the lock is triggered only once
lock_triggered = threading.Event()

# Initialize the webcam at the start of the script
print("Initializing the webcam...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open the camera.")
print("Webcam initialized.")

def minimize_current_window():
    """Minimize the currently active window."""
    window = gw.getActiveWindow()
    if window is not None:
        window.minimize()

def lock_pc():
    """Lock the PC based on the operating system."""
    try:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
    except Exception as e:
        try:
            subprocess.run(["loginctl", "lock-session"], check=True)
        except Exception as e:
            try:
                subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"], check=True)
            except Exception as e:
                try:
                    subprocess.run(["gnome-screensaver-command", "-l"], check=True)
                except Exception as e:
                    print(f"Failed to lock the system: {e}")
    os._exit(0)

def capture_image(event_type):
    """Capture an image from the webcam and save it with a timestamped filename."""
    if not lock_triggered.is_set():
        lock_triggered.set()  # Set the lock trigger to prevent re-entry
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image - end of stream reached.")
            return
        
        directory = "c:\\Users\\DEBURLUC\\Desktop\\Captures"
        print(f"Capturing image for {event_type} event...")
        print(f"Saving image to {directory}...")
        if not os.path.exists(directory):
            os.makedirs(directory)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(directory, f"{event_type}_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        
        lock_pc()

def on_move(x, y):
    print(f"Mouse moved to ({x}, {y})")
    threading.Thread(target=capture_image, args=('mouse_move',)).start()

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse click at ({x}, {y}) with {button}")
        threading.Thread(target=capture_image, args=('mouse_click',)).start()

def on_press(key):
    try:
        print(f"Key {key.char} pressed")
    except AttributeError:
        print(f"Special key {key} pressed")
    threading.Thread(target=capture_image, args=('key_press',)).start()

minimize_current_window()

mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()
print("Listeners started.")

print("Press ESC to exit.")
def on_press_for_exit(key):
    if key == keyboard.Key.esc:
        print("Just Kidding you cant escape this...")

exit_listener = keyboard.Listener(on_press=on_press_for_exit)
exit_listener.start()
exit_listener.join()

input("Press Enter to exit...")