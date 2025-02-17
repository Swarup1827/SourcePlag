import tkinter as tk
from tkinter import ttk, filedialog, messagebox,Text,Scrollbar  
import ast
import pandas as pd
import Levenshtein
import javalang
import clang.cindex
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import sys
import os
text_font = ('Times New Roman', 12)

testing_files = []
file_paths=[]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


SCRIPT_PATH = Path(__file__).resolve().parent

RELATIVE_ASSETS_PATH = Path(".")

ASSETS_PATH = SCRIPT_PATH / RELATIVE_ASSETS_PATH

def relative_to_assets(path: str) -> Path:
    
    return ASSETS_PATH / "assets" / Path(path)


def preprocess_code(code):
    return code.strip()

def generate_ast(code, language):
    try:
        if language == "Python":
            tree = ast.parse(code)
        elif language == "Java":
            tree = javalang.parse.parse(code)
        elif language == "C/C++":
            index = clang.cindex.Index.create()
            tu = index.parse('tmp.cpp', args=['-std=c++11'], unsaved_files=[('tmp.cpp', code)])
            tree = tu.cursor
        return tree
    except SyntaxError as e:
        print(f"Invalid code: {e}")
        return None

def compare_asts(ast1, ast2):
    normalized_code1 = normalize_code(ast1)
    normalized_code2 = normalize_code(ast2)
    similarity = Levenshtein.ratio(normalized_code1, normalized_code2)
    return similarity

def compare_java_asts(ast1, ast2):
    num_nodes_ast1 = count_nodes(ast1)
    num_nodes_ast2 = count_nodes(ast2)
    similarity = min(num_nodes_ast1, num_nodes_ast2) / max(num_nodes_ast1, num_nodes_ast2)
    return similarity

def compare_cpp_asts(ast1, ast2):
    num_nodes_ast1 = count_nodes_cpp(ast1)
    num_nodes_ast2 = count_nodes_cpp(ast2)
    similarity = min(num_nodes_ast1, num_nodes_ast2) / max(num_nodes_ast1, num_nodes_ast2)
    return similarity

def normalize_code(ast_tree):
    if isinstance(ast_tree, ast.AST):
        return ast.unparse(ast_tree)
    elif isinstance(ast_tree, javalang.ast.Node):
        return hierarchical_representation(ast_tree)
    elif isinstance(ast_tree, clang.cindex.Cursor):
        return hierarchical_representation_cpp(ast_tree)

def hierarchical_representation(node, depth=0):
    indent = '    ' * depth
    result = f"{indent}{node.__class__.__name__}"  
    
    if isinstance(node, (javalang.ast.Node, javalang.tree.CompilationUnit)):
        result += " {"
        for attr_name, attr_value in vars(node).items():
            if isinstance(attr_value, (list, javalang.ast.Node, javalang.tree.CompilationUnit)):
                result += f"\n{indent}    {attr_name}:"
                if isinstance(attr_value, list):
                    for i, child in enumerate(attr_value):
                        result += f"\n{indent}        [{i}] {hierarchical_representation(child, depth + 2)}"
                else:
                    result += f"\n{indent}        {hierarchical_representation(attr_value, depth + 2)}"
            else:
                result += f"\n{indent}    {attr_name}: {attr_value}"
        result += f"\n{indent}}}"
    elif isinstance(node, ast.AST): 
        result = f"{indent}{node.__class__.__name__.upper()}"  
        result += " {"
        for attr_name, attr_value in ast.iter_fields(node):
            result += f"\n{indent}    {attr_name}:"
            if isinstance(attr_value, list):
                for i, child in enumerate(attr_value):
                    result += f"\n{indent}        [{i}] {hierarchical_representation(child, depth + 2)}"
            else:
                result += f"\n{indent}        {hierarchical_representation(attr_value, depth + 2)}"
        result += f"\n{indent}}}"

    return result

def hierarchical_representation_cpp(cursor, depth=0):
    indent = '    ' * depth
    result = f"{indent}{cursor.kind.name}"

    if cursor.kind.is_declaration():
        result += f" ({cursor.displayname})"

    for child in cursor.get_children():
        result += f"\n{hierarchical_representation_cpp(child, depth + 1)}"

    return result

def count_nodes(ast_tree):
    count = 0
    for node in ast_tree:
        count += 1
        if isinstance(node, javalang.ast.Node):
            count += count_nodes(node.children)
    return count

def count_nodes_cpp(cursor):
    count = 1
    for child in cursor.get_children():
        count += count_nodes_cpp(child)
    return count

def calculate_similarity(code1, code2, language):
    ast1 = generate_ast(preprocess_code(code1), language)
    ast2 = generate_ast(preprocess_code(code2), language)
    if ast1 is None or ast2 is None:
        return "Invalid code"
    if language == "Python":
        similarity = compare_asts(ast1, ast2)
    elif language == "Java":
        similarity = compare_java_asts(ast1, ast2)
    elif language == "C/C++":
        similarity = compare_cpp_asts(ast1, ast2)
    return similarity

def similarity_formula(language):
    source_code = entry_1.get('1.0', tk.END)
    entry_5.delete(*entry_5.get_children())   
    entry_5["columns"] = ("File Name", "Plagiarism Percentage")
    entry_5.column("#0", width=0, stretch=tk.NO)
    entry_5.column("File Name", anchor=tk.CENTER, width=200)
    entry_5.column("Plagiarism Percentage", anchor=tk.CENTER, width=200)

    entry_5.heading("File Name", text="File Name")
    entry_5.heading("Plagiarism Percentage", text="Plagiarism Percentage")

    for index, file_path in enumerate(testing_files):
        with open(file_path, 'r', encoding='utf-8') as file:
            testing_code = file.read()
        similarity = calculate_similarity(source_code, testing_code, language)
        file_name = file_path.split('/')[-1]
        entry_5.insert("", tk.END, values=(file_name, f"{similarity*100:.2f}%"))

def open_file(entry_1, entry_3, language):
    file_types = []
    if language == "Python":
        file_types.append(("Python Files", "*.py"))
    elif language == "Java":
        file_types.append(("Java Files", "*.java"))
    elif language == "C/C++":
        file_types.append(("C/C++ Files", "*.c;*.cpp"))
    else:
        file_types = []
    file_path = filedialog.askopenfilename(title="Select File", filetypes=file_types)
    if not file_path:
        messagebox.showwarning("No file selected", "Please select a file.")
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        entry_1.delete('1.0', tk.END)
        entry_1.insert(tk.END, file.read())
    source_code = entry_1.get('1.0', tk.END)
    ast_tree = generate_ast(preprocess_code(source_code), language)
    if ast_tree:
        entry_3.delete('1.0', tk.END)
        if language == "Python":
            entry_3.insert(tk.END, ast.dump(ast_tree, indent=2))  
        elif language == "C/C++":
            entry_3.insert(tk.END, hierarchical_representation_cpp(ast_tree))  
        else:
            entry_3.insert(tk.END, hierarchical_representation(ast_tree))

def add_testing_files(language):
    file_types = []
    if language == "Python":
        file_types.append(("Python Files", "*.py"))
    elif language == "Java":
        file_types.append(("Java Files", "*.java"))
    elif language == "C/C++":
        file_types.append(("C/C++ Files", "*.c;*.cpp"))
    file_paths = filedialog.askopenfilenames(title="Select Testing Files", filetypes=file_types)
    testing_files.clear()
    entry_4.delete('1.0', tk.END)
    entry_2.delete('1.0', tk.END)
    for file_path in file_paths:
        testing_files.append(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            entry_4.tag_configure('file_name', foreground='green', font=('Helvetica', 10, 'bold'))
            entry_4.insert(tk.END, "------------------------------\n")
            entry_4.insert(tk.END, f"File Name: {file_path.split('/')[-1]}\n", 'file_name')
            entry_4.insert(tk.END, "------------------------------\n")
            code = file.read()
            entry_4.insert(tk.END, code)
            entry_4.insert(tk.END, "\n")
            ast_tree = generate_ast(preprocess_code(code), language)
            if ast_tree:
                entry_2.tag_configure('file_name', foreground='green', font=('Helvetica', 10, 'bold'))
                entry_2.insert(tk.END, "------------------------------\n")
                entry_2.insert(tk.END, f"File Name: {file_path.split('/')[-1]}\n", 'file_name')
                entry_2.insert(tk.END, "------------------------------\n")
                if language == "Python":
                    entry_2.insert(tk.END, ast.dump(ast_tree, indent=2))  
                elif language == "C/C++":
                    entry_2.insert(tk.END, hierarchical_representation_cpp(ast_tree))  
                else:
                    entry_2.insert(tk.END, hierarchical_representation(ast_tree))  
                entry_2.insert(tk.END, "\n\n")


def save_to_excel():
    data = []
    for item in entry_5.get_children():
        values = entry_5.item(item, 'values')
        data.append(values)
    if not data:
        messagebox.showwarning("No Data", "No data to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        df = pd.DataFrame(data, columns=["File Name", "Plagiarism Percentage"])
        df.to_excel(file_path, index=False)
        save_label.config(text="File Saved Successfully", fg="green")

def open_back_page(language,parent=None):
    global entry_1
    global entry_2
    global entry_3
    global entry_4
    global entry_5
    def open_file_wrapper():
        open_file(entry_1, entry_3, language)

    def add_testing_files_wrapper():
        add_testing_files(language)

    def similarity_formula_wrapper():
        similarity_formula(language)

    def save_to_excel_wrapper():
        save_to_excel()

    def back_to_front_page():
        window.destroy()
        if parent:
            parent.deiconify()

    def exit_program():
        window.destroy()

    if parent:
        window = tk.Toplevel(parent)
    else:
        window = tk.Tk()
   
    window.geometry("1300x700")
    window.configure(bg="#FFFFFF")
    window.title("SourcePlag")
    window.iconbitmap(resource_path(relative_to_assets("icon1.ico")))

    canvas = Canvas(
        window,
        bg="#FFFFFF",
        height=700,
        width=1300,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)

    image_image_1 = PhotoImage(
        file=relative_to_assets("img1.png"))
    canvas.create_image(
        650.0,
        350.0,
        image=image_image_1
    )

    image_image_2 = PhotoImage(
        file=relative_to_assets("img2.png"))
    canvas.create_image(
        650.0,
        33.0,
        image=image_image_2
    )

    image_image_3 = PhotoImage(
        file=relative_to_assets("img3.png"))
    canvas.create_image(
        100.00982666015625,
        132.0096435546875,
        image=image_image_3
    )

    image_image_4 = PhotoImage(
        file=relative_to_assets("img4.png"))
    canvas.create_image(
        131.0,
        595.0,
        image=image_image_4
    )

    entry_image_1 = PhotoImage(
        file=relative_to_assets("e1.png"))
    canvas.create_image(
        349.5,
        203.0,
        image=entry_image_1
    )
    entry_1 = Text(window,
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font
    )
    entry_1.place(
        x=228.0,
        y=86.0,
        width=245.0,
        height=232.0
    )

    entry_image_2 = PhotoImage(
        file=relative_to_assets("e2.png"))
    canvas.create_image(
        694.0,
        546.9999389648438,
        image=entry_image_2
    )
    entry_2 = Text(window,
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font
    )
    entry_2.place(
        x=572.0,
        y=430.0,
        width=245.0,
        height=232.0
    )

    entry_image_3 = PhotoImage(
        file=relative_to_assets("e3.png"))
    canvas.create_image(
        349.0,
        546.9999389648438,
        image=entry_image_3
    )
    entry_3 = Text(window,
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font
    )
    entry_3.place(
        x=227.0,
        y=430.0,
        width=245.0,
        height=232.0
    )

    entry_image_4 = PhotoImage(
        file=relative_to_assets("e4.png"))
    canvas.create_image(
        693.5,
        201.99993896484375,
        image=entry_image_4
    )
    entry_4 = Text(window,
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font
    )
    entry_4.place(
        x=572.0,
        y=86.0,
        width=245.0,
        height=232.0
    )

    image_image_5 = PhotoImage(
        file=relative_to_assets("img5.png"))
    canvas.create_image(
        349.0,
        412.0,
        image=image_image_5
    )

    image_image_6 = PhotoImage(
        file=relative_to_assets("img6.png"))
    canvas.create_image(
        693.0,
        412.0,
        image=image_image_6
    )

    entry_5 = ttk.Treeview(window, columns=("File Name", "Plagiarism Percentage"), show="headings")
    entry_5.heading("File Name", text="File Name")
    entry_5.heading("Plagiarism Percentage", text="Plagiarism Percentage")
    entry_5.place(x=899.1290283203125, y=109.0, width=367.74176025390625, height=286.9287109375)


    button_image_1 = PhotoImage(
        file=relative_to_assets("b1.png"))
    button_1 = Button(window,
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=exit_program,
        relief="flat"
    )
    button_1.place(
        x=1033.0,
        y=629.0,
        width=99.6661376953125,
        height=51.0
    )

    button_image_2 = PhotoImage(
        file=relative_to_assets("b2.png"))
    button_2 = Button(window,
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda:save_to_excel_wrapper(),
        relief="flat"
    )
    button_2.place(
        x=974.0,
        y=491.0,
        width=215.25296020507812,
        height=51.0
    )

    button_image_3 = PhotoImage(
        file=relative_to_assets("b3.png"))
    button_3 = Button(window,
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: open_file_wrapper(),
        relief="flat"
    )
    button_3.place(
        x=249.0,
        y=341.0,
        width=200.99999344348544,
        height=33.000000119208835
    )

    button_image_4 = PhotoImage(
        file=relative_to_assets("b4.png"))
    button_4 = Button(window,
        image=button_image_4,
        borderwidth=0,
        highlightthickness=0,
        command=lambda:add_testing_files_wrapper(),
        relief="flat"
    )
    button_4.place(
        x=594.0,
        y=341.0,
        width=200.99999344348544,
        height=33.000000119208835
    )

    button_image_5 = PhotoImage(file=relative_to_assets("b5.png"))
    button_5 = Button(window,
        image=button_image_5,
        borderwidth=0,
        highlightthickness=0,
        command=lambda:similarity_formula_wrapper(),
        relief="flat"
    )
    button_5.place(
        x=991.0,
        y=422.0,
        width=184.241943359375,
        height=51.0
    )

    button_image_6 = PhotoImage(
        file=relative_to_assets("b6.png"))
    button_6 = Button(window,
        image=button_image_6,
        borderwidth=0,
        highlightthickness=0,
        command=lambda:back_to_front_page(),
        relief="flat"
    )
    button_6.place(
        x=1033.0,
        y=560.0,
        width=99.6661376953125,
        height=51.0
    )
   
    scrollbar_1 = ttk.Scrollbar(window, orient="vertical", command=entry_1.yview)
    scrollbar_1.place(x=486, y=86, height=232)
    entry_1.config(yscrollcommand=scrollbar_1.set)

    scrollbar_2 = ttk.Scrollbar(window, orient="vertical", command=entry_2.yview)
    scrollbar_2.place(x=831, y=430, height=232)
    entry_2.config(yscrollcommand=scrollbar_2.set)

    scrollbar_3 = ttk.Scrollbar(window, orient="vertical", command=entry_3.yview)
    scrollbar_3.place(x=486, y=430, height=232)
    entry_3.config(yscrollcommand=scrollbar_3.set)

    scrollbar_4 = ttk.Scrollbar(window, orient="vertical", command=entry_4.yview)
    scrollbar_4.place(x=830, y=86, height=232)
    entry_4.config(yscrollcommand=scrollbar_4.set)

    scrollbar_5 = ttk.Scrollbar(window, orient="vertical", command=entry_5.yview)
    scrollbar_5.place(x=1270, y=109, height=286)
    entry_5.config(yscrollcommand=scrollbar_5.set)

    global save_label
    save_label = tk.Label(window, text="", fg="green")
    save_label.place(x=1030, y=70) 

    window.resizable(False, False)
    window.mainloop()

def open_front_page():
    root = Tk()
    root.title("SourcePlag")
    root.geometry("1300x700")
    root.iconbitmap(resource_path(relative_to_assets("icon1.ico")))
    root.resizable(False, False)

    canvas = Canvas(root, bg="#FFFFFF", height=700, width=1300, bd=0, highlightthickness=0, relief="ridge")
    canvas.place(x=0, y=0)

    image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
    image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
    image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
    image_5 = PhotoImage(file=relative_to_assets("image_5.png"))

    canvas.create_image(474.0, 80.0, image=image_1)
    canvas.create_image(1240.0, 495.0, image=image_2)
    canvas.create_image(504.0, 247.0, image=image_3)
    canvas.create_image(134.0, 587.0, image=image_5)

    def option1_action():
        root.withdraw() 
        open_back_page("Java", root)

    def option2_action():
        root.withdraw() 
        open_back_page("C/C++", root)

    def option3_action():
        root.withdraw()  
        open_back_page("Python", root)

    def exit_program():
        root.destroy()

    button_1_image = PhotoImage(file=relative_to_assets("button_1.png"))
    button_1 = Button(
        root,
        image=button_1_image,
        borderwidth=0,
        highlightthickness=0,
        command=option1_action,
        relief="flat"
    )
    button_1.place(x=433.77435302734375, y=358.0, width=154.22564697265625, height=180.0)

    button_2_image = PhotoImage(file=relative_to_assets("button_2.png"))
    button_2 = Button(
        root,
        image=button_2_image,
        borderwidth=0,
        highlightthickness=0,
        command=option2_action,
        relief="flat"
    )
    button_2.place(x=631.0, y=462.0, width=154.0, height=180.0)

    button_3_image = PhotoImage(file=relative_to_assets("button_3.png"))
    button_3 = Button(
        root,
        image=button_3_image,
        borderwidth=0,
        highlightthickness=0,
        command=option3_action,
        relief="flat"
    )
    button_3.place(x=245.0, y=463.0, width=154.0, height=180.0)

    exit_button_image = PhotoImage(file=relative_to_assets("button_4.png"))
    exit_button = Button(
        root,
        image=exit_button_image,
        borderwidth=0,
        highlightthickness=0,
        command=exit_program,
        relief="flat"
    )
    exit_button.place(x=450, y=629)

    root.mainloop()

if __name__ == "__main__":
    open_front_page()
