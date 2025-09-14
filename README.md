# FixPeek

FixPeek is a fast, lightweight image viewer written in **Python** with **PySide6 (Qt)**.  
It is designed for quick viewing of photos (JPEG, PNG, TIFF, WebP, RAW) with  
useful features for photographers:

## Features
- Fast navigation with mouse wheel or keyboard
- Fullscreen mode (F key / middle mouse button)
- Peek-Zoom: hold Ctrl + Left Click to zoom temporarily
- Slideshow mode with adjustable interval (0.1 s – 10 min)
- Metadata panel (EXIF info: camera, lens, exposure, ISO, …)
- Sorting by filename, date, type, camera, or lens
- Drag & Drop of files or folders
- Optional RAW support via `rawpy`
- Multilingual (German, English, Spanish, French)

## Installation
### Requirements
- Python 3.12+
- [PySide6](https://pypi.org/project/PySide6/)
- [Pillow](https://pypi.org/project/Pillow/)
- [exifread](https://pypi.org/project/ExifRead/) (optional, for EXIF metadata)
- [rawpy](https://pypi.org/project/rawpy/) + [numpy](https://pypi.org/project/numpy/) (optional, for RAW support)
- [send2trash](https://pypi.org/project/Send2Trash/)

### Run from source
```bash
git clone https://github.com/JJausF/fixpeek.git
cd fixpeek
python3 main.py