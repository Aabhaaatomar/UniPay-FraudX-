from click import style
import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
import io
import re

st.set_page_config(page_title="UniPay FraudX", layout="wide")

#  👉 NAVIGATION

nav_col1, nav_col2 = st.columns([6,2])

with nav_col1:
    page = st.radio("", ["Home", "Analysis", "Dashboard", "Prediction", "About"], horizontal=True)

with nav_col2:
    theme = st.radio("", ["🌙", "☀️"], horizontal=True)

if theme == "🌙":
    theme = "Dark"
else:   
    theme = "Light"
# 🎨 DYNAMIC CSS
if theme == "Dark":
    st.markdown("""
    <style>

    /* Background */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
    }

    /* Text */
    h1, h2, h3, h4, h5, h6, p, label, div {
        color: white !important;
    }

    /* Navbar */
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        justify-content: center;
        gap: 20px;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(90deg, #ff4b8b, #ff6b6b);
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        transition: 0.3s;
        font-weight: 600;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #ff6b6b, #ff4b8b);
    }

    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>

    /* Background */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }

    /* Text */
    h1, h2, h3, h4, h5, h6, p, label, div {
        color: black !important;
    }

    /* Navbar */
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        justify-content: center;
        gap: 20px;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(90deg, #ff4b8b, #ff6b6b);
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        transition: 0.3s;
        font-weight: 600;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #ff6b6b, #ff4b8b);
    }

    </style>
    """, unsafe_allow_html=True)


# ------------------ LOAD DATA ------------------
df = pd.read_excel("data.xlsx")
model = pickle.load(open("fraud_model.pkl", "rb"))

# ------------------ CUSTOM CSS ------------------

# 🎨 DYNAMIC CSS
if theme == "Dark":
    st.markdown("""
                <style>
                /* REMOVE SIDEBAR */
                section[data-testid="stSidebar"] {
                    display: none;
                    }
                /* BACKGROUND */
                [data-testid="stAppViewContainer"] {
                    background-color: #0e1117;
                    }
                /* HEADER */
                [data-testid="stHeader"] {
                    background: transparent;
                    }
                /* TEXT */
                h1, h2, h3, h4, h5, h6 {
                    color: white !important;
                    text-align: center;
                    }
                    p, label, div {
                        color: #e4e6eb !important;
                        }
                /* NAVBAR */
                div[data-testid="stRadio"] > div {
                    flex-direction: row;
                    justify-content: center;
                    gap: 20px;
                    }
                /* DATAFRAME */
                [data-testid="stDataFrame"] {
                    background-color: #1c1f26;
                    border-radius: 12px;
                    padding: 10px;
                    }
                /* EXPANDER */
                [data-testid="stExpander"] {
                    background-color: #1c1f26 !important;
                    border-radius: 12px;
                    border: 1px solid #333;
                }
                [data-testid="stExpander"] summary, [data-testid="stExpander"] div[role="button"] {
                    background-color: #2b303b !important;
                    color: white !important;
                    border-radius: 12px;
                }
                 
                /* BUTTON */
                .stButton {
                    opacity: 1 !important;
                }
                .stButton > button, button[kind="secondary"], button[kind="primary"] {
                    background: linear-gradient(90deg, #ff4b8b, #ff6b6b) !important;
                    color: white !important;
                    border-radius: 10px !important;
                    padding: 10px 20px !important;
                    border: none !important;
                    transition: 0.3s;
                    font-weight: 600 !important;
                    opacity: 1 !important;
                }
                .stButton > button p, .stButton > button div {
                    color: white !important;
                    font-weight: 600 !important;
                }
                .stButton > button:hover, button[kind="secondary"]:hover, button[kind="primary"]:hover {
                    transform: scale(1.05);
                    background: linear-gradient(90deg, #ff6b6b, #ff4b8b) !important;
                }
                .stButton > button:disabled, button[kind="secondary"]:disabled, button[kind="primary"]:disabled {
                    background: linear-gradient(90deg, #ff4b8b, #ff6b6b) !important;
                    opacity: 1 !important;
                }
                /* FULL WIDTH */
                .block-container {
                    padding-left: 2rem;
                    padding-right: 2rem;
                    }
                    </style>"""
                    , unsafe_allow_html=True)
else:
    st.markdown("""
    <style>

    section[data-testid="stSidebar"] {
        display: none;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    h1, h2, h3, h4, h5, h6 {
        color: black !important;
        text-align: center;
    }

    p, label, div {
        color: #222 !important;
    }

    div[data-testid="stRadio"] > div {
        flex-direction: row;
        justify-content: center;
        gap: 20px;
    }

    [data-testid="stDataFrame"] {
        background-color: #f5f5f5;
        border-radius: 12px;
        padding: 10px;
    }

    .stButton > button {
        background: linear-gradient(90deg, #ff4b8b, #ff6b6b);
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        transition: 0.3s;
        font-weight: 600;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #ff6b6b, #ff4b8b);
    }

    .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
    }

    </style>
    """, unsafe_allow_html=True)

# ================== HOME ==================
if page == "Home":

    st.markdown("""
    <style>
    .hero {
        height: 90vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background-image: url("https://elmeurope.com/wp-content/uploads/2024/10/elm-europe-high-demand-prediction-main.jpg");
        background-size: cover;
        background-position: center;
        color: white;
        text-align: center;
        border-radius: 20px;
    }

    .overlay {
        background: rgba(0,0,0,0.6);
        padding: 50px;
        border-radius: 20px;
    }

    .title {
        font-size: 50px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    .subtitle {
        font-size: 18px;
        margin-top: 10px;
    }

    .btn {
        margin-top: 20px;
        padding: 12px 30px;
        background-color: #f5f5f5;
        color: #333;
        border-radius: 10px;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        background-color: #ff6f91;
        color: white;
    }
    </style>

    <div class="hero">
        <div class="overlay">
            <div class="title">🚀 SMART TRANSACTION FRAUD DETECTION SYSTEM</div>
            <div class="subtitle">
            Detect fraudulent transactions in real-time with AI-powered insights
            </div>
            <div class="btn">🚀 UniPay FraudX</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================== ANALYSIS ==================
elif page == "Analysis":

    st.title("📊 Data Analysis")

    df = pd.read_excel("data.xlsx")

    st.subheader("📁 Dataset Preview")
    st.dataframe(df)

    st.subheader("📌 Basic Info")
    st.write(df.describe())

    # Tabs
    tab1, tab2 = st.tabs(["Charts", "Insights"])

    with tab1:
        st.subheader("📊 Charts")

        fig1 = px.histogram(df, x="amount", color="label")
        fig1.update_traces(
            marker_line_width=1.5,
            marker_line_color="black")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.scatter(df, x="amount", y="txn_count_1hr", color="label")
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("💡 Insights")
        
        st.markdown("""
                    🔍 **Key Observations:**
                    
                    • Transactions with **higher amounts and frequent activity** show a strong pattern of suspicious behavior.
                    
                    • **Late-night transactions (0–6 hours)** are more likely to be flagged as risky.
                    
                    • Users with **high transaction counts within short time** may indicate fraud attempts.
                    
                    • Normal transactions are generally **low frequency and moderate amount**.
                    
                    💡 **Conclusion:**  
                    
                    Combining transaction amount, frequency, and timing significantly improves fraud detection accuracy.
                    """)

# ================== DASHBOARD ==================
elif page == "Dashboard":

    st.title("📊 Transaction Analysis Dashboard")
    fig_bar = px.bar(
            df,
            x="hour",
            y="txn_count_1hr",
            color="label",
            title=" 🕒 Transactions by Hour"
            )
    fig_bar.update_traces(marker_line_color='black', marker_line_width=1)
    fig_bar.update_layout(plot_bgcolor="#f5f5f5")
    
    
    df_line = df.groupby("hour")["amount"].mean().reset_index()
    fig_line= px.line(df_line,
                      x="hour",
                      y="amount",
                      title=" 📈 Amount Trend Over Time")
    fig_line.update_traces(mode="markers+lines", marker=dict(size=8, color="#ff6f91"))
    fig_line.update_layout(plot_bgcolor="#f5f5f5")
        
    fraud_count = df["label"].value_counts()
    fig_donut = px.pie(
            values=fraud_count.values,
            names=["Normal", "Fraud"],
            hole=0.5,
            title=" 📊 Fraud vs Normal")
    fig_donut.update_layout(annotations=[dict(text='Transaction<br>Split', x=0.5, y=0.5, font_size=22, showarrow=False, font = dict(size=20, color="#ff4b8b"))])
    fig_donut.update_layout(plot_bgcolor="#f5f5f5")
    
    fig_location = px.pie(df,
                     names="location_type",
                     title=" 📍 Transaction by Location")
    fig_location.update_layout(plot_bgcolor="#f5f5f5")
        
    fig_sender = px.bar(
            df,
            x="sender_type",
            color="receiver_type",
            title=" 📊 Sender vs Receiver Comparison",
            barmode="group")
    fig_sender.update_layout(plot_bgcolor="#f5f5f5")
        
    fig_box = px.box(
            df,
            x="label",
            y="amount",
            title=" 📈 Amount Distribution (Fraud vs Normal)")
    fig_box.update_layout(plot_bgcolor="#f5f5f5")
    
    # ------------------ LAYOUT ------------------

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        st.plotly_chart(fig_line, use_container_width=True)

    st.plotly_chart(fig_donut, use_container_width=True, key="donut chart")

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(fig_location, use_container_width=True)
    with col4:
        st.plotly_chart(fig_sender, use_container_width=True)

# ================== PREDICTION ==================
elif page == "Prediction":

    st.title("🔮 Predict Transaction")

    if "amount_val" not in st.session_state:
        st.session_state.amount_val = 0.0
    if "txn_val" not in st.session_state:
        st.session_state.txn_val = 0
    if "hour_val" not in st.session_state:
        st.session_state.hour_val = 12

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎙️ Voice-Activated Transaction")
    st.markdown("<p style='text-align: center; color: #aaa; margin-bottom: 20px;'>Tap the microphone below and speak your transaction details.</p>", unsafe_allow_html=True)
    
    # Use columns to tightly center the recorder and button
    col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
    
    with col2:
        audio_bytes = audio_recorder(
            text="Click to speak transaction details...", 
            recording_color="#ff1e56", 
            neutral_color="#ff4b8b", 
            icon_name="microphone", 
            icon_size="2x", 
            pause_threshold=2.0
        )
        
    with col3:
        if st.button("🗑️ Delete"):
            if audio_bytes:
                st.session_state.last_audio = audio_bytes
            st.session_state.amount_val = 0.0
            st.session_state.txn_val = 0
            st.session_state.hour_val = 12
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    
    if audio_bytes and ("last_audio" not in st.session_state or st.session_state.last_audio != audio_bytes):
        st.session_state.last_audio = audio_bytes
        st.audio(audio_bytes, format="audio/wav")
        r = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = r.record(source)
            try:
                text = r.recognize_google(audio_data)
                st.success(f"🗣️ Transcribed: '{text}'")
                nums = [int(s) for s in re.findall(r'\d+', text)]
                if len(nums) >= 1:
                    st.session_state.amount_val = float(nums[0])
                if len(nums) >= 2:
                    st.session_state.txn_val = int(nums[1])
                if len(nums) >= 3:
                    st.session_state.hour_val = min(23, int(nums[2]))
            except sr.UnknownValueError:
                st.warning("⚠️ Google Speech Recognition could not understand the audio. Please try speaking a bit louder or clearer.")
                import base64
                tts = gTTS(text="Voice not heard properly, try again", lang='en')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                b64 = base64.b64encode(fp.read()).decode()
                md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                st.markdown(md, unsafe_allow_html=True)
            except sr.RequestError as e:
                st.error(f"❌ Could not request results from Google Speech Recognition service; {e}")
            except Exception as e:
                st.error(f"❌ Error processing audio: {str(e)}")

    with st.expander("⌨️ Manual Entry", expanded=True):
        amount = st.number_input("Amount", value=st.session_state.amount_val)
        txn = st.number_input("Txn Count", value=st.session_state.txn_val)
        hour = st.slider("Hour", 0, 23, value=st.session_state.hour_val)

    if st.button("Predict"):
        if amount > 10000:
            pred = 1
            reason = "High transaction amount"

        elif txn > 10:
            pred = 1
            reason = "Too many transactions"

        elif 0<= hour <= 5 and amount > 4000:
            pred = 1
            reason = "Late night transaction"
        
        else:
            pred = model.predict([[amount, txn, hour]])[0]
            reason = "Based on ML model"
            
        # Confidence calculation
        proba = model.predict_proba([[amount, txn, hour]])[0]
        confidence = max(proba) * 100
        
        # RISK SCORE CALCULATION
        risk_score = 0
        
        if amount > 10000:
            risk_score += 50
        if txn > 10:
            risk_score += 30
        if 0<= hour <= 5 and amount > 4000:
            risk_score += 20
        
        if risk_score > 70:
            pred = 1
            reason = "High risk score based on rules"
        elif risk_score > 40:
            pred = 1
            reason = "Moderate risk score based on rules"
        elif risk_score > 0:
            pred = 1
            reason = "Low risk score based on rules"
        
        
        if pred == 1:
            st.markdown(f"""
                        <div style="
                        background: linear-gradient(135deg, #ff4b8b, #ff1e56);
                        padding: 25px;
                        border-radius: 15px;
                        color: white;
                        text-align: left;
                        font-size: 18px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                        ">
                        🚨 <b>Suspicious Transaction Detected</b><br><br>
                        💰 Amount: {amount}<br>
                        🔁 Transactions: {txn}<br>
                        ⏰ Hour: {hour}<br>
                        📊 Confidence: {confidence:.2f}%<br><br>
                        📈 Risk Score: {risk_score}<br><br>
                        ⚠️ Risk Level: {"High" if risk_score > 70 else "Moderate" if risk_score > 40 else "Low"}<br>
                        📝 Reason: {reason}<br><br>
                        ⚠️ <b>Recommendation:</b><br>
                        • Verify transaction immediately<br>
                        • Enable OTP or 2FA authentication<br>
                        • Monitor account activity closely
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
            background: linear-gradient(135deg, #36cfc9, #00b894);
            padding: 25px;
            border-radius: 15px;
            color: white;
            text-align: left;
            font-size: 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
        ✅ <b>Normal Transaction</b><br><br>

        💰 Amount: {amount}<br>
        🔁 Transactions: {txn}<br>
        ⏰ Hour: {hour}<br>
        📊 Confidence: {confidence:.2f}%<br><br>
        📈 Risk Score: {risk_score}<br><br>
        ⚠️ Risk Level: {"High" if risk_score > 70 else "Moderate" if risk_score > 40 else "Low"}<br>
        📝 Reason: {reason}<br><br>

        👍 <b>Recommendation:</b><br>
        • Transaction appears safe<br>
        • No immediate action required<br>
        • Continue normal usage
        </div>
        """, unsafe_allow_html=True)
        
        # --- TTS Audio Output ---
        import base64
        warning_text = "Alert, this transaction matches a high risk profile. Please verify immediately." if pred == 1 else "Transaction appears safe. No immediate action required."
        tts = gTTS(text=warning_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    

    
# ================== ABOUT ==================
elif page == "About":

    st.title("👨‍💻 About UniPay FraudX")

    st.markdown("""
    **UniPay FraudX** is an AI-powered fraud detection system designed to identify and prevent fraudulent transactions in real-time. Leveraging advanced machine learning algorithms, UniPay FraudX analyzes transaction patterns, user behavior, and contextual data to accurately flag suspicious activities.

    Key Features:
    - Real-time fraud detection with high accuracy
    - User-friendly dashboard for monitoring transactions
    - Customizable alerts and notifications
    - Comprehensive data analysis tools

    Developed by a passionate team of data scientists and engineers, UniPay FraudX aims to provide businesses with a robust solution to combat financial fraud and enhance security.
    """)
    
