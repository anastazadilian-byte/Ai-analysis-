import io
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
from google import genai
from google.genai import types

# ---------------- Usanidi wa Ukurasa ----------------
st.set_page_config(
    page_title="BetPro Elite - Viral Slip Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

api_key = st.secrets.get("GEMINI_API_KEY", "")

# Saa za server mara nyingi ni UTC; tumia saa za kwako ili tarehe/siku iwe sahihi
TZ = ZoneInfo("Africa/Dar_es_Salaam")  # badilisha kama unahitaji

# Models zitajaribiwa kwa mpangilio huu (majina yote yanapaswa kuwa halali)
MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]

FONT_PATHS = [
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "arialbd.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]

PICK_OPTIONS = {
    "🔥 2 Odds za Uhakika (Mechi 2 Tu Zilizonyooka)": 2,
    "⭐ Mechi 4 Bora za Siku (Kama Muundo wa Picha Yako)": 4,
    "🚂 Treni Fupi la Uhakika (Mechi 6 Salama Zaidi)": 6,
}

# ---------------- Theme ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: #080d1a; color: #f8fafc; }
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stAppDeployButton { display: none; }
    .elite-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #fff; font-weight: 800; font-size: 0.75rem;
        padding: 4px 14px; border-radius: 20px; letter-spacing: 1px;
        margin-bottom: 8px; text-transform: uppercase;
    }
    .hero-title {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #10b981 0%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub { color: #94a3b8; font-size: 0.95rem; margin-top: 5px; margin-bottom: 25px; }
    .box-card {
        background: #131d31; border: 1px solid #1e293b; border-radius: 12px;
        padding: 16px; margin-bottom: 15px; color: #ffffff;
    }
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white; font-weight: 800; border: none; border-radius: 10px;
        padding: 0.75rem 1.8rem; transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<span class="elite-badge">⚡ VIRAL SLIP TERMINAL</span>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">BetPro Elite: Bango la Kisasa la Mitandaoni</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Inachambua mechi na kutoa bango la vibao vyeupe vyenye nyota na picha yako nyuma moja kwa moja.</p>',
    unsafe_allow_html=True,
)


# ---------------- Helpers ----------------
def show_image(data, **kwargs):
    """Inafanya kazi na Streamlit mpya (width='stretch') na ya zamani (use_container_width)."""
    try:
        st.image(data, width="stretch", **kwargs)
    except Exception:
        st.image(data, use_container_width=True, **kwargs)


def load_font(size):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)  # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def fit_font(draw, text, max_width, start_size, min_size=18):
    """Punguza ukubwa wa herufi hadi maandishi yatoshee kwenye upana."""
    size = start_size
    while size > min_size:
        font = load_font(size)
        box = draw.textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= max_width:
            return font
        size -= 2
    return load_font(min_size)


def call_gemini(client, contents):
    last_err = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4,
                ),
            )
            if response.text:
                return response.text
        except Exception as e:  # jaribu model inayofuata
            last_err = e
    raise RuntimeError(f"Models zote zimeshindwa. Kosa la mwisho: {last_err}")


def parse_ai_json(raw):
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None


def generate_strip_poster(picks_list, header_text):
    width, height = 1080, 1350

    # 1. Mandharinyuma
    if os.path.exists("profile.jpg"):
        bg = Image.open("profile.jpg")
        bg = ImageOps.exif_transpose(bg).convert("RGBA")
        bg = ImageOps.fit(bg, (width, height), Image.Resampling.LANCZOS)  # haipotoshi picha
        bg = bg.filter(ImageFilter.GaussianBlur(radius=2))
        bg = ImageEnhance.Brightness(bg).enhance(0.35)
        green_tint = Image.new("RGBA", (width, height), (5, 150, 60, 160))
        poster = Image.alpha_composite(bg, green_tint)
    else:
        poster = Image.new("RGBA", (width, height), (0, 195, 45, 255))

    draw = ImageDraw.Draw(poster)

    # 2. Kichwa
    f_header = fit_font(draw, header_text, width - 160, 75)
    draw.text((width // 2, 80), header_text, fill=(0, 0, 0), font=f_header, anchor="mt")

    # 3. Vibao vyeupe (vinajirekebisha kulingana na idadi ya picks)
    n = max(1, len(picks_list))
    top, bottom_reserved = 240, 160
    avail = height - top - bottom_reserved
    gap = 40
    strip_h = min(130, (avail - gap * (n - 1)) // n)
    total_h = n * strip_h + (n - 1) * gap
    start_y = top + max(0, (avail - total_h) // 2)

    for idx, item in enumerate(picks_list):
        y = start_y + idx * (strip_h + gap)
        draw.rectangle([(80, y), (width - 80, y + strip_h)], fill=(255, 255, 255))
        text_line = f"★  {item}"
        font = fit_font(draw, text_line, width - 240, 46)
        draw.text((width // 2, y + strip_h // 2), text_line, fill=(0, 0, 0), font=font, anchor="mm")

    # 4. Watermark (bila emoji, kwa sababu font haina emoji)
    f_sub = load_font(26)
    draw.text(
        (width // 2, height - 70),
        "BETPRO TACTICAL SYNDICATE",
        fill=(255, 255, 255),
        font=f_sub,
        anchor="mm",
    )

    buf = io.BytesIO()
    poster.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


# ---------------- Tabs ----------------
tab1, tab2 = st.tabs([
    "📸 Kichambuzi cha Mechi (Bango la Vibao Vyeupe)",
    "⚽ LiveScores & Ratiba ya Leo",
])

# ================= TAB 1 =================
with tab1:
    now = datetime.now(TZ)
    today_str = now.strftime("%d-%m-%Y")
    day_eng = now.strftime("%A")

    st.markdown(f"""
    <div class="box-card">
        <h4 style="margin:0 0 6px 0; color:#10b981;">🎯 Pakia Screenshot za Mechi ({day_eng} - {today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Pakia screenshot za mechi. AI itachambua na kutoa <b>Bango lenye Vibao Vyeupe na Nyota Nyeusi</b> ikiwa na picha yako nyuma, tayari kupakua na kuposti!
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Pakia Screenshot za Mechi (Ruhusa ya Picha Nyingi):",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="elite_unlimited_uploader",
        )
    with col2:
        bet_objective = st.selectbox("Idadi ya Mechi kwenye Bango:", list(PICK_OPTIONS.keys()))
        custom_title = st.text_input("Kichwa cha Bango (Hiari):", value=f"{day_eng} Picks")

    if uploaded_files:
        st.write(f"📸 **Umeingiza Jumla ya Picha:** {len(uploaded_files)}")
        processed_images = []
        cols = st.columns(min(len(uploaded_files), 4))
        for idx, file in enumerate(uploaded_files):
            img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            processed_images.append(img)
            with cols[idx % 4]:
                show_image(img, caption=f"Mechi {idx + 1}")

        if st.button("🚀 Unda Bango la Vibao Vyeupe (Generate Viral Slip)", key="btn_run_unlimited"):
            if not api_key:
                st.error("Hitilafu: GEMINI_API_KEY haipo kwenye Secrets! Hakikisha umeiweka.")
            else:
                num_picks = PICK_OPTIONS[bet_objective]
                with st.spinner("AI inachambua takwimu na kuunda bango..."):
                    try:
                        client = genai.Client(api_key=api_key)

                        prompt = f"""
                        Wewe ni mchambuzi mkuu wa soka.
                        Leo ni {day_eng}, tarehe {today_str}. Lengo: '{bet_objective}'.

                        MASHARTI:
                        1. Tumia TU mechi zinazoonekana kwenye screenshots zilizopakiwa.
                        2. Acha mechi ambazo zimeshaanza, zimeisha, au za jana. Chagua zile ambazo bado hazijaanza.
                        3. Epuka mitego ya wazi (timu kubwa zenye uchovu, dabi, mechi zisizotabirika).
                        4. Toa picks {num_picks} kamili. Kama mechi zinazofaa ni chache kuliko hizo, toa zile tu zilizopo.
                        5. Kila pick iwe fupi (jina la timu au chaguo, chini ya herufi 25).

                        Jibu kwa JSON tu, kwa muundo huu:
                        {{"picks": ["<chaguo 1>", "<chaguo 2>"], "full_analysis": "<uchambuzi wa kina kwa Kiswahili>"}}
                        """

                        contents = [prompt] + processed_images
                        result_raw = call_gemini(client, contents)
                        parsed = parse_ai_json(result_raw)

                        if not parsed or not isinstance(parsed.get("picks"), list):
                            st.error("AI haikurudisha majibu kwa muundo sahihi. Jaribu tena.")
                            with st.expander("Jibu ghafi la AI"):
                                st.write(result_raw)
                        else:
                            picks_list = [str(p).strip() for p in parsed["picks"] if str(p).strip()]
                            picks_list = picks_list[:num_picks]
                            analysis_text = parsed.get("full_analysis") or result_raw

                            if not picks_list:
                                st.warning("AI haikupata mechi inayofaa kwenye picha ulizopakia.")
                            else:
                                st.success("✅ Bango Limekamilika!")
                                poster_bytes = generate_strip_poster(picks_list, custom_title or f"{day_eng} Picks")

                                st.subheader("🖼️ Bango Lako (Tayari kwa WhatsApp & Facebook)")
                                show_image(poster_bytes, caption="Bango la Mitandaoni (PNG)")

                                st.download_button(
                                    label="📥 Pakua Picha Hii ya Bango (Download PNG)",
                                    data=poster_bytes,
                                    file_name=f"BetPro_{day_eng}_Picks.png",
                                    mime="image/png",
                                )

                                with st.expander("📄 Soma Uchambuzi Kamili"):
                                    st.write(analysis_text)

                    except Exception as e:
                        st.error(f"Hitilafu: {e}")

# ================= TAB 2: LIVESCORES =================
with tab2:
    today_str = datetime.now(TZ).strftime("%d-%m-%Y")
    st.subheader(f"⚽ LiveScores & Ratiba ya Leo ({today_str})")
    components.html(
        """
        <div style="border-radius:12px; overflow:hidden; border:1px solid #334155;">
            <iframe src="https://www.scorebat.com/embed/livescore/"
                    frameborder="0" width="100%" height="800"
                    style="width:100%;height:800px;border:none;background:#1e293b;">
            </iframe>
        </div>
        """,
        height=820,
        scrolling=True,
    )
