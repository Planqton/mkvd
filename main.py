import os
import tkinter as tk
from tkinter import filedialog, messagebox
import vlc

class VideoPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Player with Timeline")
        self.geometry("800x600")

        # VLC player instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Video panel
        self.video_panel = tk.Frame(self)
        self.canvas = tk.Canvas(self.video_panel, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.video_panel.pack(fill=tk.BOTH, expand=1)

        # Timeline slider
        self.scale = tk.Scale(self, from_=0, to=1000, orient=tk.HORIZONTAL,
                              command=self.on_slider_move)
        self.scale.pack(fill=tk.X)

        # Control buttons
        controls = tk.Frame(self)
        tk.Button(controls, text="Load", command=self.load_video).pack(side=tk.LEFT)
        tk.Button(controls, text="Play", command=self.play).pack(side=tk.LEFT)
        tk.Button(controls, text="Pause", command=self.pause).pack(side=tk.LEFT)
        tk.Button(controls, text="Stop", command=self.stop).pack(side=tk.LEFT)

        tk.Button(controls, text="Set Start", command=self.set_start).pack(side=tk.LEFT)
        tk.Button(controls, text="Set End", command=self.set_end).pack(side=tk.LEFT)
        controls.pack(fill=tk.X)

        # Segment info
        self.segment_var = tk.StringVar()
        self.segment_label = tk.Label(self, textvariable=self.segment_var)
        self.segment_label.pack(fill=tk.X)

        # Segment points
        self.start_point = None
        self.end_point = None

        # Timer
        self.update_interval = 200
        self.after(self.update_interval, self.update_ui)

    def load_video(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Video Files", "*.mkv *.avi *.mp4")
        ])
        if not path:
            return
        if os.path.exists(path):
            media = self.instance.media_new(path)
            self.player.set_media(media)
            self.player.set_hwnd(self.canvas.winfo_id())
            self.play()
            # Reset segment points
            self.start_point = None
            self.end_point = None
            self.segment_var.set("")
        else:
            messagebox.showerror("Error", f"File not found: {path}")

    def play(self):
        if self.player.get_media() is not None:
            self.player.play()

    def pause(self):
        if self.player.is_playing():
            self.player.pause()

    def stop(self):
        self.player.stop()
        self.scale.set(0)

    def on_slider_move(self, value):
        if self.player.get_media() is None:
            return
        length = self.player.get_length()
        if length > 0:
            t = int(float(value))
            self.player.set_time(int(t / 1000 * length))

    def update_ui(self):
        if self.player.get_media() is not None and self.player.is_playing():
            length = self.player.get_length()
            if length > 0:
                pos = self.player.get_time() / length * 1000
                self.scale.set(pos)
        self.after(self.update_interval, self.update_ui)

    def set_start(self):
        if self.player.get_media() is None:
            return
        self.start_point = self.player.get_time()
        self.update_segment_label()

    def set_end(self):
        if self.player.get_media() is None:
            return
        self.end_point = self.player.get_time()
        self.update_segment_label()

    def update_segment_label(self):
        if self.start_point is None:
            msg = "Set start point"
        else:
            start_sec = self.start_point / 1000
            if self.end_point is None:
                msg = f"Start: {start_sec:.2f}s"
            else:
                end_sec = self.end_point / 1000
                msg = f"Segment: {start_sec:.2f}s - {end_sec:.2f}s"
        self.segment_var.set(msg)

if __name__ == "__main__":
    app = VideoPlayer()
    app.mainloop()
