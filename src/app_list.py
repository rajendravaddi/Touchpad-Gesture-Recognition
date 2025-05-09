import os
import json
import cairosvg
def get_app_info(desktop_file_path):
    app_name = None
    exec_command = None
    icon_path = None
    try:
        with open(desktop_file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("Name=") and not app_name:
                    app_name = line.split("=", 1)[1]
                elif line.startswith("Exec=") and not exec_command:
                    exec_command = line.split("=", 1)[1]
                    exec_command = exec_command.split(" %", 1)[0]
                elif line.startswith("Icon=") and not icon_path:
                    icon_path = line.split("=", 1)[1]
    except Exception as e:
        print(f"Error reading {desktop_file_path}: {e}")
    return app_name, exec_command, icon_path

def find_icon_path(icon_name):
    # Common icon directories
    icon_dirs = [
        "/usr/share/icons/hicolor",
        "/usr/share/pixmaps",
        "/usr/share/icons",
        os.path.expanduser("~/.local/share/icons"),
    ]
    
    extensions = [".png", ".svg", ".xpm"]
    for directory in icon_dirs:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.startswith(icon_name) and any(file.endswith(ext) for ext in extensions):
                    return os.path.join(root, file)
    return None

def get_installed_gui_apps_with_commands():
    desktop_dirs = [
        "/usr/share/applications",
        "/usr/local/share/applications"
        
    ]
    app_list = {}  # To store app info
    for directory in desktop_dirs:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith(".desktop"):
                    full_path = os.path.join(directory, file)
                    app_name, exec_command, icon_name = get_app_info(full_path)
                    if app_name and exec_command:
                        icon_path = find_icon_path(icon_name) if icon_name else None
                        app_list[app_name]={
                            "command": exec_command,
                            "icon": icon_path
                        }
    app_list=update_icons(app_list)
    # Save data to JSON files
    os.makedirs("../data", exist_ok=True)
    with open("../data/app_data.json", "w") as json_file:
        json.dump(app_list, json_file, indent=4)

def update_icons(app_commands):

    
    # Ensure the temp_icons directory exists
    os.makedirs("../temp_icons", exist_ok=True)
    
    for app_name in app_commands.keys():
        app_icon_path = app_commands[app_name].get("icon")
        
        try:
            if app_icon_path and os.path.exists(app_icon_path):
                if app_icon_path.endswith(".svg"):
                    temp_png_path = f"../temp_icons/{os.path.basename(app_icon_path)}.png"
                    cairosvg.svg2png(url=app_icon_path, write_to=temp_png_path)
                    app_commands[app_name]["icon"] = temp_png_path
        except Exception as e:
            pass
    return app_commands

