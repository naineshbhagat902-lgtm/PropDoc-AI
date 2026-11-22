
import streamlit as st
import fitz
import pytesseract
import io

from PIL import Image

# -------------------------------
# 1. PAGE SETTINGS
# -------------------------------

st.set_page_config(
    page_title="PropDoc AI",
    page_icon="📄",
    layout="wide"
)

# -------------------------------
# 2. WEBSITE HEADER
# -------------------------------

st.title("📄 PropDoc AI")
st.subheader("Smart Property Document Analyzer")

st.write(
    "Upload your property documents and "
    "extract text in Marathi, Hindi, and English."
)

st.divider()

# -------------------------------
# 3. UPLOAD PDF
# -------------------------------

uploaded_file = st.file_uploader(
    "Upload your property document",
    type=["pdf"]
)

# -------------------------------
# 4. OCR SETTINGS
# -------------------------------

use_ocr = st.checkbox(
    "Use OCR for scanned or unclear PDFs",
    value=True
)

language = st.selectbox(
    "Select document languages",
    [
        "Marathi + English + Hindi",
        "Marathi + English",
        "Hindi + English"
    ]
)

language_codes = {
    "Marathi + English + Hindi": "mar+eng+hin",
    "Marathi + English": "mar+eng",
    "Hindi + English": "hin+eng"
}

# -------------------------------
# 5. PROCESS DOCUMENT
# -------------------------------

if uploaded_file is not None:

    st.success("PDF uploaded successfully!")

    pdf_bytes = uploaded_file.getvalue()

    if st.button("Extract Document Text"):

        try:
            pdf_document = fitz.open(
                stream=pdf_bytes,
                filetype="pdf"
            )

            extracted_text = ""

            progress = st.progress(0)

            with st.spinner("Reading your document..."):

                total_pages = len(pdf_document)

                for page_number, page in enumerate(pdf_document):

                    if use_ocr:

                        # Convert PDF page into an image
                        pix = page.get_pixmap(
                            matrix=fitz.Matrix(2, 2),
                            alpha=False
                        )

                        image = Image.open(
                            io.BytesIO(pix.tobytes("png"))
                        )

                        # Recognize Marathi, Hindi and English
                        page_text = pytesseract.image_to_string(
                            image,
                            lang=language_codes[language]
                        )

                    else:

                        # Extract existing PDF text
                        page_text = page.get_text()

                    extracted_text += (
                        f"\n\n--- Page {page_number + 1} ---\n\n"
                        + page_text
                    )

                    progress.progress(
                        (page_number + 1) / total_pages
                    )

            pdf_document.close()

            # -------------------------------
            # 6. DISPLAY EXTRACTED TEXT
            # -------------------------------

            st.success("Text extraction completed!")

            if extracted_text.strip():

                st.subheader("Extracted Document Text")

                st.text_area(
                    "Recognized text",
                    extracted_text,
                    height=450
                )

                st.download_button(
                    "Download Extracted Text",
                    data=extracted_text,
                    file_name="propdoc_extracted_text.txt",
                    mime="text/plain"
                )

            else:

                st.warning(
                    "No readable text found. "
                    "Try a clearer PDF or another language setting."
                )

        except Exception as error:

            st.error("Something went wrong while processing the PDF.")

            st.exception(error)

st.divider()

st.caption("PropDoc AI | Smart Property Document Analyzer")
