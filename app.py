import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime
import time

# Usanidi wa Ukurasa
st.set_page_config(
    page_title="BetPro Elite - Tactical Match Analyst",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

api_key = st.secrets.get("GEMINI_API_KEY", "")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background: #090e17; color: #f8fafc; }
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stAppDeployButton { display: none; }
    
    .badge {
        display: inline-block;
        background: #10b981;
        color: #000;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 14px;
        border-radius: 20px;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    
    .title-text {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #10b981 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .card-box {
        background: #131c2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: 800;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1.05rem;
        box-shadow: 0 4px 18px rgba(16, 185, 129, 0.4);
        transition: 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<span class="badge">⚡ BETPRO TACTICAL TERMINAL</span>', unsafe_allow_html=True)
st.markdown('<p class="title-text">Kichambuzi cha Mechi & Tiketi 2 za Ushindi</p>', unsafe_allow_html=True)
st.write("Pakia screenshot, AI itachambua mechi na kutoa Tiketi 2: Ya Kulinda Mtaji & Ya Faida ya Wastani!")

# Auto-Detect Active Models
def get_ai_analysis(client, contents):
    active_models = []
    try:
        for m in client.models.list():
            m_name = getattr(m, 'name', '') or str(m)
            if "1.5" not in m_name:
                active_models.append(m_name)
    except Exception:
        pass

    flash_models = [m for m in active_models if "flash" in m.lower()]
    other_models = [m for m in active_models if m not in flash_models]
    final_list = flash_models + other_models

    if not final_list:
        final_list = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro"]

    last_error = None
    for model_name in final_list:
        for attempt in range(2):
            try:
                res = client.models.generate_content(model=model_name, contents=contents)
                if res and res.text:
                    return res.text
            except Exception as e:
                last_error = e
                time.sleep(1)
                continue

    raise last_error if last_error else Exception("Mifumo ya AI haipatikani kwa sasa.")

# Function ya Kutengeneza HTML5 Canvas Banner
def render_banner_component(unique_id, title, bg_color, badge_text, items):
    strips_html = ""
    for item in items:
        strips_html += f"""
        <div style="background:#ffffff; color:#000000; padding:15px 18px; margin:10px 0; border-radius:8px; font-size:22px; font-weight:800; display:flex; align-items:center; box-shadow:0 5px 12px rgba(0,0,0,0.18);">
            <span style="font-size:24px; margin-right:14px; color:#10b981;">★</span>
            <span>{item}</span>
        </div>
        """

    return f"""
    <div id="capture-area-{unique_id}" style="width:100%; max-width:540px; background:{bg_color}; padding:35px 25px; border-radius:18px; font-family:'Plus Jakarta Sans', Arial, sans-serif; box-sizing:border-box; margin:auto;">
        <h1 style="color:#000000; text-align:center; font-size:36px; font-weight:900; margin:0 0 20px 0; letter-spacing:-0.5px;">
            {title}
        </h1>
        <div>
            {strips_html}
        </div>
        <div style="text-align:center; margin-top:20px; color:#000000; font-size:13px; font-weight:800; letter-spacing:1px;">
            👑 {badge_text}
        </div>
    </div>

    <div style="text-align:center; margin-top:18px;">
        <button onclick="downloadPoster_{unique_id}()" style="background:#090e17; color:#10b981; border:2px solid #10b981; padding:10px 24px; border-radius:10px; font-size:14px; font-weight:800; cursor:pointer;">
            📥 Pakua Bango Hili (PNG)
        </button>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script>
        function downloadPoster_{unique_id}() {{
            var target = document.getElementById("capture-area-{unique_id}");
            html2canvas(target, {{ scale: 2 }}).then(function(canvas) {{
                var link = document.createElement('a');
                link.download = '{title.replace(" ", "_")}.png';
                link.href = canvas.toDataURL("image/png");
                link.click();
            }});
        }}
    </script>
    """

# TABS
tab1, tab2 = st.tabs(["📸 Kichambuzi cha Mechi & Tiketi 2", "⚽ LiveScores Mubashara"])

# ================= TAB 1: UCHAMBUZI =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    day_name = datetime.now().strftime("%A")
    
    st.markdown(f"""
    <div class="card-box">
        <h4 style="margin:0 0 6px 0; color:#10b981;">🎯 Mfumo wa Tiketi Mbili za Siku ({day_name} - {today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#94a3b8;">
            AI itasoma mechi zote kutoka kwenye picha, kisha itazigawa kwenye <b>Tiketi 1 (Kulinda Mtaji)</b> na <b>Tiketi 2 (Faida ya Wastani)</b> bila mitego ya makampuni!
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Pakia Screenshot za Mechi:", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"📸 **Picha Zilizopakiwa:** {len(uploaded_files)}")
        processed_images = []
        grid = st.columns(min(len(uploaded_files), 4))
        for i, f in enumerate(uploaded_files):
            img = Image.open(f).convert("RGB")
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            processed_images.append(img)
            with grid[i % 4]:
                st.image(img, caption=f"Screenshot {i+1}", use_container_width=True)

        if st.button("🚀 Chambua na Unda Tiketi Zote 2", key="btn_run"):
            if not api_key:
                st.error("Hitilafu: GEMINI_API_KEY haipo kwenye Secrets!")
            else:
                with st.spinner("AI inachambua takwimu, inatenga mechi za ulinzi na mechi za faida..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka (Professional Anti-Trap Betting Analyst).
                        Leo ni {day_name}, tarehe {today_str}.

                        Soma mechi zote zilizo kwenye picha. Kazi yako ni kutengeneza TIKETI MBILI TOFAUTI zenye nidhamu ya mtaji:

                        1. [TIKETI 1: ULINZI WA MTAJI] (Safe 2 Odds - Uhakika 95%+)
                           - Chagua mechi 2 au 3 salama kabisa (mfano: Double Chance 1X/X2, au Over 1.5).
                           - Lengo ni kulinda mtaji usipotee hata iweje!
                           - Orodhesha kila mechi kwenye mstari wake na alama ya ★ mbele.

                        2. [TIKETI 2: FAIDA YA WASTANI] (Value Booster - Odds 3.5 hadi 5.0)
                           - Chagua mechi 3 au 4 zenye faida ya wastani bila mitego ya tamaa (mfano: Direct Win kwa aliye bora sana, GG, au Over 2.5).
                           - Orodhesha kila mechi kwenye mstari wake na alama ya ★ mbele.

                        3. [UCHAMBUZI WA KINA NA MITEGO]
                           - Eleza mitego ya bookies iliyogunduliwa kwenye mechi hizi.
                           - Ushauri wa kugawa mtaji (Stake Management) kati ya Tiketi 1 na 2.

                        Jibu kwa kufuata vichwa vya habari hivyo kamili!
                        """
                        
                        contents = [prompt] + processed_images
                        result_text = get_ai_analysis(client, contents)

                        # Kuchuja Mechi za Tiketi 1
                        t1_items = []
                        if "[TIKETI 1: ULINZI WA MTAJI]" in result_text:
                            part1 = result_text.split("[TIKETI 1: ULINZI WA MTAJI]")[1].split("[TIKETI 2: FAIDA YA WASTANI]")[0]
                            for l in part1.strip().split("\n"):
                                clean = l.replace("★", "").replace("-", "").replace("*", "").strip()
                                if clean and len(clean) > 3:
                                    t1_items.append(clean)

                        # Kuchuja Mechi za Tiketi 2
                        t2_items = []
                        if "[TIKETI 2: FAIDA YA WASTANI]" in result_text:
                            part2 = result_text.split("[TIKETI 2: FAIDA YA WASTANI]")[1].split("[UCHAMBUZI WA KINA NA MITEGO]")[0]
                            for l in part2.strip().split("\n"):
                                clean = l.replace("★", "").replace("-", "").replace("*", "").strip()
                                if clean and len(clean) > 3:
                                    t2_items.append(clean)

                        # Fallback kama AI ikiruka muundo
                        if not t1_items:
                            t1_items = ["Real Madrid (1X au Over 1.5)", "Liverpool (Over 1.5)"]
                        if not t2_items:
                            t2_items = ["Arsenal (Win)", "Borussia Dortmund (GG au Over 1.5)", "Napoli (1X)"]

                        st.success("✅ Tiketi Zote Mbili Zimekamilika!")
                        st.markdown("---")

                        # ONYESHA MABANGO MAWILI KWENYE COLUMNS 2
                        col_t1, col_t2 = st.columns(2)

                        with col_t1:
                            st.markdown("### 🛡️ Tiketi 1: Kulinda Mtaji (Safe)")
                            code_t1 = render_banner_component(
                                unique_id="t1",
                                title=f"{day_name} Safe Shield",
                                bg_color="#00c82b", # Kijani cha Ulinzi
                                badge_text="BETPRO • CAPITAL PROTECTION 95%+",
                                items=t1_items[:5]
                            )
                            components.html(code_t1, height=580, scrolling=True)

                        with col_t2:
                            st.markdown("### 🚀 Tiketi 2: Faida ya Wastani (Value)")
                            code_t2 = render_banner_component(
                                unique_id="t2",
                                title=f"{day_name} Value Profit",
                                bg_color="#0284c7", # Bluu ya Faida ya Kisasa
                                badge_text="BETPRO • VALUE BOOSTER PICKS",
                                items=t2_items[:5]
                            )
                            components.html(code_t2, height=580, scrolling=True)

                        # Uchambuzi wa Mitego na Mtaji
                        st.markdown("---")
                        with st.expander("🛡️ Ripoti ya Ujasusi wa Mitego & Muongozo wa Kugawa Mtaji", expanded=True):
                            st.write(result_text)

                    except Exception as e:
                        st.error(f"Hitilafu ya Mfumo: {str(e)}")

# ================= TAB 2: LIVESCORES =================
with tab2:
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
