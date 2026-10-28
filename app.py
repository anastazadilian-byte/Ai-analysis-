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
st.markdown('<p class="hero-sub">LiveScore, Ukaguzi wa Mitego, na Uchaguzi wa Mechi Bora za Siku (Best of the Day).</p>', unsafe_allow_html=True)

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
        help="Weka API Key yako hapa, itahifadhiwa."
    )
    if input_key:
        st.session_state.saved_api_key = input_key.strip()
    
    st.markdown("---")
    st.markdown("""
    **Vigezo vya Best of the Day:**
    - 🛡️ Zero-Trap (Haina mtego wa timu kubwa)
    - 📊 H2H thabiti & Fomu ya hivi karibuni
    - 🎯 Uhakika wa 85%+ (Double Chance au Over)
    """)

api_key = st.session_state.saved_api_key

# Tabs Kuu
tab1, tab2, tab3 = st.tabs([
    "⚽ LiveScores & Best of the Day", 
    "📸 Kichambuzi cha Screenshot (H2H & Lineups)", 
    "🔥 Sure 2 Odds Generator"
])

# ================= TAB 1: LIVESCORES + BEST OF THE DAY =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"🏆 Best of the Day Kutoka kwenye Top Matches ({today_str})")
    st.write("Bofya kitufe hapa chini ili AI ikague mechi zote za leo zilizo kwenye **Top Matches** (kama zinavyoonekana kwenye LiveScore chini) na kuchuja zile zenye usalama mkubwa zaidi:")

    if st.button("🌟 Toa 'Best of the Day' Kutoka Top Matches za Leo", key="btn_top_matches"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto kwanza!")
        else:
            with st.spinner("AI inakagua mechi zote za Top Matches, inachunguza H2H na kuondoa mitego..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_top = f"""
                    Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (Professional Betting Analyst).
                    Kazi yako ni kutathmini mechi za LEO zinazopatikana kwenye ratiba ya 'Top Matches' ya ligi kubwa (kama Serie A, Premier League, La Liga, Bundesliga, Ligue 1 na mashindano ya UEFA).
                    
                    MASHARTI YA BEST OF THE DAY (ZERO-TRAP FILTER):
                    1. Usichague mechi ambazo zina mitego ya odds ndogo (1.15 - 1.35) lakini timu ina uchovu au historia ya kutoa sare za kizembe.
                    2. Chagua mechi 2 hadi 4 BORA PEKEE zenye uwezekano wa ushindi wa 85%+.
                    3. Angalia H2H ya timu hizo na fomu ya karibuni.
                    
                    Toa majibu kwa Kiswahili chenye mpangilio safi na vichwa vya habari:
                    - ⚽ **MECHI & LIGI:** Timu na Muda
                    - 🏆 **KWANINI NI BEST OF THE DAY:** Sababu ya kiufundi (H2H na Motisha ya pointi).
                    - 🎯 **CHAGUO SALAMA (85%+):** (Mfano: 1X, Over 1.5, DNB, GG).
                    - ⚠️ **KIEPUKWE:** Kitu gani cha kuepuka ili mkeka usichanike.
                    """
                    result_text = call_gemini(client, [prompt_top])
                    st.success("✅ Mechi Bora za Siku (Best of the Day) Zimepatikana!")
                    st.markdown(result_text)
                    st.markdown("---")
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")

    st.subheader("📺 Ratiba & Matokeo Mubashara (ScoreBat Live)")
    st.write("Hapa chini unaweza kuona ratiba na matokeo mubashara ya Top Matches zote:")
    components.html(
        '<iframe src="https://www.scorebat.com/embed/livescore/" frameborder="0" width="100%" height="700" style="width:100%;height:700px;border:none;border-radius:12px;background:#161b22;"></iframe>', 
        height=720, 
        scrolling=True
    )

# ================= TAB 2: SCREENSHOT ANALYZER =================
with tab2:
    st.subheader("📸 Usomaji wa Mechi kwa Screenshot (H2H, Lineups & Vikosi)")
    st.write("Pakia screenshot ya mechi unayoitilia shaka au mkeka mzima ili AI iikague kiundani:")

    col_up1, col_up2 = st.columns([1, 1])
    with col_up1:
        uploaded_file = st.file_uploader("Pakia Picha ya Mechi au Mkeka:", type=["png", "jpg", "jpeg"], key="soccer_uploader")
    with col_up2:
        extra_info = st.text_area(
            "Taarifa za Ziada (Hiari):",
            placeholder="Mfano: Mshambuliaji majeruhi, mechi ya ugenini..."
        )

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="Screenshot Uliyopakia", use_container_width=True)

        if st.button("🚀 Anza Ukaguzi wa Kina wa Mechi", key="btn_scan"):
            if not api_key:
                st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
            else:
                with st.spinner("AI inasoma picha na kukagua H2H pamoja na mitego..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt_img = f"""
                        Wewe ni Mchambuzi Mkuu wa Soka na Kudhibiti Upotevu wa Pesa kwenye Kubashiri.
                        Chambua screenshot hii ya mechi kwa kuzingatia maelezo haya: '{extra_info}'.

                        Fanya uchambuzi kwa Kiswahili ukiwa na mpangilio huu:
                        1. ⚔️ **TIMU NA UTAMBULISHO:** Majina ya timu na mashindano.
                        2. 📊 **HEAD TO HEAD (H2H):** Tabia ya matokeo wanapokutana.
                        3. 📈 **FOMU YA KARIBUNI & LINEUPS:** Hali ya vikosi na majeruhi.
                        4. ⚠️ **UKAGUZI WA MTEGO (TRAP RISK):** Je, kuna mtego wowote?
                        5. 🎯 **CHAGUO SALAMA (85%+ CONFIDENCE):** Ushauri wa chaguo salama kabisa.
                        """
                        result_text = call_gemini(client, [prompt_img, img])
                        st.success("✅ Uchambuzi Umekamilika!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 3: SURE 2 ODDS =================
with tab3:
    st.subheader(f"🔥 Jenereta ya Sure 2 Odds ({today_str})")
    st.write("Tengeneza tiketi ya odds 2.00 iliyotokana na mechi zilizochujwa na zisizo na mitego:")

    selected_matches = st.text_input(
        "Andika mechi za leo unazotaka (Hiari):", 
        placeholder="Mfano: AC Milan vs Bologna, Inter vs Venezia..."
    )

    if st.button("🎯 Tengeneza Mkeka wa 2 Odds", key="btn_odds"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
        else:
            with st.spinner("AI inatengeneza tiketi isiyo na presha..."):
                try:
                    client = genai.Client(api_key=api_key)
                    p_odds = f"""
                    Tengeneza tiketi ya mechi 2 hadi 3 zenye jumla ya takribani Odds 2.00 kwa kuzingatia mechi hizi kama zipo: '{selected_matches}'.
                    VIGEZO:
                    1. Hakikisha hakuna mtego wowote (Zero-Trap picks pekee).
                    2. Tumia machaguo salama sana (Double Chance 1X/X2, Over 1.5, DNB).
                    3. Eleza kwanini kila timu ipo makini na siriasi kupata matokeo leo kwa Kiswahili.
                    """
                    result_text = call_gemini(client, [p_odds])
                    st.success("✅ Tiketi Yako Ipo Tayari!")
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")
