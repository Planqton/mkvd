import tkinter as tk
from tkinter import filedialog
import vlc

class MKVPlayer:
    def __init__(self, root):
        self.root = root
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = None

        root.title('MKV Player')
        root.geometry('800x600')

        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Open', command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=root.quit)
        menubar.add_cascade(label='File', menu=file_menu)
        root.config(menu=menubar)

        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.player.set_xwindow(self.canvas.winfo_id())

        self.controls = tk.Frame(root)
        self.controls.pack(fill=tk.X)

        self.play_button = tk.Button(
            self.controls,
            text='Play',
            command=self.play
        )
        self.pause_button = tk.Button(
            self.controls,
            text='Pause',
            command=self.pause
        )
        self.play_button.pack(side=tk.LEFT)
        self.pause_button.pack(side=tk.LEFT)

        self.scale = tk.Scale(
            self.controls,
            from_=0,
            to=1000,
            orient=tk.HORIZONTAL,
            command=self.seek
        )
        self.scale.pack(fill=tk.X, expand=1)

        self.update_scale()

    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[('MKV files', '*.mkv'), ('All files', '*.*')]
        )
        if path:
            self.media = self.instance.media_new(path)
            self.player.set_media(self.media)
            self.play()

    def play(self):
        if self.media is not None:
            self.player.play()

    def pause(self):
        self.player.pause()

    def seek(self, value):
        if self.player.get_length() > 0:
            pos = int(value) / 1000
            self.player.set_position(pos)

    def update_scale(self):
        if self.player.is_playing():
            length = self.player.get_length()
            if length > 0:
                pos = self.player.get_position()
                self.scale.set(int(pos * 1000))
        self.root.after(500, self.update_scale)

if __name__ == '__main__':
    root = tk.Tk()
    app = MKVPlayer(root)
    root.mainloop()
