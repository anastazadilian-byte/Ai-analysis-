import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components
from datetime import datetime

MODEL_NAME = "gemini-3.8-flash"

st.set_page_config(page_title="AI Pro: Betting & Forex", page_icon="⚡", layout="wide")
st.title("⚡ AI Deep Analyst & Sports Hub")

with st.sidebar:
    st.header("⚙️ Mipangilio")
    api_key = st.text_input("Weka Gemini API Key:", type="password")

t1, t2, t3 = st.tabs(["📸 Scanner", "🔥 Sure 2 Odds", "⚽ LiveScores"])

with t1:
    st.subheader("Uchambuzi wa Mechi au Forex kwa Picha")
    atype = st.radio("Aina:", ["⚽ Sports Betting", "📈 Forex Trading"])
    up = st.file_uploader("Pakia Screenshot:", type=["png", "jpg", "jpeg"])
    if up:
        img = Image.open(up)
        st.image(img, use_container_width=True)
        if st.button("🚀 Anza Uchambuzi"):
            if not api_key:
                st.error("Weka Gemini API Key kwenye menu ya kushoto!")
            else:
                with st.spinner("AI inachambua picha..."):
                    try:
                        client = genai.Client(api_key=api_key.strip())
                        if atype == "⚽ Sports Betting":
                            p = (
                                "Wewe ni mchambuzi wa michezo. Soma screenshot hii ya mechi na ufanye uchambuzi kwa Kiswahili:\n"
                                "1. Timu na mashindano yanayoonekana.\n"
                                "2. MOTISHA & PRESHA: Eleza nani yupo siriasi zaidi kupambana leo (kushuka daraja, ubingwa au top 4) kwa uhakika wa 80%+.\n"
                                "3. Mwelekeo wa matokeo (1X2, Over/Under, GG/NG) na machaguo salama."
                            )
                        else:
                            p = "Mchambuzi wa Forex: Soma hii chati. Eleza pair, trend, viashiria, support/resistance, na setup ya trade kwa Kiswahili."
                        
                        res = client.models.generate_content(model=MODEL_NAME, contents=[p, img])
                        st.success("✅ Uchambuzi Umekamilika!")
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

with t2:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"🔥 Sure 2 Odds Generator ({today_str})")
    st.write("Andika mechi 1 hadi 3 za leo unazotaka zifanyiwe uchambuzi wa kina (au acha wazi AI ichague mechi kubwa za sasa):")

    user_matches = st.text_input(
        "Andika timu za leo (Mfano: Simba vs Yanga, Arsenal vs Wolves):",
        placeholder="Mfano: Arsenal vs Wolves, Real Madrid vs Sevilla"
    )

    if st.button("🎯 Tengeneza Tiketi ya 2 Odds"):
        if not api_key:
            st.error("Weka Gemini API Key kwenye menu ya kushoto!")
        else:
            with st.spinner("AI inachambua timu zilizo siriasi kupambana..."):
                try:
                    client = genai.Client(api_key=api_key.strip())
                    
                    if user_matches.strip():
                        query = f"Hizi hapa ni mechi za leo: {user_matches}. "
                    else:
                        query = "Chagua timu 2 au 3 zenye mechi kubwa zenye ushindani mkali. "

                    prompt_odds = (
                        f"{query} Fanya uchambuzi wa kina kama mtaalamu wa kubashiri kwa Kiswahili:\n"
                        "1. Tengeneza tiketi ya takribani Odds 2.00 yenye machaguo salama kabisa (uwezekano 80%+ kama Double Chance, Over 1.5, n.k).\n"
                        "2. Eleza wazi kwanini timu uliyochagua ipo 'SIRIASI' kupambana kufa na kupona (motisha ya alama 3, fomu, au kulinda heshima).\n"
                        "3. Toa tathmini ya vihatarishi na ushauri wa uwekezaji."
                    )

                    res = client.models.generate_content(model=MODEL_NAME, contents=prompt_odds)
                    st.success("✅ Tiketi Yako Ipo Tayari!")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")

with t3:
    st.subheader("⚽ LiveScores Mubashara")
    st.write("Angalia mechi zinazoendelea na ratiba ya leo:")
    components.html('<iframe src="https://www.scorebat.com/embed/livescore/" frameborder="0" width="100%" height="700" style="width:100%;height:700px;border:none;border-radius:12px;"></iframe>', height=720, scrolling=True)
