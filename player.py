import tkinter as tk
from tkinter import filedialog
import vlc

class MKVPlayer:
    def __init__(self, root):
        self.root = root
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = None
        self.segments = []  # list of dicts with start, end, rect
        self.selected_index = None
        self.drag_start_x = None
        self.temp_rect = None
        self.segment_start = None  # for legacy flag buttons

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

        self.flag_start_button = tk.Button(
            self.controls,
            text='Flag Start',
            command=self.flag_start_time
        )
        self.flag_end_button = tk.Button(
            self.controls,
            text='Flag End',
            command=self.flag_end_time
        )
        self.flag_start_button.pack(side=tk.LEFT)
        self.flag_end_button.pack(side=tk.LEFT)

        self.scale = tk.Scale(
            self.controls,
            from_=0,
            to=1000,
            orient=tk.HORIZONTAL,
            command=self.seek
        )
        self.scale.pack(fill=tk.X, expand=1)

        self.timeline = tk.Canvas(root, height=20, bg='lightgray')
        self.timeline.pack(fill=tk.X)
        self.timeline.bind('<Button-1>', self.timeline_click)
        self.timeline.bind('<B1-Motion>', self.timeline_drag)
        self.timeline.bind('<ButtonRelease-1>', self.timeline_release)
        self.timeline.bind('<Double-Button-1>', self.timeline_double_click)
        self.timeline.bind('<Configure>', lambda e: self.draw_segments())

        self.segment_list = tk.Listbox(root, height=4)
        self.segment_list.pack(fill=tk.X)

        self.update_scale()

    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[('MKV files', '*.mkv'), ('All files', '*.*')]
        )
        if path:
            self.media = self.instance.media_new(path)
            self.player.set_media(self.media)
            self.segments.clear()
            self.segment_list.delete(0, tk.END)
            self.selected_index = None
            self.draw_segments()
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
        self.draw_segments()
        self.root.after(500, self.update_scale)

    def flag_start_time(self):
        if self.player.get_length() > 0:
            self.segment_start = self.player.get_time()

    def flag_end_time(self):
        if self.player.get_length() > 0 and self.segment_start is not None:
            end = self.player.get_time()
            if end > self.segment_start:
                self.segments.append({'start': self.segment_start, 'end': end})
                self.segment_list.insert(
                    tk.END,
                    f"{self.format_time(self.segment_start)} - {self.format_time(end)}"
                )
                self.draw_segments()
            self.segment_start = None

    # --- timeline helpers ---
    def timeline_to_ms(self, x):
        length = self.player.get_length()
        width = max(1, self.timeline.winfo_width())
        return int(x / width * length) if length > 0 else 0

    def ms_to_timeline(self, ms):
        length = self.player.get_length()
        width = max(1, self.timeline.winfo_width())
        return int(ms / length * width) if length > 0 else 0

    def draw_segments(self):
        self.timeline.delete('seg')
        length = self.player.get_length()
        if length <= 0:
            return
        for idx, seg in enumerate(self.segments):
            x1 = self.ms_to_timeline(seg['start'])
            x2 = self.ms_to_timeline(seg['end'])
            color = 'yellow' if idx == self.selected_index else 'blue'
            rect = self.timeline.create_rectangle(
                x1,
                2,
                x2,
                18,
                fill=color,
                outline='black',
                tags=('seg', f'seg{idx}')
            )
            seg['rect'] = rect

    def timeline_click(self, event):
        item = self.timeline.find_closest(event.x, event.y)
        if item:
            tags = self.timeline.gettags(item)
            if 'seg' in tags:
                idx = int(tags[1][3:])
                self.selected_index = idx
                self.draw_segments()
                return
        self.drag_start_x = event.x
        self.temp_rect = self.timeline.create_rectangle(
            event.x,
            2,
            event.x,
            18,
            fill='red',
            outline='red',
            tags='temp'
        )

    def timeline_drag(self, event):
        if self.temp_rect is not None:
            self.timeline.coords(self.temp_rect, self.drag_start_x, 2, event.x, 18)

    def timeline_release(self, event):
        if self.temp_rect is None:
            return
        self.timeline.delete(self.temp_rect)
        x1 = self.drag_start_x
        x2 = event.x
        self.temp_rect = None
        self.drag_start_x = None
        if abs(x2 - x1) < 2:
            return
        start = self.timeline_to_ms(min(x1, x2))
        end = self.timeline_to_ms(max(x1, x2))
        if end > start:
            self.segments.append({'start': start, 'end': end})
            self.segment_list.insert(
                tk.END,
                f"{self.format_time(start)} - {self.format_time(end)}"
            )
            self.draw_segments()

    def timeline_double_click(self, event):
        item = self.timeline.find_closest(event.x, event.y)
        if item:
            tags = self.timeline.gettags(item)
            if 'seg' in tags:
                idx = int(tags[1][3:])
                self.segment_list.delete(idx)
                del self.segments[idx]
                self.selected_index = None
                self.draw_segments()

    @staticmethod
    def format_time(ms):
        seconds = int(ms / 1000)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02}:{m:02}:{s:02}"

if __name__ == '__main__':
    root = tk.Tk()
    app = MKVPlayer(root)
    root.mainloop()
