import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage
import threading
import os
import sys
from pathlib import Path
from g4f.client import Client

# Initialize g4f Client
client = Client()

# Asset path handling functions
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Define paths
SCRIPT_PATH = Path(__file__).resolve().parent
ASSETS_PATH = SCRIPT_PATH / "assets"

def relative_to_assets(path: str) -> Path:
    """Convert relative asset path to absolute path"""
    return ASSETS_PATH / Path(path)

def ensure_assets_directory():
    """Ensure the assets directory exists"""
    if not ASSETS_PATH.exists():
        ASSETS_PATH.mkdir(parents=True, exist_ok=True)

def ask_g4f(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-405b",
            messages=[{"role": "user", "content": f"Reply in English only: {prompt}"}]
        )
        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "Error: Failed to get a response from GPT-4."
    except Exception as e:
        return f"Error: {str(e)}"

def scroll_to_bottom():
    root.after(100, lambda: chat_canvas._parent_canvas.yview_moveto(1.0))

def create_message_bubble(parent, text, color, align):
    outer_width = 580  # Maximum width for the message bubble
    
    message_frame = ctk.CTkFrame(
        parent,
        fg_color="#f0f0f0" if align == "left" else "#d9edf7",
        corner_radius=10
    )
    
    # Create a frame for the message content
    content_frame = ctk.CTkFrame(
        message_frame,
        fg_color="transparent"
    )
    content_frame.pack(padx=5, pady=5, fill="both", expand=True)
    
    # Add the message text with proper formatting
    message_label = ctk.CTkLabel(
        content_frame,
        text=text,
        wraplength=outer_width - 40,  # Account for padding
        justify="left",
        text_color=color,
        anchor="w"
    )
    message_label.pack(padx=10, pady=5, fill="both", expand=True)
    
    return message_frame

def copy_to_clipboard(text):
    """Copy text to clipboard and show notification"""
    if not text:
        messagebox.showwarning("Copy Error", "No text to copy!")
        return
        
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()  # Required for clipboard to work
        show_copy_notification()
    except Exception as e:
        messagebox.showerror("Copy Error", f"Failed to copy text: {str(e)}")

def show_copy_notification():
    """Show a temporary notification that text was copied"""
    notification_window = ctk.CTkToplevel()
    notification_window.withdraw()  # Hide initially to prevent flash
    
    # Get the main window's position
    window_x = root.winfo_x()
    window_y = root.winfo_y()
    window_width = root.winfo_width()
    
    # Calculate position (bottom right of main window)
    x = window_x + window_width - 200
    y = window_y + 50
    
    # Configure notification window
    notification_window.geometry(f"180x40+{x}+{y}")
    notification_window.overrideredirect(True)  # Remove window decorations
    notification_window.configure(fg_color="#333333")
    
    # Add message
    label = ctk.CTkLabel(
        notification_window,
        text="Copied to clipboard!",
        text_color="white",
        font=("Arial", 12)
    )
    label.pack(expand=True)
    
    notification_window.deiconify()  # Show the window
    
    # Schedule the window to close
    root.after(1500, notification_window.destroy)

def update_message_in_chat(message_frame, new_text):
    # Remove existing widgets
    for widget in message_frame.winfo_children():
        widget.destroy()
    
    # Create new message bubble
    message_widget = create_message_bubble(message_frame, new_text, "green", "left")
    message_widget.pack(anchor="w", padx=10, pady=5)
    
    # Add copy button frame
    button_frame = ctk.CTkFrame(message_frame, fg_color="transparent")
    button_frame.pack(side="left", padx=10, pady=5)
    
    # Load and create copy button
    try:
        copy_icon = PhotoImage(file=relative_to_assets("copy_icon.png"))
        copy_icon = copy_icon.subsample(15, 15)
    except:
        copy_icon = None  # Fallback if icon isn't available
    
    copy_button = ctk.CTkButton(
        button_frame,
        image=copy_icon if copy_icon else None,
        text="" if copy_icon else "Copy",
        command=lambda: copy_to_clipboard(new_text),
        width=20 if copy_icon else 60,
        height=20,
        fg_color="#f0f0f0",
        hover_color="#e0e0e0"
    )
    if copy_icon:
        copy_button.image = copy_icon
    copy_button.pack(pady=5)
    
    # Ensure proper scrolling
    chat_frame.update_idletasks()
    root.after(100, scroll_to_bottom)
    
    return message_frame

def add_message_to_chat(sender, message, color, align):
    outer_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
    outer_frame.pack(anchor="e" if align == "right" else "w", pady=5, padx=10, fill="x")
    
    # Add sender label if needed
    if sender:
        sender_label = ctk.CTkLabel(
            outer_frame,
            text=sender,
            text_color="gray",
            font=("Arial", 10)
        )
        sender_label.pack(anchor="e" if align == "right" else "w", padx=15)
    
    message_widget = create_message_bubble(outer_frame, message, color, align)
    message_widget.pack(anchor="e" if align == "right" else "w", padx=10, pady=5)
    
    chat_frame.update_idletasks()
    scroll_to_bottom()
    
    return outer_frame

def ask_question():
    query = query_entry.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a query!")
        return

    code = code_text.get("1.0", ctk.END).strip()
    if not code:
        messagebox.showwarning("Input Error", "No code loaded!")
        return

    prompt = f"{query}\n\nCode:\n{code}"
    add_message_to_chat("You", query, "blue", align="right")
    bot_message_id = add_message_to_chat("Bot", "Loading...", "green", align="left")

    def get_response():
        answer = ask_g4f(prompt)
        update_message_in_chat(bot_message_id, answer)
        root.after(100, scroll_to_bottom)

    threading.Thread(target=get_response, daemon=True).start()

def open_file():
    file_path = filedialog.askopenfilename(
        title="Open Code File",
        filetypes=[("Code Files", "*.py *.java *.cpp *.js *.txt")]
    )
    if file_path:
        with open(file_path, 'r') as file:
            code = file.read()
        code_text.delete("1.0", ctk.END)
        code_text.insert(ctk.END, code)
        status_label.configure(text=f"Loaded: {file_path}")

# Initialize assets
ensure_assets_directory()

# GUI setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Code Query Chatbot")
root.geometry("800x700")

# Sidebar
sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
sidebar.pack(side="left", fill="y")

sidebar_label = ctk.CTkLabel(sidebar, text="File Operations", font=("Arial", 16, "bold"))
sidebar_label.pack(pady=10)

upload_btn = ctk.CTkButton(sidebar, text="Upload Code File", command=open_file)
upload_btn.pack(pady=10, padx=20)

status_label = ctk.CTkLabel(sidebar, text="No file loaded", wraplength=180, font=("Arial", 12))
status_label.pack(pady=10, padx=20)

# Main frame
main_frame = ctk.CTkFrame(root)
main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Chat area
chat_canvas = ctk.CTkScrollableFrame(main_frame, width=700, height=400)
chat_canvas.pack(fill="both", expand=True)

chat_frame = ctk.CTkFrame(chat_canvas, fg_color="transparent")
chat_frame.pack(fill="both", expand=True)

# Code editor
code_frame = ctk.CTkFrame(main_frame)
code_frame.pack(fill="both", expand=False, pady=10)

code_label = ctk.CTkLabel(code_frame, text="Code Editor", font=("Arial", 14, "bold"))
code_label.pack(anchor="w")

code_text = ctk.CTkTextbox(code_frame, height=150)
code_text.pack(fill="both", expand=True)

# Query input
input_frame = ctk.CTkFrame(main_frame)
input_frame.pack(fill="x", pady=10)

query_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter your query here...", width=400)
query_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)

ask_btn = ctk.CTkButton(input_frame, text="Ask", command=ask_question)
ask_btn.pack(side="right", padx=10)

root.mainloop()