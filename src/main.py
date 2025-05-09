import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import subprocess
import json
import app_list
import touchpad, os
import cairosvg
# Global variables
is_password_validated = False  ###
app_commands = {}
view_apps = {'created':[],'uncreated':[]}
perform_keys = []
# Load commands from data.json
def load_app_commands():
    global app_commands, view_apps, perform_keys
    
    try:
        with open("../data/app_data.json", "r") as f:
            app_commands = json.load(f)
    except FileNotFoundError:
        app_list.get_installed_gui_apps_with_commands()
        with open("../data/app_data.json", "r") as f:
            app_commands = json.load(f)
    try:
        with open("../data/apps_info.json", "r") as f:
            view_apps = json.load(f)
    except FileNotFoundError:
        with open("../data/apps_info.json", "w") as f:
            view_apps['uncreated']=list(app_commands.keys())
            json.dump(view_apps, f)
    except json.JSONDecodeError:
        with open("../data/apps_info.json", "w") as f:
            view_apps['uncreated']=list(app_commands.keys())
            json.dump(view_apps, f)
    try:
        with open("../data/perform_keys.json", "r") as f:
            perform_keys = json.load(f)
    except FileNotFoundError:
        with open("../data/perform_keys.json", "w") as f:
            json.dump(perform_keys, f)
    except json.JSONDecodeError:
        with open("../data/perform_keys.json", "w") as f:
            json.dump(perform_keys, f)

# Validate password securely (called only once at startup)
def validate_password(callback=None):
    global is_password_validated

    if is_password_validated:
        if callback:
            callback()
        return

    def verify():
        global is_password_validated
        entered_password = password_entry.get()
        try:
            command = f"echo {entered_password} | sudo -S -k echo Password Validated"
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if "Password Validated" in result.stdout:
                password_window.destroy()
                is_password_validated = True
                if callback:
                    callback()
            else:
                raise subprocess.CalledProcessError(returncode=1, cmd=command)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Invalid password. Please try again.")

    # Password prompt window
    password_window = tk.Toplevel(root)
    password_window.title("Password Validation")
    password_window.geometry("300x150")

    tk.Label(password_window, text="Enter your device password:", font=("Arial", 12)).pack(pady=10)
    password_entry = tk.Entry(password_window, show="*", width=25)
    password_entry.pack(pady=5)

    tk.Button(password_window, text="Submit", command=verify).pack(pady=10)

def modify_files():
    with open("../data/apps_info.json", "w") as f:
        json.dump(view_apps, f)



# Enable scrolling with the mouse wheel
def bind_mousewheel_to_canvas(canvas):
    def on_mousewheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")  # For Windows/macOS
    canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows/macOS scrolling
    canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))  # Linux scroll up
    canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))  # Linux scroll down

def modify_filepath(app_name):
    if os.path.exists(f"../data/gestures/{app_name}.jpeg"):
        os.remove(f"../data/gestures/{app_name}.jpeg")
    os.rename(f"../data/temporary/{app_name}.jpeg", f"../data/gestures/{app_name}.jpeg")
# Create Gesture
def create_gesture():
    global is_password_validated
    def proceed_create():
        clear_right_frame()

        tk.Label(right_frame, text="Search Application", font=("Arial", 14)).pack(pady=10)
        search_var = tk.StringVar()

        def filter_apps(*args):
            search_term = search_var.get().lower()
            filtered_apps = [app for app in view_apps['uncreated'] if search_term in app.lower()]
              # No Results found 
            if not filtered_apps:
            	for widget in app_frame.winfo_children():
            		widget.destroy();
            	search_entry.config(highlightbackground="red", highlightcolor="red")
            	no_results_label = tk.Label(app_frame, text="No results found", font=("Arial", 14), fg="red")
            	no_results_label.pack(pady=20)
            else:
            	update_app_list(filtered_apps)
            	search_entry.config(highlightcolor="lightgreen")
         
        search_var.trace_add("write", filter_apps)
        search_entry = tk.Entry(right_frame,fg="blue", textvariable=search_var, font=("Arial", 15),width=50)
        search_entry.pack(pady=5)

        app_list_frame = tk.Frame(right_frame)
        app_list_frame.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(app_list_frame)
        scroll_y = tk.Scrollbar(app_list_frame, orient="vertical", command=canvas.yview)

        app_frame = tk.Frame(canvas)

        app_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=app_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

          # Bind mousewheel scrolling
        bind_mousewheel_to_canvas(canvas)
        def gesture_result(app_name, status):
            if status:
                view_apps['created'].append(app_name)
                view_apps['uncreated'].remove(app_name)
                modify_filepath(app_name)
                modify_files()
                messagebox.showinfo("Gesture created","Gesture has been created successfully!")
                filter_apps("")
            else:
                messagebox.showinfo("Gesture not created","Gesture not created!")
                filter_apps("")

        def update_app_list(applications):
            for widget in app_frame.winfo_children():
                widget.destroy()

            for app_name in applications:
                app_icon_path = app_commands[app_name].get("icon")

                if app_icon_path and os.path.exists(app_icon_path):
                    icon_image = Image.open(app_icon_path)
                    icon_image = icon_image.resize((24, 24), Image.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    btn = tk.Button(app_frame, text=app_name, image=icon_photo, compound="left",
                            command=lambda app=app_name: touchpad.capture_gesture(
                                app, app_commands[app]["command"], callback=gesture_result),
                            width=300, pady=5, bg="white", anchor='w')
                    btn.image = icon_photo  # Keep a reference to avoid garbage collection
                    btn.pack(pady=5)
                else:
                    btn = tk.Button(app_frame, text=app_name, command=lambda app=app_name: touchpad.capture_gesture(
                app, app_commands[app]["command"], callback=gesture_result), width=38, pady=5, bg="white", anchor='w')
                    btn.pack(pady=5)

                

        update_app_list(view_apps['uncreated'])
    if is_password_validated:
        proceed_create()
    else:
        validate_password()
        
def gesture_result_(app_name, status):
    if status:
        modify_filepath(app_name)
        messagebox.showinfo("Gesture modified","Gesture has been modified successfully!")
    else:
        messagebox.showinfo("Gesture not modified","Gesture already exists, please try another!")
# View Gestures
def view_gestures():
    global is_password_validated,app_commands,view_apps
    def proceed_view():
        clear_right_frame()
        tk.Label(right_frame, text="Select Application to View Gesture", font=("Arial", 14)).pack(pady=10)

        gestures = view_apps['created']

        def open_gesture_view(app_name, gesture_image_path):
            view_window = tk.Toplevel(root)
            view_window.title(app_name)
            view_window.geometry("500x350")

            tk.Label(view_window, text=f"Gesture for {app_name}", font=("Arial", 14)).pack(pady=10)

            img = Image.open(gesture_image_path)
            img = img.resize((300, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            tk.Label(view_window, image=photo).pack(pady=10)
            view_window.image = photo

            tk.Button(view_window, text="Modify Gesture", command=lambda: modify_gesture(view_window, app_name)).pack(pady=5)
            tk.Button(view_window, text="Delete Gesture", command=lambda: delete_gesture(view_window, app_name)).pack(pady=5)

        for gesture in gestures:
            app_icon_path = app_commands[gesture].get("icon")

            if app_icon_path and os.path.exists(app_icon_path):
                icon_image = Image.open(app_icon_path)
                icon_image = icon_image.resize((24, 24), Image.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                btn = tk.Button(right_frame, text=gesture, image=icon_photo, compound="left",
                                command=lambda g=gesture: open_gesture_view(g, f"../data/gestures/{g}.jpeg"),
                                width=300, pady=5, bg="white", anchor='w')
                btn.image = icon_photo  # Keep a reference to avoid garbage collection
                btn.pack(pady=5)
            else:
                btn = tk.Button(right_frame, text=gesture, command=lambda g=gesture: open_gesture_view(g, f"../data/gestures/{g}.jpeg"), width=38, pady=5, bg="white", anchor='w')
                btn.pack(pady=5)

    if is_password_validated:
        proceed_view()
    else:
        validate_password()

def select_perform_keys():
    global perform_keys
    clear_right_frame()  # Clear the right frame
    selected_keys = perform_keys
    KEYS = [
        ['esc', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'delete'],
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'backspace'],
        ['tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
        ['caps lock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'enter'],
        ['shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'right shift'],
        ['ctrl', 'alt', 'space']
    ]


    def select_key(key):
        """Handles key selection"""
        if key in selected_keys:
            selected_keys.remove(key)  # Deselect if already selected
        elif len(selected_keys) < 3:
            selected_keys.append(key)  # Allow up to 3 selections
        update_selected_display()

    def update_selected_display():
        """Update the selected keys display"""
        selected_label.config(text="Selected: " + ", ".join(selected_keys))

    def save_keys():
        if len(selected_keys)==0:
            messagebox.showinfo("NOT Saved","Please select 1-3 keys !")
            return
        """Save selected keys to JSON file"""
        with open("../data/perform_keys.json", "w") as file:
            json.dump(selected_keys, file, indent=4)
            messagebox.showinfo("Saved", "Selected keys saved successfully!")

    # Keyboard Frame inside `right_frame`
    keyboard_frame = tk.Frame(right_frame, bg="white")
    keyboard_frame.pack(pady=10)

    # Display keys as buttons in a grid
    for r, row in enumerate(KEYS):
        for c, key in enumerate(row):
            btn = tk.Button(
                keyboard_frame, text=key.capitalize() if key.islower() else key,
                width=5, height=2, command=lambda k=key: select_key(k)
            )
            btn.grid(row=r, column=c, padx=2, pady=2)

    # Selected Keys Display
    selected_label = tk.Label(right_frame, text="Selected: ", font=("Arial", 12))
    selected_label.pack(pady=10)

    # Save Button
    save_button = tk.Button(right_frame, text="Save", font=("Arial", 12, "bold"),
                            command=save_keys, width=10, bg="green", fg="white")
    save_button.pack(pady=10, side="right", padx=20)
    update_selected_display()

# Placeholder gesture methods
def modify_gesture(view_window,app_name):
    global app_commands, view_apps
    # Placeholder for modify functionality
    touchpad.capture_gesture(app_name, app_commands[app_name]["command"], callback=gesture_result_)
    
    view_window.destroy()
    messagebox.showinfo("Gesture modified","Gesture has been modified successfully!")
    view_gestures()

def delete_gesture(view_window, app_name):
    global app_commands, view_apps
    
    os.remove(f'../data/gestures/{app_name}.jpeg')
    view_apps['created'].remove(app_name)
    view_apps['uncreated'].append(app_name)
    modify_files()
    view_window.destroy()
    messagebox.showinfo("Gesture deleted","Gesture has been deleted successfully!")
    view_gestures()

# Clear right frame
def clear_right_frame():
    for widget in right_frame.winfo_children():
        widget.destroy()

# Create folders for data and gestures
folder_path = '../data/gestures'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
folder_pat = '../data/temporary'
if not os.path.exists(folder_pat):
    os.makedirs(folder_pat)

# Main Application Window
root = tk.Tk()
root.title("TouchPad Gesture Recognition")
root.geometry("800x600")

# Left Frame (Navigation)
left_frame = tk.Frame(root, width=200, bg="lightgrey")
left_frame.pack(side="left", fill="y")

# Right Frame (Content)
right_frame = tk.Frame(root, bg="white")
right_frame.pack(side="right", expand=True, fill="both")

# Buttons in the Left Frame
options = ["Create Gesture", "View Gestures", "Select Perform Keys"]
commands = [create_gesture, view_gestures, select_perform_keys]  # Add function reference


for option, command in zip(options, commands):
    btn = tk.Button(left_frame, text=option, command=command, width=20, pady=10, bg="white")
    btn.pack(pady=5)

# Load app commands
load_app_commands()

# Start the Application
root.mainloop()
validate_password(lambda:None)
