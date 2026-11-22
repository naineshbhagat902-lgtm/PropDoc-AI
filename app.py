import io
import time
import streamlit as st
import fitz
import pytesseract
from PIL import Image
from google import genai
from google.genai import types


# -------------------------------------------------
# 1. PAGE SETTINGS
# -------------------------------------------------
st.set_page_config(
    page_title="PropDoc AI",
    page_icon="📄",
    layout="wide",
)

st.title("📄 PropDoc AI")
st.subheader("Smart Property Document Analyzer")
st.write(
    "Upload property documents, extract Marathi/Hindi/English text, "
    "and use AI to understand the document."
)
st.info(
    "PropDoc AI provides document-reading assistance, not legal advice. "
    "Always verify ownership, area, compensation, and legal conclusions "
    "with the relevant government records and a qualified property lawyer."
)
st.divider()


# -------------------------------------------------
# 2. SESSION STATE
# -------------------------------------------------
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "document_name" not in st.session_state:
    st.session_state.document_name = ""
if "ai_analysis" not in st.session_state:
    st.session_state.ai_analysis = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -------------------------------------------------
# 3. GEMINI CONFIGURATION
# -------------------------------------------------
MODEL_NAME = "gemini-3.8-flash"
FALLBACK_MODEL_NAME = "gemini-3.5-flash-lite"
MAX_DOCUMENT_CHARACTERS = 60000


def get_gemini_client():
    """Create a Gemini client using the Streamlit secret."""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError(
            "Gemini API key is missing. Add GEMINI_API_KEY in "
            "Streamlit Cloud → App settings → Secrets."
        )
    return genai.Client(api_key=api_key)


def ask_gemini(prompt: str) -> str:
    """Call Gemini, retry temporary 503 errors, then try a backup model."""
    client = get_gemini_client()
    models_to_try = [MODEL_NAME, FALLBACK_MODEL_NAME]
    last_error = None

    try:
        for model_name in models_to_try:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            max_output_tokens=5000,
                        ),
                    )

                    answer = (response.text or "").strip()
                    if not answer:
                        raise RuntimeError(
                            f"{model_name} returned an empty response."
                        )
                    return answer

                except Exception as error:
                    last_error = error
                    error_text = str(error).upper()
                    error_code = (
                        getattr(error, "code", None)
                        or getattr(error, "status_code", None)
                    )
                    is_unavailable = (
                        error_code == 503
                        or "503" in error_text
                        or "UNAVAILABLE" in error_text
                    )

                    # Retry only temporary server-capacity errors.
                    if not is_unavailable:
                        raise

                    if attempt == 0:
                        time.sleep(2)

            # The primary model failed twice with 503; try the backup.
            continue

        raise RuntimeError(
            "Gemini is temporarily busy. Both the primary and backup "
            "models returned a 503 error. Please wait a minute and try again. "
            f"Last error: {last_error}"
        )

    finally:
        client.close()


def get_document_context() -> str:
    """Return the extracted document text, with a safe size limit."""
    text = st.session_state.extracted_text.strip()
    if not text:
        raise ValueError("Please extract the PDF text first.")
    return text[:MAX_DOCUMENT_CHARACTERS]


# -------------------------------------------------
# 4. PDF UPLOAD
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload your property document",
    type=["pdf"],
)

st.subheader("OCR settings")
use_ocr = st.checkbox(
    "Use OCR for scanned or unclear PDFs",
    value=True,
)
language = st.selectbox(
    "Select document languages",
    [
        "Marathi + English + Hindi",
        "Marathi + English",
        "Hindi + English",
    ],
)

language_codes = {
    "Marathi + English + Hindi": "mar+eng+hin",
    "Marathi + English": "mar+eng",
    "Hindi + English": "hin+eng",
}


# -------------------------------------------------
# 5. EXTRACT PDF TEXT
# -------------------------------------------------
if uploaded_file is not None:
    st.success(f"PDF uploaded: {uploaded_file.name}")
    pdf_bytes = uploaded_file.getvalue()

    if st.button("Extract Document Text", type="primary"):
        try:
            pdf_document = fitz.open(
                stream=pdf_bytes,
                filetype="pdf",
            )
            extracted_text = ""
            total_pages = len(pdf_document)

            if total_pages == 0:
                raise ValueError("The uploaded PDF has no pages.")

            progress = st.progress(0)

            with st.spinner("Reading your document..."):
                for page_number, page in enumerate(pdf_document):
                    if use_ocr:
                        pix = page.get_pixmap(
                            matrix=fitz.Matrix(2, 2),
                            alpha=False,
                        )
                        image = Image.open(
                            io.BytesIO(pix.tobytes("png"))
                        )
                        page_text = pytesseract.image_to_string(
                            image,
                            lang=language_codes[language],
                        )
                    else:
                        page_text = page.get_text()

                    extracted_text += (
                        f"\n\n--- Page {page_number + 1} ---\n\n"
                        + page_text
                    )
                    progress.progress((page_number + 1) / total_pages)

            pdf_document.close()

            st.session_state.extracted_text = extracted_text
            st.session_state.document_name = uploaded_file.name
            st.session_state.ai_analysis = ""
            st.session_state.chat_history = []

            if extracted_text.strip():
                st.success("Text extraction completed!")
            else:
                st.warning(
                    "No readable text found. Try a clearer PDF, "
                    "check the OCR language selection, or install "
                    "the required Tesseract language data."
                )

        except Exception as error:
            st.error("Something went wrong while processing the PDF.")
            st.exception(error)


# -------------------------------------------------
# 6. DISPLAY AND DOWNLOAD EXTRACTED TEXT
# -------------------------------------------------
if st.session_state.extracted_text:
    st.divider()
    st.subheader("📃 Extracted Document Text")
    st.caption(f"Document: {st.session_state.document_name}")

    st.text_area(
        "Recognized text",
        st.session_state.extracted_text,
        height=350,
    )

    st.download_button(
        "Download Extracted Text",
        data=st.session_state.extracted_text,
        file_name="propdoc_extracted_text.txt",
        mime="text/plain",
    )

    if len(st.session_state.extracted_text) > MAX_DOCUMENT_CHARACTERS:
        st.warning(
            f"The extracted text is longer than {MAX_DOCUMENT_CHARACTERS:,} "
            "characters. AI requests in this version use only the first "
            f"{MAX_DOCUMENT_CHARACTERS:,} characters. Check the original PDF "
            "for information beyond that point."
        )


# -------------------------------------------------
# 7. AI DOCUMENT ANALYSIS
# -------------------------------------------------
if st.session_state.extracted_text.strip():
    st.divider()
    st.header("🤖 AI Property Document Analysis")
    st.write(
        "Gemini will summarize the extracted text, identify details that "
        "are explicitly present, and flag items that may need manual review."
    )

    response_language = st.selectbox(
        "AI response language",
        ["English", "Marathi", "Hindi"],
        key="response_language",
    )

    if st.button("✨ Analyze My Property Document", type="primary"):
        try:
            document_text = get_document_context()
            analysis_prompt = f"""
You are PropDoc AI, a careful assistant that explains property documents.
Analyze only the document text provided below. Do not invent facts or fill
missing fields using assumptions.

Write the response in {response_language}.

Use these sections:
1. Simple document summary
2. Property and land details explicitly found
3. Names of owners / parties explicitly found
4. Survey number, Gat number, area, village, taluka and district, if present
5. Important dates, order numbers and reference numbers, if present
6. Compensation or payment details, only if explicitly stated
7. Clauses, inconsistencies, missing information, or unclear text that deserve
   human verification
8. Questions the user should ask the relevant government office or lawyer

For every important extracted fact, quote a short supporting phrase from the
provided text or identify its page number when possible. If a field is absent
or unreadable, write "Not found in extracted text". Distinguish facts from
possible concerns. Do not declare a title valid/invalid, determine legal
ownership, calculate an individual's entitlement without complete ownership
shares and official figures, or give a definitive legal opinion.

DOCUMENT TEXT:
{document_text}
"""
            with st.spinner("Gemini is analyzing your document..."):
                result = ask_gemini(analysis_prompt)

            st.session_state.ai_analysis = result
            st.success("AI analysis completed!")

        except Exception as error:
            st.error(f"AI analysis could not be completed: {error}")

    if st.session_state.ai_analysis:
        st.markdown(st.session_state.ai_analysis)
        st.download_button(
            "Download AI Analysis",
            data=st.session_state.ai_analysis,
            file_name="propdoc_ai_analysis.txt",
            mime="text/plain",
        )


# -------------------------------------------------
# 8. ASK QUESTIONS ABOUT THE DOCUMENT
# -------------------------------------------------
if st.session_state.extracted_text.strip():
    st.divider()
    st.header("💬 Ask Questions About Your Document")
    st.caption(
        "Ask one question at a time. Answers are based on the extracted text, "
        "which may contain OCR mistakes."
    )

    with st.form("document_question_form", clear_on_submit=True):
        user_question = st.text_input(
            "Your question",
            placeholder="Example: What survey number is mentioned?",
        )
        submitted = st.form_submit_button("Ask PropDoc AI")

    if submitted:
        if not user_question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                document_text = get_document_context()
                question_prompt = f"""
You are PropDoc AI, an assistant that answers questions about a property
document. Answer in {response_language if 'response_language' in st.session_state else 'English'}.

Use only the document text below. Do not guess or invent information.
If the answer is not present or the OCR text is unclear, say so clearly.
When possible, mention the page number or quote a short supporting phrase.
Explain calculations transparently and do not calculate a person's legal
entitlement unless all necessary official figures and ownership shares are
provided. Do not present your answer as legal advice.

DOCUMENT TEXT:
{document_text}

USER QUESTION:
{user_question}
"""
                with st.spinner("Finding the answer in your document..."):
                    answer = ask_gemini(question_prompt)

                st.session_state.chat_history.append(
                    {"question": user_question, "answer": answer}
                )

            except Exception as error:
                st.error(f"Your question could not be answered: {error}")

    for item in reversed(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(item["question"])
        with st.chat_message("assistant"):
            st.markdown(item["answer"])


# -------------------------------------------------
# 9. FOOTER
# -------------------------------------------------
st.divider()
st.caption(
    "PropDoc AI | Smart Property Document Analyzer | "
    "AI output must be checked against original records."
)
    response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=5000,
            ),
        )
        answer = response.text
        if not answer:
            raise RuntimeError("Gemini returned an empty response.")
        return answer
    finally:
        client.close()


def get_document_context() -> str:
    """Return the extracted document text, with a safe size limit."""
    text = st.session_state.extracted_text.strip()
    if not text:
        raise ValueError("Please extract the PDF text first.")
    return text[:MAX_DOCUMENT_CHARACTERS]


# -------------------------------------------------
# 4. PDF UPLOAD
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload your property document",
    type=["pdf"],
)

st.subheader("OCR settings")
use_ocr = st.checkbox(
    "Use OCR for scanned or unclear PDFs",
    value=True,
)
language = st.selectbox(
    "Select document languages",
    [
        "Marathi + English + Hindi",
        "Marathi + English",
        "Hindi + English",
    ],
)

language_codes = {
    "Marathi + English + Hindi": "mar+eng+hin",
    "Marathi + English": "mar+eng",
    "Hindi + English": "hin+eng",
}


# -------------------------------------------------
# 5. EXTRACT PDF TEXT
# -------------------------------------------------
if uploaded_file is not None:
    st.success(f"PDF uploaded: {uploaded_file.name}")
    pdf_bytes = uploaded_file.getvalue()

    if st.button("Extract Document Text", type="primary"):
        try:
            pdf_document = fitz.open(
                stream=pdf_bytes,
                filetype="pdf",
            )
            extracted_text = ""
            total_pages = len(pdf_document)

            if total_pages == 0:
                raise ValueError("The uploaded PDF has no pages.")

            progress = st.progress(0)

            with st.spinner("Reading your document..."):
                for page_number, page in enumerate(pdf_document):
                    if use_ocr:
                        pix = page.get_pixmap(
                            matrix=fitz.Matrix(2, 2),
                            alpha=False,
                        )
                        image = Image.open(
                            io.BytesIO(pix.tobytes("png"))
                        )
                        page_text = pytesseract.image_to_string(
                            image,
                            lang=language_codes[language],
                        )
                    else:
                        page_text = page.get_text()

                    extracted_text += (
                        f"\n\n--- Page {page_number + 1} ---\n\n"
                        + page_text
                    )
                    progress.progress((page_number + 1) / total_pages)

            pdf_document.close()

            st.session_state.extracted_text = extracted_text
            st.session_state.document_name = uploaded_file.name
            st.session_state.ai_analysis = ""
            st.session_state.chat_history = []

            if extracted_text.strip():
                st.success("Text extraction completed!")
            else:
                st.warning(
                    "No readable text found. Try a clearer PDF, "
                    "check the OCR language selection, or install "
                    "the required Tesseract language data."
                )

        except Exception as error:
            st.error("Something went wrong while processing the PDF.")
            st.exception(error)


# -------------------------------------------------
# 6. DISPLAY AND DOWNLOAD EXTRACTED TEXT
# -------------------------------------------------
if st.session_state.extracted_text:
    st.divider()
    st.subheader("📃 Extracted Document Text")
    st.caption(f"Document: {st.session_state.document_name}")

    st.text_area(
        "Recognized text",
        st.session_state.extracted_text,
        height=350,
    )

    st.download_button(
        "Download Extracted Text",
        data=st.session_state.extracted_text,
        file_name="propdoc_extracted_text.txt",
        mime="text/plain",
    )

    if len(st.session_state.extracted_text) > MAX_DOCUMENT_CHARACTERS:
        st.warning(
            f"The extracted text is longer than {MAX_DOCUMENT_CHARACTERS:,} "
            "characters. AI requests in this version use only the first "
            f"{MAX_DOCUMENT_CHARACTERS:,} characters. Check the original PDF "
            "for information beyond that point."
        )


# -------------------------------------------------
# 7. AI DOCUMENT ANALYSIS
# -------------------------------------------------
if st.session_state.extracted_text.strip():
    st.divider()
    st.header("🤖 AI Property Document Analysis")
    st.write(
        "Gemini will summarize the extracted text, identify details that "
        "are explicitly present, and flag items that may need manual review."
    )

    response_language = st.selectbox(
        "AI response language",
        ["English", "Marathi", "Hindi"],
        key="response_language",
    )

    if st.button("✨ Analyze My Property Document", type="primary"):
        try:
            document_text = get_document_context()
            analysis_prompt = f"""
You are PropDoc AI, a careful assistant that explains property documents.
Analyze only the document text provided below. Do not invent facts or fill
missing fields using assumptions.

Write the response in {response_language}.

Use these sections:
1. Simple document summary
2. Property and land details explicitly found
3. Names of owners / parties explicitly found
4. Survey number, Gat number, area, village, taluka and district, if present
5. Important dates, order numbers and reference numbers, if present
6. Compensation or payment details, only if explicitly stated
7. Clauses, inconsistencies, missing information, or unclear text that deserve
   human verification
8. Questions the user should ask the relevant government office or lawyer

For every important extracted fact, quote a short supporting phrase from the
provided text or identify its page number when possible. If a field is absent
or unreadable, write "Not found in extracted text". Distinguish facts from
possible concerns. Do not declare a title valid/invalid, determine legal
ownership, calculate an individual's entitlement without complete ownership
shares and official figures, or give a definitive legal opinion.

DOCUMENT TEXT:
{document_text}
"""
            with st.spinner("Gemini is analyzing your document..."):
                result = ask_gemini(analysis_prompt)

            st.session_state.ai_analysis = result
            st.success("AI analysis completed!")

        except Exception as error:
            st.error("AI analysis could not be completed.")
            st.exception(error)

    if st.session_state.ai_analysis:
        st.markdown(st.session_state.ai_analysis)
        st.download_button(
            "Download AI Analysis",
            data=st.session_state.ai_analysis,
            file_name="propdoc_ai_analysis.txt",
            mime="text/plain",
        )


# -------------------------------------------------
# 8. ASK QUESTIONS ABOUT THE DOCUMENT
# -------------------------------------------------
if st.session_state.extracted_text.strip():
    st.divider()
    st.header("💬 Ask Questions About Your Document")
    st.caption(
        "Ask one question at a time. Answers are based on the extracted text, "
        "which may contain OCR mistakes."
    )

    with st.form("document_question_form", clear_on_submit=True):
        user_question = st.text_input(
            "Your question",
            placeholder="Example: What survey number is mentioned?",
        )
        submitted = st.form_submit_button("Ask PropDoc AI")

    if submitted:
        if not user_question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                document_text = get_document_context()
                question_prompt = f"""
You are PropDoc AI, an assistant that answers questions about a property
document. Answer in {response_language if 'response_language' in st.session_state else 'English'}.

Use only the document text below. Do not guess or invent information.
If the answer is not present or the OCR text is unclear, say so clearly.
When possible, mention the page number or quote a short supporting phrase.
Explain calculations transparently and do not calculate a person's legal
entitlement unless all necessary official figures and ownership shares are
provided. Do not present your answer as legal advice.

DOCUMENT TEXT:
{document_text}

USER QUESTION:
{user_question}
"""
                with st.spinner("Finding the answer in your document..."):
                    answer = ask_gemini(question_prompt)

                st.session_state.chat_history.append(
                    {"question": user_question, "answer": answer}
                )

            except Exception as error:
                st.error("Your question could not be answered.")
                st.exception(error)

    for item in reversed(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(item["question"])
        with st.chat_message("assistant"):
            st.markdown(item["answer"])


# -------------------------------------------------
# 9. FOOTER
# -------------------------------------------------
st.divider()
st.caption(
    "PropDoc AI | Smart Property Document Analyzer | "
    "AI output must be checked against original records."
)
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
