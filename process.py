import os
import subprocess
import re
from docx import Document

def extract_latex_blocks(content):
    """Trích xuất các khối TikZ và tabular."""
    print("Nội dung đầu vào:", content)  # Debug: Kiểm tra nội dung đầu vào

    def find_nested_blocks(content, start_tag, end_tag, block_type):
        stack = []
        blocks = []
        start_pos = 0

        for i, char in enumerate(content):
            # Tìm \begin{...}
            if content[i:i+len(start_tag)] == start_tag:
                if not stack:
                    start_pos = i
                stack.append(start_tag)
            # Tìm \end{...}
            elif content[i:i+len(end_tag)] == end_tag:
                if stack:
                    stack.pop()
                    if not stack:
                        blocks.append((content[start_pos:i+len(end_tag)], start_pos, i+len(end_tag), block_type))
        return blocks

    tikz_blocks = find_nested_blocks(content, r'\begin{tikzpicture}', r'\end{tikzpicture}', "tikz")
    tabular_blocks = find_nested_blocks(content, r'\begin{tabular}', r'\end{tabular}', "tabular")

    print("TikZ blocks:", tikz_blocks)  # Debug: In ra các khối TikZ
    print("Tabular blocks:", tabular_blocks)  # Debug: In ra các khối Tabular

    return sorted(tikz_blocks + tabular_blocks, key=lambda x: x[1])


def latex_to_image(latex_code, output_file, block_type):
    """Chuyển LaTeX thành ảnh PNG."""
    if block_type == "tikz":
        template = r"""\documentclass[tikz,border=5mm]{standalone}
\usepackage[utf8]{vietnam}
\usepackage{tikz,tkz-euclide,tkz-tab,enumerate}
\usetikzlibrary{shapes,calc,intersections,angles,patterns,quotes}
\usetkzobj{all}
\begin{document}
%s
\end{document}"""
    else:
        template = r"""\documentclass[preview,border=1pt]{standalone}
\usepackage[utf8]{vietnam}
\begin{document}
%s
\end{document}"""

    tex_file = "temp.tex"
    try:
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(template % latex_code)

        result = subprocess.run(["pdflatex", tex_file], capture_output=True, text=True)
        if result.returncode != 0:
            return None

        pdf_file = tex_file.replace(".tex", ".pdf")
        if not os.path.exists(pdf_file):
            return None

        output_base = output_file.rsplit('.', 1)[0]
        result = subprocess.run(["pdftocairo", "-png", "-r", "300", "-singlefile", pdf_file, output_base], capture_output=True, text=True)
        if result.returncode != 0:
            return None

    finally:
        for ext in [".tex", ".aux", ".log", ".pdf"]:
            file_to_remove = tex_file.replace(".tex", ext)
            # if os.path.exists(file_to_remove):  # Kiểm tra file tồn tại
            #     os.remove(file_to_remove)

    return output_file

def process_latex_blocks(content, num_blocks):
    """Xử lý các khối LaTeX và trả về danh sách đường dẫn ảnh."""
    latex_blocks = extract_latex_blocks(content)
    if not latex_blocks:
        return []

    images = []
    for i, (latex_code, _, _, block_type) in enumerate(latex_blocks[:num_blocks]):
        output_file = f"output_{i+1}.png"
        image_path = latex_to_image(latex_code, output_file, block_type)
        images.append((image_path, block_type))

    return images
