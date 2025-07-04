import tkinter as tk

class SegmentBar(tk.Canvas):
    def __init__(self, master, segments=5, **kwargs):
        super().__init__(master, **kwargs)
        self.segments = segments
        self.bind("<Configure>", self.redraw)
        self.redraw()

    def redraw(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        bar_height = height // 3
        y = (height - bar_height) // 2

        # Draw background bar
        self.create_rectangle(0, y, width, y + bar_height, fill="lightgray", outline="")

        # Draw segments
        seg_width = width / self.segments
        for i in range(1, self.segments):
            x = i * seg_width
            self.create_line(x, y, x, y + bar_height, fill="black")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Segment Bar")
        self.geometry("500x100")
        self.bar = SegmentBar(self, segments=8, bg="white", highlightthickness=0)
        self.bar.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
