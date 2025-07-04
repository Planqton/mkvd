# mkvd

This project provides a simple GUI utility to convert MKV, AVI or MP4
video files to MP3 audio using `ffmpeg`.

## Requirements

- Python 3
- `ffmpeg` installed and available in `PATH`

On Debian/Ubuntu systems you can install `ffmpeg` with:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

## Usage

Run the script with Python:

```bash
python3 main.py
```

A small window will appear. Click **Export to MP3** and choose a video
file. The MP3 will be saved next to the original file.
