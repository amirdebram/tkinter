#!/usr/bin/env python3  

__author__ = 'Amir Debram'
__version__ = '1.0'
__email__ = 'amirdebram@gmail.com'

import tkinter as tk
from tkinter import ttk, messagebox
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException
import configparser
import base64

class CrystalSwitch(tk.Tk):
    def __init__(self):
        super().__init__()

        # Create menubar by setting the color
        self.menubar = tk.Menu(self)
        
        # Declare file and edit for showing in menubar
        self.file = tk.Menu(self.menubar, tearoff="off")
        self.edit = tk.Menu(self.menubar, tearoff="off")
        self.help = tk.Menu(self.menubar, tearoff="off")
        
        self.file.add_command(label="Exit", command=lambda: self.quit())
        self.edit.add_command(label="SSH Configuration", command=lambda: self.ssh_Window())
        self.help.add_command(label="About", command=lambda: self.about())
        
        self.menubar.add_cascade(label="File", menu=self.file)
        self.menubar.add_cascade(label="Edit", menu=self.edit)
        self.menubar.add_cascade(label="Help", menu=self.help)
        
        self.config(menu=self.menubar)

        self.Stop_label = ttk.Label(text='Click to Shutdown', font=('Segoe UI', 14))
        self.Stop_label.grid(column=1, row=0, columnspan=3)

        self.Stop_image = tk.PhotoImage(file='./res/StopButton.png')
        self.Stop_button = ttk.Button(self, image=self.Stop_image, command=lambda: self.stopbutton())
        self.Stop_button.grid(column=1, row=1, columnspan=3)
    
    def ssh_Window(self):
        self.sshWindow = tk.Toplevel()
        self.sshWindow.title('SSH Configuration')
        self.sshWindow.geometry(self.positioncentre(270, 200))
        self.sshWindow.grab_set()

        # Host
        self.lbl_host = ttk.Label(self.sshWindow, text='Host Address:')
        self.lbl_host.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        self.var_host = tk.StringVar(value=self.read_config_files()[0])
        self.entry_host = ttk.Entry(self.sshWindow, textvariable=self.var_host)
        self.entry_host.grid(column=1, row=0, padx=5, pady=5)

        # Port
        self.lbl_port = ttk.Label(self.sshWindow, text='Port Number:')
        self.lbl_port.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        self.var_port = tk.StringVar(value=self.read_config_files()[1])
        self.entry_port = ttk.Entry(self.sshWindow, textvariable=self.var_port)
        self.entry_port.grid(column=1, row=1, padx=5, pady=5)

        # Username
        self.lbl_username = ttk.Label(self.sshWindow, text='Username:')
        self.lbl_username.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

        self.var_username = tk.StringVar(value=self.read_config_files()[2])
        self.entry_username = ttk.Entry(self.sshWindow, textvariable=self.var_username)
        self.entry_username.grid(column=1, row=2, padx=5, pady=5)

        # Password
        self.lbl_password = ttk.Label(self.sshWindow, text='Password:')
        self.lbl_password.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)

        self.var_password = tk.StringVar(value=self.read_config_files()[3])
        self.entry_password = ttk.Entry(self.sshWindow, show='*', textvariable=self.var_password)
        self.entry_password.grid(column=1, row=3, padx=5, pady=5)

        # Timeout
        self.lbl_timeout = ttk.Label(self.sshWindow, text='timeout:')
        self.lbl_timeout.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)

        self.var_timeout = tk.StringVar(value=self.read_config_files()[4])
        self.entry_timeout = ttk.Entry(self.sshWindow, textvariable=self.var_timeout)
        self.entry_timeout.grid(column=1, row=4, padx=5, pady=5)

        # Save Button
        self.btn_save = ttk.Button(self.sshWindow, text='Save')
        self.btn_save['command'] = lambda: self.modify_config_files()
        self.btn_save.grid(column=0, row=5, padx=5, pady=5)
        
        # Close Button
        self.btn_close = ttk.Button(self.sshWindow, text='Close')
        self.btn_close['command'] = lambda: self.sshWindow.destroy()
        self.btn_close.grid(column=1, row=5, padx=5, pady=5, sticky='E')

    def stopbutton(self):
        try:
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            host, port, username, password, t = self.read_config_files()
            client.connect(host, port, username, password, timeout=int(t))
            stdin, stdout, stderr = client.exec_command('shutdown -h now')
            print(stdout.read().decode())
            msg = """Shutdown procedure has been executed.\n\
            \nPlease make sure that all lights on the server are off."""
            messagebox.showinfo("Information", msg)
            client.close()
            self.destroy()
        except TimeoutError:
            msg = f"""Shutdown procedure can't be executed.\n\
                \nHost not reachable. Check Host or Port and make sure server is on.\n\
                \nHost : {host}\
                \nPort : {port}\
                \nUsername : {username}\
                \nPassword : ** Hidden **"""
            messagebox.showerror("Error - Connection Timeout", msg)
        except AuthenticationException:
            msg = f"""Shutdown procedure can't be executed.\n\
                \nUsername or Password is incorrect.\n\
                \nHost : {host}\
                \nPort : {port}\
                \nUsername : {username}\
                \nPassword : ** Hidden **"""
            messagebox.showerror("Error - Authentication", msg)

    def read_config_files(self):
        try:
            connection = configparser.ConfigParser()
            connection.read('./connection.ini')
            host = connection['DEFAULT']['host']
            port = connection['DEFAULT']['port']
            username = connection['DEFAULT']['username']
            password = base64.b64decode(connection['DEFAULT']['password']).decode("utf-8", "ignore")
            timeout = connection['DEFAULT']['timeout']
        except KeyError:
            config = configparser.ConfigParser()
            connection = config['DEFAULT']
            connection['host'] = '192.168.0.1'
            connection['port'] = '22'
            connection['username'] = 'root'
            connection['password'] = 'password'
            connection['timeout'] = '5'
            with open('./connection.ini', 'w') as configfile:
                config.write(configfile)
            messagebox.showinfo("Crystal Switch - Created", "Configuration File has been created.")
            self.sshWindow.destroy()

        return [host, port, username, password, timeout]

    def modify_config_files(self):
        config = configparser.ConfigParser()
        connection = config['DEFAULT']
        connection['host'] = self.var_host.get()
        connection['port'] = self.var_port.get()
        connection['username'] = self.var_username.get()
        connection['password'] = base64.b64encode(self.var_password.get().encode('utf-8')).decode('utf-8')
        connection['timeout'] = self.var_timeout.get()
        
        with open('./connection.ini', 'w') as configfile:
            config.write(configfile)
        
        msg = """Configuration Saved"""
        messagebox.showinfo("Crystal Switch - Saved", msg)
        self.sshWindow.destroy()

    def about(self): # new window definition
        msg = f"""Crystal Switch.\n\
            \n>>> Shutsdown a linux machine using SSH\n\
            \nVersion : {__version__}\
            \nCreated By : {__author__}\n\
            \nFor more information please contact:\
            \n{__author__} : {__email__}"""
        messagebox.showinfo("Crystal Switch - About", msg)

    def positioncentre(self, x, y):
        s_width = self.winfo_screenwidth()
        s_height = self.winfo_screenheight()
        s_x = (s_width / 2) - (x / 2)
        s_y = (s_height / 2) - (y / 2)
        return f'{x}x{y}+{int(s_x)}+{int(s_y)}'


if __name__ == "__main__":
    application = CrystalSwitch()
    application.title('Crystal Switch')
    application.geometry(application.positioncentre(250, 260))
    application.columnconfigure(3, weight=1)
    application.resizable(False, False) # Disable window resize
    application.attributes('-alpha', 1) # Set window transparacy
    try:
        application.iconbitmap('./res/power.ico') # Window icon
    except ImportError:
        pass
    application.mainloop()