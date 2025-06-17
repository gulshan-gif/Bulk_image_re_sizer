# Bulk Image Resizer 🖼️

A simple, powerful desktop tool to resize, rename, and convert images in bulk — now enhanced with PNG conversion, drag-and-drop support, and live preview.

## 🔧 Features

- ✅ Batch image resizing
- ✅ Rename with base name and index
- ✅ Resize modes: Stretch, Fit, Fill, Pad (with background color)
- ✅ Output formats: JPEG, PNG, or Original
- ✅ NEW: **Force PNG Output** (override dropdown)
- ✅ NEW: **Drag-and-drop folder support**
- ✅ NEW: **Image preview panel**
- ✅ Real-time progress bar and error handling

## 🖥️ How to Use

1. Run the script: `Bulk_image_resizer_ENHANCED.py`
2. Select or drag in a folder containing images (JPG, PNG, or WebP)
3. Choose dimensions, rename base, and output format
4. Click `PROCESS IMAGES`

> 💡 All resized images are saved to a new output folder with a timestamp.

## 📦 Dependencies

- Python 3.x
- [Pillow](https://pypi.org/project/Pillow/)

Install via:
```bash
pip install pillow
```

## 📁 Optional EXE Packaging (For Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed Bulk_image_resizer_ENHANCED.py
```

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Created with ❤️ by [Rinnggo](https://your-link-here)
