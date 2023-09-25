import requests
import zipfile
import os
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, OptionMenu
import threading
from automation_script import *

# import os

#check path for version.txt file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE_PATH = os.path.join(BASE_DIR, "version.txt")

#Github url that will send out new update to apps as new features are added also checks for updates

GITHUB_REPO ="https://api.github.com/repos/parlo12/3cx_automation/releases/latest"

def get_appropriate_asset(data):
    #Check the user's OS
    os_name = platform.system().lower()
    print(f"Dectected os: {os_name}")

    # Checking for assets name

    for asset in data['assets']:
        print(f"Checking asset: {asset['name']}")
        if os_name in asset['name'].lower():
            return asset['browser_download_url']
    return None

def get_current_version():
    with open(VERSION_FILE_PATH,"r") as file:
        # Read the first line which contains the version
        version = file.readline().strip()
    return version

def check_for_updates(current_version):
    current_version = get_current_version()

    url = f"https://api.github.com/repos/parlo12/3cx_automation/releases/latest"
    response = requests.get(url)
    
    # Check if request was successful
    if response.status_code != 200:
        print(f"Failed to fetch updates. HTTP Status Code: {response.status_code}")
        return False, current_version
    
    data = response.json()
    
    # Check if tag_name exists in the response
    if 'tag_name' not in data:
        print("The response from GitHub does not contain a 'tag_name' key.")
        return False, current_version

    latest_version = data['tag_name']
    # download_url = data['html_url']  # Link to the release page
    #Get the appropriate asset for the user's platform 
    #Strip the 'v' prefix from the Github tag
    latest_version =latest_version.lstrip('v')

    if current_version < latest_version:
        download_url = get_appropriate_asset(data)
        if download_url:
            return True, download_url
        else:
            print("Suitable asset not found for the platfom")
            print(f"this is the download_url data: {download_url}")
        return False, current_version
    else:
        return False, current_version

def update_aplication(download_url):
    # Download the Zip

    r = requests.get(download_url, stream=True)
    zip_path = "new_app.zip"
    with open(zip_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

        # Extract the zip to the app's directory 

        with zipfile.ZipFile(zip_path,'r') as zip_ref:
            zip_ref.extractall("path_to_app_folder")
        os.remove(zip_path)

class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV to 3CX Automation")
        
        self.stop_event = None

        # File Upload
        self.label = ttk.Label(self.master, text="Upload CSV:")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.filename_var = tk.StringVar()
        self.file_entry = ttk.Entry(self.master, textvariable=self.filename_var, width=40)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = ttk.Button(self.master, text="Browse", command=self.load_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # Username and Password Inputs
        self.label2 = ttk.Label(self.master, text="Username:")
        self.label2.grid(row=1, column=0, padx=10, pady=10)

        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.master, textvariable=self.username_var, width=20)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)

        self.label3 = ttk.Label(self.master, text="Password:")
        self.label3.grid(row=2, column=0, padx=10, pady=10)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.master, textvariable=self.password_var, width=20, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Phone Column Name
        self.label4 = ttk.Label(self.master, text="Phone Column Name:")
        self.label4.grid(row=3, column=0, padx=10, pady=10)

        self.column_name_var = tk.StringVar()
        self.column_name_entry = ttk.Entry(self.master, textvariable=self.column_name_var, width=20)
        self.column_name_entry.grid(row=3, column=1, padx=10, pady=10)

      
        # URL label
        self.label5 = ttk.Label(self.master, text="URL:")
        self.label5.grid(row=4, column=0, padx=10, pady=10)

        # Message box 
        self.label6 = ttk.Label(self.master, text="Message Template:")
        self.label6.grid(row=7, column=0, padx=10, pady=10)

        self.template_text = tk.Text(self.master, height=5, width=40)
        self.template_text.grid(row=7, column=1, padx=10, pady=10, columnspan=2)
        self.template_text.insert(tk.END, "Hello {first_name} {last_name}, I'm reaching out regarding {address}, {city}, {state} {zip_code}.")

        #adding DID for different agent to use 

        self.label7 = ttk.Label(self.master, text="Enter DID assigned to you:")
        self.label7.grid(row=8, column=0, padx=10, pady=10)
        
        self.did_var = tk.StringVar()
        self.did_var_entry= tk.Entry(self.master, textvariable=self.did_var, width=10)
        self.did_var_entry.grid(row=8, column=1, padx=10, pady=10)


        # Start and Stop buttons
        self.start_button = ttk.Button(self.master, text="Start", command=self.start_script)
        self.start_button.grid(row=5, column=1, pady=20)

        self.stop_button = ttk.Button(self.master, text="Stop", command=self.stop_script)
        self.stop_button.grid(row=5, column=2, pady=20)

        self.stop_button = ttk.Button(self.master, text="Delete Messages", command=self.execute_delete_msg)
        self.stop_button.grid(row=5, column=3, pady=20)

        self.stop_button = ttk.Button(self.master, text="Delete Contacts", command=self.execute_delete_contacts)
        self.stop_button.grid(row=5, column=4, pady=20)

        self.stop_button = ttk.Button(self.master, text="Close", command=self.execute_close)
        self.stop_button.grid(row=5, column=5, pady=20)

        self.update_button = ttk.Button(self.master, text="Check for Updates", command=self.on_check_updates)
        self.update_button.grid(row=6, column=1, pady=20)

        if os.path.isfile('credentials.json'):
            self.dict_credentials = load_check_point('credentials.json')            
            
            self.file_entry.insert(0, self.dict_credentials['csv_filepath'])
            self.password_entry.insert(0, self.dict_credentials['password'])
            self.username_entry.insert(0, self.dict_credentials['username'])            
            self.column_name_entry.insert(0, self.dict_credentials['column_name'])            
            self.did_var_entry.insert(0, self.dict_credentials['did'])
            self.OPTIONS = list(self.dict_credentials['url_list'].values())
        else:
            
            self.OPTIONS = ["https://mjrealestate.3cx.us/#/login", "https://mjrealestate.3cx.us/webclient/#/people"]

        # DROPDOWN WEB PAGE SELECTION
        self.clicked = tk.StringVar(master)
        self.clicked.set(self.OPTIONS[0]) # default value
        self.drop = OptionMenu(self.master, self.clicked, *self.OPTIONS)
        self.drop.grid(row=4, column=1, padx=10, pady=10)

        # Initials settings
        self.flag_navigator = False

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        self.filename_var.set(filepath)

    def start_script(self):
        self.script_thread = threading.Thread(target=self.run_script)
        self.script_thread.start()
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL
        

    def stop_script(self):
        if self.stop_event:
            self.stop_event.set()
        self.start_button["state"] = tk.NORMAL
        self.stop_button["state"] = tk.DISABLED

    def execute_delete_msg():
        
        if self.flag_navigator:            
            self.stop_event.set()
            print("Start delete messges")
        else:
            messagebox.showerror("Error", "Unfound navigator")


    def execute_delete_contacts():
        if self.flag_navigator:            
            self.stop_event.set()
            print("Start delete contacts")
        else:
            messagebox.showerror("Error", "Unfound navigator")


    def execute_close():
        print("Close navigator")
    #checking for updates available for the app

    def on_check_updates(self):
        with open(VERSION_FILE_PATH, "r") as file:
            current_version =file.readline().strip()

        is_update_available, download_url = check_for_updates(current_version)
        if is_update_available and download_url: #added extra check for download_url here
            response = messagebox.askyesno("Update Available", f"Version {download_url.lstrip('v')} is available. Do you want to update?")
            if response:
                update_aplication(download_url)
                messagebox.showinfo("Update complete", "Please restart the application.")

            else:
                messagebox.showinfo("No Updates", "You are using the latest version.")
        
    def run_script(self):
        self.stop_event = threading.Event()
        # self.load_fields()        
        self.dict_credentials['csv_filepath'] = self.filename_var.get()
        self.dict_credentials['username'] = self.username_var.get()
        self.dict_credentials['password'] = self.password_var.get()
        self.dict_credentials['column_name'] = self.column_name_var.get()        
        self.dict_credentials['template'] = self.template_text.get("1.0", tk.END).strip()
        self.dict_credentials['current_url'] = self.clicked.get()
        self.dict_credentials['url_list'] = {'url1':self.OPTIONS[0], 'url2':self.OPTIONS[1]}
        self.dict_credentials['did'] = self.did_var.get()

        save_check_point('credentials.json', self.dict_credentials)        
        process_csv_to_webclient(self.dict_credentials, self.stop_event)


if __name__ == "__main__":
    root = tk.Tk()
app = Application(root)
root.mainloop()