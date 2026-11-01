"""BetPro Elite - Viral Slip Generator (Uchambuzi wa Kina)

Inahitaji: streamlit>=1.50, google-genai, pillow>=10.1, pydantic>=2
"""
from __future__ import annotations

import hashlib
import io
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from pydantic import BaseModel, Field

# ============================================================
# 1. USANIDI
# ============================================================
st.set_page_config(
    page_title="BetPro Elite - Viral Slip Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

TZ = ZoneInfo("Africa/Dar_es_Salaam")  # saa za server mara nyingi ni UTC
MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
BACKGROUND_PHOTO = Path("profile.jpg")
POSTER_SIZE = (1080, 1350)

FONT_PATHS = [
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "arialbd.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]

PICK_COUNTS = {2: "🔥 Mechi 2", 4: "⭐ Mechi 4", 6: "🚂 Mechi 6"}

REASONS = {
    "quota": "Quota imeisha (429): kikomo cha matumizi cha key hii kimejaa",
    "invalid_key": "API key si sahihi, imefutwa au imeisha muda",
    "permission": "Key hii haina ruhusa ya kipengele au model hii (403)",
    "not_found": "Model haipatikani kwa akaunti hii (404)",
    "network": "Tatizo la mtandao au seva ya Google (jaribu tena baadaye)",
    "other": "Kosa lingine",
}

ADVICE = {
    "quota": "Weka API key mpya kwenye sehemu ya **🔑 API Key** hapo juu, au subiri kikomo kifunguke (cha dakika huisha baada ya dakika chache, cha siku huisha usiku).",
    "invalid_key": "Angalia kama key imenakiliwa vyote bila nafasi, au tengeneza mpya kwenye ai.google.dev.",
    "permission": "Washa Gemini API kwenye project ya key hiyo, au tumia key ya project nyingine.",
    "not_found": "Model hiyo haipo kwa akaunti yako. App inajaribu zinazofuata zenyewe.",
    "network": "Jaribu tena baada ya muda mfupi.",
    "other": "Angalia ujumbe wa kosa hapo juu.",
}

OFFLINE_NOTE = (
    "\n\nONYO: Huna ufikiaji wa mtandao sasa. Tumia ujuzi wako tu. Kwa mechi ambazo huna taarifa za "
    "uhakika za majeruhi na fomu ya sasa, toa alama ya usalama ya chini na sema wazi kwamba haijathibitishwa."
)


# ============================================================
# 2. MUUNDO WA DATA
# ============================================================
class Pick(BaseModel):
    label: str = Field(description="Maandishi mafupi ya bango (chini ya herufi 28), mfano 'Roma Win' au 'Over 1.5 Goals'")
    match: str = Field(description="Mechi kamili, mfano 'Roma vs Lazio'")
    market: str = Field(description="Soko lililochaguliwa na kwa nini ni salama kuliko ushindi wa moja kwa moja")
    confidence: int = Field(description="Alama ya usalama 0 hadi 100")
    risk: str = Field(description="Low au Medium")
    reasons: list[str] = Field(description="Sababu 3 hadi 5 zenye ushahidi (fomu, majeruhi, motisha, H2H, takwimu)")


class SlipResult(BaseModel):
    picks: list[Pick]
    rejected: list[str] = Field(description="Mechi zilizotupwa, kila moja na sababu fupi")
    summary: str = Field(description="Muhtasari wa Kiswahili wa kwa nini hizi ndizo bora za leo")


@dataclass(frozen=True)
class PosterResult:
    picks: list[Pick]
    slip: SlipResult
    report: str
    title: str
    used: str
    searched: bool


@dataclass(frozen=True)
class Attempt:
    key_tag: str
    model: str
    kind: str
    message: str


class AllAttemptsFailed(RuntimeError):
    def __init__(self, attempts: list[Attempt]):
        self.attempts = attempts
        super().__init__("Majaribio yote yameshindwa")


# ============================================================
# 3. API KEYS
# ============================================================
def key_tag(key: str) -> str:
    return f"…{key[-4:]}"


def collect_api_keys() -> list[str]:
    """Key ya UI kwanza, kisha keys za Secrets, kisha environment. Hakuna marudio."""
    keys: list[str] = []
    typed = (st.session_state.get("custom_key") or "").strip()
    if typed:
        keys.append(typed)
    try:
        many = st.secrets.get("GEMINI_API_KEYS", None)
        if many:
            keys.extend(str(k).strip() for k in list(many))
        single = st.secrets.get("GEMINI_API_KEY", "")
        if single:
            keys.append(str(single).strip())
    except Exception:
        pass
    env = os.environ.get("GEMINI_API_KEY", "").strip()
    if env:
        keys.append(env)
    return list(dict.fromkeys(k for k in keys if k))


def classify(exc: Exception) -> str:
    text = str(exc).upper()
    if "RESOURCE_EXHAUSTED" in text or text.startswith("429"):
        return "quota"
    if any(s in text for s in ("API_KEY_INVALID", "API KEY NOT VALID", "API KEY EXPIRED", "UNAUTHENTICATED")) or text.startswith("401"):
        return "invalid_key"
    if "PERMISSION_DENIED" in text or text.startswith("403"):
        return "permission"
    if "NOT_FOUND" in text or text.startswith("404"):
        return "not_found"
    if any(s in text for s in ("TIMEOUT", "TIMED OUT", "CONNECTION", "UNAVAILABLE", "503", "DEADLINE")):
        return "network"
    return "other"


def explain(attempts: list[Attempt]) -> str:
    """Muhtasari wa wazi: kila key ilishindwa kwa sababu gani."""
    grouped: dict[tuple[str, str], list[str]] = {}
    for a in attempts:
        grouped.setdefault((a.key_tag, a.kind), []).append(a.model)
    lines = [
        f"- **Key {tag}**: {REASONS[kind]} _(models: {', '.join(models)})_"
        for (tag, kind), models in grouped.items()
    ]
    kinds = list(dict.fromkeys(a.kind for a in attempts))
    lines += ["", "**Cha kufanya:**"] + [f"- {ADVICE[k]}" for k in kinds]
    return "\n".join(lines)


# ============================================================
# 4. GEMINI
# ============================================================
@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def list_models(key: str, client: genai.Client) -> list[str]:
    cache = st.session_state.setdefault("_models_cache", {})
    digest = hashlib.sha256(key.encode()).hexdigest()
    if digest not in cache:
        try:
            cache[digest] = [m.name.removeprefix("models/") for m in client.models.list()]
        except Exception:
            return []
    return cache[digest]


def generate(keys: list[str], contents, config: types.GenerateContentConfig):
    """Jaribu kila key, na kwa kila key models zake. Inarudisha (jibu, 'model · key')."""
    attempts: list[Attempt] = []
    for key in keys:
        tag = key_tag(key)
        client = get_client(key)
        names = list_models(key, client)
        candidates = [m for m in MODELS if m in names] or MODELS
        for model in candidates:
            try:
                response = client.models.generate_content(model=model, contents=contents, config=config)
                if response.text or response.parsed:
                    return response, f"{model} · key {tag}"
                attempts.append(Attempt(tag, model, "other", "jibu tupu"))
            except Exception as exc:
                kind = classify(exc)
                attempts.append(Attempt(tag, model, kind, str(exc)[:250]))
                if kind == "invalid_key":
                    break  # key mbovu: hakuna haja ya kujaribu models zingine
    raise AllAttemptsFailed(attempts)


def research_prompt(day: str, date: str) -> str:
    return f"""
Wewe ni mchambuzi mkuu wa soka wa kiwango cha juu. Lengo la mteja: kuchagua mechi chache SALAMA kuliko zote
za leo ili mkeka usichanike. Ubora ni muhimu kuliko wingi. Leo ni {day}, tarehe {date} (saa za Afrika Mashariki).

HATUA 1 - Soma screenshots zote. Orodhesha kila mechi (timu, ligi, saa, odds kama zinaonekana).
Tupa mechi ambazo zimeanza, zimeisha, au ni za jana.

HATUA 2 - Kwa kila mechi inayobaki, tafuta mtandaoni taarifa za SASA na uchambue kwa kina:
1. Fomu ya mechi 5-6 za mwisho za kila timu (nyumbani na ugenini kando kando).
2. Rekodi ya mechi za hivi karibuni kati yao (H2H).
3. Majeruhi, adhabu, wachezaji muhimu kukosekana, na kikosi kinachotarajiwa.
4. Motisha: nafasi kwenye msimamo, kuepuka kushuka daraja, ubingwa, mechi ya kombe, au timu kupumzisha wachezaji.
5. Uchovu na ratiba: mechi za katikati ya wiki, safari ndefu, mechi kubwa inayofuata.
6. Mbinu za makocha, mechi-ups, na takwimu za magoli (wastani wa magoli, xG, clean sheets).
7. Mazingira: uwanja, hali ya hewa, mwamuzi kama inahusika.
8. Odds: je zinaendana na uwezekano halisi? Epuka mitego ya odds ndogo kwa timu kubwa yenye matatizo.
9. Soko salama zaidi: Double Chance, Draw No Bet, Over 1.5, Under 4.5, n.k. Chagua soko lenye uwezekano mkubwa
   zaidi badala ya ushindi wa moja kwa moja pale ushindi una hatari.

HATUA 3 - Kwa kila mechi toa alama ya usalama 0-100 na sababu zake. Kuwa mkali: ukiona shaka kubwa, ipe alama ya chini.
Tumia habari ulizozipata mtandaoni. Usibuni takwimu; kama huna uhakika na kitu, sema wazi.
Toa ripoti kamili ya maandishi kwa Kiswahili.
""".strip()


def selection_prompt(report: str, count: int, min_conf: int) -> str:
    return f"""
Hii ni ripoti ya uchambuzi wa mechi za leo:

{report}

KAZI: Chagua mechi BORA ZA SIKU, zisizozidi {count}.
- Chukua TU zenye confidence ya {min_conf} au zaidi. Kama hazifiki {count}, toa chache. Usijaze nafasi kwa mechi dhaifu.
- Panga kuanzia yenye confidence kubwa zaidi.
- 'label' iwe fupi na iseme soko wazi (mfano 'Roma Win', 'Spurs or Draw', 'Over 1.5 Goals').
- Weka kwenye 'rejected' mechi zilizotupwa pamoja na sababu fupi.
- Usibuni taarifa ambazo hazipo kwenye ripoti.
""".strip()


def research_matches(keys: list[str], images: list[Image.Image], day: str, date: str, use_search: bool):
    """Inarudisha (ripoti, 'model · key', ilitumia_utafutaji)."""
    prompt = research_prompt(day, date)
    if use_search:
        search_config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())], temperature=0.2
        )
        try:
            response, used = generate(keys, [prompt, *images], search_config)
            return response.text or "", used, True
        except AllAttemptsFailed as exc:
            if {a.kind for a in exc.attempts} <= {"invalid_key", "network"}:
                raise
            st.warning("🔎 Utafutaji wa mtandaoni umeshindikana. Sababu:\n\n" + explain(exc.attempts))
            st.write("Inaendelea bila mtandao (alama zitakuwa za tahadhari zaidi)...")
    plain_config = types.GenerateContentConfig(temperature=0.2)
    response, used = generate(keys, [prompt + OFFLINE_NOTE, *images], plain_config)
    return response.text or "", used, False


def select_picks(keys: list[str], report: str, count: int, min_conf: int) -> SlipResult:
    config = types.GenerateContentConfig(
        response_mime_type="application/json", response_schema=SlipResult, temperature=0.2
    )
    response, _ = generate(keys, selection_prompt(report, count, min_conf), config)
    if isinstance(response.parsed, SlipResult):
        return response.parsed
    return SlipResult.model_validate_json(response.text)


# ============================================================
# 5. MUONEKANO
# ============================================================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    :root { --bg:#070b16; --card:rgba(255,255,255,.04); --line:rgba(255,255,255,.09); --green:#10b981; --blue:#38bdf8; --muted:#94a3b8; }
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp {
        background:
            radial-gradient(900px 500px at 10% -10%, rgba(16,185,129,.18), transparent 60%),
            radial-gradient(800px 500px at 100% 0%, rgba(56,189,248,.14), transparent 55%),
            var(--bg);
        color: #f8fafc;
    }
    header[data-testid="stHeader"], #MainMenu, footer, .stAppDeployButton { display: none; }
    .badge { display:inline-block; padding:4px 14px; border-radius:999px; font-size:.72rem; font-weight:800;
             letter-spacing:1px; text-transform:uppercase; color:#fff; background:linear-gradient(135deg,#10b981,#059669); }
    .hero-title { margin:10px 0 0; font-size:clamp(1.6rem,4vw,2.4rem); font-weight:800; line-height:1.15;
                  background:linear-gradient(90deg,var(--green),var(--blue)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .hero-sub { color:var(--muted); margin:6px 0 22px; font-size:.95rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background:var(--card); border:1px solid var(--line) !important;
                  border-radius:16px; backdrop-filter:blur(8px); }
    .stButton > button[kind="primary"], .stDownloadButton > button {
        background:linear-gradient(135deg,#10b981,#059669); color:#fff; border:0; border-radius:12px; font-weight:800;
        padding:.75rem 1.6rem; box-shadow:0 6px 20px rgba(16,185,129,.35); transition:transform .15s ease, box-shadow .15s ease; }
    .stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {
        transform:translateY(-1px); box-shadow:0 10px 26px rgba(16,185,129,.45); color:#fff; }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# 6. PICHA / BANGO
# ============================================================
def load_font(size: int):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int = 18):
    for size in range(start, minimum, -2):
        font = load_font(size)
        left, _, right, _ = draw.textbbox((0, 0), text, font=font)
        if right - left <= max_width:
            return font
    return load_font(minimum)


@dataclass(frozen=True)
class Theme:
    top: tuple[int, int, int]          # rangi ya juu ya mandharinyuma
    bottom: tuple[int, int, int]       # rangi ya chini
    accent: tuple[int, int, int]       # rangi kuu (namba, asilimia, pill)
    on_accent: tuple[int, int, int]    # rangi ya maandishi juu ya accent
    card: tuple[int, int, int, int]    # rangi ya kadi (RGBA)
    border: tuple[int, int, int, int] | None
    text: tuple[int, int, int]
    subtext: tuple[int, int, int]
    title: tuple[int, int, int]
    foot: tuple[int, int, int]         # tarehe na maandishi ya chini
    glow: bool
    photo_tint: int                    # nguvu ya rangi juu ya picha yako


THEMES: dict[str, Theme] = {
    "Neon Night": Theme(
        top=(6, 10, 24), bottom=(8, 30, 48), accent=(16, 230, 140), on_accent=(4, 20, 14),
        card=(255, 255, 255, 22), border=(16, 230, 140, 150), text=(255, 255, 255),
        subtext=(160, 185, 205), title=(255, 255, 255), foot=(160, 185, 205), glow=True, photo_tint=215,
    ),
    "Gold VIP": Theme(
        top=(10, 10, 10), bottom=(34, 25, 8), accent=(245, 190, 60), on_accent=(25, 18, 0),
        card=(255, 255, 255, 16), border=(245, 190, 60, 170), text=(255, 246, 225),
        subtext=(195, 175, 125), title=(245, 190, 60), foot=(195, 175, 125), glow=True, photo_tint=215,
    ),
    "Sunset": Theme(
        top=(76, 29, 149), bottom=(234, 88, 12), accent=(255, 255, 255), on_accent=(76, 29, 149),
        card=(255, 255, 255, 40), border=(255, 255, 255, 120), text=(255, 255, 255),
        subtext=(255, 228, 212), title=(255, 255, 255), foot=(255, 228, 212), glow=True, photo_tint=170,
    ),
    "Classic White": Theme(
        top=(0, 120, 45), bottom=(0, 205, 75), accent=(0, 0, 0), on_accent=(255, 255, 255),
        card=(255, 255, 255, 255), border=None, text=(0, 0, 0),
        subtext=(80, 80, 80), title=(0, 0, 0), foot=(255, 255, 255), glow=False, photo_tint=160,
    ),
}


def make_canvas(theme: Theme, photo: bytes | None) -> Image.Image:
    size = POSTER_SIZE
    base = ImageOps.colorize(
        Image.linear_gradient("L").resize(size), black=theme.top, white=theme.bottom
    ).convert("RGBA")

    if photo:
        try:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(photo))).convert("RGBA")
            img = ImageOps.fit(img, size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(2))
            img = ImageEnhance.Brightness(img).enhance(0.55)
            base.putalpha(theme.photo_tint)
            base = Image.alpha_composite(img, base)
        except Exception:
            pass  # picha mbovu: tumia gradient tu

    if theme.glow:
        glow = Image.new("RGBA", size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse((-250, -250, 550, 450), fill=(*theme.accent, 70))
        gd.ellipse((600, 1000, 1400, 1700), fill=(*theme.accent, 55))
        base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(120)))
    return base


@st.cache_data(show_spinner=False, max_entries=32)
def render_poster(
    labels: tuple[str, ...],
    matches: tuple[str, ...],
    confs: tuple[int, ...],
    title: str,
    date_label: str,
    theme_name: str,
    show_conf: bool,
    show_match: bool,
    watermark: str,
    photo: bytes | None,
) -> bytes:
    t = THEMES[theme_name]
    w, h = POSTER_SIZE
    canvas = make_canvas(t, photo)
    draw = ImageDraw.Draw(canvas)

    # Pill ya juu + kichwa + tarehe
    pill_text, pill_font = "BEST OF THE DAY", load_font(26)
    left, _, right, _ = draw.textbbox((0, 0), pill_text, font=pill_font)
    pw = (right - left) + 64
    draw.rounded_rectangle((w // 2 - pw // 2, 70, w // 2 + pw // 2, 122), radius=26, fill=t.accent)
    draw.text((w // 2, 96), pill_text, fill=t.on_accent, font=pill_font, anchor="mm")
    draw.text((w // 2, 150), title, fill=t.title, font=fit_font(draw, title, w - 160, 88), anchor="mt")
    draw.text((w // 2, 265), date_label, fill=t.foot, font=load_font(30), anchor="mt")

    # Mpangilio wa kadi (unajirekebisha kulingana na idadi)
    n = max(1, len(labels))
    top, bottom_reserved, gap = 340, 190, 30
    available = h - top - bottom_reserved
    card_h = min(170, (available - gap * (n - 1)) // n)
    block_h = n * card_h + (n - 1) * gap
    y0 = top + max(0, (available - block_h) // 2)
    rects = [(70, y0 + i * (card_h + gap), w - 70, y0 + i * (card_h + gap) + card_h) for i in range(n)]

    if t.card[3] > 200:  # kivuli kwa kadi imara tu
        shadow = Image.new("RGBA", POSTER_SIZE, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        for x1, y1, x2, y2 in rects:
            sd.rounded_rectangle((x1, y1 + 14, x2, y2 + 14), radius=34, fill=(0, 0, 0, 110))
        canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(18)))

    layer = Image.new("RGBA", POSTER_SIZE, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for rect in rects:
        ld.rounded_rectangle(rect, radius=34, fill=t.card, outline=t.border, width=3 if t.border else 0)
    canvas = Image.alpha_composite(canvas, layer)
    draw = ImageDraw.Draw(canvas)

    # Maudhui ya kila kadi: namba | chaguo + mechi | asilimia
    for i, ((x1, y1, x2, y2), label) in enumerate(zip(rects, labels)):
        cy = (y1 + y2) // 2
        d = int(card_h * 0.62)
        cx = x1 + 34 + d // 2
        draw.ellipse((cx - d // 2, cy - d // 2, cx + d // 2, cy + d // 2), fill=t.accent)
        draw.text((cx, cy), str(i + 1), fill=t.on_accent, font=load_font(int(d * 0.55)), anchor="mm")

        text_x = cx + d // 2 + 30
        right_edge = x2 - 34
        if show_conf:
            conf_text = f"{confs[i]}%"
            cf = load_font(max(22, int(card_h * 0.24)))
            l, _, r, _ = draw.textbbox((0, 0), conf_text, font=cf)
            pill_w, pill_h = (r - l) + 44, int(card_h * 0.38)
            draw.rounded_rectangle(
                (right_edge - pill_w, cy - pill_h // 2, right_edge, cy + pill_h // 2),
                radius=pill_h // 2, fill=t.accent,
            )
            draw.text((right_edge - pill_w // 2, cy), conf_text, fill=t.on_accent, font=cf, anchor="mm")
            right_edge -= pill_w + 24

        max_w = right_edge - text_x
        match_line = matches[i] if show_match and matches[i] else ""
        label_font = fit_font(draw, label, max_w, int(card_h * 0.34), 20)
        if match_line:
            draw.text((text_x, cy - int(card_h * 0.12)), label, fill=t.text, font=label_font, anchor="lm")
            match_font = fit_font(draw, match_line, max_w, int(card_h * 0.2), 16)
            draw.text((text_x, cy + int(card_h * 0.2)), match_line, fill=t.subtext, font=match_font, anchor="lm")
        else:
            draw.text((text_x, cy), label, fill=t.text, font=label_font, anchor="lm")

    # Chini: watermark + tahadhari ya uwajibikaji
    mark = watermark.strip() or "BETPRO"
    draw.text((w // 2, h - 110), mark, fill=t.foot, font=fit_font(draw, mark, w - 200, 32), anchor="mm")
    draw.text(
        (w // 2, h - 60), "18+  ·  Cheza kwa uwajibikaji  ·  Hakuna ushindi wa uhakika",
        fill=t.foot, font=load_font(22), anchor="mm",
    )

    buffer = io.BytesIO()
    canvas.convert("RGB").save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def prepare_images(files) -> list[Image.Image]:
    images = []
    for file in files:
        img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        images.append(img)
    return images


# ============================================================
# 7. UI
# ============================================================
now = datetime.now(TZ)
day_name = now.strftime("%A")
date_short = now.strftime("%d-%m-%Y")

st.markdown('<span class="badge">⚡ Viral Slip Terminal</span>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">BetPro Elite: Best of the Day</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">AI inachambua kwa kina kwa kutumia taarifa za sasa za mtandaoni, kisha inachagua mechi bora na salama za leo tu.</p>',
    unsafe_allow_html=True,
)

tab_slip, tab_scores = st.tabs(["📸 Kichambuzi cha Mechi", "⚽ LiveScores"])

with tab_slip:
    with st.container(border=True):
        st.markdown(f"#### 🎯 Pakia Screenshot za Mechi · {day_name}, {date_short}")
        left, right = st.columns(2, gap="large")
        with left:
            uploaded = st.file_uploader(
                "Screenshot za mechi (pakia nyingi iwezekanavyo, AI itachagua bora)",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
            )
        with right:
            count = st.segmented_control(
                "Idadi ya juu ya mechi kwenye bango",
                options=list(PICK_COUNTS),
                format_func=PICK_COUNTS.get,
                default=4,
            ) or 4
            min_conf = st.slider(
                "Kiwango cha chini cha usalama (%)",
                min_value=60, max_value=95, value=80, step=5,
                help="Mechi chini ya kiwango hiki zinatupwa kabisa. Juu zaidi = mechi chache lakini salama zaidi.",
            )
            title = st.text_input("Kichwa cha bango (hiari)", value=f"{day_name} Picks")
            use_search = st.toggle(
                "🔎 Tumia utafutaji wa mtandaoni",
                value=True,
                help="Unatoa uchambuzi bora zaidi lakini unatumia quota nyingi. Zima ukiishiwa quota.",
            )

    with st.expander("🔑 API Key (ikifika kikomo, weka mpya hapa)"):
        st.text_input(
            "Weka API key mpya (inatumika kwa kikao hiki tu, haihifadhiwi)",
            type="password",
            key="custom_key",
            placeholder="AIza...",
        )
        keys = collect_api_keys()
        if keys:
            st.caption("Keys zinazotumika kwa mpangilio: " + ", ".join(key_tag(k) for k in keys))
        else:
            st.warning("Hakuna API key. Iweke hapa juu au kwenye Secrets.")
        st.caption(
            'Unaweza kuweka keys nyingi kwenye Secrets: `GEMINI_API_KEYS = ["key1", "key2"]`. '
            "Ikiisha quota ya ya kwanza, app inahamia inayofuata yenyewe."
        )

    keys = collect_api_keys()

    if uploaded:
        images = prepare_images(uploaded)
        with st.expander(f"📸 Picha zilizopakiwa ({len(images)})"):
            st.image(images, width=150)

        if st.button("🚀 Chambua na Unda Bango", type="primary", width="stretch"):
            if not keys:
                st.error("Hakuna API key. Iweke kwenye sehemu ya 🔑 API Key au kwenye Secrets.")
            else:
                try:
                    with st.status("Uchambuzi wa kina unaendelea (inaweza kuchukua dakika 1-2)...", expanded=True) as status:
                        st.write("🔎 Hatua 1: Inasoma mechi na kuchambua fomu, majeruhi, motisha na takwimu...")
                        report, used, searched = research_matches(keys, images, day_name, date_short, use_search)

                        st.write("🎯 Hatua 2: Inachuja na kuchagua mechi bora tu...")
                        slip = select_picks(keys, report, count, min_conf)
                        picks = sorted(
                            [p for p in slip.picks if p.confidence >= min_conf],
                            key=lambda p: p.confidence,
                            reverse=True,
                        )[:count]

                        if not picks:
                            status.update(label="Hakuna mechi iliyofikia kiwango", state="error")
                            st.session_state.pop("result", None)
                            st.warning(
                                f"Hakuna mechi iliyofikia usalama wa {min_conf}%. Bora kutoweka leo kuliko kuchana mkeka. "
                                "Pakia mechi zaidi au punguza kiwango kidogo."
                            )
                        else:
                            if len(picks) < count:
                                st.write(f"ℹ️ Mechi {len(picks)} tu ndizo zilizofikia kiwango.")
                            st.session_state["result"] = PosterResult(
                                picks=picks, slip=slip, report=report,
                                title=title or f"{day_name} Picks", used=used, searched=searched,
                            )
                            status.update(label="Bango liko tayari ✅", state="complete", expanded=False)
                except AllAttemptsFailed as exc:
                    st.error("❌ Uchambuzi umeshindikana. Sababu kwa kila key:")
                    st.markdown(explain(exc.attempts))
                    with st.expander("Maelezo ya kiufundi"):
                        for a in exc.attempts:
                            st.code(f"{a.model} · key {a.key_tag} · {a.kind}\n{a.message}")
                except Exception as exc:
                    st.error(f"Hitilafu isiyotarajiwa: {exc}")

        st.caption("Hakuna mechi yenye uhakika wa 100%. AI inapunguza hatari, haiiondoi. Weka kiasi unachoweza kukipoteza.")

    result: PosterResult | None = st.session_state.get("result")
    if result:
        st.subheader("🖼️ Bango Lako")
        st.caption(
            f"Model: {result.used} · Utafutaji wa mtandaoni: "
            f"{'umetumika ✅' if result.searched else 'haukutumika (alama ni za tahadhari)'}"
        )
        poster_col, detail_col = st.columns([1, 1.2], gap="large")

        with poster_col:
            with st.container(border=True):
                st.markdown("##### 🎨 Badilisha muonekano (haitumii quota)")
                theme_name = st.pills("Mtindo wa bango", list(THEMES), default="Neon Night") or "Neon Night"
                opt_a, opt_b = st.columns(2)
                show_conf = opt_a.toggle("Onyesha asilimia", value=True)
                show_match = opt_b.toggle("Onyesha jina la mechi", value=True)
                watermark = st.text_input("Watermark / jina lako", value="BETPRO TACTICAL SYNDICATE")
                photo_file = st.file_uploader(
                    "Picha yako ya mandharinyuma (hiari)", type=["png", "jpg", "jpeg"], key="bg_photo"
                )

            if photo_file:
                photo = photo_file.getvalue()
            elif BACKGROUND_PHOTO.exists():
                photo = BACKGROUND_PHOTO.read_bytes()
            else:
                photo = None

            poster = render_poster(
                tuple(p.label for p in result.picks),
                tuple(p.match for p in result.picks),
                tuple(int(p.confidence) for p in result.picks),
                result.title,
                now.strftime("%d %B %Y"),
                theme_name,
                show_conf,
                show_match,
                watermark,
                photo,
            )
            st.image(poster, width="stretch")
            st.download_button(
                "📥 Pakua Bango (PNG)", data=poster,
                file_name=f"BetPro_{day_name}_{theme_name.replace(' ', '')}.png",
                mime="image/png", width="stretch",
            )

        with detail_col:
            st.markdown("#### 📊 Uchambuzi wa Kila Chaguo")
            for pick in result.picks:
                with st.container(border=True):
                    st.markdown(f"**★ {pick.label}** · {pick.match}")
                    st.progress(
                        min(max(pick.confidence, 0), 100) / 100,
                        text=f"Usalama: {pick.confidence}% · Hatari: {pick.risk}",
                    )
                    st.caption(f"Soko: {pick.market}")
                    for reason in pick.reasons:
                        st.markdown(f"- {reason}")
            st.info(result.slip.summary)

        with st.expander("🗑️ Mechi zilizotupwa na sababu"):
            for item in result.slip.rejected or ["Hakuna taarifa."]:
                st.markdown(f"- {item}")
        with st.expander("📄 Ripoti kamili ya uchambuzi"):
            st.write(result.report)

with tab_scores:
    st.subheader(f"⚽ LiveScores & Ratiba ({date_short})")
    components.html(
        """
        <div style="border-radius:14px; overflow:hidden; border:1px solid #334155;">
            <iframe src="https://www.scorebat.com/embed/livescore/"
                    style="width:100%; height:800px; border:none; background:#1e293b;"></iframe>
        </div>
        """,
        height=820,
        scrolling=True,
    )
