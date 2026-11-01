"""BetPro Elite - Viral Slip Generator (Uchambuzi wa Kina)

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
    image: bytes
    picks: list[Pick]
    slip: SlipResult
    report: str
    filename: str


def get_api_key() -> str:
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.environ.get("GEMINI_API_KEY", "")


# ============================================================
# 2. MUONEKANO
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
# 3. GEMINI: UCHAMBUZI WA HATUA MBILI
# ============================================================
@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


@st.cache_data(ttl=3600, show_spinner=False)
def available_models(_client: genai.Client) -> list[str]:
    """Models ambazo akaunti yako inaruhusiwa kuzitumia sasa hivi."""
    try:
        return [m.name.removeprefix("models/") for m in _client.models.list()]
    except Exception:
        return []


def generate(client: genai.Client, contents, config: types.GenerateContentConfig):
    """Jaribu models zinazopatikana kwa mpangilio hadi mmoja ufanikiwe."""
    names = available_models(client)
    candidates = [m for m in MODELS if m in names] or MODELS
    errors: list[str] = []
    for model in candidates:
        try:
            response = client.models.generate_content(model=model, contents=contents, config=config)
            if response.text or response.parsed:
                return response
            errors.append(f"{model}: jibu tupu")
        except Exception as exc:
            errors.append(f"{model}: {str(exc)[:250]}")
    raise RuntimeError("Models zote zimeshindwa:\n\n" + "\n\n".join(f"- {e}" for e in errors))


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


def research_matches(client: genai.Client, images: list[Image.Image], day: str, date: str) -> str:
    prompt = research_prompt(day, date)
    search_config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
    )
    try:
        return generate(client, [prompt, *images], search_config).text or ""
    except RuntimeError:
        # Quota ya utafutaji imeisha: jaribu bila mtandao, kwa tahadhari zaidi
        st.write("⚠️ Utafutaji wa mtandaoni umeshindikana (quota). Inaendelea bila mtandao, alama zitakuwa za tahadhari zaidi.")
        offline_note = (
            "\n\nONYO: Huna ufikiaji wa mtandao sasa. Tumia ujuzi wako tu. Kwa mechi ambazo huna taarifa za "
            "uhakika za majeruhi na fomu ya sasa, toa alama ya usalama ya chini na sema wazi kwamba haijathibitishwa."
        )
        plain_config = types.GenerateContentConfig(temperature=0.2)
        return generate(client, [prompt + offline_note, *images], plain_config).text or ""


def select_picks(client: genai.Client, report: str, count: int, min_conf: int) -> SlipResult:
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=SlipResult,
        temperature=0.2,
    )
    response = generate(client, selection_prompt(report, count, min_conf), config)
    if isinstance(response.parsed, SlipResult):
        return response.parsed
    return SlipResult.model_validate_json(response.text)


# ============================================================
# 4. PICHA / BANGO
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


def make_background(size: tuple[int, int]) -> Image.Image:
    if BACKGROUND_PHOTO.exists():
        photo = ImageOps.exif_transpose(Image.open(BACKGROUND_PHOTO)).convert("RGBA")
        photo = ImageOps.fit(photo, size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(2))
        photo = ImageEnhance.Brightness(photo).enhance(0.35)
        return Image.alpha_composite(photo, Image.new("RGBA", size, (5, 150, 60, 160)))
    gradient = Image.linear_gradient("L").resize(size)
    return ImageOps.colorize(gradient, black=(0, 120, 45), white=(0, 205, 75)).convert("RGBA")


def make_poster(labels: list[str], title: str, date_label: str) -> bytes:
    w, h = POSTER_SIZE
    poster = make_background(POSTER_SIZE)
    draw = ImageDraw.Draw(poster)

    draw.text((w // 2, 80), title, fill=(0, 0, 0), font=fit_font(draw, title, w - 160, 78), anchor="mt")
    draw.text((w // 2, 185), date_label, fill=(255, 255, 255), font=load_font(28), anchor="mt")

    n = max(1, len(labels))
    top, reserved_bottom, gap = 260, 150, 36
    available = h - top - reserved_bottom
    card_h = min(130, (available - gap * (n - 1)) // n)
    block_h = n * card_h + (n - 1) * gap
    y0 = top + max(0, (available - block_h) // 2)
    cards = [(80, y0 + i * (card_h + gap), w - 80, y0 + i * (card_h + gap) + card_h) for i in range(n)]

    shadow = Image.new("RGBA", POSTER_SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    for x1, y1, x2, y2 in cards:
        shadow_draw.rounded_rectangle((x1, y1 + 12, x2, y2 + 12), radius=26, fill=(0, 0, 0, 120))
    poster = Image.alpha_composite(poster, shadow.filter(ImageFilter.GaussianBlur(16)))
    draw = ImageDraw.Draw(poster)

    for (x1, y1, x2, y2), label in zip(cards, labels):
        draw.rounded_rectangle((x1, y1, x2, y2), radius=26, fill=(255, 255, 255))
        line = f"★  {label}"
        draw.text(
            ((x1 + x2) // 2, (y1 + y2) // 2), line, fill=(0, 0, 0),
            font=fit_font(draw, line, (x2 - x1) - 80, 46), anchor="mm",
        )

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

    if uploaded:
        images = prepare_images(uploaded)
        with st.expander(f"📸 Picha zilizopakiwa ({len(images)})"):
            st.image(images, width=150)

        if st.button("🚀 Chambua na Unda Bango", type="primary", width="stretch"):
            api_key = get_api_key()
            if not api_key:
                st.error("GEMINI_API_KEY haipo kwenye Secrets. Iweke kwanza.")
            else:
                try:
                    client = get_client(api_key)
                    with st.status("Uchambuzi wa kina unaendelea (inaweza kuchukua dakika 1-2)...", expanded=True) as status:
                        st.write("🔎 Hatua 1: Inasoma mechi na kutafuta fomu, majeruhi, motisha na takwimu za sasa...")
                        report = research_matches(client, images, day_name, date_short)

                        st.write("🎯 Hatua 2: Inachuja na kuchagua mechi bora tu...")
                        slip = select_picks(client, report, count, min_conf)
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
                            poster = make_poster(
                                [p.label for p in picks], title or f"{day_name} Picks", now.strftime("%d %B %Y")
                            )
                            st.session_state["result"] = PosterResult(
                                image=poster, picks=picks, slip=slip, report=report,
                                filename=f"BetPro_{day_name}_Picks.png",
                            )
                            status.update(label="Bango liko tayari ✅", state="complete", expanded=False)
                except Exception as exc:
                    st.error(f"Hitilafu: {exc}")

        st.caption("Hakuna mechi yenye uhakika wa 100%. AI inapunguza hatari, haiiondoi. Weka kiasi unachoweza kukipoteza.")

    result: PosterResult | None = st.session_state.get("result")
    if result:
        st.subheader("🖼️ Bango Lako")
        poster_col, detail_col = st.columns([1, 1.2], gap="large")
        with poster_col:
            st.image(result.image, width="stretch")
            st.download_button(
                "📥 Pakua Bango (PNG)", data=result.image, file_name=result.filename,
                mime="image/png", width="stretch",
            )
        with detail_col:
            st.markdown("#### 📊 Uchambuzi wa Kila Chaguo")
            for pick in result.picks:
                with st.container(border=True):
                    st.markdown(f"**★ {pick.label}** · {pick.match}")
                    st.progress(min(max(pick.confidence, 0), 100) / 100, text=f"Usalama: {pick.confidence}% · Hatari: {pick.risk}")
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
