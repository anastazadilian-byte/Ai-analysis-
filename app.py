import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime
import time

# Usanidi wa Ukurasa
st.set_page_config(
    page_title="BetPro AI - Kikosi cha Kijasusi cha Soka",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

st.markdown('<p class="hero-title">⚽ BetPro AI: Jicho la Kijasusi cha Soka</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">LiveScores, Ukaguzi wa Mitego ya Odds, na Uchambuzi wa Uhakika (85%+ Probability).</p>', unsafe_allow_html=True)

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

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Usanidi wa AI")
    input_key = st.text_input(
        "Gemini API Key:", 
        value=st.session_state.saved_api_key, 
        type="password",
        help="Weka API Key yako hapa."
    )
    if input_key:
        st.session_state.saved_api_key = input_key.strip()
    
    st.markdown("---")
    st.markdown("""
    **Mkakati wa Zero-Trap:**
    - 🛡️ Epuka timu zenye odds 1.20 zenye uchovu
    - 📊 H2H imara & Motisha ya pointi 3
    - 🎯 Machaguo salama (Double Chance / Over 1.5)
    """)

api_key = st.session_state.saved_api_key

tab1, tab2, tab3 = st.tabs([
    "⚽ LiveScores & Best of the Day", 
    "📸 Kichambuzi cha Screenshot (H2H & Lineups)", 
    "🔥 Sure 2 Odds Generator"
])

# ================= TAB 1: LIVESCORES + BEST OF THE DAY =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"🏆 Best of the Day - Mechi Halisi za Leo ({today_str})")
    st.write("Angalia mechi zinazoonekana kwenye **Top Matches** kwenye LiveScore chini, kisha ziweke hapa chini ili AI iondoe mitego na kutoa mechi bora pekee:")

    top_matches_input = st.text_area(
        "Andika mechi za leo unazoziona kwenye LiveScore (Mfano: AC Milan vs Bologna, Genoa vs Juventus, Venezia vs Inter Milan):",
        placeholder="Mfano: AC Milan vs Bologna, Venezia vs Inter Milan, Genoa vs Juventus, Monza vs Napoli",
        help="Ili mechi zisiwe za kubuni, andika zile unazoziona kwenye orodha ya ScoreBat hapo chini."
    )

    if st.button("🌟 Chuja Mitego & Toa 'Best of the Day'", key="btn_filter_today"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto kwanza!")
        elif not top_matches_input.strip():
            st.warning("Tafadhali andika majina ya mechi 2 au zaidi za leo kutoka kwenye LiveScore hapo chini!")
        else:
            with st.spinner("AI inachambua H2H, msimamo na motisha kwa mechi hizi za leo..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_filter = f"""
                    Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (Professional Betting Risk Analyst).
                    Hizi hapa ni mechi halisi zinazochezwa LEO:
                    {top_matches_input}

                    KAZI YAKO:
                    1. Chagua mechi 2 au 3 PEKEE zenye uhakika mkubwa zaidi wa 85%+ kutoka kwenye orodha hiyo hapo juu. USIWEKE mechi nyingine ya nje ya orodha hii!
                    2. ONDOA MITEGO YOTE (TRAP ELIMINATION): Epuka timu kubwa zenye historia ya kutoa sare za kizembe au mechi za dabi zenye vurugu.
                    3. Chambua H2H na motisha ya pointi ya kila timu iliyochaguliwa.

                    Jibu kwa Kiswahili chenye mpangilio huu:
                    - ⚽ **MECHI ILIYOCHAGULIWA:**
                    - 🏆 **KWANINI NI BEST OF THE DAY (H2H & Form):**
                    - 🎯 **CHAGUO SALAMA (85%+):** (Mfano: Double Chance 1X/X2, Over 1.5 Goals, Draw No Bet).
                    - ⚠️ **KIEPUKWE (TRAP ALERT):** Kitu gani cha kuepuka kwenye mechi hii.
                    """
                    result_text = call_gemini(client, [prompt_filter])
                    st.success("✅ Mechi Bora za Leo Zimechaguliwa Bila Makosa!")
                    st.markdown(result_text)
                    st.markdown("---")
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")

    st.subheader("📺 Ratiba & Matokeo Mubashara (ScoreBat Live)")
    st.write("Tumia LiveScore hii kuona mechi za leo, nakili majina yake na uyaweke juu kwa uchambuzi wa haraka:")
    components.html(
        '<iframe src="https://www.scorebat.com/embed/livescore/" frameborder="0" width="100%" height="700" style="width:100%;height:700px;border:none;border-radius:12px;background:#161b22;"></iframe>', 
        height=720, 
        scrolling=True
    )

# ================= TAB 2: SCREENSHOT ANALYZER =================
with tab2:
    st.subheader("📸 Usomaji wa Mechi kwa Screenshot (H2H, Lineups & Vikosi)")
    st.write("Pakia screenshot ya mechi kutoka LiveScore au kwenye tovuti ya betting:")

    col_up1, col_up2 = st.columns([1, 1])
    with col_up1:
        uploaded_file = st.file_uploader("Pakia Screenshot ya Mechi:", type=["png", "jpg", "jpeg"], key="soccer_uploader")
    with col_up2:
        extra_info = st.text_area(
            "Taarifa za Ziada (Hiari):",
            placeholder="Mfano: Mchezaji fulani yupo nje..."
        )

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="Screenshot Uliyopakia", use_container_width=True)

        if st.button("🚀 Anza Ukaguzi wa Kina wa Mechi", key="btn_scan"):
            if not api_key:
                st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
            else:
                with st.spinner("AI inasoma picha na kuchambua H2H..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt_img = f"""
                        Wewe ni Mchambuzi Mkuu wa Soka. Chambua screenshot hii ya mechi kwa Kiswahili:
                        1. ⚔️ Timu na mashindano.
                        2. 📊 Historia ya H2H na fomu ya karibuni.
                        3. 🎯 Chaguo salama lenye uhakika wa 85%+.
                        4. ⚠️ Trap Alert: Kama kuna mtego wa odds.
                        """
                        result_text = call_gemini(client, [prompt_img, img])
                        st.success("✅ Uchambuzi Umekamilika!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 3: SURE 2 ODDS =================
with tab3:
    st.subheader(f"🔥 Jenereta ya Sure 2 Odds ({today_str})")
    st.write("Tengeneza tiketi ya odds 2.00 kulingana na mechi unazotaka:")

    selected_matches = st.text_input(
        "Andika mechi za leo:", 
        placeholder="Mfano: AC Milan vs Bologna, Inter vs Venezia..."
    )

    if st.button("🎯 Tengeneza Mkeka wa 2 Odds", key="btn_odds"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
        else:
            with st.spinner("AI inatengeneza tiketi salama..."):
                try:
                    client = genai.Client(api_key=api_key)
                    p_odds = f"""
                    Tengeneza tiketi ya mechi 2 au 3 zenye takribani Odds 2.00 kwa mechi hizi: '{selected_matches}'.
                    - Tumia machaguo salama sana (1X/X2, Over 1.5, DNB).
                    - Toa sababu fupi ya H2H na motisha kwa Kiswahili.
                    """
                    result_text = call_gemini(client, [p_odds])
                    st.success("✅ Tiketi Yako Ipo Tayari!")
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")
