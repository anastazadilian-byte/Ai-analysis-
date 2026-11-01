
import streamlit as st
import pandas as pd
from PIL import Image
from datetime import date
import io

st.set_page_config(
    page_title="AI Match Analyzer Pro",
    page_icon="⚽",
    layout="wide"
)

# -----------------------------
# APP DESIGN
# -----------------------------
st.markdown("""
<style>
.stApp {background-color: #0b1420; color: #edf4fa;}
[data-testid="stMetric"] {
    background: #142536;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #26394b;
}
.stButton button {
    background: #13b981;
    color: #05251b;
    font-weight: bold;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION DATA
# -----------------------------
if "matches" not in st.session_state:
    st.session_state.matches = []

st.title("⚽ AI MATCH ANALYZER PRO")
st.caption("Football analysis workspace | Manual data analysis")

st.info(
    "Mfumo huu unafanya uchambuzi kwa kutumia taarifa unazoingiza. "
    "Hauhakikishi ushindi na hauunganishwi na LiveScore au bookmaker."
)

# -----------------------------
# FUNCTIONS
# -----------------------------
def calculate_odds(home_odds, draw_odds, away_odds):
    odds = [home_odds, draw_odds, away_odds]

    if any(x <= 1 for x in odds):
        raise ValueError("Odds lazima ziwe zaidi ya 1.00")

    implied = [1 / x for x in odds]
    total = sum(implied)

    margin = (total - 1) * 100
    fair_prob = [x / total for x in implied]
    fair_odds = [1 / x for x in fair_prob]

    return {
        "margin": margin,
        "implied": implied,
        "fair_prob": fair_prob,
        "fair_odds": fair_odds
    }


def calculate_ev(probability, odds):
    return ((probability / 100) * odds - 1) * 100


def safe_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("⚙️ Navigation")

page = st.sidebar.radio(
    "Chagua ukurasa",
    [
        "Dashboard",
        "Upload Screenshot",
        "Match Scanner",
        "Odds Calculator",
        "Best Matches",
        "Settings"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("AI Match Analyzer Pro")
st.sidebar.caption("Free manual-analysis version")

# -----------------------------
# DASHBOARD
# -----------------------------
if page == "Dashboard":

    st.subheader("Dashboard")

    total_matches = len(st.session_state.matches)

    col1, col2, col3 = st.columns(3)

    col1.metric("Matches Added", total_matches)
    col2.metric("Data Source", "Manual")
    col3.metric("API Connection", "Not connected")

    st.markdown("---")
    st.subheader("Recent Matches")

    if st.session_state.matches:
        df = pd.DataFrame(st.session_state.matches)
        st.dataframe(df, use_container_width=True)
    else:
        st.info(
            "Bado hujaongeza mechi. Nenda Upload Screenshot "
            "au Match Scanner kuanza."
        )

# -----------------------------
# SCREENSHOT UPLOAD
# -----------------------------
elif page == "Upload Screenshot":

    st.subheader("📷 Upload LiveScore Screenshot")

    uploaded_file = st.file_uploader(
        "Chagua screenshot ya mechi",
        type=["png", "jpg", "jpeg", "webp"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(
            image,
            caption="Screenshot yako",
            use_container_width=True
        )

        st.warning(
            "Picha inaonyeshwa tu. Mfumo huu bado hauna OCR "
            "ya kusoma majina ya timu moja kwa moja."
        )

    st.markdown("---")
    st.subheader("Ingiza taarifa za mechi")

    with st.form("upload_match_form"):

        home = st.text_input("Home Team")
        away = st.text_input("Away Team")
        league = st.text_input("League")
        match_date = st.date_input("Match Date", value=date.today())

        submitted = st.form_submit_button("Add Match")

        if submitted:
            if not home.strip() or not away.strip():
                st.error("Weka majina ya timu zote mbili.")
            else:
                st.session_state.matches.append({
                    "Home": home.strip(),
                    "Away": away.strip(),
                    "League": league.strip(),
                    "Date": str(match_date),
                    "Status": "Awaiting analysis"
                })

                st.success("Mechi imeongezwa kwenye mfumo.")

# -----------------------------
# MATCH SCANNER
# -----------------------------
elif page == "Match Scanner":

    st.subheader("🔍 Match Performance Scanner")

    st.write(
        "Ingiza takwimu za mechi. Tumia wastani wa mechi "
        "tano zilizopita pale inapowezekana."
    )

    with st.form("scanner_form"):

        col1, col2 = st.columns(2)

        with col1:
            home = st.text_input("Home Team")
            home_points = st.number_input(
                "Home last 5 points (0–15)",
                min_value=0,
                max_value=15,
                value=0
            )
            home_scored = st.number_input(
                "Home goals scored per match",
                min_value=0.0,
                max_value=10.0,
                value=0.0
            )
            home_conceded = st.number_input(
                "Home goals conceded per match",
                min_value=0.0,
                max_value=10.0,
                value=0.0
            )

        with col2:
            away = st.text_input("Away Team")
            away_points = st.number_input(
                "Away last 5 points (0–15)",
                min_value=0,
                max_value=15,
                value=0
            )
            away_scored = st.number_input(
                "Away goals scored per match",
                min_value=0.0,
                max_value=10.0,
                value=0.0
            )
            away_conceded = st.number_input(
                "Away goals conceded per match",
                min_value=0.0,
                max_value=10.0,
                value=0.0
            )

        analyze = st.form_submit_button("Analyze Match")

    if analyze:

        if not home.strip() or not away.strip():
            st.error("Weka majina ya timu zote mbili.")

        else:
            form_difference = home_points - away_points
            total_goals = home_scored + away_scored

            performance_score = (
                50
                + form_difference * 1.6
                + (total_goals - 2.4) * 5
                - (home_conceded + away_conceded - 2.2) * 2
            )

            performance_score = max(
                0,
                min(100, round(performance_score))
            )

            if total_goals >= 2.8:
                goal_trend = "Higher scoring trend"
            elif total_goals <= 1.8:
                goal_trend = "Lower scoring trend"
            else:
                goal_trend = "Balanced trend"

            if form_difference > 1:
                form_edge = f"{home} form advantage"
            elif form_difference < -1:
                form_edge = f"{away} form advantage"
            else:
                form_edge = "No clear form advantage"

            if abs(form_difference) < 2:
                risk = "HIGH"
            else:
                risk = "MEDIUM"

            st.markdown("---")
            st.subheader("Analysis Result")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Performance Index",
                f"{performance_score}/100"
            )
            c2.metric("Goal Trend", goal_trend)
            c3.metric("Risk Flag", risk)

            st.write("**Form assessment:**", form_edge)

            st.warning(
                "Performance Index ni alama ya mfano inayotokana "
                "na takwimu ulizoingiza. Si probability ya kushinda, "
                "si utabiri uliothibitishwa, wala si AI model iliyofundishwa."
            )

# -----------------------------
# ODDS CALCULATOR
# -----------------------------
elif page == "Odds Calculator":

    st.subheader("📊 1X2 Odds Calculator")

    st.write("Ingiza odds za Home Win, Draw na Away Win.")

    with st.form("odds_form"):

        col1, col2, col3 = st.columns(3)

        home_odds = col1.number_input(
            "Home Win Odds",
            min_value=1.01,
            value=2.10,
            step=0.01
        )

        draw_odds = col2.number_input(
            "Draw Odds",
            min_value=1.01,
            value=3.40,
            step=0.01
        )

        away_odds = col3.number_input(
            "Away Win Odds",
            min_value=1.01,
            value=3.60,
            step=0.01
        )

        st.markdown("**Your estimated probabilities (%)**")

        p1, p2, p3 = st.columns(3)

        home_probability = p1.number_input(
            "Home probability",
            min_value=0.0,
            max_value=100.0,
            value=45.0
        )

        draw_probability = p2.number_input(
            "Draw probability",
            min_value=0.0,
            max_value=100.0,
            value=28.0
        )

        away_probability = p3.number_input(
            "Away probability",
            min_value=0.0,
            max_value=100.0,
            value=27.0
        )

        calculate = st.form_submit_button("Calculate Odds & EV")

    if calculate:

        try:
            result = calculate_odds(
                home_odds,
                draw_odds,
                away_odds
            )

            st.markdown("---")
            st.subheader("Bookmaker Analysis")

            st.metric(
                "Bookmaker Margin",
                f"{result['margin']:.2f}%"
            )

            if result["margin"] > 0:
                st.caption(
                    "Margin inaonyesha kiasi cha overround "
                    "kilichopo kwenye odds."
                )

            names = ["Home Win", "Draw", "Away Win"]

            table = []

            for i in range(3):
                ev = calculate_ev(
                    [
                        home_probability,
                        draw_probability,
                        away_probability
                    ][i],
                    [
                        home_odds,
                        draw_odds,
                        away_odds
                    ][i]
                )

                table.append({
                    "Outcome": names[i],
                    "Bookmaker Odds": [
                        home_odds,
                        draw_odds,
                        away_odds
                    ][i],
                    "Implied Probability": (
                        result["implied"][i] * 100
                    ),
                    "Fair Probability": (
                        result["fair_prob"][i] * 100
                    ),
                    "Fair Odds": result["fair_odds"][i],
                    "Your Estimated Probability": [
                        home_probability,
                        draw_probability,
                        away_probability
                    ][i],
                    "EV (%)": ev
                })

            df = pd.DataFrame(table)

            st.dataframe(
                df.round(2),
                use_container_width=True,
                hide_index=True
            )

            probability_total = (
                home_probability
                + draw_probability
                + away_probability
            )

            if abs(probability_total - 100) > 0.1:
                st.error(
                    f"Probabilities zako ni {probability_total:.1f}%. "
                    "Jumla inapaswa kuwa 100%."
                )
            else:
                st.success(
                    "Probabilities zako zina jumla ya 100%."
                )

            st.warning(
                "EV ni makadirio yanayotegemea probability "
                "uliyoingiza. EV chanya haimaanishi ushindi "
                "ni wa uhakika. Hakikisha probability yako "
                "ina msingi wa takwimu."
            )

        except ValueError as error:
            st.error(str(error))

# -----------------------------
# BEST MATCHES
# -----------------------------
elif page == "Best Matches":

    st.subheader("⭐ My Match List")

    if st.session_state.matches:

        df = pd.DataFrame(st.session_state.matches)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Matches CSV",
            data=csv,
            file_name="my_matches.csv",
            mime="text/csv"
        )

        if st.button("Clear All Matches"):
            st.session_state.matches = []
            st.rerun()

    else:
        st.info("Bado hakuna mechi zilizoongezwa.")

# -----------------------------
# SETTINGS
# -----------------------------
elif page == "Settings":

    st.subheader("⚙️ System Settings")

    st.write("**Current version:** Free manual-analysis prototype")
    st.write("**Football API:** Not connected")
    st.write("**Automatic screenshot OCR:** Not connected")
    st.write("**AI model:** Not connected")
    st.write("**Database:** Session storage only")

    st.warning(
        "Taarifa za mechi zilizowekwa kwenye session zinaweza "
        "kupotea ukifunga au kuanzisha upya app. CSV download "
        "inaweza kusaidia kuhifadhi orodha yako."
    )

    st.markdown("---")
    st.write(
        "Toleo hili halina gharama ya API. Baadaye unaweza "
        "kuongeza database, OCR na data provider ikiwa utahitaji."
    )

st.markdown("---")
st.caption(
    "AI Match Analyzer Pro | Educational analysis tool | "
    "No guaranteed betting outcomes"
)
