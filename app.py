
import streamlit as st

st.set_page_config(
    page_title="PropDoc AI",
    page_icon="📄",
    layout="wide"
)

st.title("PropDoc AI")
st.subheader("AI-Powered Smart Property Document Analyzer")

st.write(
    "Upload your property documents "
    "and analyze them intelligently."
)

st.divider()

st.header("Upload Property Document")

uploaded_file = st.file_uploader(
    "Choose your property document",
    type=["pdf", "docx", "txt"]
)

if uploaded_file is not None:
    st.success("Document uploaded successfully!")
    st.write("File name:", uploaded_file.name)
    st.write("File size:", uploaded_file.size, "bytes")

    st.info(
        "Your document is ready for analysis."
    )

st.divider()

st.caption("PropDoc AI | Smart Document Analysis")
