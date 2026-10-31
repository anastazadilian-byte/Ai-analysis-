import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime

# Usanidi wa Ukurasa wa Kipekee (Private Terminal)
st.set_page_config(
    page_title="BetPro Elite - Private Tactical Syndicate",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# KUSOMA API KEY KUTOKA KWENYE SECRETS
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Theme ya Kisasa
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
    
    .elite-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #fff; font-weight: 800; font-size: 0.75rem;
        padding: 4px 14px; border-radius: 20px; letter-spacing: 1px;
        margin-bottom: 8px; text-transform: uppercase;
    }
    
    .hero-title {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub { color: #94a3b8; font-size: 0.95rem; margin-top: 5px; margin-bottom: 25px; }
    
    .box-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        color: #ffffff;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white; font-weight: 700; border: none; border-radius: 10px;
        padding: 0.7rem 1.6rem; transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #1d4ed8 100%);
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<span class="elite-badge">⚡ UNLIMITED PRIVATE TERMINAL</span>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">BetPro Elite: Jicho la Kijasusi & Mjenzi wa Treni</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Hakuna kikomo cha uchambuzi. Pakia picha nyingi za mechi za leo au wikiendi na upate Tiketi Salama au Treni la Pesa Nyingi.</p>', unsafe_allow_html=True)

# Function ya Kuita AI kwa Kasi
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

# TABS MBILI TU
tab1, tab2 = st.tabs([
    "📸 Kichambuzi cha Mechi & Mjenzi wa Treni", 
    "⚽ LiveScores & Ratiba ya Leo"
])

# ================= TAB 1: UCHAMBUZI BILA KIKOMO =================
with tab1:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.markdown(f"""
    <div class="box-card">
        <h4 style="margin:0 0 6px 0; color:#38bdf8;">🎯 Pakia Screenshot za Mechi (Bila Kikomo - {today_str})</h4>
        <p style="margin:0; font-size:0.9rem; color:#cbd5e1;">
            Unaweza kupakia <b>screenshot 1 hadi 10 kwa wakati mmoja</b> kutoka SportyBet, BetPawa, au FlashScore. 
            Chagua kama unataka <b>Mikeka 2 ya Kulinda Mtaji</b> au <b>Treni Refu la Pesa Nyingi kwa Mtaji Mdogo</b>!
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Pakia Screenshot za Mechi (Ruhusa ya Picha Nyingi):", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True,
            key="elite_unlimited_uploader"
        )
    with col2:
        bet_objective = st.radio(
            "Chagua Lengo la Uchambuzi:",
            [
                "🛡️ Mikeka 2 ya Uhakika (Tiketi 1 ya 2 Odds + Tiketi 2 ya Faida)",
                "🚂 MKEKA WA TRENI LA KISAYANSI (Mechi 10-20 Salama Zaidi - Pesa Nyingi kwa Mtaji Mdogo)"
            ]
        )
        user_stake = st.text_input("Mtaji Wako (Mfano: TZS 1,000 au TZS 20,000):", value="TZS 2,000")

    if uploaded_files:
        st.write(f"📸 **Umeingiza Jumla ya Picha:** {len(uploaded_files)} (Tayari kuchakatwa)")
        processed_images = []
        cols = st.columns(min(len(uploaded_files), 4))
        for idx, file in enumerate(uploaded_files):
            img = Image.open(file).convert("RGB")
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            processed_images.append(img)
            with cols[idx % 4]:
                st.image(img, caption=f"Picha {idx+1}", use_container_width=True)

        if st.button("🚀 Anza Uchambuzi Kabambe (Unlimited AI Run)", key="btn_run_unlimited"):
            if not api_key:
                st.error("Hitilafu: GEMINI_API_KEY haipo kwenye Secrets! Hakikisha umeiweka.")
            else:
                with st.spinner(f"AI inachambua mechi zote kutoka kwenye picha {len(processed_images)}, mbinu za makocha na fomu za timu..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        prompt = f"""
                        Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka na Mtaalamu wa Kudhibiti Upotevu wa Pesa (Master Betting Analyst).
                        Leo ni tarehe {today_str}. Mtaji wa mtumiaji ni: '{user_stake}'. Lengo alilochagua: '{bet_objective}'.

                        KAZI YAKO KWENYE PICHA HIZI ZOTE:
                        1. Kagua masaa na tarehe: TUPA KABISA mechi ambazo tayari zimeshaanza, zimeisha, au ni za jana. Tumia mechi zijazo za leo au wikiendi pekee ambazo BADO HAZIJAANZA!
                        2. UCHAMBUZI WA KIMBINU WA MAKOCHA: Angalia makocha walio na presha ya kufukuzwa, timu zinazocheza mchezo wa kujilinda sana, na wachezaji majeruhi.
                        3. ONDOA MITEGO YA WAZI (TRAP ALERTS): Taja timu kubwa zilizopo kwenye picha zenye odds za uongo (1.20-1.35) ambazo zinapaswa kuepukwa.

                        4. ANDAA MIKEKA KULINGANA NA LENGO LA MTUMIAJI:
                        """

                        if "MKEKA WA TRENI" in bet_objective:
                            prompt += f"""
                            LENGO NI TRENI LA KISAYANSI LA KUSHINDA PESA NYINGI KWA MTAJI MDOGO WA {user_stake}:
                            - Kutoka kwenye picha zote, chagua MECHI 10 HADI 20 zenye machaguo SALAMA ZAIDI DUNIANI (Uhakika wa 92%+ kila mechi).
                            - USITUMIE masoko ya hatari kama Direct Win kwa timu kubwa za ugenini. Tumia machaguo kama:
                              * Double Chance (1X au X2)
                              * Over 1.5 Goals
                              * Home/Away Over 0.5 (Timu ifunge goli 1 tu)
                              * Draw No Bet (DNB)
                            - Unganisha mechi hizi kuwa Treni Moja Imara lenye jumla ya Odds nzuri (Odds 20 hadi 100+).
                            - Piga hesabu: Weka {user_stake} upate makadirio gani ya faida.
                            """
                        else:
                            prompt += f"""
                            LENGO NI MIKEKA MIWILI TU YA UHAKIKA YA KULINDA MTAJI WA {user_stake}:
                            - 🎫 **TIKETI 1: TIKETI YA CHUMA (SAFE 2.00 ODDS - UHAKIKA 95%+):** Mechi 2 tu salama kabisa za kulinda mtaji.
                            - 🚀 **TIKETI 2: TIKETI YA FAIDA (ODDS 3.50 - 5.00):** Mechi 2 au 3 zenye faida nzuri zilizolindwa.
                            - Panga mgawanyo wa mtaji wa {user_stake} (75% Tiketi 1, 25% Tiketi 2).
                            """

                        prompt += """
                        5. 📱 **MUUNDO WA KUSHAWISHI WA WHATSAPP & FACEBOOK:**
                           Mwishoni kabisa, weka muhtasari safi wenye namba za mechi, majina ya timu, machaguo, na emoji za kuvutia tayari mtumiaji aunakili na kuposti moja kwa moja kwenye magroup!
                        """

                        contents = [prompt] + processed_images
                        result_text = call_gemini_fast(client, contents)
                        st.success("✅ Uchambuzi na Ujenzi wa Mkeka Umekamilika!")
                        st.markdown(result_text)
                        
                        # Kitufe cha kupakua ujumbe wa WhatsApp/Facebook
                        st.download_button(
                            label="📋 Pakua / Nakili Mkeka Huu kwa WhatsApp & Facebook",
                            data=result_text,
                            file_name=f"BetPro_Master_Slip_{today_str}.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

# ================= TAB 2: LIVESCORES =================
with tab2:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"⚽ LiveScores & Ratiba ya Leo ({today_str})")
    st.write("Fuatilia mechi za leo mubashara. Piga screenshot ya mechi unazotaka kisha weka kwenye Kichambuzi:")
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
