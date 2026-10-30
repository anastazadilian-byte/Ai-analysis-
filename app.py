import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime

# Usanidi wa Ukurasa wa VIP
st.set_page_config(
    page_title="BetPro VIP - AI Intelligence Syndicate",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# KUSOMA API KEY KUTOKA KWENYE SECRETS
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Kumbukumbu za Mazungumzo na Kumbukumbu ya Correct Score
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "cs_history" not in st.session_state:
    st.session_state.cs_history = [
        {"date": "29-10-2026", "match": "Venezia vs Inter Milan", "pred": "0 - 2", "actual": "0 - 2", "status": "ILITOA! WON ✅", "odds": "6.50"},
        {"date": "29-10-2026", "match": "Monza vs Napoli", "pred": "0 - 2", "actual": "1 - 4", "status": "ILICHANA ❌", "odds": "7.00"}
    ]

# Theme Safi ya VIP
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { 
        background: #0b1120; 
        color: #f8fafc; 
    }
    
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stAppDeployButton { display: none; }
    
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
st.markdown('<p class="hero-sub">Scanner ya Mechi, Ushauri wa Maswali (Chat AI), na Jenereta ya Correct Score Zenye Rekodi za Uhakika.</p>', unsafe_allow_html=True)

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
    "📸 Kichambuzi cha Mechi (VIP Slip & Correct Score)", 
    "🎯 Correct Score Vault (Rekodi za Jana/Leo)", 
    "💬 Muulize Mtaalamu (Football AI Chat)", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1: SCANNER =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.markdown(f"""
    <div class="vip-card">
        <h4 style="margin:0 0 8px 0; color:#38bdf8;">🎯 Pakia Screenshot ya Mechi za Leo ({today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Pakia picha ya mechi. Mfumo utakagua H2H, utachuja mitego, na <b>kuteua mechi 2 bora pekee zenye uwezekano wa kutoa Correct Score</b> pamoja na Ticket A/B.
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
                "👑 VIP Suite Kamili (Best of Day + Mechi 2 za Correct Score + Mtaji)",
                "🎯 Correct Score Pekee (Mechi 2 Bora za Matokeo Kamili)",
                "🔥 Sure 2 Odds Pekee (Mechi Salama za Kulinda Mtaji)"
            ]
        )

    if uploaded_file is not None:
        raw_img = Image.open(uploaded_file).convert("RGB")
        max_size = (1024, 1024)
        raw_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        st.image(raw_img, caption="Screenshot Tayari kwa Uchambuzi", use_container_width=True)

        if st.button("🚀 Anza Uchambuzi wa Kina na Correct Score", key="btn_run_vip"):
            if not api_key:
                st.error("Hitilafu: Weka GEMINI_API_KEY kwenye Secrets za Streamlit!")
            else:
                with st.spinner("AI inachambua H2H, xG ya timu zote na kupiga hesabu ya Correct Score..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (VIP Correct Score & Risk Analyst).
                        Leo ni tarehe {today_str}. Mtaji: '{user_stake}'. Mfumo: '{target_mode}'.

                        KAZI YAKO KWENYE PICHA HII:
                        1. ONDOA mechi zilizokwisha chezwa au zilizoanza. Tumia mechi zijazo za leo pekee.
                        2. BEST OF THE DAY (Uhakika 85%+): Mechi 2 hadi 4 bora zenye H2H thabiti.
                        
                        3. 🎯 UCHAMBUZI WA CORRECT SCORE (MECHI 2 BORA ZA LEO):
                           - Kutoka kwenye mechi zote za picha, chagua MECHI 2 TU zenye uwezekano mkubwa zaidi wa kutoa matokeo kamili (Correct Score).
                           - Kwa kila mechi taja:
                             a) Matokeo Kamili Makuu (Primary Expected Score - mfano 2-0 au 2-1).
                             b) Matokeo Mbadala ya Kinga (Cover Score - mfano 1-0 au 1-1).
                             c) Sababu za kiufundi za safu ya ulinzi na ufungaji wa magoli (xG).
                             d) Makadirio ya Odds (mfano Odds 6.50 hadi 9.00).

                        4. UGAWAJI WA MTAJI KWA {user_stake}: Panga mgao wa pesa kwa tiketi salama na Correct Score.

                        Jibu kwa Kiswahili chenye mpangilio safi, nambari na kadi za kusomeka wazi.
                        """
                        result_text = call_gemini_fast(client, [prompt, raw_img])
                        st.success("✅ Uchambuzi na Correct Score Zimekamilika!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: CORRECT SCORE VAULT =================
with tab2:
    st.subheader("🎯 VIP Correct Score Vault: Rekodi za Jana na Leo")
    st.write("Fuatilia mechi za Correct Score zilizotabiriwa na uone kama **ZILITOA ✅** au **ZILICHANA ❌**:")

    # Orodha ya Historia
    for item in st.session_state.cs_history:
        is_won = "WON" in item["status"]
        status_bg = "rgba(34,197,94,0.2)" if is_won else "rgba(239,68,68,0.2)"
        status_border = "#22c55e" if is_won else "#ef4444"
        status_color = "#4ade80" if is_won else "#f87171"
        
        st.markdown(f"""
        <div class="vip-card" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="color:#38bdf8; font-size:0.8rem; font-weight:700;">📅 TAREHE: {item['date']}</span><br>
                <b style="font-size:1.1rem; color:#ffffff;">⚽ {item['match']}</b><br>
                <span style="color:#cbd5e1; font-size:0.9rem;">
                    Utabiri: <b>{item['pred']}</b> | Matokeo Halisi: <b>{item['actual']}</b> | Odds: <b>{item['odds']}</b>
                </span>
            </div>
            <div style="background:{status_bg}; border:1px solid {status_border}; color:{status_color}; padding:8px 16px; border-radius:10px; font-weight:800; font-size:0.95rem;">
                {item['status']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Sehemu ya Admin Kusajili Mechi za Correct Score (Kuweka kama Ilitoa au Ilichana)
    st.markdown("---")
    with st.expander("⚙️ Admin Panel: Sajili Matokeo ya Correct Score ya Jana"):
        with st.form("cs_form"):
            c_date = st.text_input("Tarehe ya Mechi", value=datetime.now().strftime("%d-%m-%Y"))
            c_match = st.text_input("Jina la Mechi (Mfano: Arsenal vs Wolves)")
            c_pred = st.text_input("Score Iliyotabiriwa (Mfano: 2 - 0)")
            c_act = st.text_input("Matokeo Halisi Yalivyotoka (Mfano: 2 - 0)")
            c_odds = st.text_input("Odds (Mfano: 7.50)", value="7.00")
            c_outcome = st.radio("Matokeo ya Utabiri:", ["ILITOA! WON ✅", "ILICHANA ❌"])
            
            save_cs = st.form_submit_button("Hifadhi Kwenye Vault")
            if save_cs and c_match:
                st.session_state.cs_history.insert(0, {
                    "date": c_date,
                    "match": c_match,
                    "pred": c_pred,
                    "actual": c_act,
                    "status": c_outcome,
                    "odds": c_odds
                })
                st.success("Rekodi ya Correct Score imehifadhiwa kikamilifu!")
                st.rerun()

# ================= TAB 3: CHATBOT =================
with tab3:
    st.subheader("💬 Ongea na Mtaalamu wa Soka wa AI")
    st.write("Uliza swali kuhusu mechi au dokezo la Correct Score:")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_question = st.chat_input("Andika swali lako hapa... (Mfano: Ni mechi gani ya leo ina nafasi ya kuisha 1-1?)")

    if user_question:
        st.session_state.chat_messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)

        if not api_key:
            st.error("Hitilafu: Weka GEMINI_API_KEY kwenye Secrets!")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Inajibu mara moja..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        chat_prompt = f"Wewe ni Mchambuzi wa Soka wa Kimataifa. Jibu swali hili kuhusu soka au Correct Score kwa Kiswahili na weledi: '{user_question}'"
                        ans = call_gemini_fast(client, [chat_prompt])
                        st.write(ans)
                        st.session_state.chat_messages.append({"role": "assistant", "content": ans})
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

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
