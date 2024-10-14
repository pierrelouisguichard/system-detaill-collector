import platform
import socket
import psutil
import subprocess
import tkinter as tk
from tkinter import scrolledtext

def get_basic_info():
    """Collects basic system information."""
    info = {
        "PC Name": socket.gethostname(),
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Machine Type": platform.machine(),
        "Processor": platform.processor(),
        "CPU Cores (Logical)": psutil.cpu_count(logical=True),
        "CPU Cores (Physical)": psutil.cpu_count(logical=False),
        "Total RAM": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        "Available RAM": f"{round(psutil.virtual_memory().available / (1024 ** 3), 2)} GB",
        "IP Address": socket.gethostbyname(socket.gethostname()),
    }
    return info

def get_windows_specific_info():
    """Fetches hardware information for Windows using WMIC."""
    try:
        cpu_info = subprocess.check_output("wmic cpu get Name, Manufacturer", shell=True).decode().strip()
        motherboard_info = subprocess.check_output("wmic baseboard get Product, Manufacturer", shell=True).decode().strip()
        gpu_info = subprocess.check_output("wmic path win32_VideoController get Name, AdapterCompatibility", shell=True).decode().strip()
        disk_info = subprocess.check_output("wmic diskdrive get Model, Manufacturer", shell=True).decode().strip()
        return f"CPU:\n{cpu_info}\n\nMotherboard:\n{motherboard_info}\n\nGPU:\n{gpu_info}\n\nDisk:\n{disk_info}"
    except Exception as e:
        return f"Failed to get Windows-specific info: {e}"

def get_mac_specific_info():
    """Fetches hardware information for macOS using system commands."""
    try:
        cpu_info = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode().strip()
        gpu_info = subprocess.check_output("system_profiler SPDisplaysDataType | grep 'Chipset Model'", shell=True).decode().strip()
        disk_info = subprocess.check_output("diskutil info / | grep 'Device / Media Name'", shell=True).decode().strip()
        return f"CPU: {cpu_info}\n\nGPU:\n{gpu_info}\n\nDisk:\n{disk_info}"
    except Exception as e:
        return f"Failed to get macOS-specific info: {e}"

def get_system_info():
    """Fetches and returns all relevant system information."""
    info = get_basic_info()
    result = "\n".join(f"{key}: {value}" for key, value in info.items())

    if platform.system() == "Windows":
        result += f"\n\n=== Windows Specific Info ===\n{get_windows_specific_info()}"
    elif platform.system() == "Darwin":
        result += f"\n\n=== macOS Specific Info ===\n{get_mac_specific_info()}"
    else:
        result += "\n\nThis tool only supports Windows and macOS."

    return result

def display_info():
    """Fetches and displays system info in the text area."""
    info = get_system_info()
    text_area.config(state=tk.NORMAL)  # Allow writing to the text area
    text_area.delete(1.0, tk.END)  # Clear previous content
    text_area.insert(tk.END, info)  # Display new content
    text_area.config(state=tk.DISABLED)  # Make text area read-only

# GUI Setup
root = tk.Tk()
root.title("PC Specs Tool")

# Button to fetch system info
fetch_button = tk.Button(root, text="Get PC Specs", command=display_info)
fetch_button.pack(pady=10)

# Scrollable text area to display the results
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=25)
text_area.pack(padx=10, pady=10)
text_area.config(state=tk.DISABLED)  # Make it read-only initially

# Run the GUI event loop
root.mainloop()
