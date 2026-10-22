import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import streamlit.components.v1 as components
from datetime import datetime

MODEL_NAME = "gemini-3.8-flash"

st.set_page_config(page_title="AI Pro: Betting & Forex", page_icon="⚡", layout="wide")
st.title("⚡ AI Deep Analyst & Sports Hub")

with st.sidebar:
    st.header("⚙️ Mipangilio")
    api_key = st.text_input("Weka Gemini API Key:", type="password")

t1, t2, t3 = st.tabs(["📸 Scanner", "🔥 Sure 2 Odds (Za Leo)", "⚽ LiveScores"])

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
                with st.spinner("AI inachambua picha na kutafuta mtandaoni..."):
                    try:
                        client = genai.Client(api_key=api_key.strip())
                        if atype == "⚽ Sports Betting":
                            p = "Soma picha hii ya mechi. Tumia Google kutafuta fomu ya karibuni, majeruhi, nani yupo siriasi kushinda (80%+), na ubashiri salama kwa Kiswahili."
                        else:
                            p = "Soma chati hii ya Forex. Eleza pair, trend, viashiria, support/resistance, na setup ya trade kwa Kiswahili."
                        res = client.models.generate_content(
                            model=MODEL_NAME, 
                            contents=[p, img],
                            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                        )
                        st.success("✅ Imekamilika!")
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"Hitilafu: {str(e)}")

with t2:
    today_str = datetime.now().strftime("%d-%m-%Y")
    st.subheader(f"🔥 Sure 2 Odds za Leo ({today_str})")
    st.write("Bonyeza kitufe hapa chini ili AI iingie mtandaoni kusoma ratiba ya mechi za LEO TU na kutoa timu zenye motisha ya ushindi:")

    if st.button("🎯 Tafuta Mechi za LEO & Tengeneza Tiketi"):
        if not api_key:
            st.error("Weka Gemini API Key kwenye menu ya kushoto!")
        else:
            with st.spinner(f"AI inatafuta ratiba na habari za mechi za leo ({today_str}) mtandaoni..."):
                try:
                    client = genai.Client(api_key=api_key.strip())
                    p_odds = (
                        f"Leo ni tarehe {today_str}. KAZI YAKO: Ingia mtandaoni kupitia Google Search na uangalie ratiba ya mechi za soka zinazochezwa LEO tarehe {today_str} au kesho asubuhi pekee.\n\n"
                        "MASHARTI MUHIMU:\n"
                        "1. USITUMIE mechi za zamani zilizokwisha kuchezwa. Mechi lazima ziwe za leo ambazo hazijaanza!\n"
                        "2. Chagua mechi 2 hadi 3 tu zenye jumla ya takribani odds 2.00.\n"
                        "3. Angalia timu zilizo 'SIRIASI' zaidi (zinazopigania pointi muhimu, nafasi ya kwanza, au kukwepa kushuka daraja) zenye uwezekano wa 80%+.\n"
                        "4. Andika majina ya timu, saa ya mechi, ligi husika, chaguo salama (kama Double Chance au Over 1.5), na sababu ya kiuchambuzi kwa Kiswahili."
                    )
                    res = client.models.generate_content(
                        model=MODEL_NAME, 
                        contents=p_odds,
                        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                    )
                    st.success("✅ Tiketi ya Leo Ipo Tayari!")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Hitilafu: {str(e)}")

with t3:
    st.subheader("⚽ LiveScores Mubashara")
    components.html('<iframe src="https://www.scorebat.com/embed/livescore/" frameborder="0" width="100%" height="700" style="width:100%;height:700px;border:none;border-radius:12px;"></iframe>', height=720, scrolling=True)
