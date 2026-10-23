import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime
import time

# Usanidi wa Ukurasa wa Kisasa
st.set_page_config(
    page_title="BetPro AI - Kikosi cha Kijasusi cha Soka",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kuhifadhi API Key Kwenye Kumbukumbu Isijitoe Kamwe
if "saved_api_key" not in st.session_state:
    st.session_state.saved_api_key = ""

# Styling ya Kisasa
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #0d1117; color: #f0f6fc; }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .hero-sub { color: #8b949e; font-size: 1rem; margin-bottom: 25px; }
    .stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; font-weight: 700; border: none; border-radius: 8px;
        padding: 0.6rem 1.2rem; transition: 0.3s;
        box-shadow: 0 4px 14px rgba(46, 160, 67, 0.35);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Kichwa cha Programu
st.markdown('<p class="hero-title">⚽ BetPro AI: Jicho la Kijasusi cha Soka</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Uchambuzi wa kina, ugunduzi wa mitego ya Odds, na usomaji wa timu zilizo SIRIASI kupambana (80%+ Probability).</p>', unsafe_allow_html=True)

# Function ya Kuita AI yenye Kuzuia Hitilafu ya 503 (Auto-Retry)
def call_gemini(client, contents):
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-3.8-flash"]
    last_error = ""
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(model=model_name, contents=contents)
                return response.text
            except Exception as e:
                last_error = str(e)
                if "503" in last_error or "UNAVAILABLE" in last_error:
                    time.sleep(2)
                    continue
                break
    raise Exception(last_error)

# Sidebar yenye kuhifadhi API Key
with st.sidebar:
    st.markdown("### ⚙️ Usanidi wa AI")
    input_key = st.text_input(
        "Gemini API Key:", 
        value=st.session_state.saved_api_key, 
        type="password",
        help="Weka API Key mara moja tu, itahifadhiwa bila kujitoa."
    )
    if input_key:
        st.session_state.saved_api_key = input_key.strip()
    
    st.markdown("---")
    st.markdown("""
    **💡 Sifa Kuu:**
    - 🎯 **Kipimo cha Motisha:** Nani anapambana kufa na kupona?
    - ⚠️ **Kikagua Mitego:** Epuka timu kubwa zenye mitego ya 1.20.
    - 🎫 **Sure 2 Odds:** Machaguo salama yasiyo na presha.
    """)

api_key = st.session_state.saved_api_key

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
    st.write("Weka screenshot ya mechi moja au mkeka wako mzima kutoka kwenye kampuni yoyote ya betting.")
    
    uploaded_file = st.file_uploader("Pakia Picha ya Mechi au Mkeka:", type=["png", "jpg", "jpeg"], key="soccer_uploader")
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="Picha Uliyopakia", use_container_width=True)
        
        if st.button("🚀 Anza Ukaguzi wa Kina wa Mechi", key="btn_scan"):
            if not api_key:
                st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
            else:
                with st.spinner("AI inasoma mechi, inachunguza mtego na kupima motisha..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = (
                            "Wewe ni Mchambuzi Bingwa wa Soka na Mtaalamu wa Kudhibiti Upotevu wa Pesa kwenye Kubashiri.\n"
                            "Chambua screenshot hii ya mechi au mkeka kwa Kiswahili chenye mpangilio mzuri wa kitaalamu na vichwa vya habari:\n\n"
                            "1. UTAMBULISHO WA MECHI: Timu zinazocheza, mashindano, na machaguo/odds zilizopo.\n"
                            "2. KIPIMO CHA MOTISHA (SERIOUS METER 0-100%): Eleza kwa nini timu fulani ipo siriasi zaidi kupambana leo.\n"
                            "3. TATHMINI YA MTEGO (TRAP RISK): Je, kuna hatari yoyote iliyojificha?\n"
                            "4. CHAGUO SALAMA (80%+ CONFIDENCE): Toa ushauri wa chaguo salama na hitimisho."
                        )
                        result_text = call_gemini(client, [prompt, img])
                        st.success("✅ Uchambuzi Umekamilika!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: SURE 2 ODDS =================
with tab2:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"🔥 Jenereta ya Sure 2 Odds ({today_str})")
    st.write("Weka mechi chache za leo au bonyeza kitufe ili AI ichague machaguo salama zaidi:")
    
    selected_matches = st.text_input(
        "Andika mechi unazotaka (Hiari):", 
        placeholder="Mfano: Arsenal vs Wolves, Inter Milan vs Torino"
    )
    
    if st.button("🎯 Tengeneza Mkeka wa 2 Odds", key="btn_odds"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
        else:
            with st.spinner("AI inachuja timu zilizo siriasi leo..."):
                try:
                    client = genai.Client(api_key=api_key)
                    p_odds = (
                        f"Kama mchambuzi mahiri wa soka, tengeneza tiketi ya mechi 2 hadi 3 zenye jumla ya takribani Odds 2.00. "
                        f"Mechi: '{selected_matches}'.\n\n"
                        "1. Chagua masoko salama zaidi yenye uhakika wa 80%+ (mfano: Double Chance 1X/X2, Over 1.5, DNB).\n"
                        "2. Eleza kwa kila mechi 'Kwanini wapo Siriasi kupambana'.\n"
                        "3. Toa ushauri wa Staking Plan kwa Kiswahili fasaha."
                    )
                    result_text = call_gemini(client, [p_odds])
                    st.success("✅ Tiketi Yako Ipo Tayari!")
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")

# ================= TAB 3: TRAP DETECTOR =================
with tab3:
    st.subheader("⚠️ Kikagua Mitego ya Mechi (Trap Alert)")
    st.write("Je, kuna timu kubwa unayoitilia shaka leo yenye odds ndogo (mfano 1.20 au 1.30)?")
    
    suspect_match = st.text_input("Andika mechi unayoihisi ni mtego:", placeholder="Mfano: Chelsea vs Everton")
    
    if st.button("🔍 Chunguza Mtego Huu", key="btn_trap"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
        elif not suspect_match.strip():
            st.warning("Tafadhali andika jina la mechi unayotaka kuikagua!")
        else:
            with st.spinner("AI inafanya upelelezi wa kina kuhusu mechi hii..."):
                try:
                    client = genai.Client(api_key=api_key)
                    trap_prompt = (
                        f"Fanya ukaguzi wa kina wa kijasusi kuhusu mechi hii: '{suspect_match}'.\n"
                        "1. JE, KUNA MTEGO? (Kiwango cha Hatari: Chini / Wastani / Juu Sana).\n"
                        "2. SABABU ZA MTEGO.\n"
                        "3. NJIA MBADALA SALAMA: Soko gani salama badala ya Direct Win?"
                    )
                    result_text = call_gemini(client, [trap_prompt])
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")

# ================= TAB 4: LIVESCORES =================
with tab4:
    st.subheader("⚽ Matokeo na Ratiba Mubashara")
    components.html(
        '<iframe src="https://www.scorebat.com/embed/livescore/" frameborder="0" width="100%" height="700" style="width:100%;height:700px;border:none;border-radius:12px;background:#161b22;"></iframe>', 
        height=720, 
        scrolling=True
    )
