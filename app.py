"""BetPro Elite - Viral Slip Generator (toleo la kisasa)

Inahitaji: streamlit>=1.50, google-genai, pillow>=10.1, pydantic>=2
"""
from __future__ import annotations

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
MODELS = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
BACKGROUND_PHOTO = Path("profile.jpg")
POSTER_SIZE = (1080, 1350)  # uwiano bora kwa Instagram / Facebook / WhatsApp
MAX_PICKS = 8

FONT_PATHS = [
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "arialbd.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]

PICK_COUNTS = {
    2: "🔥 Mechi 2",
    4: "⭐ Mechi 4",
    6: "🚂 Mechi 6",
}


class SlipResult(BaseModel):
    """Muundo ambao Gemini analazimishwa kuutoa (structured output)."""

    picks: list[str] = Field(description="Chaguo fupi, kila moja chini ya herufi 25")
    full_analysis: str = Field(description="Uchambuzi wa kina kwa Kiswahili")


@dataclass(frozen=True)
class PosterResult:
    image: bytes
    picks: list[str]
    analysis: str
    filename: str


def get_api_key() -> str:
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:  # hakuna secrets.toml
        key = ""
    return key or os.environ.get("GEMINI_API_KEY", "")


# ============================================================
# 2. MUONEKANO (CSS)
# ============================================================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    :root {
        --bg: #070b16; --card: rgba(255,255,255,.04); --line: rgba(255,255,255,.09);
        --green: #10b981; --blue: #38bdf8; --muted: #94a3b8;
    }
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp {
        background:
            radial-gradient(900px 500px at 10% -10%, rgba(16,185,129,.18), transparent 60%),
            radial-gradient(800px 500px at 100% 0%, rgba(56,189,248,.14), transparent 55%),
            var(--bg);
        color: #f8fafc;
    }
    header[data-testid="stHeader"], #MainMenu, footer, .stAppDeployButton { display: none; }

    .badge {
        display: inline-block; padding: 4px 14px; border-radius: 999px;
        font-size: .72rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;
        color: #fff; background: linear-gradient(135deg, #10b981, #059669);
    }
    .hero-title {
        margin: 10px 0 0; font-size: clamp(1.6rem, 4vw, 2.4rem); font-weight: 800; line-height: 1.15;
        background: linear-gradient(90deg, var(--green), var(--blue));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-sub { color: var(--muted); margin: 6px 0 22px; font-size: .95rem; }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--card); border: 1px solid var(--line) !important;
        border-radius: 16px; backdrop-filter: blur(8px);
    }
    .stButton > button[kind="primary"], .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: 0;
        border-radius: 12px; font-weight: 800; padding: .75rem 1.6rem;
        box-shadow: 0 6px 20px rgba(16,185,129,.35); transition: transform .15s ease, box-shadow .15s ease;
    }
    .stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px); box-shadow: 0 10px 26px rgba(16,185,129,.45); color: #fff;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# 3. GEMINI
# ============================================================
@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def build_prompt(day: str, date: str, count: int) -> str:
    return f"""
Wewe ni mchambuzi mkuu wa soka. Leo ni {day}, tarehe {date}.

MASHARTI:
1. Tumia TU mechi zinazoonekana kwenye screenshots zilizopakiwa.
2. Acha mechi zilizoanza, zilizoisha au za jana. Chagua zile ambazo bado hazijaanza.
3. Epuka mitego ya wazi (timu kubwa zenye uchovu, dabi, mechi zisizotabirika).
4. Toa picks {count} kamili. Kama mechi zinazofaa ni chache kuliko hizo, toa zilizopo tu.
5. Kila pick iwe fupi (jina la timu au chaguo, chini ya herufi 25).
6. full_analysis iwe Kiswahili, ikieleza kwa nini kila chaguo kimechaguliwa.
""".strip()


def analyse_matches(client: genai.Client, prompt: str, images: list[Image.Image]) -> SlipResult:
    """Jaribu models kwa mpangilio hadi mmoja ufanikiwe."""
    last_error: Exception | None = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=[prompt, *images],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SlipResult,
                    temperature=0.4,
                ),
            )
            if isinstance(response.parsed, SlipResult):
                return response.parsed
            if response.text:
                return SlipResult.model_validate_json(response.text)
        except Exception as exc:  # jaribu model inayofuata
            last_error = exc
    raise RuntimeError(f"Models zote zimeshindwa. Kosa la mwisho: {last_error}")


# ============================================================
# 4. PICHA / BANGO
# ============================================================
def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow ya zamani
        return ImageFont.load_default()


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int = 18):
    """Punguza herufi hadi maandishi yatoshee kwenye upana."""
    for size in range(start, minimum, -2):
        font = load_font(size)
        left, _, right, _ = draw.textbbox((0, 0), text, font=font)
        if right - left <= max_width:
            return font
    return load_font(minimum)


def make_background(size: tuple[int, int]) -> Image.Image:
    w, h = size
    if BACKGROUND_PHOTO.exists():
        photo = ImageOps.exif_transpose(Image.open(BACKGROUND_PHOTO)).convert("RGBA")
        photo = ImageOps.fit(photo, size, Image.Resampling.LANCZOS)
        photo = photo.filter(ImageFilter.GaussianBlur(2))
        photo = ImageEnhance.Brightness(photo).enhance(0.35)
        tint = Image.new("RGBA", size, (5, 150, 60, 160))
        return Image.alpha_composite(photo, tint)
    gradient = Image.linear_gradient("L").resize(size)
    return ImageOps.colorize(gradient, black=(0, 120, 45), white=(0, 205, 75)).convert("RGBA")


def make_poster(picks: list[str], title: str, date_label: str) -> bytes:
    w, h = POSTER_SIZE
    poster = make_background(POSTER_SIZE)
    draw = ImageDraw.Draw(poster)

    # Kichwa na tarehe
    title_font = fit_font(draw, title, w - 160, 78)
    draw.text((w // 2, 80), title, fill=(0, 0, 0), font=title_font, anchor="mt")
    draw.text((w // 2, 185), date_label, fill=(255, 255, 255), font=load_font(28), anchor="mt")

    # Mpangilio wa kadi (unajirekebisha kulingana na idadi)
    n = max(1, len(picks))
    top, reserved_bottom, gap = 260, 150, 36
    available = h - top - reserved_bottom
    card_h = min(130, (available - gap * (n - 1)) // n)
    block_h = n * card_h + (n - 1) * gap
    y0 = top + max(0, (available - block_h) // 2)
    cards = [(80, y0 + i * (card_h + gap), w - 80, y0 + i * (card_h + gap) + card_h) for i in range(n)]

    # Kivuli laini chini ya kadi
    shadow = Image.new("RGBA", POSTER_SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    for x1, y1, x2, y2 in cards:
        shadow_draw.rounded_rectangle((x1, y1 + 12, x2, y2 + 12), radius=26, fill=(0, 0, 0, 120))
    poster = Image.alpha_composite(poster, shadow.filter(ImageFilter.GaussianBlur(16)))
    draw = ImageDraw.Draw(poster)

    # Kadi nyeupe zenye nyota nyeusi
    for (x1, y1, x2, y2), pick in zip(cards, picks):
        draw.rounded_rectangle((x1, y1, x2, y2), radius=26, fill=(255, 255, 255))
        line = f"★  {pick}"
        font = fit_font(draw, line, (x2 - x1) - 80, 46)
        draw.text(((x1 + x2) // 2, (y1 + y2) // 2), line, fill=(0, 0, 0), font=font, anchor="mm")

    draw.text((w // 2, h - 70), "BETPRO TACTICAL SYNDICATE", fill=(255, 255, 255), font=load_font(26), anchor="mm")

    buffer = io.BytesIO()
    poster.convert("RGB").save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def prepare_images(files) -> list[Image.Image]:
    images = []
    for file in files:
        img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        images.append(img)
    return images


# ============================================================
# 5. UI
# ============================================================
now = datetime.now(TZ)
day_name = now.strftime("%A")
date_short = now.strftime("%d-%m-%Y")

st.markdown('<span class="badge">⚡ Viral Slip Terminal</span>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">BetPro Elite: Bango la Kisasa la Mitandaoni</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Pakia screenshot, AI inachambua, na unapata bango la vibao vyeupe lenye nyota na picha yako nyuma.</p>',
    unsafe_allow_html=True,
)

tab_slip, tab_scores = st.tabs(["📸 Kichambuzi cha Mechi", "⚽ LiveScores"])

# ---------------- TAB 1 ----------------
with tab_slip:
    with st.container(border=True):
        st.markdown(f"#### 🎯 Pakia Screenshot za Mechi · {day_name}, {date_short}")
        left, right = st.columns(2, gap="large")
        with left:
            uploaded = st.file_uploader(
                "Screenshot za mechi (unaweza kupakia nyingi)",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
            )
        with right:
            count = st.segmented_control(
                "Idadi ya mechi kwenye bango",
                options=list(PICK_COUNTS),
                format_func=PICK_COUNTS.get,
                default=4,
            ) or 4
            title = st.text_input("Kichwa cha bango (hiari)", value=f"{day_name} Picks")

    if uploaded:
        images = prepare_images(uploaded)
        with st.expander(f"📸 Picha zilizopakiwa ({len(images)})", expanded=False):
            st.image(images, width=150)

        if st.button("🚀 Unda Bango", type="primary", width="stretch"):
            api_key = get_api_key()
            if not api_key:
                st.error("GEMINI_API_KEY haipo kwenye Secrets. Iweke kwanza.")
            else:
                try:
                    with st.status("AI inachambua mechi...", expanded=True) as status:
                        st.write("Inasoma screenshots na kuchagua mechi bora...")
                        result = analyse_matches(
                            get_client(api_key),
                            build_prompt(day_name, date_short, count),
                            images,
                        )
                        picks = [p.strip() for p in result.picks if p.strip()][:count]
                        if not picks:
                            status.update(label="Hakuna mechi inayofaa", state="error")
                            st.warning("AI haikupata mechi inayofaa kwenye picha ulizopakia.")
                        else:
                            st.write("Inaunda bango...")
                            poster = make_poster(picks, title or f"{day_name} Picks", now.strftime("%d %B %Y"))
                            st.session_state["result"] = PosterResult(
                                image=poster,
                                picks=picks,
                                analysis=result.full_analysis,
                                filename=f"BetPro_{day_name}_Picks.png",
                            )
                            status.update(label="Bango liko tayari ✅", state="complete", expanded=False)
                except Exception as exc:
                    st.error(f"Hitilafu: {exc}")

    # Matokeo yanabaki hata baada ya kubonyeza download (session_state)
    result: PosterResult | None = st.session_state.get("result")
    if result:
        st.subheader("🖼️ Bango Lako")
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.image(result.image, width="stretch")
            st.download_button(
                "📥 Pakua Bango (PNG)",
                data=result.image,
                file_name=result.filename,
                mime="image/png",
                width="stretch",
            )
        with st.expander("📄 Uchambuzi kamili"):
            st.write(result.analysis)

# ---------------- TAB 2 ----------------
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
