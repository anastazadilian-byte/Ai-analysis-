import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime

# Usanidi wa Ukurasa wa Kipekee (Admin Terminal)
st.set_page_config(
    page_title="BetPro Elite - Kituo cha Kijasusi cha Soka",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# KUSOMA API KEY KUTOKA KWENYE SECRETS
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Theme ya Kisasa, Nyepesi na Safi
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { 
        background: #0b1120; 
        color: #f8fafc; 
    }
    
    /* Ficha Alama za Streamlit na Header */
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

st.markdown('<span class="elite-badge">⚡ PRIVATE SYNDICATE TERMINAL</span>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">BetPro Elite: Jicho la Kijasusi cha Soka</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Uchambuzi Kabambe wa Kulinda Mtaji, Mitego ya Mechi, na Uundaji wa Mikeka ya Uhakika (WhatsApp Ready).</p>', unsafe_allow_html=True)

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

# TABS MBILI TU: UCHAMBUZI NA LIVESCORE
tab1, tab2 = st.tabs([
    "📸 Kichambuzi cha Mechi (Mikeka 3 ya Uhakika)", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1: UCHAMBUZI KABAMBE =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.markdown(f"""
    <div class="box-card">
        <h4 style="margin:0 0 6px 0; color:#38bdf8;">🎯 Pakia Screenshot za Mechi za Leo ({today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Pakia screenshot 1 au nyingi kwa pamoja. AI itakagua kila kitu kwa kina 1000% na kukupa: 
            <b>Tiketi 1 (Safe 2 Odds)</b>, <b>Tiketi 2 (Multiplier)</b>, na <b>Tiketi 3 (Correct Score Mechi 2 Tu)</b> pamoja na maandishi safi ya kurusha WhatsApp.
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
            "Dokezo Lolote la Ziada (Hiari):",
            placeholder="Mfano: Mshambuliaji fulani yupo benchi, zingatia ligi kuu..."
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

        if st.button("🚀 Anza Uchambuzi Kabambe (Chuja Mitego & Unda Mikeka)", key="btn_run_elite"):
            if not api_key:
                st.error("Hitilafu: GEMINI_API_KEY haipo kwenye Secrets! Hakikisha umeiweka.")
            else:
                with st.spinner("AI inachambua picha zote, inatupa mechi zilizochezwa, na kupanga mikeka 3 ya uhakika..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (Master Football Betting Syndicate Analyst).
                        Leo ni tarehe {today_str}. Mtaji wa mtumiaji kwa leo ni: '{user_stake}'. Maelezo ya ziada: '{custom_notes}'.
                        
                        KANUNI KUU YA MTUMIAJI: "ANATAKA KULINDA MTAJI KWA 100%, HATAKI KUPOTEZA PESA, ANATAKA FAIDA NDOGO NDOGO ZA UHAKIKA WA JUU SANA."

                        KAZI YAKO KWENYE PICHA HIZI ZOTE:
                        1. KAGUA MUDA & TAREHE: Ondoa kabisa mechi ambazo zimeshaanza, zimeisha (Full Time), au za jana. Tumia mechi zijazo za leo pekee!
                        2. ⚠️ ONDOA MITEGO YA WAZI (TRAP ALERTS): Taja timu yoyote kubwa kwenye picha hizi ambayo imepewa odds ndogo lakini ina mtego wa kupoteza alama kwa sababu ya uchovu au dabi.
                        
                        3. TENGENEZA MIKEKA MITATU (3 ELITE SLIPS):
                        
                           🎫 **TIKETI 1: TIKETI YA CHUMA (SAFE 2 ODDS - UHAKIKA 95%+):**
                           - Chagua mechi 2 tu salama kabisa (mfano: Double Chance 1X/X2, Over 1.5 Goals, Draw No Bet).
                           - Lengo: Kulinda mtaji wako usipotee.

                           🚀 **TIKETI 2: TIKETI YA FAIDA (MULTIPLIER - ODDS 4.00 HADI 6.00):**
                           - Chagua mechi 3 zilizochujwa vizuri zenye faida ya ziada lakini zikiwa na kinga thabiti.
                           - Lengo: Kukuza mtaji taratibu.

                           🎯 **TIKETI 3: VIP CORRECT SCORE (MECHI 2 TU PEKEE!):**
                           - Teua MECHI 2 TU zenye nafasi kubwa zaidi ya kutoa matokeo kamili kulingana na safu ya ulinzi na ufungaji (xG).
                           - Kwa kila mechi taja Matokeo Makuu (Primary Score) na Matokeo ya Kinga (Cover Score).

                        4. 💰 **MGAO WA PESA KISAYANSI (KWA MTAJI WA {user_stake}):**
                           - Piga hesabu ya pesa ya kuweka Tiketi 1 (70% ya mtaji).
                           - Piga hesabu ya pesa ya kuweka Tiketi 2 (20% ya mtaji).
                           - Piga hesabu ya pesa ya kuweka Tiketi 3 (10% tu ya mtaji).
                           - Eleza kwanini mfumo huu unamlinda asipoteze pesa zote hata kama tiketi nyingine zikikosa!

                        5. 📲 **FOMU YA WHATSAPP (WHATSAPP READY FORMAT):**
                           Mwishoni kabisa, weka muhtasari mfupi wenye emoji safi unaosomeka kwa urahisi ili mtumiaji aunakili (copy-paste) moja kwa moja kwenye magroup ya WhatsApp!
                        """
                        contents = [prompt] + processed_images
                        result_text = call_gemini_fast(client, contents)
                        st.success("✅ Uchambuzi Kabambe Umekamilika!")
                        st.markdown(result_text)
                        
                        # Kitufe cha kupakua ripoti ya WhatsApp
                        st.download_button(
                            label="📋 Pakua / Nakili Muhtasari wa WhatsApp",
                            data=result_text,
                            file_name=f"BetPro_WhatsApp_Slip_{today_str}.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: LIVESCORES =================
with tab2:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"⚽ LiveScores & Ratiba ya Leo ({today_str})")
    st.write("Fuatilia mechi za leo, piga screenshot ya orodha ya mechi unazotaka kisha weka kwenye Kichambuzi:")
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
