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
provided buttons and slider. Segments can be defined visually by dragging on the
timeline under the slider. Each new segment appears in the list below and can be
removed by double-clicking it on the timeline. The legacy **Flag Start** and
**Flag End** buttons are also available if you prefer to set the times manually.
