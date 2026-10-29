import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime
import time

st.set_page_config(
    page_title="BetPro AI - Kikosi cha Kijasusi cha Soka",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "saved_api_key" not in st.session_state:
    st.session_state.saved_api_key = ""

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #0b0f19; color: #f0f6fc; }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .hero-sub { color: #8b949e; font-size: 1rem; margin-bottom: 20px; }
    .guide-box {
        background: #161f30;
        border: 1px solid #1f2d47;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 15px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; font-weight: 700; border: none; border-radius: 8px;
        padding: 0.6rem 1.4rem; transition: 0.3s;
        box-shadow: 0 4px 14px rgba(46, 160, 67, 0.35);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="hero-title">⚽ BetPro AI: Jicho Imara la Kijasusi cha Soka</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Mfumo maalum wa kuondoa mitego ya mechi za jana, kukagua H2H, na kutoa Best of the Day (85%+ Probability).</p>', unsafe_allow_html=True)

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
    **🧭 Muongozo wa Kuchagua Mechi Salama:**
    1. Chagua mechi za ligi zenye utulivu (EPL, Serie A, La Liga, Bundesliga, n.k.).
    2. Epuka mechi za kombe la ndani (Cup matches) maana timu kubwa huweka wachezaji wa akiba.
    3. Epuka timu kubwa iliyo ugenini yenye odds za chini (1.20 - 1.35) kama katikati ya wiki ina Champions League.
    """)

api_key = st.session_state.saved_api_key

tab1, tab2 = st.tabs([
    "📸 Kichambuzi cha Picha (Best of the Day & H2H)", 
    "⚽ LiveScores & Ratiba ya Leo Mubashara"
])

# ================= TAB 1 =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"📸 Pakia Picha ya Mechi / Odds za Leo ({today_str})")
    
    st.markdown("""
    <div class="guide-box">
    <b>💡 Hatua Rahisi:</b><br>
    Piga screenshot ya orodha ya mechi kutoka kwenye <b>SportyBet, BetPawa, FlashScore au 1xBet</b> (mechi zinazoonekana muda na timu), kisha ipandishe hapa chini. AI itatenganisha mechi zilizokwisha chezwa na kutoa <b>Best of the Day za mechi zinazokuja pekee</b>.
    </div>
    """, unsafe_allow_html=True)

    col_up1, col_up2 = st.columns([1, 1])
    with col_up1:
        uploaded_file = st.file_uploader("Pakia Screenshot ya Mechi:", type=["png", "jpg", "jpeg"], key="soccer_uploader")
    with col_up2:
        bet_strategy = st.selectbox(
            "Mkakati Unaoutaka:",
            [
                "🏆 Best of the Day (Mechi 2-3 zilizo Salama Zaidi - 85%+)",
                "🔥 Sure 2 Odds (Odds 2.00 za Uhakika)",
                "⚠️ Trap Detector (Kagua Mitego Tu)"
            ]
        )

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="Screenshot Uliyopakia", use_container_width=True)

        if st.button("🚀 Anza Uchambuzi wa Kina na AI Imara", key="btn_scan"):
            if not api_key:
                st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto!")
            else:
                with st.spinner(f"AI inakagua mechi za leo ({today_str}), inatupa mechi za jana na kuchambua H2H..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka na Kudhibiti Upotevu wa Pesa kwenye Kubashiri (Senior Football Analyst).
                        Leo ni tarehe {today_str}.
                        
                        KAZI YAKO KWENYE SCREENSHOT HII:
                        1. 🚫 **CHUNGUZA MUDA NA TAREHE:**
                           - ONDOA na USITUMIE mechi yoyote ambayo tayari imechezwa, imeisha au ni ya jana.
                           - Tumia tu mechi AMBAZO BADO KANISA HAZIJAANZA kuchezwa.
                           
                        2. 🔍 **MUONGOZO WA KUCHAGUA MECHI:**
                           - Kama picha ina mechi nyingi, chagua mechi zenye ushindani na timu zilizopo 'SIRIASI' kupambana (motisha ya ubingwa, kutinga Top 4, au kukwepa kushuka daraja).
                           - Epuka kabisa mechi zenye mitego ya wazi (timu kubwa kupewa 1.25 ugenini ikiwa na uchovu au majeruhi).
                           
                        3. 🏆 **BEST OF THE DAY / MATOKEO YA UCHAMBUZI:**
                           Kulingana na mkakati wa mtumiaji ({bet_strategy}), toa ripoti kwa Kiswahili fasaha:
                           - ⚽ **MECHI ZILIZOTEULIWA:** Majina ya timu na ligi.
                           - 📊 **H2H & FOMU:** Nani ana faida kulingana na historia ya mechi zao na fomu ya karibuni?
                           - 🎯 **CHAGUO SALAMA (85%+ CONFIDENCE):** Mfano: Double Chance 1X/X2, Over 1.5 Goals, Draw No Bet (DNB).
                           - ⚠️ **KIEPUKWE (TRAP WARNING):** Hatari zozote za kuzingatia ili mkeka usichanike.
                           - 🎫 **SLIP SUMMARY:** Mechi 2 au 3 zilizopendekezwa na machaguo yake moja kwa moja.
                        """
                        result_text = call_gemini(client, [prompt, img])
                        st.success("✅ Uchambuzi wa Uhakika Umekamilika!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2 =================
with tab2:
    st.subheader(f"⚽ LiveScores & Ratiba ya Leo ({today_str})")
    st.write("Fuatilia mechi za leo mubashara. Piga screenshot kwenye sehemu ya mechi unazotaka kisha pakia kwenye Tab ya kwanza:")

    # LiveScore yenye uhakika zaidi ya kufuata muda halisi wa sasa
    components.html(
        """
        <iframe src="https://www.scorebat.com/embed/livescore/" 
                frameborder="0" width="100%" height="750" 
                style="width:100%;height:750px;border:none;border-radius:12px;background:#161f30;">
        </iframe>
        """, 
        height=770, 
        scrolling=True
    )
