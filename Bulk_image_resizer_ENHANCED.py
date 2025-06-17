import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import glob
import time
from datetime import datetime
import threading

# Create output folder with timestamp
def create_output_folder(folder):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join(folder, f"Resized_Images_{timestamp}")
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

# Resize and rename images
def process_images():
    folder = folder_path.get()
    base_name = base_name_entry.get()
    
    try:
        width = int(width_entry.get())
        height = int(height_entry.get())
        if width <= 0 or height <= 0:
            raise ValueError
    except:
        messagebox.showerror("Input Error", "Width and height must be positive integers")
        return

    if not folder:
        messagebox.showerror("Error", "Please select a folder.")
        return
        
    if not base_name:
        messagebox.showerror("Error", "Please enter a base name.")
        return

    images = glob.glob(os.path.join(folder, "*.[jp][pn]*g"))  # .jpg and .png
    images.extend(glob.glob(os.path.join(folder, "*.webp")))  # Add WebP support
    if not images:
        messagebox.showinfo("Info", "No images found in the selected folder.")
        return

    # Get processing options
    resize_mode = resize_mode_var.get()
    bg_color = bg_color_var.get()
    output_format = format_var.get()
    jpeg_quality = quality_scale.get()
    
    # Disable process button during operation
    process_btn.config(state=tk.DISABLED)
    progress_bar['value'] = 0
    progress_bar['maximum'] = len(images)
    status_var.set(f"Processing 0 of {len(images)} images...")
    
    # Run processing in a separate thread to keep UI responsive
    processing_thread = threading.Thread(
        target=do_image_processing,
        args=(images, folder, base_name, width, height, resize_mode, bg_color, output_format, jpeg_quality)
    )
    processing_thread.daemon = True
    processing_thread.start()

def do_image_processing(images, folder, base_name, width, height, resize_mode, bg_color, output_format, jpeg_quality):
    try:
        output = create_output_folder(folder)
        count = 1
        processed_count = 0
        errors = []
        
        for img_path in images:
            try:
                img = Image.open(img_path)
                original_format = img.format
                
                # Apply resize mode
                if resize_mode == "stretch":
                    img = img.resize((width, height), Image.LANCZOS)
                elif resize_mode == "fit":
                    img.thumbnail((width, height), Image.LANCZOS)
                elif resize_mode == "fill":
                    # Calculate ratios
                    width_ratio = width / img.width
                    height_ratio = height / img.height
                    ratio = max(width_ratio, height_ratio)
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    
                    # Resize and crop
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    left = (new_width - width) / 2
                    top = (new_height - height) / 2
                    right = left + width
                    bottom = top + height
                    img = img.crop((left, top, right, bottom))
                elif resize_mode == "pad":
                    # Calculate ratios
                    width_ratio = width / img.width
                    height_ratio = height / img.height
                    ratio = min(width_ratio, height_ratio)
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    
                    # Resize and pad
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    img = Image.new("RGB", (width, height), bg_color)
                    img.paste(resized_img, ((width - new_width) // 2, (height - new_height) // 2))
                
                # Determine file extension and format
                ext = "jpg" if output_format == "jpeg" else output_format
                if output_format == "original":
                    ext = original_format.lower()
                    if ext == "jpeg": 
                        ext = "jpg"
                    output_format = original_format
                
                # Create new filename
                new_name = f"{base_name}{str(count).zfill(3)}.{ext}"
                output_path = os.path.join(output, new_name)
                
                # Save with appropriate parameters
                save_params = {}
                if output_format == "JPEG":
                    save_params['quality'] = jpeg_quality
                elif output_format == "PNG":
                    save_params['compress_level'] = 6
                
                img.save(output_path, format=output_format, **save_params)
                count += 1
                processed_count += 1
                
            except Exception as e:
                errors.append(f"Failed to process {os.path.basename(img_path)}: {str(e)}")
            
            # Update progress
            progress_bar.step(1)
            status_var.set(f"Processing {progress_bar['value']} of {len(images)} images...")
            app.update_idletasks()
        
        # Enable process button after operation
        process_btn.config(state=tk.NORMAL)
        
        # Show completion message
        message = f"Successfully processed {processed_count} of {len(images)} images!"
        if errors:
            error_msg = "\n".join(errors[:5])  # Show first 5 errors
            if len(errors) > 5:
                error_msg += f"\n...and {len(errors)-5} more errors"
            message += f"\n\nErrors occurred:\n{error_msg}"
            
        messagebox.showinfo("Processing Complete", message)
        status_var.set("Ready")
        progress_bar['value'] = 0
        
    except Exception as e:
        messagebox.showerror("Processing Error", f"An unexpected error occurred: {str(e)}")
        process_btn.config(state=tk.NORMAL)
        status_var.set("Error occurred")

# Browse folder
def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)
        
        # Count images in folder
        images = glob.glob(os.path.join(folder, "*.[jp][pn]*g"))
        images.extend(glob.glob(os.path.join(folder, "*.webp")))
        status_var.set(f"Found {len(images)} images")

# Choose background color
def choose_color():
    color = colorchooser.askcolor(title="Choose background color")[1]
    if color:
        bg_color_var.set(color)
        color_btn.config(bg=color)

# Update UI based on resize mode selection
def update_mode_ui():
    mode = resize_mode_var.get()
    if mode == "pad":
        color_frame.pack(fill=tk.X, padx=10, pady=5)
    else:
        color_frame.pack_forget()

# Create the main application window
app = tk.Tk()
app.title("Pro Image Resizer")
app.geometry("650x600")
app.resizable(True, True)

# Set application icon
try:
    icon = Image.new('RGB', (1, 1), (50, 100, 200))
    app.iconphoto(True, ImageTk.PhotoImage(icon))
except:
    pass

# Configure style
style = ttk.Style()
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0")
style.configure("TButton", font=("Arial", 10))
style.configure("Header.TLabel", font=("Arial", 14, "bold"), foreground="#2c3e50")
style.configure("Status.TLabel", font=("Arial", 9), foreground="#555555")

# Create main frame
main_frame = ttk.Frame(app, padding=15)
main_frame.pack(fill=tk.BOTH, expand=True)

# Header
header = ttk.Label(main_frame, text="Pro Image Resizer", style="Header.TLabel")
header.pack(pady=(0, 15))

# Input Section
input_frame = ttk.LabelFrame(main_frame, text="Image Settings")
input_frame.pack(fill=tk.X, padx=5, pady=5)

# Folder selection
folder_frame = ttk.Frame(input_frame)
folder_frame.pack(fill=tk.X, padx=5, pady=5)

ttk.Label(folder_frame, text="Image Folder:").pack(side=tk.LEFT, padx=(0, 5))
folder_path = tk.StringVar()
folder_entry = ttk.Entry(folder_frame, textvariable=folder_path, width=40)
folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
ttk.Button(folder_frame, text="Browse", command=browse_folder).pack(side=tk.LEFT)

# Base name
name_frame = ttk.Frame(input_frame)
name_frame.pack(fill=tk.X, padx=5, pady=5)

ttk.Label(name_frame, text="Base Name:").pack(side=tk.LEFT, padx=(0, 5))
base_name_entry = ttk.Entry(name_frame)
base_name_entry.insert(0, "image_")
base_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Dimensions
dim_frame = ttk.Frame(input_frame)
dim_frame.pack(fill=tk.X, padx=5, pady=5)

ttk.Label(dim_frame, text="Width:").pack(side=tk.LEFT, padx=(0, 5))
width_entry = ttk.Entry(dim_frame, width=8)
width_entry.insert(0, "1080")
width_entry.pack(side=tk.LEFT, padx=(0, 15))

ttk.Label(dim_frame, text="Height:").pack(side=tk.LEFT, padx=(0, 5))
height_entry = ttk.Entry(dim_frame, width=8)
height_entry.insert(0, "1080")
height_entry.pack(side=tk.LEFT)

# Processing Options Section
options_frame = ttk.LabelFrame(main_frame, text="Processing Options")
options_frame.pack(fill=tk.X, padx=5, pady=10)

# Resize mode
mode_frame = ttk.Frame(options_frame)
mode_frame.pack(fill=tk.X, padx=5, pady=5)

ttk.Label(mode_frame, text="Resize Mode:").pack(side=tk.LEFT, padx=(0, 10))

resize_mode_var = tk.StringVar(value="fit")
modes = [
    ("Stretch (distort)", "stretch"),
    ("Fit (keep aspect)", "fit"),
    ("Fill (crop)", "fill"),
    ("Pad (add background)", "pad")
]

for text, mode in modes:
    ttk.Radiobutton(
        mode_frame, 
        text=text, 
        variable=resize_mode_var, 
        value=mode,
        command=update_mode_ui
    ).pack(side=tk.LEFT, padx=(0, 10))

# Background color (only shown for pad mode)
color_frame = ttk.Frame(options_frame)
ttk.Label(color_frame, text="Background Color:").pack(side=tk.LEFT, padx=(0, 10))

bg_color_var = tk.StringVar(value="#FFFFFF")
color_btn = ttk.Button(
    color_frame, 
    text="Choose", 
    command=choose_color,
    width=8
)
color_btn.pack(side=tk.LEFT)

# Output format
format_frame = ttk.Frame(options_frame)
format_frame.pack(fill=tk.X, padx=5, pady=5)

ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=(0, 10))

format_var = tk.StringVar(value="jpeg")
formats = ["jpeg", "png", "original"]
format_combo = ttk.Combobox(
    format_frame, 
    textvariable=format_var, 
    values=formats,
    state="readonly",
    width=10
)
format_combo.pack(side=tk.LEFT, padx=(0, 15))

# Quality setting
ttk.Label(format_frame, text="JPEG Quality:").pack(side=tk.LEFT, padx=(0, 5))
quality_scale = ttk.Scale(
    format_frame, 
    from_=1, 
    to=100, 
    orient=tk.HORIZONTAL,
    length=100
)
quality_scale.set(90)
quality_scale.pack(side=tk.LEFT, padx=(0, 5))
quality_value = ttk.Label(format_frame, text="90%")
quality_value.pack(side=tk.LEFT)

# Update quality label when scale changes
def update_quality_label(event):
    quality_value.config(text=f"{int(quality_scale.get())}%")
quality_scale.bind("<Motion>", update_quality_label)

# Process button
button_frame = ttk.Frame(main_frame)
button_frame.pack(fill=tk.X, padx=5, pady=15)

process_btn = ttk.Button(
    button_frame, 
    text="PROCESS IMAGES", 
    command=process_images,
    style="TButton",
    width=20
)
process_btn.pack()

# Progress bar
progress_frame = ttk.Frame(main_frame)
progress_frame.pack(fill=tk.X, padx=5, pady=(10, 5))

progress_bar = ttk.Progressbar(
    progress_frame, 
    orient=tk.HORIZONTAL, 
    mode='determinate'
)
progress_bar.pack(fill=tk.X)

# Status bar
status_frame = ttk.Frame(main_frame)
status_frame.pack(fill=tk.X, padx=5, pady=(0, 10))

status_var = tk.StringVar(value="Ready")
status_label = ttk.Label(
    status_frame, 
    textvariable=status_var,
    style="Status.TLabel"
)
status_label.pack(side=tk.LEFT)

# Initialize UI
update_mode_ui()

# Start the application
app.mainloop()