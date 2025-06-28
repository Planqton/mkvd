# MKV Player

This repository provides a simple Python GUI application that can open and play
MKV video files using the VLC backend. The interface is built with `tkinter` and
includes basic playback controls and a progress slider.

## Requirements

- Python 3
- `python-vlc` library (`pip install python-vlc`)
- A local installation of VLC (required by `python-vlc`)

## Usage

```bash
pip install python-vlc
python3 player.py
```

Use the **File → Open** menu to select an MKV file and control playback with the
provided buttons and slider. You can mark segments of interest by pressing
**Flag Start** and **Flag End** while the video plays. Each pair of flags will be
added to the list below the slider.
