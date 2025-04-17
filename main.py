import json
import platform
import subprocess
import shutil
import os

def load_program_list(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        # "Program list file not found."
        return {}

def ensure_chocolatey_installed():
    if shutil.which("choco"):
        return True

    # "Chocolatey not found. Attempting to install..."

    choco_install_script = r'''
Set-ExecutionPolicy Bypass -Scope Process -Force; 
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
iex ((New-Object System.Net.WebClient).DownloadString('https:#chocolatey.org/install.ps1'))
'''

    try:
        subprocess.run([
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-Command", choco_install_script
        ], check=True)
        # "Chocolatey installed."
        return True
    except subprocess.CalledProcessError as e:
        # f"Error during Chocolatey installation: {e}"
        pass
    except FileNotFoundError:
        #"PowerShell not found. Installation failed."
        pass

    return False

def install_for_win(package_name):
    try:
        subprocess.run(["choco", "install", package_name, "-y"], check=True)
        # f"[Windows] Installed: {package_name}"
        return True
    except subprocess.CalledProcessError as e:
        # f"[Windows] Error installing {package_name}: {e}"
        pass
    return False

def install_for_linux(package_name):
    try:
        subprocess.run(["sudo", "apt", "install", package_name, "-y"], check=True)
        # f"[Linux] Installed: {package_name}"
        return True
    except subprocess.CalledProcessError as e:
        # f"[Linux] Error installing {package_name}: {e}"
        pass
    return False

def run_installer():
    programs = load_program_list("programs.json")
    os_type = platform.system().lower()

    if "win" in os_type:
        if not ensure_chocolatey_installed():
            # "Unable to continue without Chocolatey."
            return
        for program in programs.get("windows", []):
            install_for_win(program)

    elif "linux" in os_type:
        for program in programs.get("linux", []):
            install_for_linux(program)

    else:
        # "Unsupported operating system:", os_type
        pass

if __name__ == "main":
    run_installer()