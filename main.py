# Simple MKVD GUI
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class MKVDApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MKVD Player")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.listbox = tk.Listbox(frame)
        self.listbox.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Play", command=self.play_file).pack(side='left', padx=5)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("MKV files", "*.mkv"), ("All files", "*.*")])
        for f in files:
            self.listbox.insert('end', f)

    def play_file(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No selection", "Please select a file to play.")
            return
        file = self.listbox.get(selection[0])
        try:
            if sys.platform.startswith("win"):
                os.startfile(file)
            else:
                subprocess.Popen(["xdg-open", file])
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = MKVDApp()
    app.mainloop()

