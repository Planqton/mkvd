import os
import subprocess
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import threading
import queue
import vlc

class VideoPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Player with Timeline")
        self.geometry("800x600")
        # use a nicer ttk theme if available
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        # VLC player instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Video panel
        self.video_panel = tk.Frame(self)
        self.canvas = tk.Canvas(self.video_panel, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.video_panel.pack(fill=tk.BOTH, expand=1)

        # show loaded file
        self.video_label = ttk.Label(self, text="No video loaded", anchor='w')
        self.video_label.pack(fill=tk.X, padx=5, pady=(0, 2))

        # metadata display
        self.meta_var = tk.StringVar()
        self.meta_label = ttk.Label(self, textvariable=self.meta_var, anchor='w')
        self.meta_label.pack(fill=tk.X, padx=5, pady=(0, 2))

        # Timeline slider
        self.scale = tk.Scale(self, from_=0, to=1000, orient=tk.HORIZONTAL,
                              command=self.on_slider_move)
        self.scale.pack(fill=tk.X, padx=5, pady=(5, 0))

        # Canvas for draggable segments
        self.timeline = tk.Canvas(self, height=40, bg='grey90')
        self.timeline.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.timeline.bind('<Button-1>', self.on_timeline_click)
        self.timeline.bind('<B1-Motion>', self.on_timeline_drag)
        self.timeline.bind('<ButtonRelease-1>', self.on_timeline_release)
        self.timeline.bind('<Motion>', self.on_timeline_motion)
        self.timeline.bind('<Leave>', lambda e: self.timeline.config(cursor=''))
        self.playhead = self.timeline.create_line(0, 0, 0, 40, fill='red')

        # Segment management
        self.segments = []  # list of dicts with id, name, start, end, rect
        self.active_segment = None
        self.drag_mode = None
        self.drag_offset = 0
        self.video_path = None

        # Control buttons
        controls = ttk.Frame(self)
        self.control_widgets = []
        self.load_btn = ttk.Button(controls, text="Load", command=self.load_video)
        self.load_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.load_btn)

        self.play_btn = ttk.Button(controls, text="Play", command=self.play)
        self.play_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.play_btn)

        self.pause_btn = ttk.Button(controls, text="Pause", command=self.pause)
        self.pause_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.pause_btn)

        self.stop_btn = ttk.Button(controls, text="Stop", command=self.stop)
        self.stop_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.stop_btn)

        self.start_btn = ttk.Button(controls, text="Set Start", command=self.set_start)
        self.start_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.start_btn)

        self.end_btn = ttk.Button(controls, text="Set End", command=self.set_end)
        self.end_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.end_btn)

        self.add_btn = ttk.Button(controls, text="Add Segment", command=self.add_segment)
        self.add_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.add_btn)

        self.rename_btn = ttk.Button(controls, text="Rename", command=self.rename_segment)
        self.rename_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.rename_btn)

        self.export_btn = ttk.Button(controls, text="Export", command=self.export_segments)
        self.export_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.export_btn)

        self.export_full_btn = ttk.Button(controls, text="Export Full", command=self.export_full)
        self.export_full_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.export_full_btn)

        ttk.Label(controls, text='Jump (s):').pack(side=tk.LEFT)
        self.jump_amount = tk.DoubleVar(value=1.0)
        self.jump_spin = ttk.Spinbox(controls, from_=0.1, to=60.0,
                                     increment=0.1, width=5,
                                     textvariable=self.jump_amount)
        self.jump_spin.pack(side=tk.LEFT)
        self.control_widgets.append(self.jump_spin)

        controls.pack(fill=tk.X)

        # Segment info list
        self.segment_var = tk.StringVar()
        self.segment_label = ttk.Label(self, textvariable=self.segment_var)
        self.segment_label.pack(fill=tk.X, padx=5, pady=(5, 0))

        self.segment_list = tk.Listbox(self)
        self.segment_list.pack(fill=tk.BOTH, expand=False, padx=5, pady=(0, 5))
        self.segment_list.bind('<<ListboxSelect>>', self.on_segment_select)

        # Entry fields to edit selected segment
        edit = ttk.Frame(self)
        ttk.Label(edit, text='Start:').pack(side=tk.LEFT)
        self.start_entry = ttk.Entry(edit, width=8, state='disabled')
        self.start_entry.pack(side=tk.LEFT)
        self.control_widgets.append(self.start_entry)

        ttk.Label(edit, text='End:').pack(side=tk.LEFT)
        self.end_entry = ttk.Entry(edit, width=8, state='disabled')
        self.end_entry.pack(side=tk.LEFT)
        self.control_widgets.append(self.end_entry)

        self.update_btn = ttk.Button(edit, text='Update', command=self.update_segment_times, state='disabled')
        self.update_btn.pack(side=tk.LEFT)
        self.control_widgets.append(self.update_btn)

        edit.pack(fill=tk.X)

        # Status during export
        self.export_status_var = tk.StringVar()
        self.export_status_label = ttk.Label(self, textvariable=self.export_status_var)
        self.export_status_label.pack(fill=tk.X)

        # Log output for ffmpeg
        self.log_text = ScrolledText(self, height=12, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=False)
        self.log_queue = queue.Queue()
        self.after(100, self.process_log_queue)

        # Segment points
        self.start_point = None
        self.end_point = None

        # timeline width cached for convenience
        self.timeline_width = 1

        # Timer
        self.update_interval = 200
        self.after(self.update_interval, self.update_ui)

        # flag to disable interactions during export
        self.exporting = False

        # allow slider control via arrow keys
        self.bind('<Left>', self.on_key_left)
        self.bind('<Right>', self.on_key_right)
        # allow scrolling to move the slider
        self.bind('<MouseWheel>', self.on_mouse_wheel)
        self.bind('<Button-4>', self.on_mouse_wheel)
        self.bind('<Button-5>', self.on_mouse_wheel)

    def load_video(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Video Files", "*.mkv *.avi *.mp4")
        ])
        if not path:
            return
        self.meta_var.set('')
        if os.path.exists(path):
            media = self.instance.media_new(path)
            self.player.set_media(media)
            self.player.set_hwnd(self.canvas.winfo_id())
            self.play()
            # Reset segment points
            self.start_point = None
            self.end_point = None
            self.segment_var.set("")
            # Clear segments
            for seg in self.segments:
                if seg['rect']:
                    self.timeline.delete(seg['rect'])
            self.segments.clear()
            self.segment_list.delete(0, tk.END)
            self.video_path = path
            self.video_label.config(text=os.path.basename(path))
            self.meta_var.set(self.get_metadata(path))
        else:
            messagebox.showerror("Error", f"File not found: {path}")

    def play(self):
        if self.player.get_media() is not None:
            self.player.play()

    def pause(self):
        if self.player.is_playing():
            self.player.pause()

    def stop(self):
        if self.player.get_media() is None:
            return
        self.player.stop()
        self.scale.set(0)
        # display first frame after stopping
        self.player.play()
        self.player.pause()

    def on_slider_move(self, value):
        if self.player.get_media() is None:
            return
        length = self.player.get_length()
        if length > 0:
            t = int(float(value))
            self.player.set_time(int(t / 1000 * length))
            if not self.player.is_playing():
                self.player.play()
                self.player.pause()

    def update_ui(self):
        if self.player.get_media() is not None:
            length = self.player.get_length()
            if length > 0:
                pos = self.player.get_time() / length * 1000
                self.scale.set(pos)
                x = pos / 1000 * self.timeline_width
                self.timeline.coords(self.playhead, x, 0, x, 40)
        # update progress line on timeline
        self.timeline_width = max(self.timeline.winfo_width(), 1)
        for seg in self.segments:
            self.update_segment_rect(seg)
        self.after(self.update_interval, self.update_ui)

    def append_log(self, text):
        """Queue log text for display."""
        self.log_queue.put(text)

    def process_log_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, msg)
            self.log_text.see(tk.END)
            self.log_text.configure(state='disabled')
        self.after(100, self.process_log_queue)

    def get_metadata(self, path):
        """Return basic metadata string for the given media file."""
        ffprobe_dir = os.path.join(os.path.dirname(__file__), 'ffmpeg')
        exe = 'ffprobe.exe' if os.name == 'nt' else 'ffprobe'
        ffprobe_path = os.path.join(ffprobe_dir, exe)
        if not os.path.exists(ffprobe_path):
            return ''
        cmd = [ffprobe_path, '-v', 'quiet', '-print_format', 'json',
               '-show_format', path]
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                         text=True)
            data = json.loads(out)
            tags = data.get('format', {}).get('tags', {})
            fields = ['title', 'show', 'season_number', 'episode_id']
            info = [f'{f.capitalize()}: {tags[f]}' for f in fields if f in tags]
            return ' | '.join(info)
        except Exception as e:
            return f'Metadata error: {e}'

    def set_controls_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        for w in self.control_widgets:
            w.configure(state=state)
        self.segment_list.configure(state=state)
        self.scale.configure(state=state)
        self.exporting = not enabled

    def set_start(self):
        if self.exporting or self.player.get_media() is None:
            return
        length = self.player.get_length()
        self.start_point = max(0, min(self.player.get_time(), length))
        self.update_segment_label()

    def set_end(self):
        if self.exporting or self.player.get_media() is None:
            return
        length = self.player.get_length()
        self.end_point = max(0, min(self.player.get_time(), length))
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

    # --- segment management ---
    def add_segment(self):
        if self.exporting:
            return
        if self.start_point is None or self.end_point is None:
            return
        if self.end_point <= self.start_point:
            messagebox.showerror("Error", "End must be after start")
            return
        seg_id = len(self.segments) + 1
        name = f"Segment {seg_id}"
        length = self.player.get_length()
        start = max(0, min(self.start_point, length))
        end = max(start + 1, min(self.end_point, length))
        seg = {
            'id': seg_id,
            'name': name,
            'start': start,
            'end': end,
            'rect': None,
        }
        self.segments.append(seg)
        self.segment_list.insert(tk.END, f"{seg['id']}: {seg['name']} {seg['start']/1000:.2f}s - {seg['end']/1000:.2f}s")
        self.draw_segment(seg)

    def rename_segment(self):
        if self.exporting:
            return
        sel = self.segment_list.curselection()
        if not sel:
            return
        index = sel[0]
        seg = self.segments[index]
        new_name = simpledialog.askstring("Rename", "Segment name:", initialvalue=seg['name'])
        if new_name:
            seg['name'] = new_name
            self.update_segment_list()

    def update_segment_list(self):
        self.segment_list.delete(0, tk.END)
        for seg in self.segments:
            self.segment_list.insert(tk.END, f"{seg['id']}: {seg['name']} {seg['start']/1000:.2f}s - {seg['end']/1000:.2f}s")

    def on_segment_select(self, event=None):
        sel = self.segment_list.curselection()
        if not sel:
            self.start_entry.configure(state='disabled')
            self.end_entry.configure(state='disabled')
            self.update_btn.configure(state='disabled')
            return
        index = sel[0]
        seg = self.segments[index]
        self.start_entry.configure(state='normal')
        self.end_entry.configure(state='normal')
        self.update_btn.configure(state='normal')
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, f"{seg['start']/1000:.2f}")
        self.end_entry.delete(0, tk.END)
        self.end_entry.insert(0, f"{seg['end']/1000:.2f}")

    def update_segment_times(self):
        if self.exporting:
            return
        sel = self.segment_list.curselection()
        if not sel:
            return
        index = sel[0]
        seg = self.segments[index]
        try:
            start = float(self.start_entry.get()) * 1000
            end = float(self.end_entry.get()) * 1000
            if end <= start:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Invalid start/end times")
            return
        length = self.player.get_length()
        seg['start'] = max(0, min(start, length))
        seg['end'] = max(seg['start'] + 1, min(end, length))
        self.update_segment_rect(seg)
        self.update_segment_list()
        self.segment_list.selection_set(index)

    def draw_segment(self, seg):
        x1 = seg['start'] / max(self.player.get_length(), 1) * self.timeline_width
        x2 = seg['end'] / max(self.player.get_length(), 1) * self.timeline_width
        rect = self.timeline.create_rectangle(x1, 5, x2, 35, fill='skyblue', outline='blue', tags=f"seg{seg['id']}")
        seg['rect'] = rect

    def update_segment_rect(self, seg):
        if seg['rect'] is None:
            return
        x1 = seg['start'] / max(self.player.get_length(), 1) * self.timeline_width
        x2 = seg['end'] / max(self.player.get_length(), 1) * self.timeline_width
        self.timeline.coords(seg['rect'], x1, 5, x2, 35)

    # --- timeline interaction ---
    def find_segment_at(self, x):
        items = self.timeline.find_overlapping(x, 5, x, 35)
        for item in items:
            for seg in self.segments:
                if seg['rect'] == item:
                    return seg
        return None

    def on_timeline_click(self, event):
        if self.exporting:
            return
        seg = self.find_segment_at(event.x)
        self.active_segment = seg
        self.drag_mode = None
        if seg:
            x1, _, x2, _ = self.timeline.coords(seg['rect'])
            if abs(event.x - x1) < 5:
                self.drag_mode = 'resize_left'
            elif abs(event.x - x2) < 5:
                self.drag_mode = 'resize_right'
            else:
                self.drag_mode = 'move'
            self.drag_offset = event.x

    def on_timeline_drag(self, event):
        if self.exporting or not self.active_segment:
            return
        delta = event.x - self.drag_offset
        length = max(self.player.get_length(), 1)
        px_to_time = length / self.timeline_width
        if self.drag_mode == 'move':
            seg_len = self.active_segment['end'] - self.active_segment['start']
            new_start = self.active_segment['start'] + delta * px_to_time
            new_start = max(0, min(length - seg_len, new_start))
            self.active_segment['start'] = new_start
            self.active_segment['end'] = new_start + seg_len
        elif self.drag_mode == 'resize_left':
            new_start = self.active_segment['start'] + delta * px_to_time
            max_start = self.active_segment['end'] - 1
            self.active_segment['start'] = max(0, min(max_start, new_start))
        elif self.drag_mode == 'resize_right':
            new_end = self.active_segment['end'] + delta * px_to_time
            min_end = self.active_segment['start'] + 1
            self.active_segment['end'] = max(min_end, min(length, new_end))
        self.drag_offset = event.x
        self.update_segment_rect(self.active_segment)
        self.update_segment_list()

    def on_timeline_release(self, event):
        if self.exporting:
            return
        self.active_segment = None
        self.drag_mode = None

    def on_timeline_motion(self, event):
        if self.exporting:
            return
        seg = self.find_segment_at(event.x)
        cursor = ''
        if seg:
            x1, _, x2, _ = self.timeline.coords(seg['rect'])
            if abs(event.x - x1) < 5 or abs(event.x - x2) < 5:
                cursor = 'sb_h_double_arrow'
            else:
                cursor = 'fleur'
        self.timeline.config(cursor=cursor)

    def export_segments(self):
        if not self.video_path or not self.segments:
            messagebox.showinfo("Export", "No segments to export")
            return
        export_dir = filedialog.askdirectory(title="Select Export Folder")
        if not export_dir:
            return
        self.set_controls_state(False)
        self.export_status_var.set("Starting export...")
        threading.Thread(target=self._export_worker, args=(export_dir,), daemon=True).start()

    def _export_worker(self, export_dir):
        ffmpeg_dir = os.path.join(os.path.dirname(__file__), 'ffmpeg')
        exe = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
        ffmpeg_path = os.path.join(ffmpeg_dir, exe)
        if not os.path.exists(ffmpeg_path):
            self.append_log(f"ffmpeg not found at {ffmpeg_path}\n")
            self.after(0, lambda: self.export_status_var.set("ffmpeg not found"))
            self.after(0, lambda: self.set_controls_state(True))
            return
        os.makedirs(export_dir, exist_ok=True)
        for seg in self.segments:
            self.after(0, lambda name=seg['name']: self.export_status_var.set(f"Exporting {name}"))
            start = seg['start'] / 1000
            duration = (seg['end'] - seg['start']) / 1000
            outfile = os.path.join(export_dir, f"{seg['name']}.mp3")
            cmd = [ffmpeg_path, '-y', '-i', self.video_path,
                   '-ss', str(start), '-t', str(duration),
                   '-vn', '-acodec', 'mp3', outfile]
            self.append_log("Running: " + " ".join(cmd) + "\n")
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    self.append_log(line)
                proc.wait()
            except Exception as e:
                self.append_log(f"Failed to export {outfile}: {e}\n")
        self.after(0, lambda: self.export_status_var.set("Export finished"))
        self.after(0, lambda: self.set_controls_state(True))

    def export_full(self):
        if not self.video_path:
            messagebox.showinfo("Export", "No video loaded")
            return
        export_dir = filedialog.askdirectory(title="Select Export Folder")
        if not export_dir:
            return
        self.set_controls_state(False)
        self.export_status_var.set("Starting export...")
        threading.Thread(target=self._export_full_worker, args=(export_dir,), daemon=True).start()

    def _export_full_worker(self, export_dir):
        ffmpeg_dir = os.path.join(os.path.dirname(__file__), 'ffmpeg')
        exe = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
        ffmpeg_path = os.path.join(ffmpeg_dir, exe)
        if not os.path.exists(ffmpeg_path):
            self.append_log(f"ffmpeg not found at {ffmpeg_path}\n")
            self.after(0, lambda: self.export_status_var.set("ffmpeg not found"))
            self.after(0, lambda: self.set_controls_state(True))
            return
        os.makedirs(export_dir, exist_ok=True)
        outfile = os.path.join(export_dir, 'full_audio.mp3')
        cmd = [ffmpeg_path, '-y', '-i', self.video_path,
               '-vn', '-acodec', 'mp3', outfile]
        self.append_log("Running: " + " ".join(cmd) + "\n")
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self.append_log(line)
            proc.wait()
        except Exception as e:
            self.append_log(f"Failed to export {outfile}: {e}\n")
        self.after(0, lambda: self.export_status_var.set("Export finished"))
        self.after(0, lambda: self.set_controls_state(True))

    # --- keyboard slider control ---
    def adjust_time(self, seconds):
        if self.exporting or self.player.get_media() is None:
            return
        length = self.player.get_length()
        if length <= 0:
            return
        current = self.player.get_time()
        new_time = max(0, min(length, current + int(seconds * 1000)))
        self.player.set_time(new_time)
        pos = new_time / length * 1000
        self.scale.set(pos)
        if not self.player.is_playing():
            self.player.play()
            self.player.pause()

    def on_key_left(self, event):
        step = self.jump_amount.get()
        self.adjust_time(-step)

    def on_key_right(self, event):
        step = self.jump_amount.get()
        self.adjust_time(step)

    def on_mouse_wheel(self, event):
        if self.exporting or self.player.get_media() is None:
            return
        direction = 1
        if hasattr(event, 'delta') and event.delta != 0:
            direction = -1 if event.delta > 0 else 1
        elif getattr(event, 'num', None) == 4:
            direction = -1
        elif getattr(event, 'num', None) == 5:
            direction = 1
        step = self.jump_amount.get()
        self.adjust_time(direction * step)


if __name__ == "__main__":
    app = VideoPlayer()
    app.mainloop()
