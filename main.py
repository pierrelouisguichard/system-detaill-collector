import psutil
import platform
from datetime import datetime
import cpuinfo
import socket
import uuid
import re
import getpass
import json
import firebase_admin
from firebase_admin import credentials, firestore
import customtkinter as ctk  # Import customtkinter

# Initialize Firebase with Firestore
cred = credentials.Certificate("creds.json")  # Replace with the path to your key
firebase_admin.initialize_app(cred)

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def System_information():
    uname = platform.uname()
    system_info = {
        "user": getpass.getuser(),
        "pc_name": uname.node,
        "os": f"{uname.system} {uname.release} ({uname.version})",
        "processor": cpuinfo.get_cpu_info().get('brand_raw', "Unknown CPU Brand"),
        "ram": get_size(psutil.virtual_memory().total),
        "ip_address": get_ip_address(),
        "mac_address": get_mac_address(),
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime('%Y/%m/%d %H:%M:%S'),
        "partitions": get_partitions()
    }
    return system_info

def get_ip_address():
    hostname, _, ip_list = socket.gethostbyname_ex(socket.gethostname())
    return ip_list[0] if ip_list else "No IP Found"

def get_mac_address():
    return ':'.join(re.findall('..', '%012x' % uuid.getnode()))

def get_partitions():
    partitions_list = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError as e:
            partition_info = {
                "device": partition.device,
                "error": str(e)
            }
        else:
            partition_info = {
                "device": partition.device,
                "total_size": get_size(partition_usage.total),
                "used": get_size(partition_usage.used),
                "free": get_size(partition_usage.free),
                "percentage": partition_usage.percent
            }
        partitions_list.append(partition_info)
    return partitions_list

def send_to_firestore(data):
    # Connect to Firestore and add the data to the 'system_info' collection
    firestore_db = firestore.client()
    doc_ref_tuple = firestore_db.collection("system_info").add(data)

    # Extract the DocumentReference from the returned tuple
    doc_ref = doc_ref_tuple[1]  # The DocumentReference is the second element of the tuple

    # Print the ID of the document saved to Firestore
    print(f"Data saved to Firestore with ID: {doc_ref.id}")

def collect_and_send():
    # Disable the button and show loading message
    run_button.configure(state="disabled")
    result_label.configure(text="Collecting system information...")
    loading_label.grid(row=2, column=0, columnspan=2)  # Show loading label

    # Collect system information and add a timestamp
    system_info = System_information()
    system_info["collected_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save the data to Firestore
    send_to_firestore(system_info)

    # Update the result label and enable the button again
    result_label.configure(text="Success! System information collected and sent.")
    run_button.configure(state="normal")
    loading_label.grid_forget()  # Hide loading label

# Create the main window
ctk.set_appearance_mode("dark")  # Set the appearance mode
ctk.set_default_color_theme("blue")  # Set the color theme

root = ctk.CTk()  # Use customtkinter's CTk class
root.title("System Info Collector")
root.geometry("400x200")  # Set a fixed size for the window
root.resizable(False, False)  # Disable resizing

# Create a button that triggers the collect_and_send function
run_button = ctk.CTkButton(root, text="Collect System Info", command=collect_and_send)
run_button.grid(row=0, column=0, padx=10, pady=(40, 30), sticky="nsew")  # Center button with padding

# Create a label to show the result
result_label = ctk.CTkLabel(root, text="", font=("Arial", 12))
result_label.grid(row=1, column=0, padx=10, pady=10)

# Create a loading label
loading_label = ctk.CTkLabel(root, text="Loading...", font=("Arial", 12))

# Make the grid expand to fill the window
root.grid_rowconfigure(0, weight=1)  # Make row 0 expand
root.grid_columnconfigure(0, weight=1)  # Make column 0 expand

# Start the GUI event loop
root.mainloop()
