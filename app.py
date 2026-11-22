
import streamlit as st
import fitz

# Page configuration
st.set_page_config(
    page_title="PropDoc AI",
    page_icon="📄",
    layout="wide"
)

# Main heading
st.title("PropDoc AI")
st.subheader("AI-Powered Smart Property Document Analyzer")

st.write(
    "Upload your property documents and analyze them intelligently."
)

# Document upload
uploaded_file = st.file_uploader(
    "Upload your Property Document",
    type=["pdf"]
)

# Read PDF document
if uploaded_file is not None:

    st.success("Document uploaded successfully!")

    st.write("File name:", uploaded_file.name)

    # Open PDF
    pdf_document = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    # Extract text
    extracted_text = ""

    for page in pdf_document:
        extracted_text += page.get_text()

    # Display extracted text
    st.subheader("Extracted Document Text")

    if extracted_text.strip():
        st.text_area(
            "PDF Content",
            extracted_text,
            height=400
        )
    else:
        st.warning(
            "No selectable text found. This PDF may need OCR."
        )

# Footer
st.divider()
st.caption("PropDoc AI | Smart Document Analysis")
