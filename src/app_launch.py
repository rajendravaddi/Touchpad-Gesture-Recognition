import os
import subprocess
from tkinter import messagebox
def get_user_path():
    try:

        sudo_user = os.getenv("SUDO_USER")
        if not sudo_user:
            raise ValueError("SUDO_USER is not set. Are you running this script with sudo?")
        

        command = [
            'runuser', '-l', sudo_user, '-c',
            'source ~/.profile; source ~/.bashrc; echo $PATH'
        ]


        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  
        )
        

        if result.stderr:
            print("Error fetching PATH:")
            print(result.stderr.strip())
            return None
        

        return result.stdout.strip()

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def launch_application(app_command):
    user_env = os.environ.copy()
    command=app_command

    if command.startswith('sudo '):
        subprocess.Popen(command.split(), env=user_env)
        return

    username = os.getenv("SUDO_USER", os.getlogin())

    display = os.getenv("DISPLAY", ":0")

    user_path=get_user_path()
    command_parts = app_command.split(" ")

    try:

        app_path = subprocess.check_output(
            ["sudo", "-u", username, "env", f"PATH={user_path}", "which", command_parts[0]],
            stderr=subprocess.STDOUT
        ).decode("utf-8").strip()

        if app_path:


            subprocess.Popen(
                ["sudo", "-u", username, "env", f"DISPLAY={display}", app_path] + command_parts[1:],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print(f"Successfully launched {app_command} as the user.")
        else:
            print(f"{command_parts[0]} not found in the user's PATH.")

    except FileNotFoundError as fnf_error:
        print(f"Command not found: {fnf_error}")
        messagebox.showinfo("Command Error", f"Command not found: {fnf_error}")
    except Exception as e:
        print(f"Error launching {command}: {e}")
        messagebox.showinfo("Command Error", f"Failed to open application! Error: {e}")


