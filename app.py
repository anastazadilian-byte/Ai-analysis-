import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from google import genai
import streamlit.components.v1 as components
from datetime import datetime
import io
import textwrap

# Usanidi wa Ukurasa wa Kipekee
st.set_page_config(
    page_title="BetPro Elite - Tactical Syndicate",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# KUSOMA API KEY KUTOKA KWENYE SECRETS
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Theme ya Kisasa
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { 
        background: #0b1120; 
        color: #f8fafc; 
    }
    
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
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub { color: #94a3b8; font-size: 0.95rem; margin-top: 5px; margin-bottom: 25px; }
    
    .box-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        color: #ffffff;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white; font-weight: 700; border: none; border-radius: 10px;
        padding: 0.7rem 1.6rem; transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #1d4ed8 100%);
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<span class="elite-badge">⚡ PRIVATE TACTICAL TERMINAL</span>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">BetPro Elite: Jicho la Kijasusi & Jenereta ya Picha za Mikeka</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Inachambua mechi na kutoa BANGO LA PICHA (PNG) lenye picha yako nyuma tayari kupostiwa WhatsApp Status na Facebook.</p>', unsafe_allow_html=True)

# Function ya Kuita AI kwa Kasi
def call_gemini_fast(client, contents):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=contents
        )
        return response.text
    except Exception:
        response = client.models.generate_content(
            model="gemini-3.8-flash", 
            contents=contents
        )
        return response.text

# Function ya Kutengeneza Picha ya Mkeka (Poster Generator yenye Background)
def create_slip_poster(text_content, bg_image=None):
    width, height = 1080, 1920  # Muundo wa WhatsApp Status & Story
    
    if bg_image:
        # Punguza mwangaza wa picha yako ili maandishi yasomeke wazi
        poster = bg_image.convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
        enhancer = ImageEnhance.Brightness(poster)
        poster = enhancer.enhance(0.25)  # Fanya iwe na giza la asilimia 75%
    else:
        # Kama hakuweka picha, tumia background ya giza ya kisasa
        poster = Image.new("RGBA", (width, height), color=(11, 17, 32, 255))
        
    draw = ImageDraw.Draw(poster)
    
    # Mistari na Kichwa
    draw.rectangle([(40, 40), (width - 40, height - 40)], outline=(56, 189, 248, 180), width=4)
    draw.rectangle([(50, 50), (width - 50, 200)], fill=(30, 41, 59, 220))
    
    # Jaribu kupata font, vinginevyo tumia default
    try:
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 52)
        font_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
        font_body = ImageFont.truetype("DejaVuSans.ttf", 26)
    except:
        font_header = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((70, 75), "⚡ BETPRO ELITE SYNDICATE", fill=(56, 189, 248), font=font_header)
    draw.text((70, 140), f"📅 RATIBA YA LEO: {datetime.now().strftime('%d-%m-%Y')} | VIP SLIP", fill=(245, 158, 11), font=font_sub)
    
    # Andika ujumbe wa mechi
    y_text = 240
    lines = text_content.split("\n")
    for line in lines:
        if y_text > height - 120:
            break
        wrapped = textwrap.wrap(line, width=55)
        for w in wrapped:
            if any(k in w for k in ["TIKETI", "TRENI", "SAFE", "ODDS", "CORRECT"]):
                color = (56, 189, 248)  # Bluu inayong'aa
            elif "✅" in w or "WON" in w or "95%" in w:
                color = (74, 222, 128)  # Kijani
            elif "⚠️" in w or "TRAP" in w:
                color = (248, 113, 113)  # Nyekundu
            else:
                color = (241, 245, 249)  # Nyeupe safi
                
            draw.text((70, y_text), w, fill=color, font=font_body)
            y_text += 36
        y_text += 8

    # Watermark chini
    draw.text((width // 2 - 180, height - 85), "👑 BETPRO TACTICAL ANALYST", fill=(148, 163, 184), font=font_sub)

    # Convert kwenda byte array kwa ajili ya kupakua
    buf = io.BytesIO()
    poster.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()

# TABS MBILI TU
tab1, tab2 = st.tabs([
    "📸 Kichambuzi cha Mechi & Jenereta ya Bango", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1: UCHAMBUZI & BANGO LA PICHA =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.markdown(f"""
    <div class="box-card">
        <h4 style="margin:0 0 6px 0; color:#38bdf8;">🎯 Pakia Screenshot za Mechi (Bila Kikomo - {today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Pakia screenshot za mechi. Matokeo yatakayotoka <b>yatatengenezwa kama PICHA (Banner)</b> ikiwa na picha yako nyuma, tayari kupakua na kuposti WhatsApp Status au Facebook!
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "1. Pakia Screenshot za Mechi:", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True,
            key="elite_unlimited_uploader"
        )
    with col2:
        custom_bg_file = st.file_uploader(
            "2. Weka Picha Yako ya Background ya Bango (Hiari):",
            type=["png", "jpg", "jpeg"],
            key="user_poster_bg"
        )
        
    col3, col4 = st.columns([1, 1])
    with col3:
        bet_objective = st.radio(
            "Chagua Mfumo:",
            [
                "🛡️ Mikeka 2 ya Uhakika (Tiketi 1 ya 2 Odds + Tiketi 2 ya Faida)",
                "🚂 Treni la Kisayansi (Mechi 10-20 Salama Zaidi - Mtaji Mdogo)"
            ]
        )
    with col4:
        user_stake = st.text_input("Mtaji Wako (Mfano: TZS 1,000 au 20,000):", value="TZS 2,000")

    if uploaded_files:
        st.write(f"📸 **Umeingiza Jumla ya Picha za Mechi:** {len(uploaded_files)}")
        processed_images = []
        cols = st.columns(min(len(uploaded_files), 4))
        for idx, file in enumerate(uploaded_files):
            img = Image.open(file).convert("RGB")
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            processed_images.append(img)
            with cols[idx % 4]:
                st.image(img, caption=f"Mechi {idx+1}", use_container_width=True)

        user_bg_img = None
        if custom_bg_file:
            user_bg_img = Image.open(custom_bg_file)
            st.image(user_bg_img, caption="Picha Itakayotumika Kama Background ya Bango", width=200)

        if st.button("🚀 Fanya Uchambuzi & Unda Picha ya Bango (Generate Poster)", key="btn_run_unlimited"):
            if not api_key:
                st.error("Hitilafu: GEMINI_API_KEY haipo kwenye Secrets! Hakikisha umeiweka.")
            else:
                with st.spinner("AI inachambua mechi zote na kuandaa picha ya bango..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (Master Betting Analyst).
                        Leo ni tarehe {today_str}. Mtaji wa mtumiaji: '{user_stake}'. Mfumo: '{bet_objective}'.

                        MASHARTI MAKUU:
                        1. TUPA KABISA mechi zilizoanza, zilizopita au za jana. Tumia mechi za leo au wikiendi ambazo HAZIJAANZA!
                        2. Taja timu kubwa zenye MTEGO (TRAP ALERTS) wa kuepuka.
                        """

                        if "Treni" in bet_objective:
                            prompt += f"""
                            LENGO: MKEKA WA TRENI LA KISAYANSI (Pesa Nyingi kwa Mtaji wa {user_stake}):
                            - Teua mechi 10 hadi 18 zenye machaguo SALAMA ZAIDI (92%+ confidence) kama Double Chance 1X/X2 au Over 1.5.
                            - Weka orodha fupi na nambari safi.
                            """
                        else:
                            prompt += f"""
                            LENGO: MIKEKA MIWILI TU YA UHAKIKA (Mtaji: {user_stake}):
                            - 🎫 TIKETI 1 (SAFE 2.00 ODDS - 95%+ PROBABILITY): Mechi 2 tu salama.
                            - 🚀 TIKETI 2 (ODDS 3.50 - 5.00): Mechi 2 au 3 zenye faida zilizolindwa.
                            - Mgao wa mtaji: 75% Tiketi 1, 25% Tiketi 2.
                            """

                        prompt += """
                        Mwishoni weka orodha safi yenye vichwa vya habari na emoji kwa ajili ya bango la picha!
                        """

                        contents = [prompt] + processed_images
                        result_text = call_gemini_fast(client, contents)
                        
                        st.success("✅ Uchambuzi Umekamilika!")
                        st.markdown(result_text)
                        
                        # TENGENEZA PICHA YA BANGO LA MKAKA
                        st.markdown("---")
                        st.subheader("🖼️ Bango Lako la Picha (Tayari kwa WhatsApp & Facebook)")
                        poster_bytes = create_slip_poster(result_text, user_bg_img)
                        st.image(poster_bytes, caption="Bango la Mkeka wa Leo (PNG Image)", use_container_width=True)
                        
                        # Kitufe cha kupakua picha moja kwa moja
                        st.download_button(
                            label="📥 Pakua Picha Hii ya Mkeka (Download Image PNG)",
                            data=poster_bytes,
                            file_name=f"BetPro_Poster_{today_str}.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: LIVESCORES =================
with tab2:
    today_str = datetime.now().strftime("%d-%m-%Y")
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
        scrolling=True
    )
