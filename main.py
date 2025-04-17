import shutil
import tkinter as tk
from tkinter import messagebox
import json
import platform
import subprocess
import os
import sys


def load_program_list(file_name):
    try:
        if getattr(sys, 'frozen', False):
            file_name = os.path.join(sys._MEIPASS, file_name)

        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def ensure_chocolatey_installed():
    if shutil.which("choco"):
        return True

    # Chocolatey не найден, пытаемся установить его
    choco_install_script = r'''
    Set-ExecutionPolicy Bypass -Scope Process -Force; 
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    '''

    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", choco_install_script],
            check=True,
            shell=True
        )
        #"Chocolatey installed successfully."
        return True
    except subprocess.CalledProcessError as e:
        # Ошибка при установке
        messagebox.showerror("Error", f"Error during Chocolatey installation: {e}")
        return False
    except FileNotFoundError:
        # PowerShell не найден
        messagebox.showerror("Error", "PowerShell not found. Chocolatey installation failed.")
        return False

def is_installed_win(package_name):
    try:
        result = subprocess.run(
            ["choco", "list", "--local-only", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        return package_name.lower() in result.stdout.lower()
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"[Linux] Error installing {package_name}: {e}")
        return False


def install_for_win(package_name):
    if is_installed_win(package_name):
        return True

    try:
        subprocess.run(["choco", "install", package_name, "-y"], check=True)
        # f"[Windows] Installed: {package_name}"
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"[Windows] Error installing {package_name}: {e}")
        return False


def is_installed_linux(package_name):
    try:
        subprocess.run(
            ["dpkg", "-s", package_name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"[Linux] Error installing {package_name}: {e}")
        return False


def install_for_linux(package_name):
    def install_for_linux(package_name):
        if is_installed_linux(package_name):
            return True

    try:
        subprocess.run(["sudo", "apt", "install", package_name, "-y"], check=True)
        # f"[Linux] Installed: {package_name}"
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"[Linux] Error installing {package_name}: {e}")
        return False


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Program Installer")
    root.geometry("400x400")

    programs = load_program_list("programs.json")
    os_type = platform.system().lower()
    programs_user_choice = []

    for program in programs:
        name = program["name"]
        var = tk.BooleanVar()
        chk = tk.Checkbutton(root, text=name, variable=var)
        chk.pack(anchor="w")
        programs_user_choice.append((var, program))

    def install_selected():
        for var, program in programs_user_choice:
            if var.get():
                if "win" in os_type:
                    if not ensure_chocolatey_installed():
                        messagebox.showerror("Error", "Chocolatey installation failed.")
                        return
                    install_for_win(program["windows"])
                elif "linux" in os_type:
                    install_for_linux(program["linux"])
                else:
                    messagebox.showerror("Error", f"Unsupported OS: {os_type}")
        messagebox.showinfo("Done", "Installation complete!")

    install_button = tk.Button(root, text="Install Selected", command=install_selected)
    install_button.pack(pady=10)

    root.mainloop()