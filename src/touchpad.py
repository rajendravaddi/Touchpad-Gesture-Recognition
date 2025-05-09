import tkinter as tk
from evdev import InputDevice, categorize, ecodes
import threading
import json
from PIL import Image
import cv2,os
import recognization_gesture_model as rgm
# Find your touchpad device
TOUCHPAD_DEVICE_PATH = '/dev/input/event5'  # Replace this with your touchpad's event path

# Global variables to store touch positions
touch_positions = []
touch_positions2 = []
stop_capture = False  # Flag to control when to stop capture
App_name=''
App_command=''
# Function to capture touchpad events
def capture_touchpad_events():
    global touch_positions, touch_positions2, stop_capture
    dev = InputDevice(TOUCHPAD_DEVICE_PATH)

    for event in dev.read_loop():
        if stop_capture:  # Check if data collection should stop
            break
        if event.type == ecodes.EV_ABS:
            abs_event = categorize(event)
            # Capture X and Y positions (ABS_MT_POSITION_X, ABS_MT_POSITION_Y for multi-touch devices)
            if abs_event.event.code == ecodes.ABS_MT_POSITION_X:
                x = abs_event.event.value
            elif abs_event.event.code == ecodes.ABS_MT_POSITION_Y:
                y = abs_event.event.value
                # Append the x and y positions to touch_positions
                touch_positions.append((x, y))
                touch_positions2.append((x, y))

# Function to save the data to a JSON file and save the canvas as an image
def on_window_close(event=None):
    global touch_positions, stop_capture,Callback,App_name

    # Clear touch_positions
    touch_positions.clear()
    touch_positions2.clear()
    print("Window closed. Touch positions cleared.")

    # Stop capturing events
    stop_capture = True

    # Exit the Tkinter main loop after ensuring capture is stopped
    root.after(100, lambda: [root.quit(), root.destroy()])
    Callback(App_name,False)
def save_data_and_exit():
    global touch_positions, touch_positions2, root, canvas, stop_capture,App_name,App_command,Callback
    # Set the flag to stop capturing data
    stop_capture = True

    # Save the canvas as a PostScript file
    canvas.postscript(file=f"../data/temporary/{App_name}.ps", colormode="color")
    print("Canvas saved as PostScript file.")

    # Convert the PostScript file to a PNG image
    with Image.open(f"../data/temporary/{App_name}.ps") as img:
        img.save(f"../data/temporary/{App_name}.jpeg", "jpeg")
    os.remove(f"../data/temporary/{App_name}.ps")
    print("Canvas image saved as canvas_output.png.")
    # Exit the Tkinter main loop after a small delay to ensure the quit works
    root.after(100, lambda: [root.quit(), root.destroy()])  # Ensure both quit and destroy are called
    check_validity()
def check_validity():
    global App_name,Callback,App_command
    validity=rgm.match_already_exists(f'../data/temporary/{App_name}.jpeg')
    if validity is None:
        #img1 = cv2.imread(f"data/temporary/{App_name}.jpeg", cv2.IMREAD_GRAYSCALE)   #image2.jpg is created collecting the data
        print('Unique')
#img is a array .convert to list to store in json

        Callback(App_name,True)
    else:
        print('exist')
        os.remove(f'../data/temporary/{App_name}.jpeg')
        Callback(App_name,False)
# Function to handle Enter key press in Tkinter
def on_enter_press(event):
    if not stop_capture:  # Ensure that Enter only stops the capture once
        print("Enter key pressed. Stopping data collection.")
        save_data_and_exit()

# Function to draw touchpad input on the canvas
def draw_on_canvas():
    global touch_positions

    for pos in touch_positions:
        x, y = pos
        # Scaling the touchpad values to fit on the canvas (adjust scaling as necessary)
        scaled_x = x / 10  # Adjust this scaling factor based on your touchpad resolution
        scaled_y = y / 10
        canvas.create_oval(scaled_x, scaled_y, scaled_x + 5, scaled_y + 5, fill="black")

    # Clear the list after drawing to avoid redundant drawing
    touch_positions.clear()

    # Continuously update the canvas unless data capture has stopped
    if not stop_capture:
        root.after(50, draw_on_canvas)

# Main function to set up the Tkinter GUI
def setup_gui():
    global root, canvas,App_name

    # Initialize the Tkinter window
    root = tk.Tk()
    root.title(App_name)
    root.geometry("500x350")
    tk.Label(root, text=f"Draw Gesture for {App_name} on touchpad", font=("Arial", 14)).pack(pady=10)
    canvas = tk.Canvas(root, bg="white", width=300, height=170, borderwidth=2, relief="solid")
    canvas.pack(pady=10)
    tk.Label(root, text="Press 'Enter' to Save \nPress 'Esc' to cancel", font=("Arial", 14)).pack(pady=10)

    # Bind the Enter key to trigger data saving and exit
    root.bind('<Return>', on_enter_press)
    root.protocol("WM_DELETE_WINDOW", on_window_close)
    root.bind("<Escape>",on_window_close)
    # Start drawing on the canvas at intervals
    root.after(50, draw_on_canvas)

    # Start the Tkinter main loop
    root.mainloop()

# Function to start the touchpad event capture in a separate thread
def start_touchpad_thread():
    touchpad_thread = threading.Thread(target=capture_touchpad_events)
    touchpad_thread.daemon = True  # Ensure the thread exits when the main program does
    touchpad_thread.start()

# Main execution
def capture_gesture(app_name,app_command,callback):
    global stop_capture,App_name,App_command,Callback
    App_name=app_name
    App_command=app_command
    Callback=callback
    stop_capture = False
    # Start capturing touchpad events in the background
    start_touchpad_thread()

    # Set up and run the GUI
    setup_gui()

