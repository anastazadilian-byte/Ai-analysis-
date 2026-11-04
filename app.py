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

# KUSOMA API KEY KUTOKA KWENYE SECRETS
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Styling ya Kisasa
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { 
        background: #090e17; 
        color: #f8fafc; 
    }
    
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
st.markdown('<p class="title-text">Kichambuzi cha Mechi & Jenereta ya Bango la Picha</p>', unsafe_allow_html=True)
st.write("Pakia screenshot ya mechi za leo, AI itafanya uchambuzi wa kina na kukutengenezea bango safi lenye vibao vyeupe tayari kupostiwa!")

# FUNCTION YA KUITA AI INAYOTAFUTA MODELS ZILIZO HAI MOJA KWA MOJA
def get_ai_analysis(client, contents):
    # 1. Uliza Google models zilizopo kwenye hii API key sasa hivi
    active_models = []
    try:
        for m in client.models.list():
            m_name = getattr(m, 'name', '') or str(m)
            # Epuka matoleo ya zamani yaliyofutwa (kama 1.5)
            if "1.5" not in m_name:
                active_models.append(m_name)
    except Exception:
        pass

    # Kipaumbele kwa models za Flash (haraka na nzuri sana kwa kusoma picha)
    flash_models = [m for m in active_models if "flash" in m.lower()]
    other_models = [m for m in active_models if m not in flash_models]
    final_list = flash_models + other_models

    # Kama orodha haikurudi, tumia matoleo mapya yaliyopo rasmi
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

# TABS MBILI TU
tab1, tab2 = st.tabs(["📸 Kichambuzi cha Mechi & Bango", "⚽ LiveScores Mubashara"])

# ================= TAB 1: UCHAMBUZI =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    day_name = datetime.now().strftime("%A")
    
    st.markdown(f"""
    <div class="card-box">
        <h4 style="margin:0 0 6px 0; color:#10b981;">🎯 Pakia Screenshot za Mechi ({day_name} - {today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#94a3b8;">
            Unaweza kupakia screenshot 1 au nyingi kwa mkupuo. AI itasoma mechi zote, itagundua mitego ya makampuni na kuunda bango la kisasa.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        uploaded_files = st.file_uploader(
            "1. Pakia Screenshot za Mechi:", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
    with c2:
        poster_title = st.text_input("Kichwa cha Bango la Picha:", value=f"{day_name} VIP Picks")
        pick_count = st.selectbox(
            "Idadi ya Mechi kwenye Bango:",
            ["Mechi 4 za Uhakika (Kama Muundo Wako)", "Mechi 2 za Chuma (Safe 2 Odds)", "Treni la Mechi 6-8", "Mechi Zote Zilizopo Kwenye Picha"]
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
                st.image(img, caption=f"Mechi {i+1}", use_container_width=True)

        if st.button("🚀 Anza Uchambuzi & Unda Bango la Picha", key="btn_run"):
            if not api_key:
                st.error("Hitilafu: GEMINI_API_KEY haipo kwenye Secrets! Hakikisha umeiweka.")
            else:
                with st.spinner("AI inasoma mechi zote, inasanua mitego ya bookies na kuandaa bango la picha..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka na Mchambuzi wa Mitego ya Kubeti (Pro Anti-Trap Betting Analyst).
                        Leo ni tarehe {today_str}. Lengo la bango: '{pick_count}'.

                        MASHARTI MAKALI YA UCHAMBUZI:
                        1. SOMA PICHA KWA MAKINI: Tambua mechi zote zilizoonyeshwa kwenye screenshot (timu ya nyumbani na ugenini).
                        2. TUPA KABISA mechi zilizokwisha au zilizopita.
                        3. KUGUNDUA MITEGO YA BOOKIES: 
                           - Angalia timu zenye mitego ya odds ndogo lakini zina majeruhi, uchovu au ziko ugenini. 
                           - Kataa 'Direct Win' zenye mitego na badala yake chagua 'Double Chance' (1X/X2) au 'Over 1.5 Goals'.
                        4. Chagua timu zilizonyooka zaidi zenye uhakika wa 90%+.

                        MUUNDO WA MAJIBU YAKO UWE HUU BILA KUBADILI:
                        
                        [SEHEMU YA BANGO]
                        Orodhesha mechi zilizoteuliwa tu (kila timu na tip yake kwenye mstari wake, na nyota mbele) mfano:
                        ★ Real Madrid (Win au 1X)
                        ★ Liverpool (Over 1.5)
                        ★ Arsenal (Win)
                        ★ Dortmund (GG au Over 1.5)

                        [SEHEMU YA UCHAMBUZI WA KINA]
                        Eleza kwa Kiswahili:
                        - ⚠️ Mitego iliyogunduliwa kwenye mechi hizi (nini cha kuepuka).
                        - Sababu za kiufundi kwa nini tips hizi zitatepeli bookies leo.
                        - Ushauri wa kiasi cha mtaji ili kulinda faida.
                        """
                        
                        contents = [prompt] + processed_images
                        result_text = get_ai_analysis(client, contents)
                        
                        # Tenganisha Sehemu ya Bango na Sehemu ya Uchambuzi
                        banner_items = []
                        if "[SEHEMU YA BANGO]" in result_text and "[SEHEMU YA UCHAMBUZI WA KINA]" in result_text:
                            part_banner = result_text.split("[SEHEMU YA BANGO]")[1].split("[SEHEMU YA UCHAMBUZI WA KINA]")[0]
                            for l in part_banner.strip().split("\n"):
                                clean = l.replace("★", "").replace("-", "").replace("*", "").strip()
                                if clean:
                                    banner_items.append(clean)
                        else:
                            lines = [l.strip() for l in result_text.split("\n") if l.strip()]
                            banner_items = [l.replace("★", "").replace("*", "") for l in lines[:6]]

                        st.success("✅ Uchambuzi na Bango Vimekamilika!")
                        st.markdown("---")
                        
                        # ================= HTML5 CANVAS POSTER =================
                        st.subheader("🖼️ Bango Lako la Picha (Tayari Kupakuliwa)")
                        
                        strips_html = ""
                        for team in banner_items[:8]:
                            strips_html += f"""
                            <div style="background:#ffffff; color:#000000; padding:16px 20px; margin:12px 0; border-radius:8px; font-size:26px; font-weight:800; display:flex; align-items:center; box-shadow:0 6px 14px rgba(0,0,0,0.18);">
                                <span style="font-size:28px; margin-right:16px; color:#10b981;">★</span>
                                <span>{team}</span>
                            </div>
                            """

                        canvas_code = f"""
                        <div id="capture-area" style="width:580px; background:#00c82b; padding:40px 30px; border-radius:18px; font-family:'Plus Jakarta Sans', Arial, sans-serif; box-sizing:border-box; margin:auto;">
                            <h1 style="color:#000000; text-align:center; font-size:42px; font-weight:900; margin:0 0 25px 0; letter-spacing:-1px;">
                                {poster_title}
                            </h1>
                            <div>
                                {strips_html}
                            </div>
                            <div style="text-align:center; margin-top:20px; color:#000000; font-size:14px; font-weight:800; letter-spacing:1px;">
                                👑 BETPRO TACTICAL TERMINAL • ANTI-TRAP PICKS
                            </div>
                        </div>

                        <div style="text-align:center; margin-top:25px;">
                            <button onclick="downloadPoster()" style="background:#090e17; color:#10b981; border:2px solid #10b981; padding:12px 28px; border-radius:10px; font-size:16px; font-weight:800; cursor:pointer;">
                                📥 Bofya Hapa Kupakua Picha ya Bango (PNG)
                            </button>
                        </div>

                        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                        <script>
                            function downloadPoster() {{
                                var target = document.getElementById("capture-area");
                                html2canvas(target, {{ scale: 2 }}).then(function(canvas) {{
                                    var link = document.createElement('a');
                                    link.download = '{poster_title.replace(" ", "_")}.png';
                                    link.href = canvas.toDataURL("image/png");
                                    link.click();
                                }});
                            }}
                        </script>
                        """
                        components.html(canvas_code, height=680, scrolling=True)
                        
                        # Sehemu ya Kusoma Uchambuzi wa Mitego
                        st.markdown("---")
                        with st.expander("🛡️ Ripoti ya Ujasusi wa Mitego & Mbinu za Mechi Hizi", expanded=True):
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
