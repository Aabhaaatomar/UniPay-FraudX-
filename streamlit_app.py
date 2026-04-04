from click import style
import streamlit as st
import pandas as pd
import pickle
import plotly.express as px

st.set_page_config(page_title="UniPay FraudX", layout="wide")

# 🔥 NAVBAR STYLE
theme = st.radio("Theme", ["Dark", "Light"], horizontal=True,key="theme_toggle")
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

# 👉 NAVIGATION

page = st.radio(
    "",
    ["Home", "Analysis", "Dashboard", "Prediction", "About"],
    horizontal=True,
    key="nav"
)

# 👉 THEME BELOW / SIDE
theme = st.radio(
    "",
    ["🌙", "☀️"],
    horizontal=True,
    key="theme_toggle"
)

nav_col1, nav_col2 = st.columns([6,2])

with nav_col1:
    page = st.radio("", ["Home", "Analysis", "Dashboard", "Prediction", "About"], horizontal=True)

with nav_col2:
    theme = st.radio("", ["🌙", "☀️"], horizontal=True)

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
                 
                /* BUTTON */
                
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

    amount = st.number_input("Amount")
    txn = st.number_input("Txn Count")
    hour = st.slider("Hour", 0, 23)

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
    
