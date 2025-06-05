import cv2
import numpy as np
import os

from PIL import Image
import threading
import time
import tkinter as tk
import mss  # Add this import

# ASCII grayscale shading from dark to light
ASCII_CHARS = " .:-=+*#%@"

# Shared variables for Tkinter controls
resolution = {"width": 1727}
fps_info = {"fps": 0, "spf": 0}

def frame_to_ascii(frame, new_width=3600):
    """Convert a frame to ASCII grayscale representation with reduced resolution."""
    image = Image.fromarray(frame).convert("L")  # Convert to grayscale using PIL

    # Calculate new height to maintain aspect ratio (adjust for font aspect ratio)
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.5)  # 0.5 compensates for font aspect

    # Resize image
    image = image.resize((new_width, new_height))
    pixels = np.array(image)

    ascii_image = "\n".join(
        "".join(ASCII_CHARS[min(pixel // 25, len(ASCII_CHARS) - 1)] for pixel in row)
        for row in pixels
    )
    return ascii_image

def live_screen_capture():
    """Capture actual screen, render grayscale ASCII at reduced resolution, and overlay mouse cursor."""
    prev_time = time.time()
    frame_count = 0
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Full primary screen
        while True:
            start_time = time.time()
            sct_img = sct.grab(monitor)
            screenshot = Image.frombytes('RGB', sct_img.size, sct_img.rgb)

            # Draw mouse cursor
            try:
                import pyautogui
                mouse_x, mouse_y = pyautogui.position()
            except ImportError:
                mouse_x, mouse_y = 0, 0
            draw = screenshot.copy()
            cursor_size = 8  # Size of the cursor marker
            cursor_color = (0, 0, 0)  # Black color for visibility

            for dx in range(-cursor_size, cursor_size + 1):
                for dy in range(-cursor_size, cursor_size + 1):
                    if 0 <= mouse_x + dx < draw.width and 0 <= mouse_y + dy < draw.height:
                        if abs(dx) == cursor_size or abs(dy) == cursor_size:
                            draw.putpixel((mouse_x + dx, mouse_y + dy), cursor_color)

            screen_shot = np.array(draw)[:, :, :3]  # Convert PIL image to numpy array and get RGB
            printcontent = frame_to_ascii(screen_shot, new_width=resolution["width"])
            os.system("cls" if os.name == "nt" else "clear")  # Clear terminal
            print(printcontent)  # Reduced resolution

            frame_count += 1
            elapsed = time.time() - prev_time
            if elapsed >= 1.0:
                fps_info["fps"] = frame_count / elapsed
                fps_info["spf"] = elapsed / frame_count
                prev_time = time.time()
                frame_count = 0

            if cv2.waitKey(1) == ord('q'):
                break

            # Optional: Limit FPS for CPU savings
            time.sleep(max(0, 0.1 - (time.time() - start_time)))
def tk_window():
    def update_labels():
        fps_label.config(text=f"FPS: {fps_info['fps']:.2f}")
        spf_label.config(text=f"SPF: {fps_info['spf']:.3f}")
        root.after(200, update_labels)

    def set_resolution(val):
        resolution["width"] = int(val)

    root = tk.Tk()
    root.title("ASCII Screen Capture Controls")
    root.geometry("300x200")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    tk.Label(root, text="Resolution (width):").pack()
    res_slider = tk.Scale(root, from_=80, to=3600, orient=tk.HORIZONTAL, command=set_resolution)
    res_slider.set(resolution["width"])
    res_slider.pack()

    fps_label = tk.Label(root, text="FPS: 0.00")
    fps_label.pack()
    spf_label = tk.Label(root, text="SPF: 0.000")
    spf_label.pack()

    update_labels()
    root.mainloop()

if __name__ == "__main__":
    # Start Tkinter window in a separate thread
    threading.Thread(target=tk_window, daemon=True).start()
    live_screen_capture()
