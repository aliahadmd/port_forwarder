import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import sys
import os
import logging
import psutil

class PortForwarder:
    def __init__(self, master):
        self.master = master
        self.master.title("Port Forwarder")
        self.master.geometry("500x600")
        
        self.ports = {}
        
        self.setup_logging()
        self.create_widgets()
        
    def setup_logging(self):
        log_file = os.path.join(os.path.dirname(sys.executable), 'port_forwarder.log') if getattr(sys, 'frozen', False) else 'port_forwarder.log'
        logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        
    def create_widgets(self):
        # Port input
        ttk.Label(self.master, text="Port:").pack(pady=5)
        self.port_entry = ttk.Entry(self.master)
        self.port_entry.pack(pady=5)
        
        # Submit button
        ttk.Button(self.master, text="Add Port", command=self.add_port).pack(pady=5)
        
        # Port list
        self.port_list = ttk.Treeview(self.master, columns=("Port", "Status"), show="headings")
        self.port_list.heading("Port", text="Port")
        self.port_list.heading("Status", text="Status")
        self.port_list.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Remove button
        ttk.Button(self.master, text="Remove Selected", command=self.remove_port).pack(pady=5)
        
        # Start/Stop button
        self.toggle_button = ttk.Button(self.master, text="Start Forwarding", command=self.toggle_forwarding)
        self.toggle_button.pack(pady=5)
        
        # Log display
        self.log_display = scrolledtext.ScrolledText(self.master, height=10)
        self.log_display.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.is_forwarding = False
        
    def add_port(self):
        port = self.port_entry.get()
        if port and port.isdigit() and int(port) not in self.ports:
            self.ports[int(port)] = {"process": None, "status": "Offline"}
            self.port_list.insert("", "end", values=(port, "Offline"))
            self.port_entry.delete(0, tk.END)
        
    def remove_port(self):
        selected = self.port_list.selection()
        if selected:
            port = int(self.port_list.item(selected)['values'][0])
            if port in self.ports:
                if self.ports[port]["process"]:
                    self.ports[port]["process"].terminate()
                del self.ports[port]
            self.port_list.delete(selected)
        
    def toggle_forwarding(self):
        if self.is_forwarding:
            self.stop_forwarding()
        else:
            self.start_forwarding()
        
    def start_forwarding(self):
        self.is_forwarding = True
        self.toggle_button.config(text="Stop Forwarding")
        for port in self.ports:
            thread = threading.Thread(target=self.forward_port, args=(port,))
            thread.start()
        
    def stop_forwarding(self):
        self.is_forwarding = False
        self.toggle_button.config(text="Start Forwarding")
        for port, port_info in self.ports.items():
            if port_info["process"]:
                self.terminate_process(port_info["process"])
                port_info["process"] = None
                port_info["status"] = "Offline"
        self.update_port_list()
    
    def terminate_process(self, process):
        try:
            if sys.platform == 'win32':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
            else:
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                gone, still_alive = psutil.wait_procs([parent] + parent.children(recursive=True), timeout=5)
                for p in still_alive:
                    p.kill()
        except (psutil.NoSuchProcess, subprocess.SubprocessError) as e:
            self.log(f"Error terminating process: {str(e)}")
        
    def forward_port(self, port):
        try:
            ssh_command = f"ssh -tt -L {port}:localhost:{port} p@p.local -o ServerAliveInterval=60 -o ServerAliveCountMax=3"
            self.log(f"Executing command: {ssh_command}")
            
            process = subprocess.Popen(
                ssh_command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            self.ports[port]["process"] = process
            self.ports[port]["status"] = "Online"
            self.update_port_list()
            
            def read_output(pipe, prefix):
                for line in pipe:
                    self.log(f"{prefix}: {line.strip()}")
            
            threading.Thread(target=read_output, args=(process.stdout, f"Port {port} output"), daemon=True).start()
            threading.Thread(target=read_output, args=(process.stderr, f"Port {port} error"), daemon=True).start()
            
            return_code = process.wait()
            self.log(f"Port {port} process exited with return code {return_code}")
        except Exception as e:
            self.log(f"Error forwarding port {port}: {str(e)}")
        finally:
            self.ports[port]["status"] = "Offline"
            self.update_port_list()
        
    def update_port_list(self):
        for item in self.port_list.get_children():
            port = int(self.port_list.item(item)['values'][0])
            status = self.ports[port]["status"]
            self.port_list.item(item, values=(port, status))
        
    def log(self, message):
        logging.info(message)
        self.log_display.insert(tk.END, message + '\n')
        self.log_display.see(tk.END)
        
    def run(self):
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.mainloop()
        
    def on_closing(self):
        self.stop_forwarding()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PortForwarder(root)
    app.run()