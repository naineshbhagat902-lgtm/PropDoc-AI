"""Visual layer: iPhone-style Liquid Glass theme + touch-to-flip glass icon cards.

Drop-in replacement: same functions as before
(inject_css, hero, section, chips, icon, feature_cards_html, speech_html).
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
  --ink:#14213d; --muted:#5f6f8a; --blue:#0a84ff; --violet:#7c5cff; --pink:#ff6fa8; --mint:#30d5c8;
  --glass:rgba(255,255,255,.34); --glass-strong:rgba(255,255,255,.55);
  --edge:rgba(255,255,255,.85); --shadow:0 18px 50px rgba(40,70,140,.16);
  --blur:blur(32px) saturate(185%);
}
html,body,.stApp{font-family:-apple-system,'SF Pro Display','Inter',system-ui,sans-serif;color:var(--ink);}

/* ---------- Living "plasma" background ---------- */
.stApp{isolation:isolate;background:linear-gradient(135deg,#e8f2ff,#f4f0ff 50%,#e6f7ff)!important;}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:transparent!important;}
.stApp::before,.stApp::after{content:"";position:fixed;z-index:-1;pointer-events:none;border-radius:50%;filter:blur(60px);opacity:.85}
.stApp::before{width:55vw;height:55vw;left:-12vw;top:-14vw;
  background:radial-gradient(circle at 35% 35%,rgba(10,132,255,.55),rgba(124,92,255,.35) 55%,transparent 72%);
  animation:plasmaA 22s ease-in-out infinite alternate}
.stApp::after{width:50vw;height:50vw;right:-14vw;bottom:-16vw;
  background:radial-gradient(circle at 60% 60%,rgba(255,111,168,.45),rgba(48,213,200,.35) 55%,transparent 72%);
  animation:plasmaB 26s ease-in-out infinite alternate}
@keyframes plasmaA{to{transform:translate(18vw,14vh) scale(1.2) rotate(40deg)}}
@keyframes plasmaB{to{transform:translate(-20vw,-12vh) scale(1.15) rotate(-35deg)}}

header[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1280px;padding-top:1.6rem;padding-bottom:4rem;}
h1,h2,h3,h4{color:var(--ink)!important;font-weight:750!important;letter-spacing:-.02em;}
p,label,li,span{color:var(--ink);}

/* ---------- Shared glass recipe ---------- */
.glass,[data-testid="stMetric"],[data-testid="stExpander"],[data-testid="stAlert"],[data-testid="stChatMessage"],
div[data-testid="stFileUploader"]>section,[data-testid="stAudioInput"],.say,.docchip,.hero{
  background:var(--glass)!important;
  -webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);
  border:1px solid var(--edge)!important;
  box-shadow:var(--shadow),inset 0 1.5px 2px rgba(255,255,255,.95),inset 0 -1px 2px rgba(120,150,210,.18);
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"]{background:rgba(255,255,255,.26)!important;-webkit-backdrop-filter:blur(42px) saturate(190%);backdrop-filter:blur(42px) saturate(190%);
  border-right:1px solid rgba(255,255,255,.8);box-shadow:10px 0 40px rgba(60,100,170,.10);}
section[data-testid="stSidebar"]>div{background:transparent!important;}
section[data-testid="stSidebar"] [role="radiogroup"]{gap:.35rem;}
section[data-testid="stSidebar"] [role="radiogroup"] label{background:rgba(255,255,255,.30);border:1px solid rgba(255,255,255,.75);border-radius:16px;padding:.6rem .85rem;
  box-shadow:inset 0 1px 2px #fff,0 4px 14px rgba(60,100,170,.08);transition:all .28s cubic-bezier(.2,.8,.2,1);}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(255,255,255,.6);transform:translateX(5px) scale(1.01);}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){
  background:linear-gradient(135deg,rgba(10,132,255,.30),rgba(124,92,255,.22));border-color:rgba(255,255,255,.95);
  box-shadow:0 8px 22px rgba(10,132,255,.22),inset 0 1.5px 2px #fff;}
section[data-testid="stSidebar"] [role="radiogroup"] label>div:first-child{display:none;}
.brand{display:flex;gap:.75rem;align-items:center;padding:.2rem .2rem 1rem;margin-bottom:1rem;border-bottom:1px solid rgba(255,255,255,.7);}
.brand .seal{width:48px;height:48px;border-radius:15px;display:grid;place-items:center;font-size:23px;
  background:linear-gradient(145deg,rgba(255,255,255,.85),rgba(255,255,255,.25));border:1px solid #fff;
  box-shadow:0 8px 20px rgba(10,132,255,.25),inset 0 2px 3px #fff;}
.brand b{font-size:1.4rem;font-weight:800;color:var(--ink);line-height:1;letter-spacing:-.02em}
.brand small{display:block;color:var(--muted);font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;margin-top:4px}
.docchip{margin-top:1rem;padding:.75rem .9rem;border-radius:16px;font-size:.82rem;color:var(--ink)}

/* ---------- Hero ---------- */
.hero{position:relative;overflow:hidden;border-radius:32px;padding:2.3rem 2.5rem;margin-bottom:1.5rem;}
.hero:before{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;
  background:linear-gradient(180deg,rgba(255,255,255,.65),rgba(255,255,255,0) 42%);}
.hero:after{content:"";position:absolute;top:-40%;left:-60%;width:40%;height:180%;pointer-events:none;transform:rotate(18deg);
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.65),transparent);animation:sheen 7s ease-in-out infinite}
@keyframes sheen{0%,60%{left:-60%}100%{left:130%}}
.hero .eyebrow{position:relative;display:inline-block;padding:4px 14px;border-radius:999px;font-size:.72rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;
  color:#0a63c9;background:rgba(10,132,255,.12);border:1px solid rgba(255,255,255,.9)}
.hero h1{position:relative;font-size:3rem;margin:.6rem 0 .35rem;line-height:1.02;
  background:linear-gradient(135deg,#14213d,#0a84ff 70%,#7c5cff);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent!important}
.hero p{position:relative;color:#3b4d6b;max-width:780px;font-size:1.05rem;margin:0}
.hero .orn{position:absolute;right:30px;top:6px;font-size:96px;opacity:.14;filter:saturate(.3)}
.sec-title{display:flex;align-items:center;gap:.7rem;margin:.5rem 0 .8rem}
.sec-title .ic{width:44px;height:44px;border-radius:14px;display:grid;place-items:center;font-size:20px;color:#fff;
  background:linear-gradient(145deg,#4aa3ff,#7c5cff);border:1px solid rgba(255,255,255,.9);box-shadow:0 8px 20px rgba(10,132,255,.3),inset 0 2px 3px rgba(255,255,255,.7)}
.sec-title h2{margin:0;border:0;padding:0}
.sec-sub{color:var(--muted);margin:-.2rem 0 1rem}

/* ---------- Widgets ---------- */
[data-testid="stMetric"]{border-radius:24px!important;padding:18px 20px!important;transition:transform .3s cubic-bezier(.2,.8,.2,1),box-shadow .3s}
[data-testid="stMetric"]:hover{transform:translateY(-6px) scale(1.015);box-shadow:0 26px 60px rgba(40,70,140,.24),inset 0 1.5px 2px #fff}
[data-testid="stMetricLabel"] *{color:var(--muted)!important;font-weight:600}
[data-testid="stMetricValue"] *{color:var(--ink)!important;font-weight:800;letter-spacing:-.02em}
.stTextInput input,.stNumberInput input,.stTextArea textarea,[data-baseweb="select"]>div{
  background:rgba(255,255,255,.5)!important;border:1px solid rgba(255,255,255,.95)!important;border-radius:16px!important;color:var(--ink)!important;
  -webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);box-shadow:inset 0 2px 4px rgba(90,120,180,.12),0 1px 0 #fff;}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus{box-shadow:0 0 0 3px rgba(10,132,255,.35)!important}
.stButton>button,.stDownloadButton>button{position:relative;overflow:hidden;background:var(--glass-strong)!important;color:#0b4a94!important;border:1px solid var(--edge)!important;border-radius:18px!important;
  -webkit-backdrop-filter:blur(22px) saturate(180%);backdrop-filter:blur(22px) saturate(180%);font-weight:650;
  box-shadow:0 8px 22px rgba(40,90,170,.14),inset 0 1.5px 2px #fff;transition:all .28s cubic-bezier(.2,.8,.2,1);}
.stButton>button:hover,.stDownloadButton>button:hover{background:rgba(255,255,255,.82)!important;transform:translateY(-3px);box-shadow:0 16px 34px rgba(40,90,170,.22),inset 0 1.5px 2px #fff}
.stButton>button:active,.stDownloadButton>button:active{transform:scale(.96)}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,rgba(10,132,255,.92),rgba(124,92,255,.88))!important;color:#fff!important;border:1px solid rgba(255,255,255,.75)!important;
  box-shadow:0 12px 30px rgba(10,132,255,.38),inset 0 2px 3px rgba(255,255,255,.55)}
.stButton>button[kind="primary"]:hover{background:linear-gradient(135deg,#2b96ff,#8f72ff)!important}
.stButton>button p,.stDownloadButton>button p{color:inherit!important}
div[data-testid="stFileUploader"]>section,[data-testid="stAudioInput"]{border-radius:24px!important;border:1.5px dashed rgba(255,255,255,.95)!important;padding:14px}
[data-testid="stTabs"] [role="tablist"]{gap:6px;background:rgba(255,255,255,.3);padding:5px;border-radius:18px;border:1px solid var(--edge);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px)}
[data-testid="stTabs"] button[role="tab"]{border-radius:14px;font-weight:650;color:var(--muted);padding:.4rem 1rem}
[data-testid="stTabs"] button[aria-selected="true"]{color:var(--ink);background:rgba(255,255,255,.85);box-shadow:0 4px 14px rgba(40,90,170,.15)}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],[data-testid="stTabs"] [data-baseweb="tab-border"]{display:none}
[data-testid="stAlert"],[data-testid="stExpander"]{border-radius:22px!important}
[data-testid="stChatMessage"]{border-radius:22px!important}
[data-testid="stDataFrame"]{border-radius:20px;overflow:hidden;border:1px solid var(--edge)}
hr{border-color:rgba(255,255,255,.8)!important}
.chip{display:inline-block;margin:3px 6px 3px 0;padding:5px 14px;border-radius:999px;font-size:.8rem;font-weight:600;color:#fff;
  background:linear-gradient(135deg,rgba(10,132,255,.85),rgba(124,92,255,.8));border:1px solid rgba(255,255,255,.85);box-shadow:0 6px 16px rgba(10,132,255,.25),inset 0 1px 2px rgba(255,255,255,.6)}
.chip.alt{color:#0b4a94;background:rgba(255,255,255,.55);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);box-shadow:0 4px 12px rgba(40,90,170,.10),inset 0 1px 2px #fff}
.fact-h{font-weight:750;color:var(--ink);font-size:1.05rem;margin:.7rem 0 .2rem}
.say{padding:.65rem 1rem;border-radius:18px;margin:.4rem 0;font-style:italic;color:#2c4268}
.disc{font-size:.8rem;color:var(--muted);border-top:1px solid rgba(255,255,255,.8);padding-top:.8rem;margin-top:1.4rem}
@media(max-width:768px){.hero{padding:1.5rem 1.25rem;border-radius:26px}.hero h1{font-size:2.1rem}.block-container{padding:1rem}.stApp::before,.stApp::after{filter:blur(40px)}}
@media(prefers-reduced-motion:reduce){.stApp::before,.stApp::after,.hero:after{animation:none}}
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

# one glowing hue per card so the glass has colour to refract
HUES = [210, 265, 190, 320, 25, 150, 235, 345]


def feature_cards_html():
    cards = ""
    for i, (ic, title, desc, _) in enumerate(CARDS):
        cards += f"""
<div class="card" style="--d:{i * 70}ms;--h:{HUES[i]}" tabindex="0">
  <div class="orb"></div>
  <div class="inner">
    <div class="face front">
      <div class="shine"></div>
      <div class="medal">{icon(ic, 56)}</div>
      <div class="t">{title}</div>
      <div class="hint">tap to reveal</div>
    </div>
    <div class="face back">
      <div class="shine"></div>
      <div class="plate"><div class="plate-in">{icon(ic, 72)}</div></div>
      <div class="t">{title}</div>
      <div class="d">{desc}</div>
    </div>
  </div>
</div>"""
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{{box-sizing:border-box;margin:0}}
body{{font-family:-apple-system,'SF Pro Display',Inter,system-ui,sans-serif;background:transparent;padding:8px;color:#14213d}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:22px}}
.card{{position:relative;perspective:1200px;height:250px;cursor:pointer;outline:none;animation:rise .7s cubic-bezier(.2,.8,.2,1) both;animation-delay:var(--d);-webkit-tap-highlight-color:transparent}}
@keyframes rise{{from{{opacity:0;transform:translateY(22px) scale(.96)}}to{{opacity:1;transform:none}}}}
/* glowing colour orbs behind the glass */
.orb{{position:absolute;width:150px;height:150px;left:50%;top:50%;margin:-95px 0 0 -105px;border-radius:50%;filter:blur(26px);opacity:.9;
  background:radial-gradient(circle at 35% 35%,hsl(var(--h) 100% 68%),hsl(calc(var(--h) + 50) 95% 62%) 60%,transparent 72%);
  animation:float 6s ease-in-out infinite alternate}}
@keyframes float{{to{{transform:translate(34px,26px) scale(1.15)}}}}
.inner{{position:relative;width:100%;height:100%;transition:transform .8s cubic-bezier(.2,.8,.2,1);transform-style:preserve-3d}}
.card.flipped .inner{{transform:rotateY(180deg)}}
@media(hover:hover){{.card:hover .inner{{transform:rotateY(180deg)}}.card:hover .orb{{opacity:1}}}}
.face{{position:absolute;inset:0;overflow:hidden;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:30px;padding:22px 16px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
.shine{{position:absolute;inset:0;border-radius:inherit;pointer-events:none;
  background:radial-gradient(circle at var(--mx,30%) var(--my,10%),rgba(255,255,255,.75),transparent 42%),linear-gradient(180deg,rgba(255,255,255,.45),transparent 38%)}}
.front{{background:rgba(255,255,255,.30);-webkit-backdrop-filter:blur(26px) saturate(190%);backdrop-filter:blur(26px) saturate(190%);
  border:1.5px solid rgba(255,255,255,.9);box-shadow:0 18px 44px rgba(40,70,140,.2),inset 0 2px 3px #fff,inset 0 -2px 4px rgba(120,150,210,.25)}}
.medal{{position:relative;width:92px;height:92px;border-radius:30px;display:grid;place-items:center;color:#fff;
  background:linear-gradient(145deg,hsl(var(--h) 95% 62%),hsl(calc(var(--h) + 45) 90% 52%));border:1.5px solid rgba(255,255,255,.9);
  box-shadow:0 14px 28px hsl(var(--h) 90% 50% / .45),inset 0 3px 5px rgba(255,255,255,.7),inset 0 -4px 8px rgba(0,0,0,.12);transition:transform .3s cubic-bezier(.2,.8,.2,1)}}
.card:active .medal{{transform:scale(.88) rotate(-5deg)}}
.t{{position:relative;font-weight:780;font-size:1.12rem;letter-spacing:-.01em;color:#14213d;margin-top:15px;line-height:1.15}}
.hint{{position:relative;font-size:.64rem;letter-spacing:.2em;text-transform:uppercase;color:#5f6f8a;margin-top:7px;font-weight:600}}
/* back: vintage engraved plate set in dark glass */
.back{{transform:rotateY(180deg);color:#fff;background:linear-gradient(160deg,rgba(20,33,61,.72),rgba(38,57,95,.6));
  -webkit-backdrop-filter:blur(26px) saturate(170%);backdrop-filter:blur(26px) saturate(170%);
  border:1.5px solid rgba(255,255,255,.55);box-shadow:0 20px 46px rgba(20,33,61,.38),inset 0 2px 3px rgba(255,255,255,.5)}}
.plate{{position:relative;width:116px;height:116px;border-radius:50%;padding:6px;background:conic-gradient(from 0deg,#f1d89a,#a98443,#fbeab9,#a98443,#f1d89a);box-shadow:0 8px 20px rgba(0,0,0,.4)}}
.plate-in{{width:100%;height:100%;border-radius:50%;display:grid;place-items:center;color:#4a3519;filter:sepia(.55);
  background:radial-gradient(circle,#f8efd6 40%,#dcc795 100%),repeating-linear-gradient(45deg,transparent 0 2px,rgba(90,60,20,.12) 2px 3px);
  background-blend-mode:multiply;box-shadow:inset 0 0 14px rgba(90,60,20,.5)}}
.back .t{{color:#fff;font-size:1.05rem;margin-top:11px}}
.d{{position:relative;font-size:.75rem;line-height:1.4;color:rgba(255,255,255,.82);margin-top:6px;padding:0 4px}}
@media(prefers-reduced-motion:reduce){{.orb,.card{{animation:none}}}}
</style>
<div class="grid">{cards}</div>
<script>
document.querySelectorAll('.card').forEach(c=>{{
  c.addEventListener('click',()=>c.classList.toggle('flipped'));
  c.addEventListener('keydown',e=>{{if(e.key==='Enter'||e.key===' '){{e.preventDefault();c.classList.toggle('flipped')}}}});
  const move=e=>{{const r=c.getBoundingClientRect();
    c.style.setProperty('--mx',((e.clientX-r.left)/r.width*100)+'%');
    c.style.setProperty('--my',((e.clientY-r.top)/r.height*100)+'%')}};
  c.addEventListener('pointermove',move);c.addEventListener('pointerdown',move);
}});
</script>
"""


def speech_html(text, lang="en-IN"):
    """Browser text-to-speech with a glass replay button (works on phones too)."""
    import json
    t = json.dumps(text)
    l = json.dumps(lang)
    return f"""
<style>body{{margin:0;font-family:-apple-system,Inter,system-ui,sans-serif}}
button{{background:linear-gradient(135deg,rgba(10,132,255,.92),rgba(124,92,255,.88));color:#fff;border:1px solid rgba(255,255,255,.85);border-radius:999px;
  padding:8px 18px;cursor:pointer;font-weight:650;box-shadow:0 8px 20px rgba(10,132,255,.35),inset 0 2px 3px rgba(255,255,255,.55);transition:transform .2s}}
button:active{{transform:scale(.94)}}
span{{color:#5f6f8a;font-size:.8rem;margin-left:8px}}</style>
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
