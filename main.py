import streamlit as st
from pylatex import Document
from pathlib import Path
from pdf2image import convert_from_path
import tempfile

# Hàm biên dịch LaTeX thành PDF
def compile_latex_to_pdf(latex_code):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = Path(temp_dir) / "document.tex"
            pdf_file = Path(temp_dir) / "document.pdf"

            # Ghi mã LaTeX vào file
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_code)

            # Sử dụng lệnh pdflatex để biên dịch
            import subprocess
            result = subprocess.run([
                "pdflatex",
                "-interaction=nonstopmode",
                f"-output-directory={temp_dir}",
                tex_file
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0 and pdf_file.exists():
                return pdf_file.read_bytes()
            else:
                error_message = result.stderr.decode("utf-8")
                return None, error_message
    except Exception as e:
        return None, str(e)

# Giao diện Streamlit
st.title("LaTeX to PDF Compiler")

# Khu vực nhập mã LaTeX
latex_code = st.text_area("Enter your LaTeX code below:",
                          """
                          \documentclass{article}
                          \begin{document}
                          Hello, LaTeX World!
                          \end{document}
                          """)

# Nút biên dịch
if st.button("Compile LaTeX"):
    with st.spinner("Compiling..."):
        pdf_bytes, error_message = compile_latex_to_pdf(latex_code)

    if pdf_bytes:
        st.success("Compilation successful!")

        # Hiển thị PDF
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="output.pdf",
            mime="application/pdf"
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf_path = tmp_pdf.name

        images = convert_from_path(tmp_pdf_path)
        for img in images:
            st.image(img, use_column_width=True)
    else:
        st.error(f"Compilation failed: {error_message}")
