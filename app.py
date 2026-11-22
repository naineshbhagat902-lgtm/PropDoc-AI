import io
import streamlit as st
import fitz
import pytesseract
from PIL import Image
from openai import OpenAI


# -------------------------------------------------
# 1. PAGE SETTINGS
# -------------------------------------------------
st.set_page_config(
    page_title="PropDoc AI",
    page_icon="📄",
    layout="wide",
)


# -------------------------------------------------
# IPHONE LIQUID GLASS UI
# -------------------------------------------------
st.markdown("""
<style>
:root {
    --text-main: #17243a;
    --text-muted: #687991;
}

/* Background */
.stApp {
    background:
        radial-gradient(circle at 12% 12%, rgba(105,190,255,.30), transparent 34%),
        radial-gradient(circle at 88% 18%, rgba(174,150,255,.24), transparent 36%),
        radial-gradient(circle at 50% 90%, rgba(130,220,255,.22), transparent 40%),
        linear-gradient(135deg,#eaf4ff,#f5f7ff 48%,#e9f1ff) !important;
    color: var(--text-main);
    font-family: Inter, sans-serif;
}

/* Layout */
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Headings */
h1,h2,h3,h4 {
    color: #17243a !important;
    font-weight: 750 !important;
}

/* Glass Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,.22) !important;
    border-right: 1px solid rgba(255,255,255,.65);
    backdrop-filter: blur(35px) saturate(180%);
    -webkit-backdrop-filter: blur(35px) saturate(180%);
    box-shadow: 8px 0 35px rgba(60,100,160,.08);
}
section[data-testid="stSidebar"] > div {
    background: transparent !important;
    padding: 2rem 1.2rem;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #263b58 !important;
}

/* Glass Metric Cards */
[data-testid="stMetric"] {
    background: rgba(255,255,255,.30) !important;
    border: 1px solid rgba(255,255,255,.82) !important;
    border-radius: 23px !important;
    padding: 20px !important;
    backdrop-filter: blur(28px) saturate(180%);
    box-shadow: 0 12px 35px rgba(50,80,130,.09),
                inset 0 1px 2px white;
    transition: all .3s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
}
[data-testid="stMetricLabel"] {
    color: #687991 !important;
}
[data-testid="stMetricValue"] {
    color: #172b49 !important;
}

/* Glass Inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
[data-baseweb="select"] > div {
    background: rgba(255,255,255,.40) !important;
    border: 1px solid rgba(255,255,255,.90) !important;
    border-radius: 14px !important;
    color: #17243a !important;
    backdrop-filter: blur(18px);
}

/* Glass Buttons */
.stButton > button,
.stDownloadButton > button {
    background: rgba(255,255,255,.38) !important;
    color: #1b4775 !important;
    border: 1px solid rgba(255,255,255,.90) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(22px);
    box-shadow: 0 7px 22px rgba(50,90,150,.09),
                inset 0 1px 2px white;
    font-weight: 700;
    transition: all .3s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: rgba(255,255,255,.72) !important;
    transform: translateY(-3px);
}

/* Glass Upload */
div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,.25);
    border: 1px solid rgba(255,255,255,.80);
    border-radius: 22px;
    padding: 15px;
    backdrop-filter: blur(25px);
}

/* Alerts and Dividers */
[data-testid="stAlert"],
[data-testid="stExpander"] {
    border-radius: 19px !important;
    border: 1px solid rgba(255,255,255,.75);
}
hr {
    border-color: rgba(255,255,255,.75) !important;
}

/* Mobile */
@media(max-width:768px) {
    .block-container { padding: 1rem; }
    h1 { font-size: 28px !important; }
}
</style>
""", unsafe_allow_html=True)




# -------------------------------------------------
# GLASS SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding:15px 5px;">
        <h2 style="color:#17243a;">📄 PropDoc AI</h2>
        <p style="color:#687991;">
            Smart Document Intelligence
        </p>
        <hr>
        <p style="color:#263b58;">📁 Document Workspace</p>
        <p style="color:#263b58;">🤖 AI Analysis</p>
        <p style="color:#263b58;">🔍 Document Verification</p>
        <p style="color:#263b58;">💬 AI Assistant</p>
        <hr>
        <p style="color:#687991;font-size:12px;">
            Powered by Gemini AI
        </p>
    </div>
    """, unsafe_allow_html=True)




# -------------------------------------------------
# GLASS HERO HEADER
# -------------------------------------------------
st.markdown("""
<div style="background: rgba(255,255,255,0.28);
border: 1px solid rgba(255,255,255,0.85);
border-radius: 28px;
padding: 35px;
margin-bottom: 25px;
backdrop-filter: blur(32px) saturate(190%);
-webkit-backdrop-filter: blur(32px) saturate(190%);
box-shadow: 0 15px 45px rgba(45,75,125,0.10), inset 0 1px 2px rgba(255,255,255,0.95);">
<h1 style="color:#17243a !important; margin:0;">📄 PropDoc AI</h1><p style="color:#344d6b; font-size:19px; font-weight:600;">Smart Document Intelligence</p><p style="color:#526780; font-size:15px;">Upload, read, compare and understand any document with Artificial Intelligence.</p>
</div>
""", unsafe_allow_html=True)


st.info(
    "PropDoc AI provides document-reading assistance, not legal advice. "
    "Always verify important details with official records "
    "and a qualified property lawyer."
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
# 3. OPENAI CONFIGURATION
# -------------------------------------------------

OPENAI_MODEL = "gpt-5.4-mini"
MAX_DOCUMENT_CHARACTERS = 60000


def get_openai_client():
    """Create an OpenAI client using Streamlit Secrets."""

    api_key = st.secrets.get("OPENAI_API_KEY", "")

    if not api_key:
        raise ValueError(
            "OpenAI API key is missing. Add OPENAI_API_KEY "
            "in Streamlit Cloud → App settings → Secrets."
        )

    return OpenAI(api_key=api_key)


def ask_openai(prompt: str) -> str:
    """Generate an AI response using OpenAI."""

    client = get_openai_client()

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            max_output_tokens=5000
        )

        answer = (response.output_text or "").strip()

        if not answer:
            raise RuntimeError(
                "OpenAI returned an empty response."
            )

        return answer

    except Exception as error:
        raise RuntimeError(
            f"OpenAI API request failed: {error}"
        ) from error

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
    "Upload your document",
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
    st.header("🤖 Smart Document Analysis")
    st.write(
        "Gemini will summarize the extracted text, identify details that "
        "are explicitly present, and flag items that may need manual review."
    )

    response_language = st.selectbox(
        "AI response language",
        ["English", "Marathi", "Hindi"],
        key="response_language",
    )

    if st.button("✨ Analyze My Document", type="primary"):
        try:
            document_text = get_document_context()
    
            analysis_prompt = f"""
You are PropDoc AI, an intelligent universal document
reader and information analysis assistant.

Automatically identify the document type.

The document may be:
- Property or real estate
- Legal or agreement
- Educational or certificate
- Business or company
- Financial or banking
- Identity document
- Government document
- General document

Do not assume every document is property-related.

Write the response in {response_language}.

Use these sections:

1. Document Type
2. Simple Document Summary
3. Important Information
4. Names and Organizations
5. Important Dates and Reference Numbers
6. Amounts, Payments and Financial Details
7. Important Clauses and Conditions
8. Missing or Unclear Information
9. Possible Inconsistencies
10. Important Things to Remember

Extract information according to the actual document type.
For example, extract marks from educational documents,
clauses from legal agreements, and property details
from property documents.

RULES:
- Use only the provided document text.
- Never invent information.
- Write "Not found" when information is unavailable.
- Mention page numbers or short supporting quotes when possible.
- Distinguish facts from possible concerns.
- Do not claim that a document is authentic or legally valid.
- Do not provide definitive legal or financial advice.

DOCUMENT TEXT:
{document_text}
"""

            with st.spinner("Gemini is analyzing your document..."):
                result = ask_openai(analysis_prompt)

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
           placeholder="Example: What are the important details in this document?",
        )
        submitted = st.form_submit_button("Ask PropDoc AI")

    if submitted:
        if not user_question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                document_text = get_document_context()
                question_prompt = f"""
You are PropDoc AI, a universal assistant that answers questions
about any type of document. Answer in {response_language if 'response_language' in st.session_state else 'English'}.

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
                  answer = ask_openai(question_prompt)

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
# 9. SMART DOCUMENT COMPARISON
# -------------------------------------------------

st.divider()

st.header("🔍 Smart Document Comparison")

st.write(
    "Upload a second PDF to compare it with your "
    "currently extracted document using Gemini AI."
)

# Initialize comparison session state
st.session_state.setdefault("comparison_result", "")
st.session_state.setdefault("comparison_first_name", "")
st.session_state.setdefault("comparison_second_name", "")

if st.session_state.extracted_text.strip():

    st.success(
        f"First Document: {st.session_state.document_name}"
    )

    second_document = st.file_uploader(
        "Upload your second document (PDF)",
        type=["pdf"],
        key="comparison_second_pdf"
    )

    if second_document is not None:

        st.info(
            f"Second Document: {second_document.name}"
        )

        if st.button(
            "✨ Compare Both Documents",
            type="primary",
            key="compare_documents_button"
        ):

            try:
                second_pdf = fitz.open(
                    stream=second_document.getvalue(),
                    filetype="pdf"
                )

                second_text = ""

                with st.spinner(
                    "Extracting text from the second document..."
                ):

                    for page_number, page in enumerate(second_pdf):

                        if use_ocr:
                            pix = page.get_pixmap(
                                matrix=fitz.Matrix(2, 2),
                                alpha=False
                            )

                            image = Image.open(
                                io.BytesIO(pix.tobytes("png"))
                            )

                            page_text = pytesseract.image_to_string(
                                image,
                                lang=language_codes[language]
                            )

                        else:
                            page_text = page.get_text()

                        second_text += (
                            f"\n\n--- Page {page_number + 1} ---\n\n"
                            + page_text
                        )

                second_pdf.close()

                if not second_text.strip():
                    st.warning(
                        "No readable text found in the second PDF. "
                        "Try another PDF or check your OCR settings."
                    )

                else:

                    first_text = get_document_context()

                    second_text = second_text[
                        :MAX_DOCUMENT_CHARACTERS
                    ]

                    comparison_prompt = f"""
You are PropDoc AI, an expert document comparison assistant.

Compare the following two documents carefully.

DOCUMENT 1:
{first_text}

DOCUMENT 2:
{second_text}

Write the comparison in a clear and professional format.

Use these sections:

1. DOCUMENT TYPE
Identify the type of each document.

2. OVERALL SUMMARY
Explain the main purpose of both documents.

3. MATCHING INFORMATION
List information that appears consistent in both documents.

4. DIFFERENCES FOUND
Identify changed names, dates, amounts, addresses,
reference numbers, clauses and other important details.

5. MISSING INFORMATION
Identify important information present in one document
but not found in the other.

6. POSSIBLE CONFLICTS
Flag information that appears inconsistent or contradictory.

7. IMPORTANT CHANGES
Explain the most significant differences in simple language.

8. FINAL COMPARISON SUMMARY
Explain what the user should manually review.

RULES:
- Never invent information.
- Use only the supplied document text.
- Mention document name and page number when possible.
- Clearly distinguish confirmed differences from possible concerns.
- If information is unavailable, write "Not found".
- Do not claim that either document is authentic or legally valid.
- Do not provide definitive legal or financial advice.

"""

                    with st.spinner(
                        "open AI is comparing both documents..."
                    ):

                comparison = ask_openai(
                    comparison_prompt
                )

                    st.session_state.comparison_result = comparison

                    st.session_state.comparison_first_name = (
                        st.session_state.document_name
                    )

                    st.session_state.comparison_second_name = (
                        second_document.name
                    )

                    st.success(
                        "Document comparison completed!"
                    )

            except Exception as error:

                st.error(
                    "Document comparison could not be completed."
                )

                st.exception(error)

    # Display comparison only for the current first document
    if (
        st.session_state.comparison_result
        and st.session_state.comparison_first_name
        == st.session_state.document_name
    ):

        st.divider()

        st.subheader("📊 Comparison Results")

        st.caption(
            f"Comparing: "
            f"{st.session_state.comparison_first_name} "
            f"vs "
            f"{st.session_state.comparison_second_name}"
        )

        st.markdown(
            st.session_state.comparison_result
        )

        st.download_button(
            "📥 Download Comparison Report",
            data=st.session_state.comparison_result,
            file_name="propdoc_comparison_report.txt",
            mime="text/plain",
            key="download_comparison_report"
        )

else:

    st.info(
        "Please upload and extract your first PDF document "
        "in the Document Workspace before using comparison."
    )


