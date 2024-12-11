import streamlit as st
from pylatex import Document
from pathlib import Path
import tempfile
import os
import base64

# Hàm biên dịch LaTeX thành PDF
def compile_latex_to_pdf(latex_code):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = Path(temp_dir) / "document.tex"
            pdf_file = Path(temp_dir) / "document.pdf"

            # Ghi mã LaTeX vào file
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_code)

            # Gọi pdflatex
            import subprocess
            env = {**os.environ, "TEXINPUTS": f"{Path(__file__).parent / 'latex_packages'}:"}
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", f"-output-directory={temp_dir}", tex_file],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
            )

            if result.returncode == 0 and pdf_file.exists():
                return pdf_file.read_bytes(), None
            else:
                error_message = result.stderr.decode("utf-8")
                return None, error_message
    except Exception as e:
        return None, str(e)

# Hàm tạo URL base64 cho PDF
def pdf_to_base64_url(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    return f"data:application/pdf;base64,{base64_pdf}"

# Giao diện Streamlit
st.title("LaTeX to PDF Compiler")

# Khu vực nhập mã LaTeX
latex_code = st.text_area("Enter your LaTeX code below:",
                          r"""
                          \documentclass{article}
                          \usepackage{amsmath}
                          \usepackage{amssymb}
                          \usepackage[utf8]{vietnam}
                          \usepackage[loigiai]{ex_test}
                          \begin{document}
                          \begin{ex} xin chào
                          \loigiai{
                            Nội dung lời giải
                          }
                          \end{ex}
                          Hello, LaTeX World!
                          \end{document}
                          """)

# Nút biên dịch
if st.button("Compile LaTeX"):
    with st.spinner("Compiling..."):
        pdf_bytes, error_message = compile_latex_to_pdf(latex_code)

    if pdf_bytes:
        st.success("Compilation successful!")

        # Hiển thị nút tải xuống
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="output.pdf",
            mime="application/pdf"
        )

        # Nhúng PDF trực tiếp bằng iframe
        pdf_url = pdf_to_base64_url(pdf_bytes)
        pdf_html = f'<iframe src="{pdf_url}" width="100%" height="800px" type="application/pdf"></iframe>'
        st.markdown(pdf_html, unsafe_allow_html=True)

    else:
        st.error(f"Compilation failed: {error_message}")
