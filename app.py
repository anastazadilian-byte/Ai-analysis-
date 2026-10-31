import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime

# Usanidi wa Ukurasa wa Kipekee
st.set_page_config(
    page_title="BetPro Elite - Tactical Football Syndicate",
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
st.markdown('<p class="hero-title">BetPro Elite: Uchambuzi wa Kimbinu & Mikeka 2 ya Uhakika</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Uchambuzi wa mbinu za makocha, usomaji wa mitego ya mechi, na miundo inayovutia kwa ajili ya Facebook na WhatsApp.</p>', unsafe_allow_html=True)

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

# Tabs Mbili Tu
tab1, tab2 = st.tabs([
    "📸 Kichambuzi cha Mechi (Tiketi 2 za Uhakika)", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1: UCHAMBUZI & TIKETI 2 =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.markdown(f"""
    <div class="box-card">
        <h4 style="margin:0 0 6px 0; color:#38bdf8;">🎯 Pakia Screenshot za Mechi za Leo ({today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Pakia screenshot 1 au nyingi. AI itafanya uchambuzi wa kina hadi <b>mbinu za makocha na motisha ya wachezaji</b>, kisha itatoa <b>Tiketi 2 pekee zenye uhakika mkubwa</b> zilizopangwa tayari kupostiwa Facebook au WhatsApp!
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Pakia Screenshot 1 au Nyingi za Mechi:", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True,
            key="elite_uploader"
        )
    with col2:
        user_stake = st.text_input("Mtaji Wako wa Leo:", value="TZS 20,000")
        custom_notes = st.text_input(
            "Dokezo Lolote (Hiari):",
            placeholder="Mfano: Mshambuliaji ana majeraha, dabi ya kukata na shoka..."
        )

    if uploaded_files:
        st.write(f"📸 **Picha Zilizopakiwa:** {len(uploaded_files)}")
        processed_images = []
        cols = st.columns(min(len(uploaded_files), 4))
        for idx, file in enumerate(uploaded_files):
            img = Image.open(file).convert("RGB")
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            processed_images.append(img)
            with cols[idx % 4]:
                st.image(img, caption=f"Picha {idx+1}", use_container_width=True)

        if st.button("🚀 Fanya Uchambuzi wa Kimbinu & Tengeneza Tiketi 2", key="btn_run_elite"):
            if not api_key:
                st.error("Hitilafu: GEMINI_API_KEY haipo kwenye Secrets! Hakikisha umeiweka.")
            else:
                with st.spinner("AI inachambua mbinu za makocha, fomu, H2H na kuandaa Tiketi 2 za Uhakika..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka na Mtaalamu wa Mbinu za Makocha (Elite Tactical Betting Analyst).
                        Leo ni tarehe {today_str}. Mtaji wa mtumiaji kwa leo ni: '{user_stake}'. Maelezo: '{custom_notes}'.

                        KAZI YAKO KWENYE SCREENSHOT HIZI:
                        1. Kagua tarehe na masaa: TUPA KABISA mechi zilizoanza, zilizopita au za jana. Tumia mechi za leo ambazo HAZIJAANZA tu!
                        2. UCHAMBUZI WA KIMBINU WA MAKOCHA (TACTICAL BREAKDOWN):
                           - Eleza mbinu za makocha (kujilinda, kushambulia kwa kushtukiza, au kumiliki mpira).
                           - Motisha ya timu (nani anapigania heshima, ubingwa au kutoshuka daraja) na hali ya vyumbani.
                           - Taja wazi mechi yenye MTEGO (TRAP ALERT) ambapo timu kubwa inaweza kupoteza au kutoa sare.

                        3. TENGENEZA TIKETI MBILI TU ZILIZO SALAMA (2 ELITE SLIPS):
                        
                           🎫 **TIKETI 1: TIKETI YA CHUMA (SAFE 2.00 ODDS - UHAKIKA 95%+):**
                           - Chagua mechi 2 tu salama kabisa (mfano: Double Chance 1X/X2, Over 1.5 Goals, Draw No Bet).
                           - Hii tiketi ndiyo msingi mkuu wa kulinda mtaji usichanike kirahisi.

                           🚀 **TIKETI 2: TIKETI YA FAIDA & MBINU (ODDS 3.50 - 5.00):**
                           - Chagua mechi 2 au 3 zenye faida nzuri lakini zikiwa zimezingatia udhaifu wa makocha wapinzani.

                        4. UGAWAJI WA MTAJI KWA {user_stake}:
                           - Weka 75% ya mtaji kwenye Tiketi 1 (Kulinda mtaji).
                           - Weka 25% ya mtaji kwenye Tiketi 2 (Kutafuta faida).

                        5. 📱 **MUUNDO WA KUSHAWISHI KWA FACEBOOK & WHATSAPP (VIRAL SOCIAL MEDIA POST):**
                           Weka muhtasari mzuri sana mwishoni wenye vichwa vya kuvutia, emoji za soka, na maneno ya ushawishi ili mtumiaji aunakili (copy-paste) moja kwa moja kwenye kurasa za Facebook au magroup ya WhatsApp!
                        """
                        contents = [prompt] + processed_images
                        result_text = call_gemini_fast(client, contents)
                        st.success("✅ Uchambuzi wa Kimbinu na Tiketi 2 Zimekamilika!")
                        st.markdown(result_text)
                        
                        # Kitufe cha kupakua ujumbe wa Facebook/WhatsApp
                        st.download_button(
                            label="📋 Pakua / Nakili Muhtasari wa Facebook & WhatsApp",
                            data=result_text,
                            file_name=f"BetPro_Social_Ticket_{today_str}.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: LIVESCORES =================
with tab2:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"⚽ LiveScores & Ratiba ya Leo ({today_str})")
    st.write("Fuatilia mechi za leo mubashara, piga screenshot ya mechi unazotaka kisha weka kwenye Kichambuzi:")
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
