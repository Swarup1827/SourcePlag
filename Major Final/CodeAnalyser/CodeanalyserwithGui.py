import tkinter as tk
from tkinter import filedialog, ttk
import re
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from tkinter import Canvas, Text, PhotoImage, Button
from pathlib import Path
import os
import sys
nltk.download('punkt_tab')
text_font = ('Times New Roman', 12)


# OUTPUT_PATH = Path(__file__).parent
# ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\SIDDHARTH\Desktop\Final\CodeAnalyser")
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

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH/ "assets" / Path(path)

def analyze_code():
    global functions_text, variables_text, comments_text, code_tree

    result_label.config(text="")
    result_label.config(fg="black")

    filename = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if not filename:
        return

    try:
        with open(filename, 'r') as file:
            code = file.read()

            tokens = word_tokenize(code)

            functions = re.findall(r'def\s+(\w+)', code)
            numbered_functions = [f"{i + 1}. {func}" for i, func in enumerate(functions)]

            variables = set(re.findall(r'\b(\w+)\s*=', code))
            numbered_variables = [f"{i + 1}. {var}" for i, var in enumerate(sorted(variables))]

            comments = re.findall(r'#(.+)', code)
            docstrings = re.findall(r'(\'\'\'(.+?)\'\'\'|\"\"\"(.+?)\"\"\")', code, re.DOTALL)
            comments.extend([docstring[0] if docstring[0] else docstring[1] for docstring in docstrings])

            # Function to filter out non-alphabetic words
            def filter_words(tokens):
                return [word.lower() for word in tokens if word.isalpha()]

            comments_word_freq = Counter(filter_words(word_tokenize(" ".join(comments))))
            code_word_freq = Counter(filter_words(tokens))

            functions_text.delete(1.0, tk.END)
            variables_text.delete(1.0, tk.END)
            comments_text.delete(1.0, tk.END)
            code_tree.delete(*code_tree.get_children())

            functions_text.insert(tk.END, '\n'.join(numbered_functions))
            variables_text.insert(tk.END, '\n'.join(numbered_variables))
            comments_text.insert(tk.END, '\n'.join([f"{i + 1}. {comment}" for i, comment in enumerate(comments)]))

            sorted_code_word_freq = dict(sorted(code_word_freq.items(), key=lambda item: item[1], reverse=True))

            for i, (word, freq) in enumerate(sorted_code_word_freq.items(), start=1):
                code_tree.insert("", tk.END, values=(i, word, freq))

            total_functions = len(functions)
            total_variables = len(variables)
            total_comments = len(comments)
            total_docstrings = len(docstrings)

            functions_text.insert(tk.END, f"\n\n--------------------------------------")
            functions_text.insert(tk.END, f"\nTotal Functions: {total_functions}")
            functions_text.insert(tk.END, f"\n--------------------------------------")
            variables_text.insert(tk.END, f"\n\n--------------------------------------")
            variables_text.insert(tk.END, f"\nTotal Variables: {total_variables}")
            variables_text.insert(tk.END, f"\n--------------------------------------")
            comments_text.insert(tk.END, f"\n\n-------------------------------------")
            comments_text.insert(tk.END, f"\nTotal Comments and Docstrings: {total_comments + total_docstrings}")
            comments_text.insert(tk.END, f"\n-------------------------------------")

    except FileNotFoundError:
        result_label.config(text="File not found.", fg="red")


def save_report():
    global result_label
    if not code_tree.get_children():
        tk.messagebox.showwarning("No File Analyzed", "Please Select Input File For Generating Report.")
        return

    filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if filename:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Function Names
        functions_text_content = functions_text.get("1.0", tk.END).strip().split('\n')
        total_functions = len(functions_text_content)
        elements.append(Paragraph("Function Names:", styles['Heading1']))
        for line in functions_text_content:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Paragraph("\n", styles['Normal']))

        # Variable Names
        variables_text_content = variables_text.get("1.0", tk.END).strip().split('\n')
        total_variables = len(variables_text_content)
        elements.append(Paragraph("Variable Names:", styles['Heading1']))
        for line in variables_text_content:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Paragraph("\n", styles['Normal']))

        # Comments and Docstrings
        comments_text_content = comments_text.get("1.0", tk.END).strip().split('\n')
        total_comments = len(comments_text_content)
        elements.append(Paragraph("Comments and Docstrings:", styles['Heading1']))
        for line in comments_text_content:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Paragraph("\n", styles['Normal']))

        # Word Frequencies in Code
        elements.append(Paragraph("Word Frequencies in Code:", styles['Heading1']))
        data = [("Serial No.", "Word", "Frequency")]
        for item in code_tree.get_children():
            data.append(code_tree.item(item)['values'])
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), 'grey'),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                    ('BACKGROUND', (0, 1), (-1, -1), 'lightgrey'),
                                    ('GRID', (0, 0), (-1, -1), 1, 'BLACK')]))
        elements.append(table)

        doc.build(elements)

        result_label.config(text="Report saved successfully.", fg="green")


# Initialize main window
window = tk.Tk()
window.geometry("1400x700")
window.configure(bg="#FFFFFF")

# Setup canvas for layout
canvas = Canvas(window, bg="#FFFFFF", height=700, width=1400, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

# Load images for the buttons and backgrounds
image_image_1 = PhotoImage(file=relative_to_assets("image_2.png"))
image_1 = canvas.create_image(
    700.0,
    350.0,
    image=image_image_1
)

# Buttons
button_image_1 = PhotoImage(file=relative_to_assets("button_4.png"))  # Adjust the path as necessary
button_1 = Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=save_report, relief="flat")
button_1.place(
    x=587.0,
    y=612.0,
    width=226.0390625,
    height=62.0
)

button_image_2 = PhotoImage(file=relative_to_assets("button_6.png"))  # Adjust the path as necessary
button_2 = Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=exit, relief="flat")
button_2.place(
    x=850.0,
    y=618.0,
    width=95.42030334472656,
    height=51.2669677734375
)

# New Button 3
button_image_3 = PhotoImage(file=relative_to_assets("button_5.png"))  # Adjust the path as necessary
button_3 = Button(image=button_image_3, borderwidth=0, highlightthickness=0, command=analyze_code, relief="flat")
button_3.place(
    x=587.0,
    y=25.0,
    width=225.0390625,
    height=58.0
)

# Entry boxes for displaying results
entry_image_1 = PhotoImage(file=relative_to_assets("entry_5.png"))  # Adjust the path as necessary
canvas.create_image(199.0, 370.0, image=entry_image_1)
functions_text = Text(bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0, font=text_font)
functions_text.place(
    x=45.0,
    y=160.0,
    width=308.0,
    height=420.0
)

entry_image_2 = PhotoImage(file=relative_to_assets("entry_5.png"))  # Adjust the path as necessary
canvas.create_image(534.0, 370.0, image=entry_image_2)
variables_text = Text(bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0, font=text_font)
variables_text.place(
    x=381.0,
    y=160.0,
    width=306.0,
    height=420.0
)

entry_image_3 = PhotoImage(
    file=relative_to_assets("entry_5.png"))
entry_bg_3 = canvas.create_image(
    868.0,
    370.5,
    image=entry_image_3
)
comments_text = Text(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=text_font
)
comments_text.place(
    x=716.0,
    y=160.0,
    width=305.0,
    height=420.0
)

entry_image_4 = PhotoImage(
    file=relative_to_assets("entry_5.png"))
entry_bg_4 = canvas.create_image(
    1202.0,
    372.5,
    image=entry_image_4
)
entry_4 = Text(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=text_font
)
entry_4.place(
    x=1051.0,
    y=160.0,
    width=303.0,
    height=410.0
)


style = ttk.Style()
style.configure("Custom.Treeview",
                borderwidth=0,          # No border
                highlightthickness=0,   # No highlight border
                background="#FFFFFF",
                fieldbackground="#FFFFFF",
                font=("Arial", 10))

style.map("Custom.Treeview", background=[('selected', '#e6e6e6')])

# Create Treeview without borders
code_tree = ttk.Treeview(window, columns=("serial_no", "word", "frequency"), show="headings", style="Custom.Treeview")
code_tree.heading("serial_no", text="Serial No.")
code_tree.heading("word", text="Word")
code_tree.heading("frequency", text="Frequency")
code_tree.column("serial_no", width=15)
code_tree.column("word", width=60)
code_tree.column("frequency", width=20)

# Set the position and dimensions of the Treeview
code_tree.place(x=1051.0, y=160.0, width=303.0, height=423.0)

# Result Label
result_label = tk.Label(window, text="", bg="#FFFFFF", fg="black")
result_label.place(x=630.0, y=90)

# Run the application
window.mainloop()
