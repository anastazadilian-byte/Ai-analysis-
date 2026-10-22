import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Forex & Betting Deep Analyst", page_icon="⚡", layout="wide")
st.title("⚡ AI Deep Analyst: Betting & Forex")
st.write("Weka screenshot ya chati ya Forex au mechi ya Betting kwa uchambuzi wa kina mubashara.")

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
            with st.spinner("AI inachambua picha na kutafuta taarifa mtandaoni... Subiri kidogo..."):
                try:
                    client = genai.Client(api_key=api_key.strip())

                    if analysis_type == "⚽ Football / Sports Betting":
                        prompt = (
                            "Wewe ni mchambuzi wa michezo. Soma screenshot hii ya mechi na ufanye uchambuzi wa kina kwa Kiswahili:\n"
                            "1. Timu na mashindano yanayoonekana.\n"
                            "2. Tafuta mtandaoni (Google Search) majeruhi, wachezaji waliopo nje, umuhimu wa mechi na fomu ya hivi karibuni.\n"
                            "3. Mwelekeo wa matokeo (1X2, Over/Under, GG/NG), asilimia ya uhakika (Confidence %) na vihatarishi (Risks)."
                        )
                    else:
                        prompt = (
                            "Wewe ni Senior Forex Analyst. Soma screenshot hii ya chati ya Forex na ufanye uchambuzi kwa Kiswahili:\n"
                            "1. Pair, Timeframe, na Market Structure (Trend/Range).\n"
                            "2. Viashiria (Indicators), Candlestick patterns, Support na Resistance.\n"
                            "3. Habari za soko (Economic News) kwa pair hii mtandaoni.\n"
                            "4. Trade Setup: Pendekezo (BUY/SELL/WAIT), Entry zone, SL, TP1, TP2."
                        )

                    response = client.models.generate_content(
                        model="gemini-8.3-flash",
                        contents=[image, prompt],
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())],
                            temperature=0.2
                        )
                    )

                    st.success("✅ Uchambuzi Umekamilika!")
                    st.markdown("### 📊 Ripoti ya Uchambuzi:")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Kumetokea hitilafu: {str(e)}")
