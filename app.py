import io
import re
import hashlib
import streamlit as st
import streamlit.components.v1 as components
import fitz  # PyMuPDF
import pandas as pd
import pytesseract
from PIL import Image

import ai
import tax_engine as tx
import ui

st.set_page_config(page_title="PropDoc AI", page_icon="📜", layout="wide")
ui.inject_css()

S = st.session_state
MAX_CHARS = 60000

PAGES = ["Home", "Workspace", "AI Analysis", "Ask Questions", "Compare", "Tax Planner", "Voice Assistant"]
PAGE_ICON = {"Home": "🏛️", "Workspace": "📁", "AI Analysis": "🔍", "Ask Questions": "💬",
             "Compare": "⚖️", "Tax Planner": "🪙", "Voice Assistant": "🎙️"}
LANG_CODES = {"Marathi + English + Hindi": "mar+eng+hin", "Marathi + English": "mar+eng", "Hindi + English": "hin+eng"}
SPEECH_LANG = {"English": "en-IN", "Hindi": "hi-IN", "Marathi": "mr-IN"}
TAX_DEFAULTS = dict(value=0.0, stamp_pct=6.0, reg_pct=1.0, reg_cap=30000.0, sale=0.0, cost=0.0,
                    improvement=0.0, expenses=0.0, months=0.0, indexed_cost=0.0, surcharge=0.0,
                    slab_pct=30.0, house=0.0, bonds=0.0)

# ---------------------------------------------------------------- state
for k, v in dict(extracted_text="", document_name="", ai_analysis="", chat_history=[], voice_log=[],
                 comparison_result="", comparison_first="", comparison_second="", pending_nav=None,
                 pending_speech=None, last_audio="", tax_ver=0, nav="Home").items():
    S.setdefault(k, v)
S.setdefault("tax", dict(TAX_DEFAULTS))
if S.pending_nav:                       # set by buttons / voice before the radio is drawn
    S.nav, S.pending_nav = S.pending_nav, None


def go(page):
    S.pending_nav = page


# ---------------------------------------------------------------- helpers
def extract_pdf_text(data: bytes, mode: str, lang_code: str, progress=None) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    total = len(doc)
    if total == 0:
        raise ValueError("The uploaded PDF has no pages.")
    out = []
    for i, page in enumerate(doc):
        text = "" if mode == "ocr" else page.get_text()
        if mode == "ocr" or (mode == "auto" and len(text.strip()) < 40):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            text = pytesseract.image_to_string(Image.open(io.BytesIO(pix.tobytes("png"))), lang=lang_code)
        out.append(f"\n\n--- Page {i + 1} ---\n\n{text}")
        if progress:
            progress((i + 1) / total)
    doc.close()
    return "".join(out)


def doc_context() -> str:
    text = S.extracted_text.strip()
    if not text:
        raise ValueError("Please extract a PDF in the Workspace first.")
    return text[:MAX_CHARS]


def need_doc() -> bool:
    if S.extracted_text.strip():
        return True
    st.info("No document loaded yet. Upload and extract a PDF in the Workspace first.")
    st.button("📁 Open Workspace", on_click=go, args=("Workspace",))
    return False


MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
FACTS = {
    "Amounts": (r"(?:₹|Rs\.?|INR)\s?[\d,]+(?:\.\d+)?(?:\s?(?:lakh|lac|crore|cr)\b)?", re.I),
    "Dates": (rf"\b\d{{1,2}}[/.-]\d{{1,2}}[/.-]\d{{2,4}}\b|\b\d{{1,2}}\s(?:{MONTHS})[a-z]*\.?,?\s\d{{4}}\b", re.I),
    "Survey / plot numbers": (r"\b(?:survey|gat|cts|plot|s\.?\s?no\.?|khasra)\s*(?:no\.?|number)?\s*[:\-]?\s*\d+[\w/.\-]*", re.I),
    "PAN-style IDs": (r"\b[A-Z]{5}\d{4}[A-Z]\b", 0),
}


def find_facts(text):
    found = {}
    for name, (pat, fl) in FACTS.items():
        seen = []
        for m in re.finditer(pat, text, fl):
            v = " ".join(m.group(0).split())
            if v not in seen:
                seen.append(v)
        found[name] = seen
    return found


def amount_value(s: str) -> float:
    m = re.search(r"[\d,]+(?:\.\d+)?", s)
    if not m:
        return 0.0
    n = float(m.group(0).replace(",", "") or 0)
    low = s.lower()
    if "crore" in low or re.search(r"\bcr\b", low):
        n *= 1e7
    elif "lakh" in low or "lac" in low:
        n *= 1e5
    return n


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown('<div class="brand"><div class="seal">📜</div><div><b>PropDoc AI</b>'
                '<small>Document · Tax · Voice</small></div></div>', unsafe_allow_html=True)
    st.radio("Navigate", PAGES, key="nav", label_visibility="collapsed",
             format_func=lambda p: f"{PAGE_ICON[p]}   {p}")
    st.selectbox("AI reply language", ["English", "Hindi", "Marathi"], key="response_language")
    chip = (f"📄 <b>{S.document_name}</b><br>{len(S.extracted_text):,} characters ready"
            if S.extracted_text else "📄 No document loaded")
    st.markdown(f'<div class="docchip">{chip}</div>', unsafe_allow_html=True)
    if S.extracted_text and st.button("🗑️ Clear workspace", use_container_width=True):
        for k in ("extracted_text", "document_name", "ai_analysis", "comparison_result"):
            S[k] = ""
        S.chat_history = []
        st.rerun()
    st.caption("Powered by OpenAI · Not legal or tax advice")

RLANG = S.response_language


# ================================================================ HOME
def page_home():
    ui.hero("PropDoc AI", "Read, compare and understand property papers, then plan your tax the lawful, "
            "minimal way. Speak to it if you prefer.", "Smart Document Intelligence")
    ui.section("✦", "Explore", "Tap any card to turn it over. On a computer, just hover.")
    components.html(ui.feature_cards_html(), height=560, scrolling=False)

    ui.section("➜", "Jump straight in")
    cols = st.columns(4)
    for i, p in enumerate(PAGES[1:]):
        cols[i % 4].button(f"{PAGE_ICON[p]}  {p}", key=f"jump_{p}", on_click=go, args=(p,), use_container_width=True)

    if S.extracted_text:
        st.write("")
        a, b, c = st.columns(3)
        a.metric("Loaded document", S.document_name[:22])
        b.metric("Pages", S.extracted_text.count("--- Page "))
        c.metric("Words", f"{len(S.extracted_text.split()):,}")
    st.markdown('<div class="disc">PropDoc AI assists with reading documents and illustrative tax maths. '
                'It is not legal or tax advice. Verify important details with official records, a property lawyer '
                'and a Chartered Accountant.</div>', unsafe_allow_html=True)


# ================================================================ WORKSPACE
def page_workspace():
    ui.hero("Document Workspace", "Upload a PDF and let smart OCR read it. Marathi, Hindi and English supported.",
            "Step 1", "📁")
    up = st.file_uploader("Upload your document", type=["pdf"])
    c1, c2 = st.columns(2)
    mode_label = c1.radio("Reading mode", ["Auto (text first, OCR if scanned)", "Always use OCR", "Text layer only (fastest)"])
    lang = c2.selectbox("Document languages", list(LANG_CODES))
    mode = {"A": "auto", "O": "ocr", "T": "text"}[mode_label[0]]

    if up is not None:
        st.success(f"PDF ready: {up.name}")
        if st.button("✨ Extract Document Text", type="primary"):
            try:
                bar = st.progress(0)
                with st.spinner("Reading your document..."):
                    text = extract_pdf_text(up.getvalue(), mode, LANG_CODES[lang], bar.progress)
                S.extracted_text, S.document_name = text, up.name
                S.ai_analysis, S.chat_history = "", []
                (st.success if text.strip() else st.warning)(
                    "Text extraction completed!" if text.strip() else
                    "No readable text found. Try 'Always use OCR' or check the language selection.")
            except Exception as e:
                st.error("Something went wrong while processing the PDF.")
                st.exception(e)

    if not S.extracted_text:
        return
    text = S.extracted_text
    st.divider()
    ui.section("🔖", "Key facts found", "Detected automatically (no AI needed). OCR can misread digits, so check the original.")
    facts = find_facts(text)
    cols = st.columns(len(facts))
    for col, (name, vals) in zip(cols, facts.items()):
        col.metric(name, len(vals))
    for name, vals in facts.items():
        if vals:
            st.markdown(f'<div class="fact-h">{name}</div>' + ui.chips(vals[:25], alt=True), unsafe_allow_html=True)
    amounts = [amount_value(a) for a in facts["Amounts"]]
    if amounts and max(amounts) > 0:
        big = max(amounts)
        st.button(f"🪙 Use largest amount ({tx.inr(big)}) as property value in Tax Planner",
                  on_click=lambda: (S.tax.update(value=big, sale=big), S.__setitem__("tax_ver", S.tax_ver + 1), go("Tax Planner")))

    st.divider()
    ui.section("📃", "Extracted text", S.document_name)
    q = st.text_input("🔎 Search inside the document", placeholder="e.g. survey number, buyer name, 7/12")
    if q.strip():
        hits = [ln.strip() for ln in text.splitlines() if q.lower() in ln.lower()]
        st.caption(f"{len(hits)} matching line(s)")
        for h in hits[:40]:
            st.markdown(f'<div class="say">{h}</div>', unsafe_allow_html=True)
    st.text_area("Recognized text", text, height=320)
    st.download_button("⬇️ Download extracted text", text, "propdoc_extracted_text.txt", "text/plain")
    if len(text) > MAX_CHARS:
        st.warning(f"AI requests use only the first {MAX_CHARS:,} characters of this document.")


# ================================================================ ANALYSIS
def page_analysis():
    ui.hero("Smart Analysis", "A structured reading of your document: facts, parties, dates, money and red flags.",
            "Step 2", "🔍")
    if not need_doc():
        return
    if st.button("✨ Analyze My Document", type="primary"):
        try:
            prompt = f"""
You are PropDoc AI, an intelligent universal document reader and information analysis assistant.
Automatically identify the document type (property, legal, educational, business, financial, identity,
government or general). Do not assume every document is property-related.
Write the response in {RLANG}.
Use these sections:
1. Document Type 2. Simple Document Summary 3. Important Information 4. Names and Organizations
5. Important Dates and Reference Numbers 6. Amounts, Payments and Financial Details
7. Important Clauses and Conditions 8. Missing or Unclear Information 9. Possible Inconsistencies
10. Important Things to Remember
RULES: use only the provided text; never invent information; write "Not found" when unavailable;
mention page numbers or short quotes; distinguish facts from possible concerns; do not claim the
document is authentic or legally valid; no definitive legal or financial advice.
DOCUMENT TEXT:
{doc_context()}
"""
            with st.spinner("Analyzing your document..."):
                S.ai_analysis = ai.ask(prompt)
            st.success("AI analysis completed!")
        except Exception as e:
            st.error(f"AI analysis could not be completed: {e}")
    if S.ai_analysis:
        st.markdown(S.ai_analysis)
        st.download_button("⬇️ Download analysis", S.ai_analysis, "propdoc_ai_analysis.txt", "text/plain")


# ================================================================ ASK
QUICK_QS = ["Who are the parties and what are their roles?", "What amounts and payment terms are mentioned?",
            "List all important dates.", "Are there any red flags or missing details?",
            "Summarise this document in 5 simple lines."]


def page_ask():
    ui.hero("Ask the Document", "Questions answered only from your document, with page references.", "Step 3", "💬")
    if not need_doc():
        return
    st.markdown("**Quick questions**")
    cols = st.columns(len(QUICK_QS))
    quick = None
    for c, q in zip(cols, QUICK_QS):
        if c.button(q, key=f"qq_{q}", use_container_width=True):
            quick = q
    typed = st.chat_input("Ask anything about this document…")
    question = quick or typed
    if question:
        try:
            prompt = f"""
You are PropDoc AI. Answer in {RLANG}. Use only the document text below. Do not guess or invent.
If the answer is absent or the OCR text is unclear, say so. Mention page numbers or short quotes.
Explain calculations transparently. This is not legal advice.
DOCUMENT TEXT:
{doc_context()}
USER QUESTION:
{question}
"""
            with st.spinner("Finding the answer in your document..."):
                S.chat_history.append({"question": question, "answer": ai.ask(prompt)})
        except Exception as e:
            st.error(f"Your question could not be answered: {e}")
    for item in S.chat_history:
        with st.chat_message("user"):
            st.write(item["question"])
        with st.chat_message("assistant"):
            st.markdown(item["answer"])
    if S.chat_history:
        log = "\n\n".join(f"Q: {i['question']}\nA: {i['answer']}" for i in S.chat_history)
        a, b = st.columns([1, 1])
        a.download_button("⬇️ Download conversation", log, "propdoc_chat.txt", "text/plain")
        if b.button("🧹 Clear conversation"):
            S.chat_history = []
            st.rerun()


# ================================================================ COMPARE
def page_compare():
    ui.hero("Compare Documents", "Upload a second PDF to find changes, gaps and conflicts against your loaded document.",
            "Step 4", "⚖️")
    if not need_doc():
        return
    st.success(f"First document: {S.document_name}")
    second = st.file_uploader("Upload your second document (PDF)", type=["pdf"], key="cmp_pdf")
    mode = st.radio("Reading mode for the second file", ["auto", "ocr", "text"], horizontal=True)
    lang = st.selectbox("Second document languages", list(LANG_CODES), key="cmp_lang")
    if second is not None and st.button("✨ Compare Both Documents", type="primary"):
        try:
            with st.spinner("Extracting and comparing…"):
                t2 = extract_pdf_text(second.getvalue(), mode, LANG_CODES[lang])[:MAX_CHARS]
                if not t2.strip():
                    st.warning("No readable text found in the second PDF.")
                    return
                prompt = f"""
You are PropDoc AI, an expert document comparison assistant. Write in {RLANG}.
Compare the two documents carefully.
DOCUMENT 1 ({S.document_name}):
{doc_context()}
DOCUMENT 2 ({second.name}):
{t2}
Sections: 1. DOCUMENT TYPE 2. OVERALL SUMMARY 3. MATCHING INFORMATION 4. DIFFERENCES FOUND
(names, dates, amounts, addresses, reference numbers, clauses) 5. MISSING INFORMATION
6. POSSIBLE CONFLICTS 7. IMPORTANT CHANGES 8. FINAL COMPARISON SUMMARY (what to review manually)
RULES: never invent; use only supplied text; cite document name and page; separate confirmed
differences from possible concerns; write "Not found" if unavailable; do not claim authenticity
or legal validity; no definitive legal or financial advice.
"""
                S.comparison_result = ai.ask(prompt)
            S.comparison_first, S.comparison_second = S.document_name, second.name
            st.success("Document comparison completed!")
        except Exception as e:
            st.error("Document comparison could not be completed.")
            st.exception(e)
    if S.comparison_result and S.comparison_first == S.document_name:
        st.divider()
        ui.section("📊", "Comparison results", f"{S.comparison_first}  vs  {S.comparison_second}")
        st.markdown(S.comparison_result)
        st.download_button("⬇️ Download comparison report", S.comparison_result,
                           "propdoc_comparison_report.txt", "text/plain")


# ================================================================ TAX
def tnum(label, key, step=100000.0, show_words=True, **kw):
    v = st.number_input(label, min_value=0.0, value=float(S.tax[key]), step=step, format="%.0f",
                        key=f"t_{key}_{S.tax_ver}", **kw)
    S.tax[key] = v
    if show_words and v >= 1e5:
        st.caption(f"= {tx.words(v)}")
    return v


def cg_args():
    t = S.tax
    return dict(sale=t["sale"], cost=t["cost"], improvement=t["improvement"], expenses=t["expenses"],
                months=t["months"], indexed_cost=t["indexed_cost"], surcharge_pct=t["surcharge"],
                slab_pct=t["slab_pct"])


def tax_summary() -> str:
    t = S.tax
    if t["sale"] <= 0:
        return "No sale details entered yet."
    r = tx.capital_gains(**cg_args(), house=t["house"], bonds=t["bonds"])
    kind = "long-term" if r["is_long"] else "short-term"
    return (f"{kind} gain {tx.inr(r['gain'])}, exemptions {tx.inr(r['ex54'] + r['ex54ec'])}, "
            f"tax {tx.inr(r['total'])} ({r['method']})")


def page_tax():
    ui.hero("Minimal Tax Planner", "Compare lawful ways to lower tax on a property sale or purchase. "
            "Every figure is editable; rates are defaults you should confirm.", "Lawful tax planning", "🪙")
    tab1, tab2, tab3 = st.tabs(["💰 Capital gains · lowest tax", "🏛️ Stamp duty & TDS", "📋 Saving checklist"])

    with tab1:
        left, right = st.columns([1, 1.15], gap="large")
        with left:
            st.markdown("##### Sale details")
            tnum("Sale price (₹)", "sale")
            tnum("Original purchase cost (₹)", "cost")
            tnum("Improvement / renovation cost (₹)", "improvement")
            tnum("Brokerage & transfer expenses (₹)", "expenses", 10000.0)
            tnum("Months you held the property", "months", 1.0, show_words=False,
                 help="More than 24 months = long-term for property.")
            tnum("Indexed cost of acquisition (₹), optional", "indexed_cost",
                 help="Only for property bought before 23 July 2024 (resident individual / HUF). "
                      "The calculator picks whichever method gives lower tax.")
            st.markdown("##### Reinvestment plan")
            tnum("New house purchase / construction (₹), Sec 54", "house")
            tnum("54EC bonds (₹), max ₹50 lakh", "bonds", 50000.0)
            c1, c2 = st.columns(2)
            with c1:
                tnum("Slab rate % (short-term)", "slab_pct", 1.0, show_words=False)
            with c2:
                tnum("Surcharge %", "surcharge", 1.0, show_words=False)
        with right:
            t = S.tax
            if t["sale"] <= 0:
                st.info("Enter the sale price on the left, or say it to the Voice Assistant.")
            else:
                r = tx.capital_gains(**cg_args(), house=t["house"], bonds=t["bonds"])
                m1, m2 = st.columns(2)
                m1.metric("Capital gain", tx.inr(r["gain"]), "long-term" if r["is_long"] else "short-term")
                m2.metric("Exemptions used", tx.inr(r["ex54"] + r["ex54ec"]))
                m3, m4 = st.columns(2)
                m3.metric("Taxable gain", tx.inr(r["taxable"]))
                m4.metric("Total tax (incl. cess)", tx.inr(r["total"]))
                st.caption(f"Method: {r['method']}.")
                if not r["is_long"] and r["gain"] > 0:
                    st.warning("Held 24 months or less: short-term gain, taxed at slab rate. "
                               "Sec 54 / 54EC exemptions are not available. Holding past 24 months may cut the tax sharply.")
                rows = tx.scenarios(**cg_args())
                df = pd.DataFrame(rows)
                st.markdown("##### Strategy comparison")
                shown = df.copy()
                shown["You invest"] = shown["You invest"].map(tx.inr)
                shown["Tax payable"] = shown["Tax payable"].map(tx.inr)
                st.dataframe(shown, hide_index=True, use_container_width=True)
                st.bar_chart(df.set_index("Strategy")["Tax payable"], color="#b08d57")
                best = df.sort_values(["Tax payable", "You invest"]).iloc[0]
                saved = df["Tax payable"].max() - best["Tax payable"]
                if saved > 0:
                    st.success(f"Lowest lawful tax here: **{best['Strategy']}**, saving about **{tx.inr(saved)}** "
                               f"versus paying outright. Mind the deadlines: reinvest in a house 1 year before to 2 years "
                               f"after the sale (3 years if constructing); 54EC bonds within 6 months with a 5-year lock-in; "
                               f"park unspent money in a Capital Gains Account Scheme before the return due date.")
        st.caption("Sections 54 / 54EC / 54F were renumbered by the Income-tax Act 2025 (in force 1 April 2026) "
                   "with the same substance. Ask your CA for the current section numbers.")

    with tab2:
        c1, c2 = st.columns([1, 1.15], gap="large")
        with c1:
            tnum("Property value for stamp duty (₹)", "value", help="Higher of agreement value and ready-reckoner value.")
            tnum("Total stamp duty % (incl. cess / LBT)", "stamp_pct", 0.5, show_words=False,
                 help="Maharashtra urban areas are commonly about 6%, but it varies by location and buyer. Verify on the IGR portal.")
            tnum("Registration fee %", "reg_pct", 0.5, show_words=False)
            tnum("Registration fee cap (₹)", "reg_cap", 5000.0, show_words=False)
        with c2:
            v = S.tax["value"]
            if v <= 0:
                st.info("Enter the property value to see the buyer's costs.")
            else:
                b = tx.buyer_costs(v, S.tax["stamp_pct"], S.tax["reg_pct"], S.tax["reg_cap"])
                a1, a2 = st.columns(2)
                a1.metric("Stamp duty", tx.inr(b["stamp"]))
                a2.metric("Registration fee", tx.inr(b["registration"]))
                a3, a4 = st.columns(2)
                a3.metric("Buyer's TDS (1%)", tx.inr(b["tds"]), "applies ≥ ₹50 lakh" if b["tds"] else "not applicable")
                a4.metric("All-in cost to buyer", tx.inr(b["all_in"]))
                st.caption(f"The buyer deducts 1% TDS from the price and deposits it with the government, so the seller "
                           f"receives {tx.inr(b['seller_receives'])} in hand. It is credited to the seller's tax account. "
                           f"Different rules apply when the seller is an NRI.")

    with tab3:
        tips = [
            ("Reinvest the gain, not the whole sale price (Sec 54)", "For a long-term gain on a house, buying or building another residential house within the time limits exempts the gain you reinvest, up to ₹10 crore."),
            ("54EC bonds for up to ₹50 lakh", "Invest in notified bonds within 6 months of the sale. There is a 5-year lock-in and the cap is ₹50 lakh per financial year."),
            ("Capital Gains Account Scheme", "If you cannot buy before the return due date, deposit the unspent gain in a CGAS account so the exemption is protected."),
            ("Compare 12.5% and 20% with indexation", "For property bought before 23 July 2024 you may choose the lower tax. Enter your indexed cost to see it."),
            ("Add every legitimate cost", "Brokerage, legal fees, stamp duty and registration paid at purchase, and documented improvements all reduce the gain."),
            ("Time the sale", "Crossing the 24-month holding mark converts a slab-rate gain into a long-term gain taxed at 12.5%."),
            ("Home-loan benefits (old regime)", "Interest on a self-occupied house (up to ₹2 lakh) and principal repayment plus stamp duty and registration in the year of payment (within the ₹1.5 lakh Sec 80C limit) apply only if you choose the old regime."),
            ("Joint ownership", "Co-owners each use their own slab and exemption limits, but only with genuine ownership and funding."),
            ("Keep the paperwork clean", "Declare the full value, pay by banking channels and keep Form 26QB, bond certificates and valuation proofs. Under-declaring invites penalties and is not tax planning."),
        ]
        for t, d in tips:
            with st.expander(t):
                st.write(d)
        st.caption("General information, not advice. Rules change; confirm with a Chartered Accountant.")


# ================================================================ VOICE
def run_command(text: str):
    try:
        raw = ai.ask(ai.voice_command_prompt(text, RLANG, S.tax, tax_summary(), S.extracted_text[:6000]), 900)
        try:
            data = ai.parse_json(raw)
        except Exception:
            data = {"action": "answer", "reply": raw}
        reply = (data.get("reply") or "Done.").strip()
        action, page = data.get("action"), data.get("page")
        if action == "set_tax":
            for k, v in (data.get("tax") or {}).items():
                if k in S.tax:
                    try:
                        S.tax[k] = max(float(v), 0.0)
                    except (TypeError, ValueError):
                        pass
            S.tax_ver += 1
            go(page if page in PAGES else "Tax Planner")
        elif action == "navigate" and page in PAGES:
            go(page)
        S.voice_log.append({"said": text, "reply": reply})
        S.pending_speech = reply
    except Exception as e:
        st.error(f"Voice command failed: {e}")
        return
    if S.pending_nav:
        st.rerun()


def page_voice():
    ui.hero("Voice Assistant", "Speak a command in English, Hindi or Marathi. Ask for the lowest lawful tax, "
            "set property figures, or open any screen. The reply is spoken back.", "Hands-free", "🎙️")
    S.voice_engine = st.radio("Spoken reply", ["Browser voice (free)", "OpenAI voice"], horizontal=True)
    left, right = st.columns([1, 1], gap="large")
    with left:
        if hasattr(st, "audio_input"):
            audio = st.audio_input("🎙️ Tap, speak, then tap stop")
            if audio is not None:
                data = audio.getvalue()
                digest = hashlib.md5(data).hexdigest()
                if digest != S.last_audio:
                    S.last_audio = digest
                    try:
                        with st.spinner("Listening…"):
                            heard = ai.transcribe(data)
                    except Exception as e:
                        st.error(str(e))
                        heard = ""
                    if heard:
                        run_command(heard)
        else:
            st.warning("Microphone recording needs Streamlit 1.40 or newer. You can still type commands.")
        with st.form("voice_text", clear_on_submit=True):
            typed = st.text_input("…or type a command", placeholder="e.g. Minimum tax if I sell for 1.2 crore")
            if st.form_submit_button("Send command") and typed.strip():
                run_command(typed.strip())
    with right:
        st.markdown("**Try saying**")
        for s in ["“I sold my flat for one crore twenty lakh, bought for sixty lakh, held for five years. How do I pay minimum tax?”",
                  "“What if I put fifty lakh in 54EC bonds?”",
                  "“Stamp duty on a property worth eighty-five lakh.”",
                  "“Open the comparison screen.”",
                  "“Summarise my document.”"]:
            st.markdown(f'<div class="say">{s}</div>', unsafe_allow_html=True)
    if S.voice_log:
        st.divider()
        for item in reversed(S.voice_log[-8:]):
            with st.chat_message("user"):
                st.write(item["said"])
            with st.chat_message("assistant"):
                st.write(item["reply"])


# ---------------------------------------------------------------- router
{"Home": page_home, "Workspace": page_workspace, "AI Analysis": page_analysis, "Ask Questions": page_ask,
 "Compare": page_compare, "Tax Planner": page_tax, "Voice Assistant": page_voice}[S.nav]()

# spoken reply (rendered on whichever page is showing)
if S.pending_speech:
    spoken, S.pending_speech = S.pending_speech, None
    if S.get("voice_engine", "") == "OpenAI voice":
        try:
            st.audio(ai.speak_bytes(spoken), format="audio/mp3", autoplay=True)
        except Exception:
            components.html(ui.speech_html(spoken, SPEECH_LANG[RLANG]), height=50)
    else:
        components.html(ui.speech_html(spoken, SPEECH_LANG[RLANG]), height=50)
