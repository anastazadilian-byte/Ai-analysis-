import streamlit as st
from PIL import Image
from google import genai
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Pro: Betting & Forex Analyst", page_icon="⚡", layout="wide")
st.title("⚡ AI Deep Analyst & Sports Hub")

with st.sidebar:
    st.header("⚙️ Mipangilio")
    api_key = st.text_input("Weka Gemini API Key:", type="password")

tab1, tab2, tab3 = st.tabs(["📸 AI Screenshot Scanner", "🔥 Sure 2 Odds (Za Leo)", "⚽ LiveScores Mubashara"])

with tab1:
    st.subheader("Uchambuzi wa Screenshot (Betting au Forex)")
    analysis_type = st.radio("Chagua Aina ya Uchambuzi:", ["⚽ Football / Sports Betting", "📈 Forex Trading"])
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
                        client = genai.Client(api_key=api_key.strip())
                        if analysis_type == "⚽ Football / Sports Betting":
                            prompt = (
                                "Wewe ni mchambuzi bingwa wa michezo na saikolojia ya timu. "
                                "Soma screenshot hii ya mechi na ufanye uchambuzi wa kina sana kwa Kiswahili:\n"
                                "1. Timu na mashindano yanayoonekana.\n"
                                "2. MOTISHA & PRESHA: Je, timu ipi ipo 'siriasi' zaidi? (Kushuka daraja, kuwania ubingwa au top 4?).\n"
                                "3. Tathmini ya odds na ubashiri wenye uwezekano mkubwa wa 80%+.\n"
                                "4. Vihatarishi (Risks) vinavyoweza kutokea."
                            )
                        else:
                            prompt = (
                                "Wewe ni Senior Forex Analyst. Soma screenshot hii ya chati ya Forex na ufanye uchambuzi kwa Kiswahili:\n"
                                "1. Pair na mwelekeo wa soko (Trend/Range).\n"
                                "2. Viashiria muhimu, Support na Resistance.\n"
                                "3. Setup: Pendekezo (BUY, SELL, WAIT), Entry, SL na TP."
                            )
                        response = client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=[prompt, image]
                        )
                        st.success("✅ Uchambuzi Umekamilika!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Kumetokea hitilafu: {str(e)}")

with tab2:
    st.subheader("🔥 Jenereta ya 'Sure 2 Odds' za Leo")
    st.write("Bonyeza kitufe hapa chini ili AI itoe mechi zenye ushindani mkali na timu zilizo 'siriasi' kupambana.")

    if st.button("🎯 Tengeneza Tiketi ya 2 Odds za Leo"):
        if not api_key:
            st.error("Tafadhali weka Gemini API Key yako kwenye menu ya kushoto (Sidebar)!")
        else:
            with st.spinner("AI inachuja timu zilizo 'siriasi'..."):
                try:
                    client = genai.Client(api_key=api_key.strip())
                    odds_prompt = (
                        "Wewe ni mchambuzi mtaalamu wa betting. Toa tiketi ya mechi 2 hadi 3 za uhakika zenye jumla ya takribani Odds 2.00.\n"
                        "1. Chagua machaguo salama yenye asilimia 80%+ (mfano: Double Chance 1X/X2, Over 1.5, Win either half).\n"
                        "2. Eleza kwanini timu hiyo ipo SIRIASI kupambana leo kwa Kiswahili fasaha."
                    )
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=odds_prompt
                    )
                    st.success("✅ Tiketi Yako Ipo Tayari!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Kumetokea hitilafu: {str(e)}")

with tab3:
    st.subheader("⚽ Matokeo ya Mechi Mubashara (LiveScores)")
    livescore_html = """
    <iframe src="https://www.scorebat.com/embed/livescore/" 
            frameborder="0" width="100%" height="700" 
            style="width:100%;height:700px;border:none;border-radius:12px;">
    </iframe>
    """
    components.html(livescore_html, height=720, scrolling=True)
