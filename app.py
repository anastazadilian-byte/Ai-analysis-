import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime
import time

# Usanidi wa Ukurasa wa Hadhi ya VIP
st.set_page_config(
    page_title="BetPro VIP - AI Intelligence Syndicate",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "saved_api_key" not in st.session_state:
    st.session_state.saved_api_key = ""

# Muonekano wa Kisasa wa Kulipia (Ultra-Premium VIP Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0d1527 0%, #070a12 90%);
        color: #e6edf3;
    }
    
    /* VIP Header */
    .vip-badge {
        display: inline-block;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #000;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 20px;
        letter-spacing: 1px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .hero-sub {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 5px;
        margin-bottom: 25px;
    }
    
    /* Kadi za Kisasa za VIP */
    .vip-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    
    /* Vitufe vya Kulipia */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.6rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 18px rgba(14, 165, 233, 0.35);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #1d4ed8 100%);
        box-shadow: 0 6px 24px rgba(56, 189, 248, 0.5);
        color: #fff;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Kichwa Kikuu cha Programu
st.markdown('<span class="vip-badge">👑 VIP AI Terminal</span>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">BetPro Intelligence: Mfumo wa Kijasusi wa Soka</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Uchambuzi wa H2H, Usomaji wa Motisha (Serious Meter), Ugunduzi wa Mitego, na Ujenzi wa Mikeka ya Uhakika (85%+).</p>', unsafe_allow_html=True)

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
    st.markdown("### 👑 VIP Account Settings")
    input_key = st.text_input(
        "Gemini API Access Key:", 
        value=st.session_state.saved_api_key, 
        type="password",
        help="Weka ufunguo wako wa Google Gemini hapa."
    )
    if input_key:
        st.session_state.saved_api_key = input_key.strip()
    
    st.markdown("---")
    st.markdown("""
    **🛡️ Mfumo wa Udhibiti wa Mtaji:**
    - 🔒 **Ticket A (Safe 2 Odds):** 70% ya bajeti yako.
    - 🚀 **Ticket B (Multiplier):** 30% ya bajeti yako.
    - 🚫 **Zero-Trap Rule:** Timu kubwa zenye uchovu hutupwa nje mara moja.
    """)
    st.info("💡 Hali ya App: **PRO VERSION ACTIVE**")

api_key = st.session_state.saved_api_key

# Tabs Kuu Mbili Zilizonyooka
tab1, tab2 = st.tabs([
    "📸 Scanner ya Mechi & VIP Slip Builder", 
    "⚽ LiveScores & Ratiba Mubashara"
])

# ================= TAB 1 =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    
    st.markdown(f"""
    <div class="vip-card">
        <h4 style="margin:0 0 8px 0; color:#38bdf8;">🎯 Pakia Screenshot ya Mechi za Leo ({today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#94a3b8;">
            Piga screenshot ya orodha ya mechi kutoka app yoyote ya soka (SportyBet, FlashScore, BetPawa, 1xBet). 
            AI itachambua H2H, itaondoa mitego, na <b>kukujengea mikeka 2 iliyopangwa kisayansi</b> pamoja na hesabu ya mtaji wako.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file = st.file_uploader("Pakia Screenshot ya Mechi/Odds:", type=["png", "jpg", "jpeg"], key="vip_uploader")
    with col2:
        user_stake = st.text_input("Mtaji Wako wa Leo (Mfano: TZS 10,000 au 50,000):", value="TZS 20,000")
        target_mode = st.selectbox(
            "Chagua Mfumo wa Uchambuzi:",
            [
                "👑 VIP Complete Suite (Best of Day + Mikeka 2 + Mgao wa Pesa)",
                "🔥 Sure 2 Odds Pekee (Mechi 2 za Kulinda Mtaji)",
                "⚠️ Trap Alert (Ukaguzi wa Mitego ya Timu Kubwa Pekee)"
            ]
        )

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="Screenshot Uliyopakia", use_container_width=True)

        if st.button("🚀 Anza Uchambuzi wa Kijeshi wa VIP (Deep AI Run)", key="btn_run_vip"):
            if not api_key:
                st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto kwanza!")
            else:
                with st.spinner("AI inakagua mechi za leo, inachambua H2H, motisha, na kupanga bajeti yako kisayansi..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka na Mshauri Mkuu wa Uwekezaji wa Michezo (Senior Betting Syndicate Manager).
                        Leo ni tarehe {today_str}. Mtaji wa mtumiaji kwa leo ni: '{user_stake}'. Mfumo aliouchagua: '{target_mode}'.

                        KAZI YAKO KWENYE PICHA HII:
                        1. Kagua mechi zote zinazoonekana. Ondoa kabisa mechi ambazo zimeshachezwa au ni za jana.
                        2. ONDOA MITEGO YA WAZI (TRAP ELIMINATION): Taja timu yoyote kubwa iliyo kwenye picha ambayo ni mtego wa kuepuka (kwa sababu ya uchovu, majeruhi, au dabi ngumu).
                        3. BEST OF THE DAY (Uhakika 85%+): Teua mechi 2 hadi 4 bora zaidi zenye takwimu imara za H2H na motisha kubwa ya pointi 3.
                        
                        4. JENGA MIKEKA MIWILI (SMART SLIP BUILDER):
                           - 🎫 **TICKET A (SAFE 2 ODDS - 90% PROBABILITY):**
                             Mechi 2 tu salama zaidi (kama Double Chance 1X/X2, Over 1.5 Goals, Draw No Bet).
                           - 🚀 **TICKET B (VALUE MULTIPLIER - ODDS 4.00+):**
                             Mechi 3 au 4 zenye faida nzuri zilizolindwa vizuri.
                        
                        5. USHAURI WA UGAWAJI WA MTAJI (BANKROLL MANAGEMENT KWA {user_stake}):
                           - Piga hesabu ya kiasi cha shilingi cha kuweka kwenye Ticket A (70% ya mtaji).
                           - Piga hesabu ya kiasi cha shilingi cha kuweka kwenye Ticket B (30% ya mtaji).
                           - Eleza kwanini mfumo huu unamlinda asipoteze pesa zote hata kama tiketi moja ikikosa.

                        Toa ripoti nzima kwa Kiswahili fasaha chenye heshima, maneno ya kitaalamu na mpangilio mzuri wa kadi na vielelezo!
                        """
                        result_text = call_gemini(client, [prompt, img])
                        st.success("✅ Uchambuzi wa VIP na Mgawanyo wa Mikeka Umekamilika!")
                        st.markdown(result_text)
                        
                        # Kitufe cha kupakua ripoti ya mkeka
                        st.download_button(
                            label="📥 Pakua / Nakili Tiketi Hizi (TXT)",
                            data=result_text,
                            file_name=f"BetPro_VIP_Ticket_{today_str}.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2 =================
with tab2:
    st.subheader(f"⚽ LiveScores & Ratiba ya Leo Mubashara ({today_str})")
    st.write("Fuatilia mechi za leo, piga screenshot ya orodha unayoitilia shaka kisha weka kwenye Kichambuzi cha VIP:")
    components.html(
        """
        <iframe src="https://www.scorebat.com/embed/livescore/" 
                frameborder="0" width="100%" height="750" 
                style="width:100%;height:750px;border:none;border-radius:14px;background:#0d1527;">
        </iframe>
        """, 
        height=770, 
        scrolling=True
    )
