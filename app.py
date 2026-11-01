
import streamlit as st
import pandas as pd
import pytesseract
import re
import os
from PIL import Image, ImageOps, ImageEnhance

# ==========================================
# 1. APP CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Match Analyzer Pro",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ AI MATCH ANALYZER PRO")
st.caption("Football Screenshot Reader & Match Analysis")

st.info(
    "Pakia screenshot ya LiveScore. Mfumo utajaribu "
    "kusoma maandishi na kutambua mechi zilizopo."
)

# ==========================================
# 2. SESSION STORAGE
# ==========================================

if "matches" not in st.session_state:
    st.session_state.matches = []

if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

if "detected_matches" not in st.session_state:
    st.session_state.detected_matches = []


# ==========================================
# 3. TESSERACT CONFIGURATION
# ==========================================

# Windows: Badilisha path ikiwa Tesseract
# imewekwa sehemu tofauti kwenye computer yako.

WINDOWS_TESSERACT = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if os.name == "nt" and os.path.exists(WINDOWS_TESSERACT):
    pytesseract.pytesseract.tesseract_cmd = WINDOWS_TESSERACT


# ==========================================
# 4. IMAGE PROCESSING
# ==========================================

def prepare_image(image):

    image = ImageOps.exif_transpose(image)

    image = image.convert("RGB")

    # Kuongeza ukubwa kusaidia OCR
    width, height = image.size

    if width < 1600:
        scale = 1600 / width
        image = image.resize(
            (1600, int(height * scale))
        )

    # Kuboresha maandishi
    image = ImageOps.grayscale(image)

    image = ImageEnhance.Contrast(image).enhance(2)

    image = ImageEnhance.Sharpness(image).enhance(2)

    return image


# ==========================================
# 5. READ TEXT FROM SCREENSHOT
# ==========================================

def read_screenshot(image):

    processed = prepare_image(image)

    text = pytesseract.image_to_string(
        processed,
        lang="eng",
        config="--psm 6"
    )

    return text


# ==========================================
# 6. DETECT MATCHES FROM OCR TEXT
# ==========================================

def detect_matches(text):

    detected = []

    lines = text.splitlines()

    patterns = [
        r"(.+?)\s+vs\.?\s+(.+)",
        r"(.+?)\s+v\s+(.+)",
        r"(.+?)\s+-\s+(.+)"
    ]

    for line in lines:

        line = re.sub(r"\s+", " ", line).strip()

        if not line or len(line) < 5:
            continue

        for pattern in patterns:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE
            )

            if match:

                home = match.group(1).strip()
                away = match.group(2).strip()

                # Ondoa mistari isiyo na majina ya timu
                if len(home) < 2 or len(away) < 2:
                    continue

                if len(home) > 45 or len(away) > 45:
                    continue

                detected.append({
                    "Home Team": home,
                    "Away Team": away
                })

                break

    # Ondoa duplicates
    unique = []
    seen = set()

    for item in detected:

        key = (
            item["Home Team"].lower(),
            item["Away Team"].lower()
        )

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


# ==========================================
# 7. NAVIGATION
# ==========================================

page = st.sidebar.radio(
    "MENU",
    [
        "Dashboard",
        "Read Screenshot",
        "Match Scanner",
        "Odds Calculator",
        "Best Matches"
    ]
)


# ==========================================
# 8. DASHBOARD
# ==========================================

if page == "Dashboard":

    st.subheader("Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Matches Saved",
        len(st.session_state.matches)
    )

    col2.metric(
        "Matches Detected",
        len(st.session_state.detected_matches)
    )

    col3.metric(
        "OCR System",
        "Ready"
    )

    st.markdown("---")

    st.subheader("Saved Matches")

    if st.session_state.matches:

        st.dataframe(
            pd.DataFrame(st.session_state.matches),
            use_container_width=True
        )

    else:

        st.info("Bado hakuna mechi zilizohifadhiwa.")


# ==========================================
# 9. SCREENSHOT READER
# ==========================================

elif page == "Read Screenshot":

    st.subheader("📷 Read LiveScore Screenshot")

    uploaded_file = st.file_uploader(
        "Upload LiveScore screenshot",
        type=["png", "jpg", "jpeg", "webp"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded screenshot",
            use_container_width=True
        )

        if st.button("🔍 READ MATCHES FROM IMAGE"):

            try:

                with st.spinner("Reading screenshot..."):

                    extracted_text = read_screenshot(image)

                    detected = detect_matches(extracted_text)

                    st.session_state.ocr_text = extracted_text

                    st.session_state.detected_matches = detected

                st.success("Screenshot imesomwa.")

            except Exception as error:

                st.error(
                    "OCR imeshindwa. Hakikisha Tesseract "
                    "imewekwa kwenye computer yako."
                )

                st.code(str(error))

    # OCR RESULTS
    if st.session_state.ocr_text:

        st.markdown("---")

        st.subheader("1. Text Read From Image")

        st.text_area(
            "OCR Text",
            value=st.session_state.ocr_text,
            height=180
        )

        st.subheader("2. Detected Matches")

        if st.session_state.detected_matches:

            df = pd.DataFrame(
                st.session_state.detected_matches
            )

            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic"
            )

            if st.button("SAVE DETECTED MATCHES"):

                for _, row in edited_df.iterrows():

                    home = str(row["Home Team"]).strip()
                    away = str(row["Away Team"]).strip()

                    if home and away:

                        st.session_state.matches.append({
                            "Home": home,
                            "Away": away,
                            "Source": "Screenshot OCR"
                        })

                st.success("Mechi zimehifadhiwa.")

        else:

            st.warning(
                "OCR imesoma maandishi lakini haijatambua "
                "muundo wa mechi. Unaweza kunakili majina "
                "kutoka kwenye OCR Text na kuyajaza mwenyewe."
            )


# ==========================================
# 10. MATCH SCANNER
# ==========================================

elif page == "Match Scanner":

    st.subheader("🔍 Match Performance Scanner")

    if st.session_state.matches:

        match_options = [
            f"{m['Home']} vs {m['Away']}"
            for m in st.session_state.matches
        ]

        selected = st.selectbox(
            "Select Match",
            match_options
        )

        selected_index = match_options.index(selected)

        selected_match = st.session_state.matches[
            selected_index
        ]

        home = selected_match["Home"]
        away = selected_match["Away"]

    else:

        st.info("Hakuna mechi. Soma screenshot kwanza.")

        home = st.text_input("Home Team")
        away = st.text_input("Away Team")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.write("HOME TEAM")

        home_points = st.number_input(
            "Last 5 points",
            min_value=0,
            max_value=15,
            value=0
        )

        home_goals = st.number_input(
            "Goals scored per match",
            min_value=0.0,
            value=0.0
        )

        home_conceded = st.number_input(
            "Goals conceded per match",
            min_value=0.0,
            value=0.0
        )

    with col2:

        st.write("AWAY TEAM")

        away_points = st.number_input(
            "Last 5 points ",
            min_value=0,
            max_value=15,
            value=0
        )

        away_goals = st.number_input(
            "Goals scored per match ",
            min_value=0.0,
            value=0.0
        )

        away_conceded = st.number_input(
            "Goals conceded per match ",
            min_value=0.0,
            value=0.0
        )

    if st.button("ANALYZE MATCH"):

        if not home or not away:

            st.error("Chagua mechi kwanza.")

        else:

            form_difference = home_points - away_points

            total_goals = home_goals + away_goals

            score = (
                50
                + form_difference * 1.6
                + (total_goals - 2.4) * 5
                - (
                    home_conceded + away_conceded - 2.2
                ) * 2
            )

            score = max(0, min(100, round(score)))

            st.markdown("---")

            st.subheader(f"{home} vs {away}")

            st.metric(
                "Illustrative Performance Index",
                f"{score}/100"
            )

            st.write(
                "Goal trend:",
                "Higher" if total_goals >= 2.8
                else "Lower" if total_goals <= 1.8
                else "Balanced"
            )

            st.write(
                "Form advantage:",
                home if form_difference > 1
                else away if form_difference < -1
                else "No clear advantage"
            )

            st.warning(
                "Hii ni alama ya mfano, si probability "
                "iliyothibitishwa wala utabiri wa uhakika."
            )


# ==========================================
# 11. ODDS CALCULATOR
# ==========================================

elif page == "Odds Calculator":

    st.subheader("📊 1X2 Odds Calculator")

    h = st.number_input(
        "Home odds",
        min_value=1.01,
        value=2.10
    )

    d = st.number_input(
        "Draw odds",
        min_value=1.01,
        value=3.40
    )

    a = st.number_input(
        "Away odds",
        min_value=1.01,
        value=3.60
    )

    if st.button("CALCULATE"):

        odds = [h, d, a]

        implied = [1 / x for x in odds]

        total = sum(implied)

        margin = (total - 1) * 100

        fair_prob = [
            (x / total) * 100 for x in implied
        ]

        fair_odds = [
            1 / (x / total) for x in implied
        ]

        result = pd.DataFrame({
            "Outcome": [
                "Home Win",
                "Draw",
                "Away Win"
            ],
            "Odds": odds,
            "Implied Probability (%)": [
                x * 100 for x in implied
            ],
            "Fair Probability (%)": fair_prob,
            "Fair Odds": fair_odds
        })

        st.metric(
            "Bookmaker Margin",
            f"{margin:.2f}%"
        )

        st.dataframe(
            result.round(2),
            use_container_width=True
        )

        st.info(
            "Fair odds zinatokana na kuondoa overround "
            "ya bookmaker kwa njia ya normalization."
        )


# ==========================================
# 12. BEST MATCHES
# ==========================================

elif page == "Best Matches":

    st.subheader("⭐ Best Matches")

    if st.session_state.matches:

        df = pd.DataFrame(st.session_state.matches)

        st.dataframe(
            df,
            use_container_width=True
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "DOWNLOAD MATCHES",
            data=csv,
            file_name="matches.csv",
            mime="text/csv"
        )

    else:

        st.info("Bado hakuna mechi zilizohifadhiwa.")


# ==========================================
# 13. FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "AI Match Analyzer Pro | Free OCR prototype | "
    "No guaranteed betting outcomes"
)
