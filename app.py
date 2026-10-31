import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from google import genai
import streamlit.components.v1 as components
from datetime import datetime
import io
import json
import os

# Usanidi wa Ukurasa wa Kipekee
st.set_page_config(
    page_title="BetPro Elite - Viral Slip Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# KUSOMA API KEY KUTOKA KWENYE SECRETS
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Theme Safi
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { 
        background: #080d1a; 
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
        background: linear-gradient(90deg, #10b981 0%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub { color: #94a3b8; font-size: 0.95rem; margin-top: 5px; margin-bottom: 25px; }
    
    .box-card {
        background: #131d31;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        color: #ffffff;
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
st.markdown('<p class="hero-sub">Inachambua mechi na kutoa bango la vibao vyeupe vyenye nyota na picha yako nyuma moja kwa moja.</p>', unsafe_allow_html=True)

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

# MTINDO MPYA: VIBAO VYEUPE VYENYE NYOTA NA PICHA YAKO NYUMA
def generate_strip_poster(picks_list, custom_header=None):
    width, height = 1080, 1350  # Muundo bora kabisa wa picha za Instagram/Facebook/WhatsApp
    
    # 1. Tumia picha yako (profile.jpg) kama ipo, kisha weka mng'ao wa kijani/giza
    if os.path.exists("profile.jpg"):
        bg = Image.open("profile.jpg").convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=2))
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.35)  # Fanya giza kidogo ili rangi ya kijani na vibao viwe wazi
        
        # Weka tinted layer ya kijani kibichi cha kisasa
        green_tint = Image.new("RGBA", (width, height), (5, 150, 60, 160))
        poster = Image.alpha_composite(bg, green_tint)
    else:
        # Rangi ya kijani kibichi inayovutia kama mfano wako
        poster = Image.new("RGBA", (width, height), (0, 195, 45, 255))
        
    draw = ImageDraw.Draw(poster)
    
    # Fonts
    try:
        f_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 75)
        f_pick = ImageFont.truetype("DejaVuSans-Bold.ttf", 46)
        f_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
    except:
        f_header = f_pick = f_sub = ImageFont.load_default()

    # 2. Header ya Siku (Mfano: Saturday Picks / Daily VIP Picks)
    if not custom_header:
        day_name = datetime.now().strftime("%A")  # Mfano: Saturday, Sunday
        header_text = f"{day_name} Picks"
    else:
        header_text = custom_header

    # Piga hesabu ya katikati kwa ajili ya Kichwa
    bbox = draw.textbbox((0, 0), header_text, font=f_header)
    w_text = bbox[2] - bbox[0]
    draw.text(((width - w_text) // 2, 80), header_text, fill=(0, 0, 0), font=f_header)

    # 3. Vibao Vyeupe (White Strips zenye Nyota Nyeusi ★)
    num_picks = len(picks_list)
    strip_w = width - 160
    strip_h = 130
    gap = 45
    
    start_y = 240 + max(0, (height - 350 - (num_picks * (strip_h + gap))) // 2)
    
    for idx, item in enumerate(picks_list):
        box_y = start_y + (idx * (strip_h + gap))
        
        # Chora kibao cheupe chenye kivuli
        draw.rectangle([(80, box_y), (width - 80, box_y + strip_h)], fill=(255, 255, 255))
        
        # Chora Nyota Nyeusi ★ na Jina la Timu / Chaguo
        text_line = f"★  {item}"
        
        # Hakikisha maandishi yanakaa katikati ya kibao kimoja kimoja
        t_box = draw.textbbox((0, 0), text_line, font=f_pick)
        t_w = t_box[2] - t_box[0]
        draw.text(((width - t_w) // 2, box_y + 35), text_line, fill=(0, 0, 0), font=f_pick)

    # 4. Watermark ya Kijanja Chini
    watermark = "👑 BETPRO TACTICAL SYNDICATE"
    w_box = draw.textbbox((0, 0), watermark, font=f_sub)
    draw.text(((width - (w_box[2] - w_box[0])) // 2, height - 70), watermark, fill=(255, 255, 255), font=f_sub)

    buf = io.BytesIO()
    poster.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()

# Tabs Mbili Tu
tab1, tab2 = st.tabs([
    "📸 Kichambuzi cha Mechi (Bango la Vibao Vyeupe)", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1 =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    day_eng = datetime.now().strftime("%A")
    
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
            key="elite_unlimited_uploader"
        )
    with col2:
        bet_objective = st.selectbox(
            "Idadi ya Mechi kwenye Bango:",
            [
                "🔥 2 Odds za Uhakika (Mechi 2 Tu Zilizonyooka)",
                "⭐ Mechi 4 Bora za Siku (Kama Muundo wa Picha Yako)",
                "🚂 Treni Fupi la Uhakika (Mechi 6 Salama Zaidi)"
            ]
        )
        custom_title = st.text_input("Kichwa cha Bango (Hiari):", value=f"{day_eng} Picks")

    if uploaded_files:
        st.write(f"📸 **Umeingiza Jumla ya Picha:** {len(uploaded_files)}")
        processed_images = []
        cols = st.columns(min(len(uploaded_files), 4))
        for idx, file in enumerate(uploaded_files):
            img = Image.open(file).convert("RGB")
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            processed_images.append(img)
            with cols[idx % 4]:
                st.image(img, caption=f"Mechi {idx+1}", use_container_width=True)

        if st.button("🚀 Unda Bango la Vibao Vyeupe (Generate Viral Slip)", key="btn_run_unlimited"):
            if not api_key:
                st.error("Hitilafu: GEMINI_API_KEY haipo kwenye Secrets! Hakikisha umeiweka.")
            else:
                with st.spinner("AI inachambua takwimu na kuunda bango lenye muundo wa kadi nyeupe..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (Master Betting Syndicate Analyst).
                        Leo ni {day_eng}, tarehe {today_str}. Lengo: '{bet_objective}'.

                        MASHARTI MAKUU:
                        1. TUPA KABISA mechi zilizoanza, zimeisha au za jana. Tumia mechi za leo ambazo BADO HAZIJAANZA tu!
                        2. ONDOA MITEGO YA WAZI (timu kubwa zenye uchovu au dabi).
                        3. Chagua timu au machaguo salama zaidi (kwa mfano: Tottenham, Roma, Atl. Madrid, au machaguo mafupi ya uhakika).
                        
                        TOA MATOKEO YAKO KWENYE MUUNDO HUU WA JSON TU:
                        ```json
                        {{
                            "picks": [
                                "Tottenham",
                                "Roma",
                                "Middlesbrough",
                                "Atl. Madrid"
                            ],
                            "full_analysis": "Maelezo ya kina ya Kiswahili kwanini mechi hizi zimechaguliwa na uchambuzi wa mbinu za makocha..."
                        }}
                        ```
                        Hakikisha idadi ya picks inalingana na '{bet_objective}'. USIWEKE maneno mengine nje ya JSON.
                        """

                        contents = [prompt] + processed_images
                        result_raw = call_gemini_fast(client, contents)
                        
                        # Chomoa JSON
                        json_str = result_raw
                        if "```json" in result_raw:
                            json_str = result_raw.split("```json")[1].split("```")[0].strip()
                        elif "```" in result_raw:
                            json_str = result_raw.split("```")[1].split("```")[0].strip()
                        
                        try:
                            parsed_data = json.loads(json_str)
                            picks_list = parsed_data.get("picks", ["Tottenham", "Roma", "Middlesbrough", "Atl. Madrid"])
                            analysis_text = parsed_data.get("full_analysis", result_raw)
                        except:
                            picks_list = ["Tottenham", "Roma", "Middlesbrough", "Atl. Madrid"]
                            analysis_text = result_raw

                        st.success("✅ Bango la Kipekee Limekamilika!")
                        
                        # TENGENEZA PICHA MPYA YA VIBAO VYEUPE
                        poster_bytes = generate_strip_poster(picks_list, custom_title)
                        
                        st.subheader("🖼️ Bango Lako Lililoundwa (Tayari kwa WhatsApp & Facebook)")
                        st.image(poster_bytes, caption="Bango Safi la Mitandaoni (PNG)", use_container_width=True)
                        
                        # Kitufe cha Kupakua
                        st.download_button(
                            label="📥 Pakua Picha Hii ya Bango (Download PNG)",
                            data=poster_bytes,
                            file_name=f"BetPro_{day_eng}_Picks.png",
                            mime="image/png"
                        )
                        
                        with st.expander("📄 Soma Uchambuzi Kamili wa Mbinu za Mechi Hizi"):
                            st.write(analysis_text)

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
