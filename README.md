# Video Player with Segment Selection

This repository contains a Tkinter-based application for playing video files (`.mkv`, `.avi`, `.mp4`).
The application uses the `python-vlc` package to handle video playback and provides a draggable timeline where multiple segments can be created and edited.

## Requirements
- Python 3.12+
- [python-vlc](https://pypi.org/project/python-vlc/) (installed automatically with `pip`)
- VLC media player installed on the system (required by `python-vlc`)

Install dependencies with:

```bash
pip install python-vlc
```

## Usage

Run the application with:

```bash
python main.py
```

Use the **Load** button to open a video file. The slider and timeline update as the video plays.
Mark a section with **Set Start** and **Set End**, then click **Add Segment** to store it.
All segments appear in the list below the controls. They can be renamed with **Rename** and adjusted directly on the timeline by dragging or resizing the colored bars.

Click **Export** to save each segment as an MP3 file. The application expects
an `ffmpeg` directory next to `main.py` containing the `ffmpeg` executable
(e.g. `ffmpeg/ffmpeg.exe` on Windows).

During export, ffmpeg's output is displayed in the log panel at the bottom of
the window so you can follow the conversion progress.

