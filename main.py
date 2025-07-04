import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import os


def convert_to_mp3():
    file_path = filedialog.askopenfilename(
        title="Select video file",
        filetypes=[
            ("Video Files", "*.mkv *.avi *.mp4"),
            ("All Files", "*.*"),
        ],
    )
    if not file_path:
        return
    base, _ = os.path.splitext(file_path)
    output_path = base + ".mp3"
    try:
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i",
            file_path,
            "-q:a",
            "0",
            "-map",
            "a",
            output_path,
        ], check=True)
        messagebox.showinfo("Success", f"Saved MP3 to {output_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Conversion failed: {e}")


def main():
    root = tk.Tk()
    root.title("Video to MP3 Converter")
    root.geometry("300x100")

    button = tk.Button(root, text="Export to MP3", command=convert_to_mp3)
    button.pack(expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
