# Video Player with Segment Selection

This repository contains a simple Tkinter-based application for playing video files (`.mkv`, `.avi`, `.mp4`).
The application uses the `python-vlc` package to handle video playback and includes a timeline slider that allows selecting start and end points for segments, similar to basic video editing tools.

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

Use the **Load** button to open a video file. The timeline slider updates as the video plays. Use **Set Start** and **Set End** to mark a segment of interest. The selected segment range is displayed below the controls.
