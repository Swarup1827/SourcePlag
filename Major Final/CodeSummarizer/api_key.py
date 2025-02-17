import openai
import os
import sys
import threading
from tkinter import filedialog, messagebox, PhotoImage
import customtkinter as ctk
from pathlib import Path

# Set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Function to resolve paths dynamically
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # For PyInstaller bundled apps
    except Exception:
        base_path = os.path.abspath(".")  # Fallback for regular execution
    return os.path.join(base_path, relative_path)

# Set the base path of the script
SCRIPT_PATH = Path(__file__).resolve().parent
ASSETS_PATH = SCRIPT_PATH / "assets"

# Function to resolve paths dynamically for assets
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Function to handle user queries using OpenAI's API
def ask_openai(prompt):
    try:
        # Send request to OpenAI API using the new method
        response = openai.completions.create(
            model="gpt-4",  # You can change this to other models if needed
            prompt=f"Reply in English only: {prompt}",
            max_tokens=150
        )
        if response and response.choices:
            return response.choices[0].text.strip()
        else:
            return "Error: Failed to get a response from GPT-4."
    except Exception as e:
        return f"Error: {str(e)}"


# Function to handle user queries
def ask_question():
    query = query_entry.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a query!")
        return

    code = code_text.get("1.0", ctk.END).strip()
    if not code:
        messagebox.showwarning("Input Error", "No code loaded!")
        return

    # Combine the code and user query for OpenAI's prompt
    prompt = f"{query}\n\nCode:\n{code}"

    # Add user's query to the chat immediately
    add_message_to_chat("You", query, "blue", align="right")

    # Add "Loading..." placeholder for bot's response
    bot_message_id = add_message_to_chat("Bot", "Loading...", "green", align="left")

    # Run the AI request in a separate thread
    def get_response():
        answer = ask_openai(prompt)

        # Update the placeholder with the actual response
        update_message_in_chat(bot_message_id, answer)

    threading.Thread(target=get_response, daemon=True).start()

# Function to add messages to the chat area
def add_message_to_chat(sender, message, color, align):
    message_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
    message_frame.pack(anchor="e" if align == "right" else "w", pady=5, padx=10, fill="x")

    message_label = ctk.CTkLabel(
        message_frame,
        text=message,
        wraplength=600,
        text_color=color,
        anchor="w" if align == "left" else "e",
        justify="left" if align == "left" else "right",
        fg_color="#f0f0f0" if align == "left" else "#d9edf7",
        corner_radius=10,
        padx=10,
        pady=5,
    )
    message_label.pack(anchor="e" if align == "right" else "w", padx=10, pady=5)

    if align == "left":
        copy_icon = PhotoImage(file=relative_to_assets("copy_icon.png"))
        copy_icon = copy_icon.subsample(15, 15)  
        copy_button = ctk.CTkButton(
            message_frame,
            image=copy_icon,
            text="",
            command=lambda: copy_to_clipboard(message_label),
            width=20, height=20,
            fg_color="#f0f0f0",
            hover_color="#e0e0e0"
        )
        copy_button.image = copy_icon  
        copy_button.pack(side="left", pady=5)

    chat_canvas.update_idletasks()
    chat_canvas._parent_canvas.yview_moveto(1.0)

    return message_label

# Function to update a message in the chat area
def update_message_in_chat(message_label, new_text):
    message_label.configure(text=new_text)

# Function to copy text to clipboard
def copy_to_clipboard(message_label):
    root.clipboard_clear()
    root.clipboard_append(message_label.cget("text"))
    root.update()
    show_copy_message_dialog()

# Dialog box after copying
def show_copy_message_dialog():
    messagebox.showinfo("Copied", "The message has been copied to the clipboard!")

# Function to read code from uploaded file
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

# GUI setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Code Query Chatbot")
root.geometry("800x700")

sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
sidebar.pack(side="left", fill="y")

sidebar_label = ctk.CTkLabel(sidebar, text="File Operations", font=("Arial", 16, "bold"))
sidebar_label.pack(pady=10)

upload_btn = ctk.CTkButton(sidebar, text="Upload Code File", command=open_file)
upload_btn.pack(pady=10, padx=20)

status_label = ctk.CTkLabel(sidebar, text="No file loaded", wraplength=180, font=("Arial", 12))
status_label.pack(pady=10, padx=20)

main_frame = ctk.CTkFrame(root)
main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

chat_canvas = ctk.CTkScrollableFrame(main_frame, width=700, height=400)
chat_canvas.pack(fill="both", expand=True)

chat_frame = ctk.CTkFrame(chat_canvas)
chat_frame.pack(fill="both", expand=True)

code_frame = ctk.CTkFrame(main_frame)
code_frame.pack(fill="both", expand=False, pady=10)

code_label = ctk.CTkLabel(code_frame, text="Code Editor", font=("Arial", 14, "bold"))
code_label.pack(anchor="w")

code_text = ctk.CTkTextbox(code_frame, height=150)
code_text.pack(fill="both", expand=True)

input_frame = ctk.CTkFrame(main_frame)
input_frame.pack(fill="x", pady=10)

query_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter your query here...", width=400)
query_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)

ask_btn = ctk.CTkButton(input_frame, text="Ask", command=ask_question)
ask_btn.pack(side="right", padx=10)

root.mainloop()
