import tkinter as tk
from tkinter import Canvas, Button, PhotoImage
import os
import sys
from pathlib import Path
import subprocess

# This function handles the resource path, whether running normally or from PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # For PyInstaller bundled apps
    except Exception:
        base_path = os.path.abspath(".") # Fallback for regular execution

    return os.path.join(base_path, relative_path)

# Set the base path of the script
SCRIPT_PATH = Path(__file__).resolve().parent

# Define the assets folder where you've placed your image files
ASSETS_PATH = SCRIPT_PATH  # Pointing to the Final directory where the images are located

# Function to resolve paths dynamically
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / "assets" / Path(path)

root = tk.Tk()
root.geometry("1400x700")
root.configure(bg="#FFFFFF")

def exit_program():
    sys.exit()

def open_summarize_window(root):
    root.withdraw()  # Hide the main window
    summarize_script = SCRIPT_PATH /"CodeSummarizer" /"CodeSummarizer.py"
    subprocess.run(["python", resource_path(str(summarize_script))], cwd=SCRIPT_PATH)
    root.deiconify()  # Show the main window again when done

def open_analyze_window(root):
    root.withdraw()  # Hide the main window
    analyze_script = SCRIPT_PATH / "CodeAnalyser" /"CodeanalyserwithGui.py"
    subprocess.run(["python", resource_path(str(analyze_script))], cwd=SCRIPT_PATH)
    root.deiconify()  # Show the main window again when done

def open_Sourceplag_window(root):
    root.withdraw()  # Hide the main window
    sourceplag_script = SCRIPT_PATH / "SourcePlag" / "SourcePlag.py"
    subprocess.run(["python", resource_path(str(sourceplag_script))], cwd=SCRIPT_PATH / "SourcePlag")
    root.deiconify()  # Show the main window again when done

canvas = Canvas(
    root,
    bg="#FFFFFF",
    height=700,
    width=1400,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)

try:
    image_image_1 = PhotoImage(
        file=relative_to_assets("Frame 7.png")  
    )
    image_1 = canvas.create_image(
        700.0,
        350.0,
        image=image_image_1
    )
except tk.TclError as e:
    print(f"Error loading image: {e}")

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png")  # Ensure that button_1.png exists in the Final directory
)
summarize_button = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: open_summarize_window(root),
    relief="flat"
)
summarize_button.place(
    x=810.0,
    y=343.0,
    width=225.0390625,
    height=57.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png")  # Ensure that button_2.png exists in the Final directory
)
analyze_button = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: open_analyze_window(root),
    relief="flat"
)
analyze_button.place(
    x=455.0,
    y=322.0,
    width=225.0390625,
    height=57.0
)

button_image_4 = PhotoImage(
    file=relative_to_assets("button_7.png")  # Ensure that button_7.png exists in the Final directory
)
sourceplag_button = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: open_Sourceplag_window(root),
    relief="flat"
)
sourceplag_button.place(
    x=117.0,
    y=339.0,
    width=225.0390625,
    height=57.0
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png")  # Ensure that button_3.png exists in the Final directory
)
exit_button = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: exit_program(),
    relief="flat"
)

exit_button.place(
    x=591.0,
    y=631.0,
    width=95.42,
    height=51.27
)

root.resizable(False, False)
root.mainloop()
