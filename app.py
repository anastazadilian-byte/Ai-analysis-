import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime

MODEL_NAME = "gemini-3.8-flash"

# Usanidi wa Ukurasa wa Kisasa
st.set_page_config(
    page_title="BetPro AI - Kikosi cha Kijasusi cha Soka",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling ya Kisasa (CSS & Fonts za Kisasa)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #0d1117;
        color: #f0f6fc;
    }
    
    /* Header yenye Gradient */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .hero-sub {
        color: #8b949e;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    
    /* Kadi za kisasa */
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
    }
    
    /* Vitufe vyenye mtindo wa Neon */
    .stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: 0.3s;
        box-shadow: 0 4px 14px rgba(46, 160, 67, 0.35);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 6px 20px rgba(63, 185, 80, 0.5);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Kichwa cha Programu
st.markdown('<p class="hero-title">⚽ BetPro AI: Jicho la Kijasusi cha Soka</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Uchambuzi wa kina, ugunduzi wa mitego ya Odds, na usomaji wa timu zilizo SIRIASI kupambana (80%+ Probability).</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Usanidi wa AI")
    api_key = st.text_input("Gemini API Key:", type="password", help="Weka API Key yako ya Google Gemini hapa.")
    st.markdown("---")
    st.markdown("""
    **💡 Sifa Kuu:**
    - 🎯 **Kipimo cha Motisha:** Nani anapambana kufa na kupona?
    - ⚠️ **Kikagua Mitego:** Epuka timu kubwa zenye mitego ya 1.20.
    - 🎫 **Sure 2 Odds:** Machaguo salama yasiyo na presha.
    """)

# Tabs za Kisasa
tab1, tab2, tab3, tab4 = st.tabs([
    "📸 Kichambuzi cha Picha/Tiketi", 
    "🔥 Sure 2 Odds (Za Leo)", 
    "⚠️ Kikagua Mitego (Trap Alert)", 
    "⚽ LiveScores Mubashara"
])

# ================= TAB 1: SCREENSHOT ANALYZER =================
with tab1:
    st.subheader("📸 Usomaji wa Mechi au Mkeka Mzima")
    st.write("Weka screenshot ya mechi moja au mkeka wako mzima kutoka kwenye kampuni yoyote ya betting (Sportybet, Betpawa, 1xBet n.k).")
    
    uploaded_file = st.file_uploader("Pakia Picha ya Mechi au Mkeka:", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Picha Uliyopakia", use_container_width=True)
        
        if st.button("🚀 Anza Ukaguzi wa Kina wa Mechi"):
            if not api_key:
                st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
            else:
                with st.spinner("AI inasoma mechi, inachunguza mtego na kupima motisha..."):
                    try:
                        client = genai.Client(api_key=api_key.strip())
                        prompt = (
                            "Wewe ni Mchambuzi Bingwa wa Soka na Mtaalamu wa Kudhibiti Upotevu wa Pesa kwenye Kubashiri (Professional Betting Analyst).\n"
                            "Chambua screenshot hii ya mechi au mkeka kwa Kiswahili chenye mpangilio mzuri wa kitaalamu na vichwa vya habari:\n\n"
                            "1. UTAMBULISHO WA MECHI: Timu zinazocheza, mashindano, na machaguo/odds zilizopo.\n"
                            "2. KIPIMO CHA MOTISHA (SERIOUS METER 0-100%): Eleza kwa nini timu fulani ipo siriasi zaidi kupambana leo (kushuka daraja, ubingwa, nafasi ya kimataifa, au presha ya kocha).\n"
                            "3. TATHMINI YA MTEGO (TRAP RISK): Je, kuna hatari yoyote iliyojificha kwenye mechi hii? (Mfano: Wachezaji kupumzishwa au uchovu).\n"
                            "4. CHAGUO SALAMA (80%+ CONFIDENCE): Toa ushauri wa chaguo salama (kama Double Chance, Over/Under, DNB) na hitimisho la mwisho."
                        )
                        res = client.models.generate_content(model=MODEL_NAME, contents=[prompt, img])
                        st.success("✅ Uchambuzi Umekamilika!")
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: SURE 2 ODDS =================
with tab2:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"🔥 Jenereta ya Sure 2 Odds ({today_str})")
    st.write("Weka mechi chache za leo au bonyeza kitufe ili AI ichague machaguo salama zaidi yenye uwezekano wa 80%+:")
    
    selected_matches = st.text_input(
        "Andika mechi unazotaka (Hiari):", 
        placeholder="Mfano: Arsenal vs Wolves, Inter Milan vs Torino"
    )
    
    if st.button("🎯 Tengeneza Mkeka wa 2 Odds"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
        else:
            with st.spinner("AI inachuja timu zilizo siriasi leo..."):
                try:
                    client = genai.Client(api_key=api_key.strip())
                    p_odds = (
                        f"Kama mchambuzi mahiri wa soka, tengeneza tiketi ya mechi 2 hadi 3 zenye jumla ya takribani Odds 2.00. "
                        f"Mechi zilizotajwa na mtumiaji: '{selected_matches}'.\n\n"
                        "MIONGOZO YA KITAALAMU:\n"
                        "1. Chagua masoko salama zaidi yenye kiwango cha uhakika cha 80%+ (mfano: Double Chance 1X/X2, Over 1.5 Goals, DNB, Clean Sheet No).\n"
                        "2. Eleza kwa kila mechi 'Kwanini wapo Siriasi kupambana' (Motisha ya pointi 3).\n"
                        "3. Toa ushauri wa Staking Plan (Asilimia salama ya kuweka mtaji wako) kwa Kiswahili fasaha."
                    )
                    res = client.models.generate_content(model=MODEL_NAME, contents=p_odds)
                    st.success("✅ Tiketi Yako Ipo Tayari!")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")

# ================= TAB 3: TRAP DETECTOR =================
with tab3:
    st.subheader("⚠️ Kikagua Mitego ya Mechi (Trap Alert)")
    st.write("Je, kuna timu kubwa unayoitilia shaka leo yenye odds ndogo (mfano 1.20 au 1.30)? Iweke hapa kuona kama ni mtego wa kubomoa mkeka.")
    
    suspect_match = st.text_input("Andika mechi unayoihisi ni mtego:", placeholder="Mfano: Chelsea vs Everton")
    
    if st.button("🔍 Chunguza Mtego Huu"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
        elif not suspect_match.strip():
            st.warning("Tafadhali andika jina la mechi unayotaka kuikagua!")
        else:
            with st.spinner("AI inafanya upelelezi wa kina kuhusu mechi hii..."):
                try:
                    client = genai.Client(api_key=api_key.strip())
                    trap_prompt = (
                        f"Fanya ukaguzi wa kina wa kijasusi kuhusu mechi hii: '{suspect_match}'.\n"
                        "Wachambuzi wengi wanapoteza pesa kwa timu zinazopewa odds ndogo lakini zinatoa sare au kufungwa.\n"
                        "Jibu kwa Kiswahili chenye mpangilio:\n"
                        "1. JE, KUNA MTEGO? (Kiwango cha Hatari: Chini / Wastani / Juu Sana).\n"
                        "2. SABABU ZA MTEGO: (Ratiba ngumu mbele, historia ya dabi, au majeruhi makuu).\n"
                        "3. NJIA MBADALA SALAMA: Ikiwa mtu hataki kuacha mechi hii, acheze soko gani salama badala ya Direct Win?"
                    )
                    res = client.models.generate_content(model=MODEL_NAME, contents=trap_prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")

# ================= TAB 4: LIVESCORES =================
with tab4:
    st.subheader("⚽ Matokeo na Ratiba Mubashara")
    st.write("Fuatilia matokeo ya soka duniani kote mubashara:")
    components.html(
        '<iframe src="https://www.scorebat.com/embed/livescore/" frameborder="0" width="100%" height="700" style="width:100%;height:700px;border:none;border-radius:12px;background:#161b22;"></iframe>', 
        height=720, 
        scrolling=True
    )
