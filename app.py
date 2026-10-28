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
st.markdown('<p class="hero-sub">Pakia Screenshot ya Top Matches, AI inachuja H2H, inaondoa mitego na kutoa Best of the Day (85%+ Probability).</p>', unsafe_allow_html=True)

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
    **Jinsi ya Kupata Ushindi:**
    1. Fungua Tab ya 2 (LiveScore), piga screenshot sehemu ya **Top Matches**.
    2. Weka picha hiyo kwenye Tab ya 1 (Scanner).
    3. AI itasoma mechi zote na kutoa **Best of the Day** zisizo na mitego!
    """)

api_key = st.session_state.saved_api_key

tab1, tab2 = st.tabs([
    "📸 Kichambuzi cha Picha (Top Matches & Best of Day)", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1: SCREENSHOT TO BEST OF THE DAY =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"📸 Pakia Screenshot ya 'Top Matches' ya Leo ({today_str})")
    st.write("Chukua screenshot ya orodha ya mechi kutoka ScoreBat (chini), SportyBet, BetPawa au Flashscore kisha weka hapa:")

    col_up1, col_up2 = st.columns([1, 1])
    with col_up1:
        uploaded_file = st.file_uploader("Pakia Screenshot ya Mechi:", type=["png", "jpg", "jpeg"], key="soccer_uploader")
    with col_up2:
        target_odds = st.selectbox(
            "Lengo la Mkeka wako:",
            ["🎯 Best of the Day (Mechi 2-3 zilizo Salama Zaidi)", "🔥 Sure 2 Odds Pekee", "⚠️ Ukaguzi wa Mitego (Trap Check Pekee)"]
        )

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="Screenshot Uliyopakia", use_container_width=True)

        if st.button("🚀 Anza Uchambuzi & Toa 'Best of the Day'", key="btn_scan"):
            if not api_key:
                st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
            else:
                with st.spinner("AI inasoma mechi zote kwenye picha, inachunguza H2H na kuondoa mitego..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt_img = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (Chief Betting Analyst & Risk Manager).
                        Soma kwa makini screenshot hii inayoonyesha mechi/odds za mpira. Lengo la mtumiaji ni: '{target_odds}'.

                        FANYA KAZI KWA HATUA HIZI KWA KISWAHILI KINACHOELEWEKA NA KITAALAMU:
                        
                        1. 📋 **MECHI ZILIZOGUNDULIKA KWENYE PICHA:**
                           - Orodhesha mechi zote zinazoonekana wazi kwenye screenshot hii.

                        2. 🏆 **BEST OF THE DAY (MECHI BORA 2 HADI 3 SALAMA ZAIDI - 85%+ CONFIDENCE):**
                           - Kutoka kwenye zile mechi za picha, teua zile tu zenye usalama mkubwa zaidi wa kutoa matokeo.
                           - Eleza H2H yao na kwanini timu husika ipo 'SIRIASI' kupambana (motisha ya pointi, kulinda ubingwa au kutoshuka daraja).
                           - Toa soko salama (mf. Double Chance 1X/X2, Over 1.5 Goals, Draw No Bet, n.k).

                        3. ⚠️ **UKAGUZI WA MITEGO (TRAP ALERT - ZIKWEPE HIZI!):**
                           - Taja mechi yoyote iliyopo kwenye picha hiyo ambayo ni mtego wa kubomoa mikeka (kwa mfano: timu kubwa kupewa odds ndogo lakini ina uchovu, wachezaji majeruhi au ni dabi ngumu).

                        4. 🎫 **MUHTASARI WA TIKETI SALAMA YA LEO:**
                           - Orodha fupi ya kubetia (Mechi + Chaguo Salama).
                        """
                        result_text = call_gemini(client, [prompt_img, img])
                        st.success("✅ Uchambuzi na Best of the Day Zimekamilika!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: LIVESCORES =================
with tab2:
    st.subheader("📺 Ratiba & Matokeo Mubashara (LiveScores)")
    st.write("Angalia sehemu ya **TOP MATCHES**, piga screenshot, kisha rudi kwenye Tab ya kwanza kuichambua:")
    
    # LiveScore iliyoboreshwa kusasisha tarehe ya leo
    components.html(
        f"""
        <iframe src="https://www.scorebat.com/embed/livescore/" 
                frameborder="0" width="100%" height="750" 
                style="width:100%;height:750px;border:none;border-radius:12px;background:#161b22;">
        </iframe>
        """, 
        height=770, 
        scrolling=True
    )
