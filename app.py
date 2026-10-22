import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# Usanidi wa Ukurasa
st.set_page_config(
    page_title="AI Forex & Betting Deep Analyst",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ AI Deep Analyst: Betting & Forex")
st.write("Weka screenshot ya chati ya Forex au mechi ya Betting kwa ajili ya uchambuzi wa kina unaotumia taarifa za mtandaoni mubashara.")

# Jaribu kusoma secret kama ipo, vinginevyo tumia inayowekwa na mtumiaji
default_key = st.secrets.get("GEMINI_API_KEY", "")

# Sidebar ya Mipangilio
with st.sidebar:
    st.header("⚙️ Mipangilio")
    api_key = st.text_input(
        "Weka Gemini API Key yako hapa:",
        value=default_key,
        type="password",
        help="Pata API key ya bure kupitia aistudio.google.com"
    )
    analysis_type = st.radio(
        "Chagua Aina ya Uchambuzi:",
        ["⚽ Football / Sports Betting", "📈 Forex Trading"]
    )
    st.markdown("---")
    st.info("💡 **Jinsi inavyofanya kazi:**\nAI inachanganua picha uliyoweka, kisha inatumia **Google Search** kutafuta taarifa za karibuni mtandaoni kama majeruhi, habari za soko, na fomu ya timu.")

# Eneo la kupakia picha
uploaded_file = st.file_uploader("Pakia Screenshot hapa (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Screenshot Uliyopakia", use_container_width=True)

    if st.button("🚀 Anza Uchambuzi wa Kina (Deep Analysis)"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto (Sidebar)!")
        else:
            with st.spinner("AI inasoma picha na inatafuta taarifa live mtandaoni... Tafadhali subiri kidogo..."):
                try:
                    # Safisha key kuondoa nafasi zisizo za lazima
                    clean_api_key = api_key.strip()
                    client = genai.Client(api_key=clean_api_key)

                    if analysis_type == "⚽ Football / Sports Betting":
                        prompt = """
                        Wewe ni Mchambuzi Bingwa wa Michezo (Sports Analyst) na Data Scientist.
                        Kazi yako ni kuchambua screenshot hii na kufanya uchambuzi wa kina sana:
                        
                        1. USOMAJI WA PICHA:
                           - Tambua timu zinazocheza, mashindano, na takwimu zozote zinazoonekana (odds, matokeo, au form).
                        
                        2. LIVE WEB SEARCH (Tumia Google Search kutafuta taarifa za sasa):
                           - Majeruhi na Wachezaji Waliopo Nje (Injuries & Suspensions): Nani anacheza na nani hayupo?
                           - Umuhimu/Pressure ya Mechi: Je, ni timu inayopambana kushuka daraja, kuwania ubingwa, au wamepumzisha wachezaji?
                           - Fomu ya Karibuni (Recent Form) & H2H (Historia ya mechi zao walipokutana).
                           
                        3. MAPENDEKEZO NA TATHMINI YA UHAKIKA:
                           - Mwelekeo wa Matokeo (Match Outcome: 1X2, Over/Under, GG/NG).
                           - Asilimia ya Uwezekano (Confidence Score: 1-100%).
                           - Vihatarishi (Key Risks): Sababu zinazoweza kuharibu ubashiri huu.
                        
                        Toa majibu kwa mpangilio mzuri, wenye vichwa vya habari na lugha ya Kiswahili iliyo wazi na ya kitaalamu.
                        """
                    else:
                        prompt = """
                        Wewe ni Senior Forex Technical & Fundamental Analyst.
                        Kazi yako ni kuchambua screenshot hii ya chati ya Forex:
                        
                        1. USOMAJI WA CHATI:
                           - Tambua Pair (mf. EUR/USD, GBP/JPY, XAU/USD) na Timeframe kama vinaonekana.
                           - Market Structure: Je, soko lipo kwenye Uptrend, Downtrend, au linajirudia (Range/Consolidation)?
                           - Candlestick Patterns & Indicators: Eleza viashiria vyovyote (RSI, Moving Averages, MACD) au mishumaa muhimu.
                           - Support & Resistance: Taja nambari za maeneo makuu ya bei kubadilika.
                        
                        2. FUNDAMENTAL SEARCH (Tumia Google Search):
                           - Kuna habari yoyote ya kiuchumi (Economic News, CPI, Interest Rates, NFP) iliyotoka au inayotarajiwa kutoka leo inayohusu currency hizi?
                        
                        3. TRADE EXECUTION SETUP:
                           - Pendekezo: (BUY, SELL, au WAIT).
                           - Entry Zone inayofaa.
                           - Stop Loss (SL) na Take Profit (TP1 & TP2).
                           - Risk to Reward Ratio.
                        
                        Toa majibu kwa mpangilio mzuri wa kitaalamu na lugha ya Kiswahili.
                        """

                    # Jaribu kutumia gemini-2.5-flash kwanza, ikikosa ibadilishe kwenda gemini-1.5-flash
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[image, prompt],
                            config=types.GenerateContentConfig(
                                tools=[{"go
