# mkvd

This tool provides a simple video player with segment management. It no longer
requires VLC and instead uses OpenCV and Pillow for video display. Install the
`opencv-python` package (imported in code as `cv2`) and `Pillow`:

```bash
pip install opencv-python Pillow
```

Attempting to install a package named `cv2` will fail, as the module is
distributed under the `opencv-python` name.
