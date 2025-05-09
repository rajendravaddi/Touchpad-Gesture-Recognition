import threading
import keyboard
import time,create_canvas
import json
from evdev import InputDevice, categorize, ecodes, list_devices
from select import select
import app_launch
# Global variables
collecting = False  # Flag to control collection
coordinates = []    # List to store coordinates
with open('../data/perform_keys.json','r') as f:
    Trigger_keys = json.load(f)
Trigger_keys=set(Trigger_keys)
# Identify the touchpad device
devices = [InputDevice(path) for path in list_devices()]
touchpad = None
for device in devices:
    if 'touchpad' in device.name.lower():
        touchpad = device
        break

if not touchpad:
    raise Exception("Touchpad device not found")

def clear_touchpad_buffer():
    """Clear all pending events from the touchpad buffer."""
    while True:
        try:
            for _ in touchpad.read():
                pass  # Consume and discard all events
        except BlockingIOError:
            break  # Exit when no more events are available
            
def collect_coordinates():
    """Read events from the touchpad device."""
    global collecting, coordinates
    print("Collecting coordinates... Press 'space bar' to stop.")
    clear_touchpad_buffer()
    # Variables to store the last known x and y values
    last_x = None
    last_y = None

    while collecting:
        r, w, x = select([touchpad], [], [])
        if not collecting:
            break
        try:
            for event in touchpad.read(): # Attempt to read all available events
                if event.type == ecodes.EV_ABS:
                    absevent = categorize(event)
                    if absevent.event.code == ecodes.ABS_X:
                        last_x = absevent.event.value
                    elif absevent.event.code == ecodes.ABS_Y:
                        last_y = absevent.event.value

                    # Append only when both x and y are available
                    if last_x is not None and last_y is not None:
                        #print("reading coordinate",[last_x, last_y])
                        coordinates.append([last_x, last_y])
                        # Clear the values to avoid duplicates
                        last_x = None
                        last_y = None
        except BlockingIOError:
            # No data is available to read; continue to next iteration
            continue

def toggle_collecting():
    global collecting,coordinates
    if not collecting:
        collecting = True
        print("Recording started... Draw on the touchpad.")
        threading.Thread(target=collect_coordinates, daemon=True).start()
    else:
        collecting = False
        if coordinates:
            command=create_canvas.draw(coordinates)
            if command:
                app_launch.launch_application(command)
        coordinates.clear()
        print("Stopping recording... Please wait.")

def main():
    print("Program is running.")
    print(f"Press and hold {Trigger_keys} to start collecting coordinates.")
    print(f"Release {Trigger_keys} stop recording.")

    while True:
        if all(keyboard.is_pressed(key) for key in Trigger_keys):  # Check if the space bar is held down
            if not collecting:
                toggle_collecting()  # Start collecting coordinates
        else:
            if collecting:
                toggle_collecting()  # Stop collecting coordinates

        if keyboard.is_pressed('esc'):  # Exit condition for the program
            print("Program terminated.")
            break
if __name__ == "__main__":
    main()
