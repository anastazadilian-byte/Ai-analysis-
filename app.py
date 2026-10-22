import streamlit as st
from PIL import Image
import google.generativeai as genai

st.set_page_config(page_title="AI Forex & Betting Deep Analyst", page_icon="⚡", layout="wide")
st.title("⚡ AI Deep Analyst: Betting & Forex")
st.write("Weka screenshot ya chati ya Forex au mechi ya Betting kwa uchambuzi wa kina.")

with st.sidebar:
    st.header("⚙️ Mipangilio")
    api_key = st.text_input("Weka Gemini API Key:", type="password")
    analysis_type = st.radio("Chagua Aina:", ["⚽ Football / Sports Betting", "📈 Forex Trading"])

uploaded_file = st.file_uploader("Pakia Screenshot hapa (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Screenshot Uliyopakia", use_container_width=True)

    if st.button("🚀 Anza Uchambuzi wa Kina (Deep Analysis)"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto (Sidebar)!")
        else:
            with st.spinner("AI inachambua picha... Subiri kidogo..."):
                try:
                    genai.configure(api_key=api_key.strip())
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    if analysis_type == "⚽ Football / Sports Betting":
                        prompt = (
                            "Wewe ni mchambuzi wa michezo. Soma screenshot hii ya mechi na ufanye uchambuzi kwa Kiswahili:\n"
                            "1. Timu na mashindano yanayoonekana.\n"
                            "2. Odds na tathmini ya mchezo.\n"
                            "3. Utabiri wa matokeo (1X2, Over/Under, GG/NG) na asilimia ya uhakika (Confidence %)."
                        )
                    else:
                        prompt = (
                            "Wewe ni Senior Forex Analyst. Soma screenshot hii ya chati ya Forex na ufanye uchambuzi kwa Kiswahili:\n"
                            "1. Pair na mwelekeo wa soko (Trend/Range).\n"
                            "2. Viashiria muhimu, Support na Resistance.\n"
                            "3. Setup: Pendekezo (BUY, SELL, WAIT), Entry, SL na TP."
                        )

                    response = model.generate_content([prompt, image])

                    st.success("✅ Uchambuzi Umekamilika!")
                    st.markdown("### 📊 Ripoti ya Uchambuzi:")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Kumetokea hitilafu: {str(e)}")
