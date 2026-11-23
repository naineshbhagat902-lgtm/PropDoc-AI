"""OpenAI helpers (text, speech-to-text, text-to-speech, voice commands)."""
import json
import streamlit as st
from openai import OpenAI

def _secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:  # no secrets.toml yet
        return default


OPENAI_MODEL = _secret("OPENAI_MODEL", "gpt-5.4-mini")


def get_client() -> OpenAI:
    key = _secret("OPENAI_API_KEY")
    if not key:
        raise ValueError("OpenAI API key is missing. Add OPENAI_API_KEY in Streamlit "
                         "Cloud → App settings → Secrets.")
    return OpenAI(api_key=key)


def ask(prompt: str, max_tokens: int = 5000) -> str:
    client = get_client()
    try:
        r = client.responses.create(model=OPENAI_MODEL, input=prompt, max_output_tokens=max_tokens)
        out = (r.output_text or "").strip()
        if not out:
            raise RuntimeError("OpenAI returned an empty response.")
        return out
    except Exception as e:
        raise RuntimeError(f"OpenAI API request failed: {e}") from e
    finally:
        client.close()


def transcribe(audio_bytes: bytes, filename: str = "voice.wav") -> str:
    client = get_client()
    last = None
    try:
        for model in ("gpt-4o-mini-transcribe", "whisper-1"):
            try:
                r = client.audio.transcriptions.create(model=model, file=(filename, audio_bytes))
                return (r.text or "").strip()
            except Exception as e:  # try the next model
                last = e
        raise RuntimeError(f"Speech recognition failed: {last}")
    finally:
        client.close()


def speak_bytes(text: str, voice: str = "alloy") -> bytes:
    client = get_client()
    try:
        for model in ("gpt-4o-mini-tts", "tts-1"):
            try:
                return client.audio.speech.create(model=model, voice=voice, input=text[:1500]).content
            except Exception:
                continue
        raise RuntimeError("OpenAI voice output is unavailable.")
    finally:
        client.close()


def parse_json(text: str) -> dict:
    a, b = text.find("{"), text.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no JSON found")
    return json.loads(text[a:b + 1])


PAGES_HELP = "Home, Workspace, AI Analysis, Ask Questions, Compare, Tax Planner, Voice Assistant"

TAX_KEYS = {
    "value": "property value being BOUGHT (rupees)",
    "stamp_pct": "stamp duty percent",
    "sale": "sale price when SELLING (rupees)",
    "cost": "original purchase cost (rupees)",
    "improvement": "cost of improvements (rupees)",
    "expenses": "brokerage / transfer expenses (rupees)",
    "months": "months the property was held (years x 12)",
    "indexed_cost": "indexed cost of acquisition (rupees)",
    "house": "amount to reinvest in a new house, Sec 54 (rupees)",
    "bonds": "amount to invest in 54EC bonds (rupees)",
    "slab_pct": "income-tax slab rate percent for short-term gains",
}


def voice_command_prompt(transcript, lang, tax_state, tax_summary, doc_snippet):
    return f"""
You are PropDoc AI's voice assistant for Indian property documents and LAWFUL
minimal-tax planning. The user spoke a command (it may be English, Hindi or Marathi,
or a mix). Reply ONLY with one JSON object, no markdown fences:

{{"action": "navigate" | "set_tax" | "answer",
  "page": "<one of: {PAGES_HELP}>"   (for navigate; optional for set_tax),
  "tax": {{ ...only the keys the user mentioned... }}   (for set_tax),
  "reply": "short spoken reply in {lang}, max 90 words, plain sentences, no markdown, no bullet points"}}

Rules:
- "navigate": user wants to open a screen ("open tax planner", "show comparison").
- "set_tax": user gives property numbers. Convert spoken amounts to plain rupee numbers
  (1 lakh = 100000, 1 crore = 10000000). Years to months. Allowed tax keys and meaning:
  {json.dumps(TAX_KEYS)}
  Then briefly explain, in the reply, the lowest LAWFUL tax route using the numbers
  below if available (Sec 54 house reinvestment, Sec 54EC bonds up to Rs 50 lakh within 6 months,
  Sec 54F, Capital Gains Account Scheme, indexation choice for pre 23-Jul-2024 property,
  cost of improvement, claiming transfer expenses, joint ownership). The Income-tax Act 2025
  renumbered these sections, so say "Section 54 (renumbered under the 2025 Act)" style and
  advise confirming with a CA.
- "answer": any other question (tax or document). Use the document text if present.
- Lawful planning only. If asked to hide income, take cash off the books, under-declare the
  registered value or evade tax, decline briefly and give lawful alternatives.
- Never promise a result. Mention to verify with a Chartered Accountant when giving tax advice.
- Do not invent facts about the document.

CURRENT TAX INPUTS: {json.dumps(tax_state)}
CURRENT TAX RESULT: {tax_summary}
DOCUMENT TEXT (may be empty): {doc_snippet}

USER SAID: {transcript}
"""
