import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime

# Usanidi wa Ukurasa
st.set_page_config(
    page_title="BetPro VIP - AI Intelligence Syndicate",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# KUSOMA API KEY KUTOKA KWENYE MAFUTA YA SIRI (SECRETS) BILA MTU KUJUA
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Kumbukumbu za Mazungumzo na Historia
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "vip_history" not in st.session_state:
    st.session_state.vip_history = [
        {"match": "Arsenal vs Wolves", "pick": "Arsenal 1X & Over 1.5", "status": "WON ✅", "odds": "1.32"},
        {"match": "Inter Milan vs Venezia", "pick": "Inter Milan Win", "status": "WON ✅", "odds": "1.25"},
        {"match": "Monza vs Napoli", "pick": "Napoli Double Chance (X2)", "status": "WON ✅", "odds": "1.28"},
        {"match": "Bologna vs AC Milan", "pick": "Over 1.5 Goals", "status": "WON ✅", "odds": "1.30"},
    ]

# CSS MAALUM YA KUFICHA MANAGE APP, GITHUB, FOOTER NA WATERMARKS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { 
        background: #0b1120; 
        color: #f8fafc; 
    }
    
    /* 1. FICHA HEADER YA STREAMLIT, GITHUB ICON NA FORK BUTTON */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0%;
    }
    
    /* 2. FICHA MANAGE APP BUTTON CHINI KULIA NA STREAMLIT BADGES */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob, 
    .manageAppContainer, 
    [data-testid="manage-app-button"], 
    [class*="manageApp"], 
    [class*="viewerBadge"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* 3. FICHA KILE KIALAMA CHA DEPLOY AU GITHUB JUU KULIA */
    .stAppDeployButton {display: none;}
    
    /* 4. DESIGN YA KISASA YA VIP */
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
    
    .stChatInputContainer textarea {
        color: #ffffff !important;
        background-color: #1e293b !important;
        border: 1px solid #38bdf8 !important;
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

# Function ya Kuita Gemini kwa Kasi
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

tab1, tab2, tab3, tab4 = st.tabs([
    "📸 Kichambuzi cha Mechi (VIP Slip)", 
    "💬 Muulize Mtaalamu (Football AI Chat)", 
    "🏆 VIP Won Archive (Rekodi ya Tiki)", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1: SCANNER =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.markdown(f"""
    <div class="vip-card">
        <h4 style="margin:0 0 8px 0; color:#38bdf8;">🎯 Pakia Screenshot ya Mechi za Leo ({today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Pakia picha ya mechi. Mfumo wa AI utakagua H2H, utaondoa mitego, na kukupa <b>Best of the Day & Ticket A/B</b> moja kwa moja.
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
        raw_img = Image.open(uploaded_file).convert("RGB")
        max_size = (1024, 1024)
        raw_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        st.image(raw_img, caption="Screenshot Tayari kwa Uchambuzi", use_container_width=True)

        if st.button("🚀 Anza Uchambuzi wa Haraka", key="btn_run_vip"):
            if not api_key:
                st.error("Hitilafu ya Mfumo: Wasiliana na Utawala kupata ruhusa ya VIP!")
            else:
                with st.spinner("AI inachakata picha mara moja..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (VIP Betting Manager).
                        Leo ni tarehe {today_str}. Mtaji: '{user_stake}'. Mfumo: '{target_mode}'.

                        KAZI YAKO:
                        1. ONDOA mechi zilizokwisha chezwa au zilizoanza. Tumia mechi zijazo za leo pekee.
                        2. BEST OF THE DAY (Uhakika 85%+): Mechi 2 hadi 4 bora zenye H2H thabiti na motisha ya pointi.
                        3. TRAP ALERT: Taja timu kubwa yenye mtego wa kuepuka.
                        4. UGAWAJI WA MTAJI: Gawanya {user_stake} kwenye Ticket A (70%) na Ticket B (30%).

                        Jibu kwa Kiswahili chenye mpangilio safi na mfupi wa moja kwa moja.
                        """
                        result_text = call_gemini_fast(client, [prompt, raw_img])
                        st.success("✅ Uchambuzi Umekamilika!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: CHATBOT =================
with tab2:
    st.subheader("💬 Ongea na Mtaalamu wa Soka wa AI")
    st.write("Uliza swali kuhusu mechi yoyote au dokezo la ushindi:")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_question = st.chat_input("Andika swali lako hapa...")

    if user_question:
        st.session_state.chat_messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)

        if not api_key:
            st.error("Hitilafu ya Mfumo: Wasiliana na Utawala!")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Inajibu mara moja..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        chat_prompt = f"Wewe ni Mchambuzi wa Soka wa Kimataifa. Jibu swali hili kwa Kiswahili na weledi mfupi wa moja kwa moja: '{user_question}'"
                        ans = call_gemini_fast(client, [chat_prompt])
                        st.write(ans)
                        st.session_state.chat_messages.append({"role": "assistant", "content": ans})
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 3: VIP WON ARCHIVE =================
with tab3:
    st.subheader("🏆 VIP Won Archive: Historia ya Mechi Zilizoshinda")
    st.write("Hapa huwekwa rekodi za mechi zilizochambuliwa na matokeo yake:")
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

# ================= TAB 4: LIVESCORES =================
with tab4:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"⚽ LiveScores & Ratiba ya Leo ({today_str})")
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
