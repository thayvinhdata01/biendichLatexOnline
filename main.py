# File giao diện (interface.py)
import streamlit as st
from process import extract_latex_blocks, process_latex_blocks

st.title("LaTeX Block Extractor")

st.write("Tải lên file LaTeX hoặc nhập nội dung LaTeX để trích xuất các khối \texttt{tikzpicture} và \texttt{tabular}.")

uploaded_file = st.file_uploader("Tải lên file .tex", type=["tex"])
input_content = st.text_area("Hoặc nhập nội dung LaTeX tại đây:")

content = ""
if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
elif input_content:
    content = input_content

latex_blocks = extract_latex_blocks(content)
block_count = len(latex_blocks)
st.write(f"Tìm thấy {block_count} khối LaTeX.")

num_blocks = st.selectbox("Chọn số lượng khối muốn xử lý:", range(1, block_count + 1) if block_count > 0 else [0])
if st.button("Tạo ảnh"):
    if block_count > 0:
        images = process_latex_blocks(content, num_blocks)
        for i, (image_path, block_type) in enumerate(images):
            if image_path:
                st.image(image_path, caption=f"Block {i+1}: {block_type}")
            else:
                st.error(f"Không thể chuyển đổi block {i+1}.")
    else:
        st.warning("Không có khối LaTeX nào để xử lý.")