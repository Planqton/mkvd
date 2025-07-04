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
You can also move the slider with the left and right arrow keys even while playback is paused.
Mark a section with **Set Start** and **Set End**, then click **Add Segment** to store it.
All segments appear in the list below the controls. They can be renamed with **Rename**, edited by entering new start or end values in the fields under the list, and adjusted directly on the timeline by dragging or resizing the colored bars. When the mouse hovers over a segment edge the cursor changes to a left-right arrow so you know it can be resized.

Click **Export** to save each segment as an MP3 file. A folder dialog will ask
where to place the resulting files. The application expects an `ffmpeg`
directory next to `main.py` containing the `ffmpeg` executable
(e.g. `ffmpeg/ffmpeg.exe` on Windows).

The ffmpeg output appears in a dedicated log text field at the bottom of the
window. The field is fairly tall so longer command output remains readable and
above it a small status label shows which segment is being exported. While
export is running all other controls are disabled to prevent changes.


