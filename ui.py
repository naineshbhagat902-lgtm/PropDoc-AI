"""Visual layer: classic ivory / navy / brass theme + touch-to-flip icon cards."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');
:root{--ivory:#f7f1e3;--parch:#efe4cb;--navy:#1b2a49;--navy2:#26395f;--brass:#b08d57;--gold:#d4b06a;--wine:#7a2e3a;--ink:#1f2a3d;--muted:#6c7587;}
html,body,.stApp{font-family:'Inter',system-ui,sans-serif;color:var(--ink);}
.stApp{background:
 radial-gradient(circle at 8% 6%,rgba(212,176,106,.28),transparent 32%),
 radial-gradient(circle at 92% 12%,rgba(122,46,58,.10),transparent 30%),
 radial-gradient(circle at 50% 100%,rgba(27,42,73,.10),transparent 40%),
 linear-gradient(160deg,#fbf6ea,#f3ead4 55%,#f7f1e3)!important;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1280px;padding-top:1.6rem;padding-bottom:4rem;}
h1,h2,h3,h4{font-family:'Cormorant Garamond',Georgia,serif!important;color:var(--navy)!important;font-weight:700!important;letter-spacing:.2px;}
h2{border-bottom:1px solid rgba(176,141,87,.45);padding-bottom:.35rem;}

/* Sidebar */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#16233f,#1f3158 60%,#16233f)!important;border-right:2px solid var(--brass);}
section[data-testid="stSidebar"] *{color:#efe6d0!important;}
section[data-testid="stSidebar"] [role="radiogroup"]{gap:.25rem;}
section[data-testid="stSidebar"] [role="radiogroup"] label{background:rgba(255,255,255,.05);border:1px solid rgba(212,176,106,.25);border-radius:12px;padding:.55rem .8rem;transition:all .25s;}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(212,176,106,.22);transform:translateX(4px);}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(90deg,rgba(212,176,106,.45),rgba(212,176,106,.10));border-color:var(--gold);}
section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child{display:none;}
section[data-testid="stSidebar"] [data-baseweb="select"] *{color:#1f2a3d!important;}
.brand{display:flex;gap:.7rem;align-items:center;padding:.2rem .2rem 1rem;border-bottom:1px solid rgba(212,176,106,.4);margin-bottom:1rem;}
.brand .seal{width:46px;height:46px;border-radius:50%;border:2px solid var(--gold);display:grid;place-items:center;font-size:22px;background:rgba(212,176,106,.15);}
.brand b{font-family:'Cormorant Garamond',serif;font-size:1.55rem;color:#fff!important;line-height:1}
.brand small{display:block;opacity:.75;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;margin-top:3px}
.docchip{margin-top:1rem;padding:.7rem .8rem;border-radius:12px;background:rgba(0,0,0,.22);border:1px dashed rgba(212,176,106,.5);font-size:.82rem}

/* Hero */
.hero{position:relative;overflow:hidden;background:linear-gradient(135deg,var(--navy),var(--navy2));border-radius:26px;padding:2.2rem 2.4rem;margin-bottom:1.4rem;border:1px solid var(--brass);box-shadow:0 18px 50px rgba(27,42,73,.25),inset 0 0 0 5px rgba(212,176,106,.12);}
.hero:after{content:"";position:absolute;inset:10px;border:1px solid rgba(212,176,106,.45);border-radius:18px;pointer-events:none}
.hero .eyebrow{color:var(--gold);letter-spacing:.28em;text-transform:uppercase;font-size:.74rem;font-weight:600}
.hero h1{color:#fff!important;font-size:2.8rem;margin:.2rem 0 .3rem;line-height:1.05}
.hero p{color:#d9d3c0;max-width:760px;font-size:1.02rem;margin:0}
.hero .orn{position:absolute;right:28px;top:14px;font-size:84px;opacity:.12;color:var(--gold)}
.sec-title{display:flex;align-items:center;gap:.6rem;margin:.4rem 0 .8rem}
.sec-title .ic{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:var(--navy);color:var(--gold);border:2px solid var(--brass);font-size:19px}
.sec-title h2{margin:0;border:0;padding:0}
.sec-sub{color:var(--muted);margin:-.2rem 0 1rem}

/* Widgets */
[data-testid="stMetric"]{background:linear-gradient(180deg,#fffdf7,#f5ecd6)!important;border:1px solid rgba(176,141,87,.55)!important;border-radius:18px!important;padding:16px 18px!important;box-shadow:0 8px 22px rgba(27,42,73,.08),inset 0 1px 0 #fff;transition:transform .25s}
[data-testid="stMetric"]:hover{transform:translateY(-4px)}
[data-testid="stMetricLabel"] *{color:var(--muted)!important;font-weight:600}
[data-testid="stMetricValue"] *{color:var(--navy)!important;font-family:'Cormorant Garamond',serif;font-weight:700}
.stTextInput input,.stNumberInput input,.stTextArea textarea,[data-baseweb="select"]>div{background:#fffdf7!important;border:1px solid rgba(176,141,87,.6)!important;border-radius:12px!important;color:var(--ink)!important;}
.stButton>button,.stDownloadButton>button{background:#fffdf7!important;color:var(--navy)!important;border:1px solid var(--brass)!important;border-radius:12px!important;font-weight:600;transition:all .25s;box-shadow:0 4px 12px rgba(27,42,73,.08);}
.stButton>button:hover,.stDownloadButton>button:hover{background:var(--parch)!important;transform:translateY(-2px);border-color:var(--navy)!important}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,var(--navy),var(--navy2))!important;color:#f6e7c3!important;border:1px solid var(--gold)!important}
.stButton>button[kind="primary"]:hover{background:linear-gradient(135deg,#223662,#31497a)!important}
div[data-testid="stFileUploader"]>section,[data-testid="stAudioInput"]{background:#fffdf7;border:2px dashed var(--brass);border-radius:16px;}
[data-testid="stTabs"] button[role="tab"]{font-weight:600;color:var(--muted)}
[data-testid="stTabs"] button[aria-selected="true"]{color:var(--navy)}
[data-testid="stAlert"],[data-testid="stExpander"]{border-radius:14px!important;border:1px solid rgba(176,141,87,.5)!important}
[data-testid="stChatMessage"]{background:#fffdf7;border:1px solid rgba(176,141,87,.4);border-radius:16px}
hr{border-color:rgba(176,141,87,.5)!important}
.chip{display:inline-block;margin:3px 6px 3px 0;padding:4px 12px;border-radius:999px;background:var(--navy);color:#f6e7c3;font-size:.8rem;border:1px solid var(--gold)}
.chip.alt{background:#fffdf7;color:var(--navy);border-color:var(--brass)}
.fact-h{font-family:'Cormorant Garamond',serif;font-weight:700;color:var(--navy);font-size:1.15rem;margin:.6rem 0 .2rem}
.say{background:#fffdf7;border-left:4px solid var(--brass);padding:.55rem .9rem;border-radius:0 12px 12px 0;margin:.35rem 0;font-style:italic;color:var(--navy2)}
.disc{font-size:.8rem;color:var(--muted);border-top:1px solid rgba(176,141,87,.4);padding-top:.7rem;margin-top:1.4rem}
@media(max-width:768px){.hero{padding:1.4rem 1.2rem}.hero h1{font-size:2rem}.block-container{padding:1rem}}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title, subtitle, eyebrow="Smart Document Intelligence", orn="⚖"):
    st.markdown(
        f'<div class="hero"><div class="orn">{orn}</div><div class="eyebrow">{eyebrow}</div>'
        f"<h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)


def section(icon, title, sub=""):
    st.markdown(f'<div class="sec-title"><div class="ic">{icon}</div><h2>{title}</h2></div>'
                + (f'<div class="sec-sub">{sub}</div>' if sub else ""), unsafe_allow_html=True)


def chips(items, alt=False):
    cls = "chip alt" if alt else "chip"
    return "".join(f'<span class="{cls}">{i}</span>' for i in items)


# ---------------------------------------------------------------------------
# Classic engraved-style line icons (inline SVG, 64x64)
# ---------------------------------------------------------------------------
ICONS = {
    "doc": '<path d="M16 8h24l10 10v38H16z"/><path d="M40 8v10h10"/><path d="M23 28h20M23 35h20M23 42h14"/>',
    "lens": '<circle cx="28" cy="28" r="15"/><path d="M39 39l14 14"/><path d="M21 28a7 7 0 0 1 7-7"/>',
    "quill": '<path d="M50 8C32 10 20 22 18 44l-6 10 10-6c22-2 34-14 28-40z"/><path d="M18 44L40 22M30 40h8"/>',
    "scale": '<path d="M32 10v40M20 54h24M12 18h40"/><path d="M12 18l-7 18h14zM52 18l-7 18h14z"/><path d="M5 36a7 5 0 0 0 14 0M45 36a7 5 0 0 0 14 0"/>',
    "coin": '<circle cx="32" cy="32" r="22"/><circle cx="32" cy="32" r="17"/><path d="M24 22h16M24 29h16M26 22c11 0 11 14 0 14h-3l14 11"/>',
    "mic": '<rect x="23" y="8" width="18" height="30" rx="9"/><path d="M15 30a17 17 0 0 0 34 0M32 47v9M24 56h16"/><path d="M23 20h18M23 27h18"/>',
    "hall": '<path d="M8 24L32 8l24 16z"/><path d="M12 28h40M12 52h40M6 57h52"/><path d="M16 28v24M28 28v24M36 28v24M48 28v24"/>',
    "seal": '<circle cx="32" cy="30" r="19"/><circle cx="32" cy="30" r="14"/><path d="M23 30l6 6 12-13"/><path d="M22 47l-5 12 8-3 4 6 3-14M42 47l5 12-8-3-4 6-3-14"/>',
}


def icon(name, size=64):
    return (f'<svg viewBox="0 0 64 64" width="{size}" height="{size}" fill="none" stroke="currentColor" '
            f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


CARDS = [
    ("doc", "Document Workspace", "Upload any PDF. Smart OCR reads Marathi, Hindi and English, including scans.", "Workspace"),
    ("seal", "Key Facts Finder", "Instantly pulls amounts, dates, survey numbers and PAN-style IDs from the text.", "Workspace"),
    ("lens", "AI Analysis", "A structured, section-by-section reading of the document and what needs review.", "AI Analysis"),
    ("quill", "Ask the Document", "Chat with your file. Answers cite pages and admit when something is missing.", "Ask Questions"),
    ("scale", "Compare Documents", "Spot changed names, dates, amounts and conflicting clauses across two PDFs.", "Compare"),
    ("coin", "Minimal Tax Planner", "Capital gains, Sec 54 / 54EC strategies and the lowest lawful tax.", "Tax Planner"),
    ("hall", "Stamp Duty & TDS", "Buyer's stamp duty, registration fee and 1% TDS worked out in seconds.", "Tax Planner"),
    ("mic", "Voice Assistant", "Speak to the app: navigate, run tax scenarios and hear the answer back.", "Voice Assistant"),
]


def feature_cards_html():
    cards = ""
    for i, (ic, title, desc, _) in enumerate(CARDS):
        cards += f"""
<div class="card" style="--d:{i * 70}ms" tabindex="0">
  <div class="inner">
    <div class="face front">
      <div class="medal">{icon(ic, 58)}</div>
      <div class="t">{title}</div>
      <div class="hint">tap to reveal</div>
    </div>
    <div class="face back">
      <div class="plate"><div class="plate-in">{icon(ic, 74)}</div></div>
      <div class="t">{title}</div>
      <div class="d">{desc}</div>
    </div>
  </div>
</div>"""
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500&display=swap');
*{{box-sizing:border-box;margin:0}}
body{{font-family:Inter,system-ui,sans-serif;background:transparent;padding:6px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:18px}}
.card{{perspective:1100px;height:250px;cursor:pointer;outline:none;animation:rise .6s both;animation-delay:var(--d)}}
@keyframes rise{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
.inner{{position:relative;width:100%;height:100%;transition:transform .75s cubic-bezier(.2,.8,.2,1);transform-style:preserve-3d}}
.card.flipped .inner{{transform:rotateY(180deg)}}
@media(hover:hover){{.card:hover .inner{{transform:rotateY(180deg)}}}}
.face{{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:22px;padding:22px 16px;
 display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;border:1.5px solid #b08d57}}
.front{{background:linear-gradient(160deg,#fffdf7,#f1e6cc);box-shadow:0 10px 26px rgba(27,42,73,.12),inset 0 0 0 5px rgba(212,176,106,.15)}}
.front:before{{content:"";position:absolute;inset:8px;border:1px solid rgba(176,141,87,.55);border-radius:15px}}
.medal{{width:96px;height:96px;border-radius:50%;display:grid;place-items:center;color:#d4b06a;
 background:radial-gradient(circle at 30% 25%,#2c426e,#1b2a49);border:3px double #d4b06a;box-shadow:0 8px 18px rgba(27,42,73,.35);transition:transform .3s}}
.card:active .medal{{transform:scale(.9) rotate(-6deg)}}
.t{{font-family:'Cormorant Garamond',Georgia,serif;font-weight:700;font-size:1.28rem;color:#1b2a49;margin-top:14px;line-height:1.1}}
.hint{{font-size:.66rem;letter-spacing:.2em;text-transform:uppercase;color:#a08658;margin-top:7px}}
.back{{transform:rotateY(180deg);color:#f3e7c9;background:linear-gradient(160deg,#1b2a49,#26395f);box-shadow:0 12px 30px rgba(27,42,73,.3)}}
.back:before{{content:"";position:absolute;inset:8px;border:1px solid rgba(212,176,106,.6);border-radius:15px}}
.plate{{width:118px;height:118px;border-radius:50%;padding:7px;background:conic-gradient(from 0deg,#d4b06a,#8a6a3a,#e8cd90,#8a6a3a,#d4b06a);box-shadow:0 6px 16px rgba(0,0,0,.4)}}
.plate-in{{width:100%;height:100%;border-radius:50%;display:grid;place-items:center;color:#4a3519;filter:sepia(.6);
 background:radial-gradient(circle,#f6ecd2 40%,#e0cc9d 100%),repeating-linear-gradient(45deg,transparent 0 2px,rgba(90,60,20,.12) 2px 3px);
 background-blend-mode:multiply;box-shadow:inset 0 0 14px rgba(90,60,20,.5)}}
.back .t{{color:#f6e7c3;font-size:1.12rem;margin-top:11px}}
.d{{font-size:.76rem;line-height:1.35;color:#d9d3c0;margin-top:6px;padding:0 4px}}
</style>
<div class="grid">{cards}</div>
<script>
document.querySelectorAll('.card').forEach(c=>{{
  c.addEventListener('click',()=>c.classList.toggle('flipped'));
  c.addEventListener('keydown',e=>{{if(e.key==='Enter'||e.key===' '){{e.preventDefault();c.classList.toggle('flipped')}}}});
}});
</script>
"""


def speech_html(text, lang="en-IN"):
    """Browser text-to-speech with a replay button (works on phones too)."""
    import json
    t = json.dumps(text)
    l = json.dumps(lang)
    return f"""
<style>body{{margin:0;font-family:Inter,system-ui,sans-serif}}
button{{background:#1b2a49;color:#f6e7c3;border:1px solid #d4b06a;border-radius:999px;padding:7px 16px;cursor:pointer;font-weight:600}}
span{{color:#6c7587;font-size:.8rem;margin-left:8px}}</style>
<button id="b">🔊 Speak reply again</button><span id="s"></span>
<script>
const text={t}, lang={l};
function speak(){{
  if(!('speechSynthesis' in window)){{document.getElementById('s').textContent='Voice output not supported in this browser.';return}}
  speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(text);u.lang=lang;u.rate=.97;
  const v=speechSynthesis.getVoices().find(v=>v.lang===lang)||speechSynthesis.getVoices().find(v=>v.lang.startsWith(lang.slice(0,2)));
  if(v)u.voice=v;speechSynthesis.speak(u);
}}
document.getElementById('b').onclick=speak;
setTimeout(speak,250);
</script>
"""
