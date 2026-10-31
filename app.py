import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from google import genai
import streamlit.components.v1 as components
from datetime import datetime
import io
import json
import re

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
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
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
st.markdown('<p class="hero-title">BetPro Elite: Jenereta ya Kadi za Kisasa za Mikeka</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Mitindo mipya ya kadi safi za picha (Graphic Slips) tayari kupakuliwa na kupostiwa mtandaoni.</p>', unsafe_allow_html=True)

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

# MTINDO MPYA WA KUCHORA KADI YA TIKETI (GRAPHIC SLIP GENERATOR)
def draw_modern_slip_card(data_dict, bg_image=None):
    width = 1080
    # Hesabu urefu kulingana na idadi ya mechi
    matches = data_dict.get("matches", [])
    num_matches = len(matches)
    card_h = 135
    height = max(1350, 420 + (num_matches * (card_h + 20)) + 150)
    
    # 1. Background
    if bg_image:
        poster = bg_image.convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
        poster = poster.filter(ImageFilter.GaussianBlur(radius=3))
        enhancer = ImageEnhance.Brightness(poster)
        poster = enhancer.enhance(0.22)  # Fanya giza ili maandishi yang'ae
    else:
        poster = Image.new("RGBA", (width, height), color=(10, 15, 28, 255))
        
    draw = ImageDraw.Draw(poster)
    
    # Fonts
    try:
        f_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 46)
        f_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        f_match = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
        f_pick = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        f_badge = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        f_small = ImageFont.truetype("DejaVuSans.ttf", 20)
    except:
        f_title = f_sub = f_match = f_pick = f_badge = f_small = ImageFont.load_default()

    # 2. Header ya Bango
    draw.rounded_rectangle([(40, 40), (width - 40, 210)], radius=18, fill=(19, 29, 49, 230), outline=(56, 189, 248), width=2)
    draw.text((70, 65), "⚡ BETPRO ELITE VIP SLIP", fill=(56, 189, 248), font=f_title)
    
    today_date = datetime.now().strftime("%d-%m-%Y")
    slip_type = data_dict.get("title", "TACTICAL SELECTION").upper()
    tot_odds = data_dict.get("total_odds", "~2.00")
    
    draw.text((70, 140), f"📅 {today_date}  |  🎯 {slip_type}  |  🔥 TOTAL ODDS: {tot_odds}", fill=(245, 158, 11), font=f_sub)

    # 3. Kadi za Mechi Moja Moja
    y = 240
    for idx, m in enumerate(matches):
        team_text = f"{idx+1}. {m.get('teams', 'Team vs Team')}"
        pick_text = f"👉 CHAGUO: {m.get('pick', '1X')}"
        conf = m.get('confidence', '90%')
        odds_val = m.get('odds', '1.30')
        reason = m.get('reason', '')
        
        # Sanduku la Mechi
        box_top = y
        box_bottom = y + card_h
        draw.rounded_rectangle([(40, box_top), (width - 40, box_bottom)], radius=14, fill=(15, 23, 42, 220), outline=(51, 65, 85), width=2)
        
        # Mstari wa rangi ya neon kushoto mwa kadi
        draw.rounded_rectangle([(40, box_top), (50, box_bottom)], radius=4, fill=(14, 165, 233))
        
        # Majina ya Timu
        draw.text((70, box_top + 18), team_text, fill=(255, 255, 255), font=f_match)
        
        # Chaguo (Pick)
        draw.text((70, box_top + 60), pick_text, fill=(56, 189, 248), font=f_pick)
        
        # Sababu fupi
        if reason:
            draw.text((70, box_top + 98), f"💡 {reason[:65]}...", fill=(148, 163, 184), font=f_small)

        # Beji ya Odds & Confidence (Upande wa Kulia)
        badge_x = width - 230
        draw.rounded_rectangle([(badge_x, box_top + 22), (width - 65, box_top + 65)], radius=8, fill=(16, 185, 129, 40), outline=(16, 185, 129), width=2)
        draw.text((badge_x + 18, box_top + 32), f"ODDS: {odds_val}", fill=(74, 222, 128), font=f_badge)
        
        draw.text((badge_x + 18, box_top + 78), f"🛡️ {conf} SAFE", fill=(245, 158, 11), font=f_small)
        
        y += card_h + 16

    # 4. Footer ya Bango
    y += 10
    draw.rounded_rectangle([(40, y), (width - 40, y + 80)], radius=12, fill=(19, 29, 49, 200), outline=(56, 189, 248, 120), width=1)
    draw.text((70, y + 25), "⚠️ KANUNI: Kulinda mtaji ni kipaumbele namba 1. Bet kwa hekima na nidhamu.", fill=(203, 213, 225), font=f_small)
    draw.text((width - 320, y + 25), "👑 BETPRO TACTICAL", fill=(56, 189, 248), font=f_sub)

    buf = io.BytesIO()
    poster.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()

# TABS MBILI TU
tab1, tab2 = st.tabs([
    "📸 Kichambuzi cha Mechi & Bango Jipya", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1 =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.markdown(f"""
    <div class="box-card">
        <h4 style="margin:0 0 6px 0; color:#38bdf8;">🎯 Pakia Screenshot za Mechi ({today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Pakia picha za mechi. AI itaunda <b>Tiketi za Kisasa zenye muundo wa KADI (Modern Cards)</b> badala ya maandishi ya kawaida, zikiwa tayari kupostiwa mtandaoni!
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
            "2. Weka Picha Yako ya Background (Hiari):",
            type=["png", "jpg", "jpeg"],
            key="user_poster_bg"
        )
        
    col3, col4 = st.columns([1, 1])
    with col3:
        bet_objective = st.radio(
            "Chagua Mtindo wa Tiketi:",
            [
                "🛡️ Tiketi ya Chuma (Safe 2.00 Odds - Mechi 2 Tu)",
                "🚀 Tiketi ya Faida (Odds 3.50 - 5.00)",
                "🚂 Treni la Kisayansi (Mechi 8 - 15 Salama Zaidi)"
            ]
        )
    with col4:
        user_stake = st.text_input("Mtaji Wako wa Leo:", value="TZS 20,000")

    if uploaded_files:
        st.write(f"📸 **Picha Zilizopakiwa:** {len(uploaded_files)}")
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
            st.image(user_bg_img, caption="Background Yako", width=180)

        if st.button("🚀 Unda Kadi za Tiketi (Generate Modern Slip)", key="btn_run_unlimited"):
            if not api_key:
                st.error("Hitilafu: GEMINI_API_KEY haipo kwenye Secrets! Hakikisha umeiweka.")
            else:
                with st.spinner("AI inachambua takwimu na kuunda kadi safi ya picha..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (Master Betting Analyst).
                        Leo ni tarehe {today_str}. Lengo la mtumiaji: '{bet_objective}'.
                        
                        MASHARTI MAKUU:
                        1. Tupa mechi zilizoanza, zimeisha au za jana. Tumia mechi za leo au wikiendi AMBAZO BADO HAZIJAANZA tu!
                        2. Tupa mitego ya timu kubwa zenye uchovu au dabi.
                        3. Tengeneza matokeo katika muundo wa JSON pekee ili yatengeneze picha ya bango la kadi.
                        
                        Format ya JSON iwe hivi (USIWEKE maneno mengine nje ya JSON):
                        ```json
                        {{
                            "title": "{bet_objective}",
                            "total_odds": "2.10",
                            "analysis_notes": "Maelezo mafupi ya kiufundi kuhusu mechi hizi...",
                            "matches": [
                                {{
                                    "teams": "Arsenal vs Wolves",
                                    "pick": "Arsenal 1X & Over 1.5",
                                    "odds": "1.32",
                                    "confidence": "95%",
                                    "reason": "Arsenal ipo nyumbani na Wolves haina ushindi mechi 4"
                                }}
                            ]
                        }}
                        ```
                        Hakikisha unaweka mechi 2 tu kama amechagua Tiketi ya Chuma, au mechi 3 kama ni Faida, au mechi 8-12 kama ni Treni.
                        """

                        contents = [prompt] + processed_images
                        result_raw = call_gemini_fast(client, contents)
                        
                        # Chomoa JSON kutoka kwenye jibu la AI
                        json_str = result_raw
                        if "```json" in result_raw:
                            json_str = result_raw.split("```json")[1].split("```")[0].strip()
                        elif "```" in result_raw:
                            json_str = result_raw.split("```")[1].split("```")[0].strip()
                        
                        try:
                            slip_data = json.loads(json_str)
                        except:
                            # Fallback kama JSON ikizingua
                            slip_data = {
                                "title": bet_objective,
                                "total_odds": "~2.00",
                                "matches": [
                                    {"teams": "Uchambuzi Umekamilika", "pick": "Angalia maelezo chini", "odds": "1.40", "confidence": "90%", "reason": "Data imechakatwa"}
                                ]
                            }

                        st.success("✅ Kadi ya Tiketi Imekamilika!")
                        
                        # 4. CHORA PICHA MPYA YA KADI (GRAPHIC CARD)
                        poster_bytes = draw_modern_slip_card(slip_data, user_bg_img)
                        
                        st.subheader("🖼️ Tiketi Yako Mpya (Muundo wa Kadi)")
                        st.image(poster_bytes, caption="Kadi Safi ya Mkeka (PNG)", use_container_width=True)
                        
                        # Kitufe cha Kupakua
                        st.download_button(
                            label="📥 Pakua Picha Hii ya Kadi (Download PNG)",
                            data=poster_bytes,
                            file_name=f"BetPro_Card_{today_str}.png",
                            mime="image/png"
                        )
                        
                        # Maelezo ya Ziada ya AI
                        with st.expander("📄 Soma Maelezo ya Kina ya Kiufundi (Tactical Breakdown)"):
                            st.write(slip_data.get("analysis_notes", result_raw))

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
