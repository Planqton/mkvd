import tkinter as tk
from tkinter import filedialog


def open_file():
    path = filedialog.askopenfilename(filetypes=[('MKV files', '*.mkv'), ('All files', '*.*')])
    if path:
        path_var.set(path)


root = tk.Tk()
root.title('MKVD')

root.geometry('400x200')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

container = tk.Frame(root, padx=20, pady=20)
container.grid(sticky='nsew')
container.columnconfigure(0, weight=1)

open_button = tk.Button(container, text='Open MKV File', command=open_file, height=2)
open_button.grid(row=0, column=0, pady=(0, 10), sticky='ew')

path_var = tk.StringVar()
path_label = tk.Label(container, textvariable=path_var, wraplength=360, justify='left')
path_label.grid(row=1, column=0, sticky='w')

root.mainloop()
