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

# Kumbukumbu za Mazungumzo na Correct Score History
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
st.markdown('<p class="hero-sub">Kikokotozi cha Uhakika: Tiketi 1 (Safe 2 Odds), Tiketi 2 (Multiplier), na Tiketi 3 (Correct Score Mechi 2 Tu).</p>', unsafe_allow_html=True)

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
    "📸 Kichambuzi cha Mechi (Mikeka 3 ya VIP)", 
    "🎯 Correct Score Vault (Rekodi za Jana/Leo)", 
    "💬 Muulize Mtaalamu (Football AI Chat)", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1: SCANNER & 3 TICKETS =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.markdown(f"""
    <div class="vip-card">
        <h4 style="margin:0 0 8px 0; color:#38bdf8;">🎯 Pakia Screenshot ya Mechi za Leo ({today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Pakia picha ya mechi unazotaka kubetia. AI itazikagua zote, itaondoa mitego, na kuzigawa katika: 
            <b>Tiketi 1 (Safe 2 Odds)</b>, <b>Tiketi 2 (Multiplier)</b>, na <b>Tiketi 3 (Correct Score Mechi 2 Tu)</b> pamoja na mgao sahihi wa mtaji ili usipoteze pesa.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file = st.file_uploader("Pakia Screenshot ya Mechi:", type=["png", "jpg", "jpeg"], key="vip_uploader")
    with col2:
        user_stake = st.text_input("Mtaji Wako wa Leo (Mfano: TZS 10,000 au TZS 30,000):", value="TZS 20,000")

    if uploaded_file is not None:
        raw_img = Image.open(uploaded_file).convert("RGB")
        max_size = (1024, 1024)
        raw_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        st.image(raw_img, caption="Screenshot Tayari kwa Uchambuzi", use_container_width=True)

        if st.button("🚀 Anza Uchambuzi wa Uhakika (Tengeneza Mikeka 3)", key="btn_run_vip"):
            if not api_key:
                st.error("Hitilafu: Weka GEMINI_API_KEY kwenye Secrets za Streamlit!")
            else:
                with st.spinner("AI inachambua takwimu halisi, H2H, na kuandaa Mikeka 3 ya kulinda mtaji..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Kudhibiti Upotevu wa Pesa kwenye Kubashiri (Senior Risk & Betting Manager).
                        Leo ni tarehe {today_str}. Mtaji wa mtumiaji kwa leo ni: '{user_stake}'.
                        
                        KANUNI KUU YA MTUMIAJI: "HATAKI KUPOTEZA PESA, ANATAKA KULINDA MTAJI NA KUPATA FAIDA NDOGO NDOGO YA UHAKIKA."

                        KAZI YAKO KWENYE SCREENSHOT HII:
                        1. ONDOA KABISA mechi yoyote iliyokwisha chezwa au ya jana. Tumia mechi za leo ambazo HAZIJAANZA tu.
                        2. ONDOA MITEGO YA WAZI (TRAP ALERT): Taja timu yoyote kubwa kwenye picha ambayo ina mtego wa kutoa sare au kufungwa.
                        
                        3. TENGENEZA MIKEKA MITATU (3 SMART SLIPS):
                        
                           🎫 **TIKETI 1: TIKETI YA CHUMA (SAFE 2 ODDS - UHAKIKA 90%+):**
                           - Chagua mechi 2 tu salama kabisa (mfano: Double Chance 1X/X2, Over 1.5 Goals, Draw No Bet).
                           - Lengo: Hii tiketi ndiyo ya uhakika wa kulinda mtaji.

                           🚀 **TIKETI 2: TIKETI YA FAIDA (MULTIPLIER - ODDS 3.50 HADI 5.00):**
                           - Chagua mechi 3 zenye faida nzuri lakini zilizolindwa vizuri (mfano: Over 2.5 au Win Either Half).
                           - Lengo: Kukuza mtaji taratibu.

                           🎯 **TIKETI 3: VIP CORRECT SCORE (MECHI 2 TU BASI!):**
                           - Kutoka mechi zote za picha, teua MECHI 2 TU zenye uwezekano mkubwa zaidi wa kutoa matokeo kamili.
                           - Kwa kila mechi taja Matokeo Makuu (mfano 2-0 au 2-1) na Matokeo Mbadala ya Kinga (mfano 1-0 au 1-1).

                        4. 💰 **MGAO WA PESA KISAYANSI (KWA MTAJI WA {user_stake}):**
                           - Piga hesabu ya pesa halisi ya kuweka kwenye TIKETI 1 (Weka 70% ya mtaji).
                           - Piga hesabu ya pesa halisi ya kuweka kwenye TIKETI 2 (Weka 20% ya mtaji).
                           - Piga hesabu ya pesa halisi ya kuweka kwenye TIKETI 3 (Weka 10% tu ya mtaji kwenye Correct Score).
                           - Eleza kwanini hata Tiketi 2 na 3 zikikosa, Tiketi 1 pekee itarudisha mtaji wote pamoja na faida!

                        Toa majibu kwa Kiswahili fasaha, nambari na mpangilio safi wa kitaalamu.
                        """
                        result_text = call_gemini_fast(client, [prompt, raw_img])
                        st.success("✅ Uchambuzi na Mikeka 3 ya Uhakika Imekamilika!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: CORRECT SCORE VAULT =================
with tab2:
    st.subheader("🎯 VIP Correct Score Vault: Rekodi za Jana na Leo")
    st.write("Fuatilia mechi 2 za Correct Score zilizotabiriwa na uone matokeo halisi kama **ZILITOA ✅** au **ZILICHANA ❌**:")

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

    st.markdown("---")
    with st.expander("⚙️ Admin Panel: Sajili Matokeo ya Correct Score ya Jana"):
        with st.form("cs_form"):
            c_date = st.text_input("Tarehe ya Mechi", value=datetime.now().strftime("%d-%m-%Y"))
            c_match = st.text_input("Jina la Mechi (Mfano: Real Madrid vs Osasuna)")
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
    st.write("Uliza swali kuhusu mechi au dokezo la soka:")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_question = st.chat_input("Andika swali lako hapa...")

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
                        chat_prompt = f"Wewe ni Mchambuzi wa Soka wa Kimataifa. Jibu swali hili kwa Kiswahili na weledi: '{user_question}'"
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
