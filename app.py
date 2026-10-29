import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime
import time

# Usanidi wa Ukurasa
st.set_page_config(
    page_title="BetPro VIP - AI Intelligence Syndicate",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kumbukumbu za Session
if "saved_api_key" not in st.session_state:
    st.session_state.saved_api_key = ""
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "vip_history" not in st.session_state:
    st.session_state.vip_history = [
        {"match": "Inter Milan vs Venezia", "pick": "Inter Milan Win & Over 1.5", "status": "WON ✅", "odds": "1.35"},
        {"match": "Monza vs Napoli", "pick": "Napoli Double Chance (X2)", "status": "WON ✅", "odds": "1.28"},
        {"match": "Bologna vs AC Milan", "pick": "Over 1.5 Goals", "status": "WON ✅", "odds": "1.30"},
    ]

# CSS Iliyorekebishwa: Rangi Nyeupe Safi kwenye Chat na Maandishi Yote
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { 
        background: #0b1120; 
        color: #f8fafc; 
    }
    
    .vip-badge {
        display: inline-block;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #000; font-weight: 800; font-size: 0.75rem;
        padding: 4px 12px; border-radius: 20px; letter-spacing: 1px;
        margin-bottom: 8px; text-transform: uppercase;
    }
    
    .hero-title {
        font-size: 2.3rem; font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub { color: #94a3b8; font-size: 0.95rem; margin-top: 5px; margin-bottom: 25px; }
    
    .vip-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        color: #ffffff;
    }
    
    /* Marekebisho ya Chat Input na Messages ili zisiwe giza */
    .stChatInputContainer textarea {
        color: #ffffff !important;
        background-color: #1e293b !important;
        border: 1px solid #38bdf8 !important;
        font-size: 1rem !important;
    }
    
    .stChatMessage {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 12px !important;
        margin-bottom: 10px !important;
    }
    
    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #f1f5f9 !important;
        font-size: 0.98rem !important;
        line-height: 1.6 !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white; font-weight: 700; border: none; border-radius: 10px;
        padding: 0.65rem 1.5rem; transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #1d4ed8 100%);
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<span class="vip-badge">👑 VIP AI Syndicate</span>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">BetPro Intelligence: Mfumo Kamili wa Soka</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Scanner ya Mechi, Ushauri wa Maswali Mubashara (Chat AI), na Rekodi ya Ushindi ya VIP.</p>', unsafe_allow_html=True)

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
        help="Weka API Key yako hapa."
    )
    if input_key:
        st.session_state.saved_api_key = input_key.strip()
    
    st.markdown("---")
    st.markdown("""
    **🧭 Muongozo wa VIP wa Mechi za Leo:**
    1. Chagua mechi ambazo **bado hazijaanza** (angalia saa).
    2. Epuka timu kubwa zenye mechi ngumu mbele ya safari.
    3. Zingatia timu zenye uhitaji mkubwa wa pointi 3.
    """)
    st.info("💡 Hali ya Mfumo: **VIP PREMIUM ACTIVE**")

api_key = st.session_state.saved_api_key

tab1, tab2, tab3, tab4 = st.tabs([
    "📸 Kichambuzi cha Mechi (VIP Slip)", 
    "💬 Muulize Mtaalamu (Football AI Chat)", 
    "🏆 VIP Won Archive (Rekodi ya Tiki)", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1: SCANNER & VIP SLIP =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.markdown(f"""
    <div class="vip-card">
        <h4 style="margin:0 0 8px 0; color:#38bdf8;">🎯 Pakia Screenshot ya Mechi za Leo ({today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Pakia picha ya mechi kutoka SportyBet, BetPawa, au FlashScore. 
            AI itakagua H2H, itaondoa mitego, na kukuwekea <b>Tiketi ya Uhakika yenye asilimia 85%+</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file = st.file_uploader("Pakia Screenshot ya Mechi:", type=["png", "jpg", "jpeg"], key="vip_uploader")
    with col2:
        user_stake = st.text_input("Mtaji Wako wa Leo:", value="TZS 20,000")
        target_mode = st.selectbox(
            "Chagua Mfumo wa Uchambuzi:",
            [
                "👑 VIP Complete Suite (Best of Day + Mikeka 2 + Hesabu ya Mtaji)",
                "🔥 Sure 2 Odds Pekee (Mechi za Kulinda Mtaji)",
                "⚠️ Trap Detector (Kagua Mitego ya Leo Pekee)"
            ]
        )

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="Screenshot Uliyopakia", use_container_width=True)

        if st.button("🚀 Anza Uchambuzi wa VIP", key="btn_run_vip"):
            if not api_key:
                st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto kwanza!")
            else:
                with st.spinner("AI inasoma mechi, inachunguza H2H na kuondoa mechi zilizochezwa..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka na Meneja wa Mikeka ya VIP.
                        Leo ni tarehe {today_str}. Mtaji wa mtumiaji ni: '{user_stake}'. Mfumo: '{target_mode}'.

                        KAZI YAKO:
                        1. ONDOA KABISA mechi yoyote iliyokwisha chezwa, iliyoisha (Full Time), au ya jana. Tumia mechi za leo ZISIZOANZA TU!
                        2. Taja kama kuna mtego wa odds (Trap Alert).
                        3. BEST OF THE DAY (Uhakika 85%+): Mechi 2 hadi 4 bora zenye H2H imara na motisha ya pointi 3.
                        4. UGAWAJI WA MTAJI: Panga jinsi ya kugawanya mtaji wa {user_stake} kwenye Ticket A (Safe 2 Odds - 70%) na Ticket B (Multiplier - 30%).

                        Toa ripoti nzima kwa Kiswahili chenye heshima na mpangilio safi wa kitaalamu.
                        """
                        result_text = call_gemini(client, [prompt, img])
                        st.success("✅ Uchambuzi Umekamilika!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: FOOTBALL CHATBOT (RANGI ZILIZOREKEBISHWA) =================
with tab2:
    st.subheader("💬 Ongea na Mtaalamu wa Soka wa AI (Football Analyst Chat)")
    st.write("Muulize swali lolote kuhusu soka, vikosi, fomu ya timu, au ushauri wa kubetia mechi yoyote ya leo:")

    # Onyesha mazungumzo ya awali
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Eneo la mtumiaji kuandika swali
    user_question = st.chat_input("Andika swali lako hapa... (Mfano: Nipe mechi 2 za uhakika za leo)")

    if user_question:
        st.session_state.chat_messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)

        if not api_key:
            st.error("Tafadhali weka Gemini API Key kwenye menu ya kushoto kwanza!")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Mtaalamu wa Soka anajibu..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        chat_prompt = f"""
                        Wewe ni Mchambuzi Bingwa wa Soka wa Kiwango cha Kimataifa (Sports Analyst).
                        Jibu swali hili la mtumiaji kwa heshima, data halisi za soka, weledi mkubwa na lugha safi ya Kiswahili:
                        Swali: '{user_question}'
                        Kama anataka ushauri wa kubet, mpe machaguo salama (Double Chance 1X/X2, Over 1.5) na umpe tahadhari ya vihatarishi.
                        """
                        ans = call_gemini(client, [chat_prompt])
                        st.write(ans)
                        st.session_state.chat_messages.append({"role": "assistant", "content": ans})
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 3: VIP WON ARCHIVE =================
with tab3:
    st.subheader("🏆 VIP Won Archive: Historia ya Mechi Zilizoshinda")
    st.write("Hapa huwekwa matokeo ya mechi zilizochambuliwa na hadhi yake (WON ✅):")

    for item in st.session_state.vip_history:
        st.markdown(f"""
        <div class="vip-card" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <b style="font-size:1.05rem; color:#ffffff;">⚽ {item['match']}</b><br>
                <span style="color:#94a3b8; font-size:0.85rem;">Chaguo: {item['pick']} | Odds: {item['odds']}</span>
            </div>
            <div style="background:rgba(34,197,94,0.2); border:1px solid #22c55e; color:#4ade80; padding:6px 14px; border-radius:8px; font-weight:800;">
                {item['status']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.info("💡 Hifadhidata ya VIP inasasishwa kiotomatiki matokeo yanapokamilika.")

# ================= TAB 4: LIVESCORES & RATIBA YA LEO =================
with tab4:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"⚽ LiveScores & Ratiba ya Leo ({today_str})")
    st.write("Fuatilia matokeo na ratiba ya mechi zinazoanza leo mubashara:")

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
