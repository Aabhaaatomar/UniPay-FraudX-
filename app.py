import sys
import os
# Make models/ importable regardless of working directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"))

import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
import joblib
import plotly.graph_objects as go
import io
import re
import speech_recognition as sr
from gtts import gTTS
from audio_recorder_streamlit import audio_recorder
import base64
from fraud_detector import analyze_transaction

st.set_page_config(page_title="UniPay FraudX", layout="wide", initial_sidebar_state="expanded")

if "amount_val" not in st.session_state:
    st.session_state.amount_val = 1500.0
if "txn_val" not in st.session_state:
    st.session_state.txn_val = 2
if "hour_val" not in st.session_state:
    st.session_state.hour_val = 14

# ================== CSS THEME INJECTION ==================
def inject_custom_css(theme):
    # Base Google Font
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            padding-top: 2rem;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Modern Metric Card */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }
        
        /* Metric Styling */
        .metric-title {
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            opacity: 0.8;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(90deg, #ff4b8b, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metric-subtitle {
            font-size: 0.85rem;
            opacity: 0.6;
            margin-top: 8px;
        }

        /* Gradient Button */
        .stButton > button {
            background: linear-gradient(135deg, #ff4b8b 0%, #ff1e56 100%);
            color: white !important;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            border: none;
            box-shadow: 0 4px 15px rgba(255, 75, 139, 0.3);
            transition: all 0.3s ease;
            font-weight: 600;
            width: 100%;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 75, 139, 0.4);
            background: linear-gradient(135deg, #ff1e56 0%, #ff4b8b 100%);
        }

        /* Probability Meter Animation */
        @keyframes fillBar {
            from { width: 0%; }
        }
        .progress-bg {
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            height: 12px;
            width: 100%;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            border-radius: 8px;
            animation: fillBar 1.5s cubic-bezier(0.1, 0.7, 0.1, 1) forwards;
        }

        /* Result Alert Boxes */
        .result-box {
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-top: 20px;
            border-left: 6px solid transparent;
        }
        .result-danger {
            background: linear-gradient(145deg, rgba(255, 30, 86, 0.1) 0%, rgba(255, 75, 139, 0.05) 100%);
            border-color: #ff1e56;
            border: 1px solid rgba(255, 30, 86, 0.2);
            border-left: 6px solid #ff1e56;
        }
        .result-success {
            background: linear-gradient(145deg, rgba(0, 184, 148, 0.1) 0%, rgba(54, 207, 201, 0.05) 100%);
            border-color: #00b894;
            border: 1px solid rgba(0, 184, 148, 0.2);
            border-left: 6px solid #00b894;
        }
        
        /* Top Spacing fix */
        .block-container {
            padding-top: 2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if theme == "Dark":
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] { background-color: #0b0f19; }
            [data-testid="stSidebar"] { background-color: #111827; }
            h1, h2, h3, h4, h5, h6, p, label, .metric-title, .metric-subtitle { color: #f3f4f6 !important; }
            .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255,255,255,0.05); }
            [data-testid="stDataFrame"] { background-color: #1f2937; border-radius: 12px; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] { background-color: #f8fafc; }
            [data-testid="stSidebar"] { background-color: #ffffff; }
            h1, h2, h3, h4, h5, h6, p, label, .metric-title, .metric-subtitle { color: #1e293b !important; }
            .glass-card { background: rgba(255, 255, 255, 1); border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 20px rgba(0,0,0,0.03); }
            .progress-bg { background: rgba(0,0,0,0.05); }
            [data-testid="stDataFrame"] { background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); }
            </style>
        """, unsafe_allow_html=True)

# ================== DATA LOADING ==================
@st.cache_data
def load_data():
    dataset_path = os.path.join("dataset", "data.xlsx")
    if not os.path.exists(dataset_path):
        st.error(f"Dataset not found at {dataset_path}. Please ensure the data file exists.")
        return pd.DataFrame()
    return pd.read_excel(dataset_path)

@st.cache_resource
def load_model():
    model_path = os.path.join("models", "fraud_model.pkl")
    if not os.path.exists(model_path):
        st.error(f"Model not found at {model_path}. Please train or place the model file.")
        return None
    try:
        return pickle.load(open(model_path, "rb"))
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

df = load_data()
model = load_model()

if df.empty or model is None:
    st.warning("⚠️ Application is running in limited mode due to missing data or model.")
    st.stop()

# ================== NAVIGATION & SIDEBAR ==================
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; font-weight: 700; background: linear-gradient(90deg, #ff4b8b, #ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;">UniPay FraudX</h1>
        <p style="font-size: 0.8rem; opacity: 0.7; margin-top: 0;">AI Fraud Intelligence</p>
    </div>
    """, unsafe_allow_html=True
)

st.sidebar.markdown("### Navigation")
page = st.sidebar.radio(
    label="Navigation", 
    options=[
        "🏠 Home", 
        "📊 Dashboard", 
        "🔍 Analysis", 
        "🔮 Prediction Engine", 
        "⚙️ About"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown("### Settings")
theme_choice = st.sidebar.radio("Theme Mode", ["🌙 Dark", "☀️ Light"])
theme = "Dark" if "Dark" in theme_choice else "Light"

inject_custom_css(theme)

# Plotly Theme Settings
chart_font_color = "#f3f4f6" if theme == "Dark" else "#1e293b"
chart_bg_color = "rgba(0,0,0,0)"

def apply_plotly_layout(fig):
    fig.update_layout(
        plot_bgcolor=chart_bg_color,
        paper_bgcolor=chart_bg_color,
        font=dict(family="Inter", color=chart_font_color),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.1)', zeroline=False)
    )
    return fig

# ================== PAGES ==================

if "Home" in page:
    st.markdown("""
        <style>
        .hero-container {
            height: 70vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: linear-gradient(135deg, rgba(255, 75, 139, 0.1) 0%, rgba(255, 30, 86, 0.05) 100%);
            border-radius: 24px;
            padding: 40px;
            border: 1px solid rgba(255, 75, 139, 0.2);
            position: relative;
            overflow: hidden;
        }
        .hero-container::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(255,75,139,0.1) 0%, transparent 50%);
            animation: pulse 15s infinite linear;
        }
        @keyframes pulse {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ff4b8b, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            z-index: 1;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            max-width: 600px;
            opacity: 0.8;
            margin-bottom: 40px;
            z-index: 1;
        }
        </style>
        
        <div class="hero-container">
            <div class="hero-title">Next-Gen Fraud Defense</div>
            <div class="hero-subtitle">
                Protect your digital ecosystem with real-time AI analytics, robust machine learning predictions, and enterprise-grade transaction intelligence.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown("<div class='glass-card'><h4>⚡ Real-Time ML</h4><p style='opacity:0.7; font-size:0.9rem;'>Millisecond inference times for active transaction streams.</p></div>", unsafe_allow_html=True)
    c2.markdown("<div class='glass-card'><h4>📊 Deep Analytics</h4><p style='opacity:0.7; font-size:0.9rem;'>Identify complex behavioral patterns and emerging threats.</p></div>", unsafe_allow_html=True)
    c3.markdown("<div class='glass-card'><h4>🛡️ Enterprise Scale</h4><p style='opacity:0.7; font-size:0.9rem;'>Designed for high-throughput fintech infrastructure.</p></div>", unsafe_allow_html=True)

elif "Dashboard" in page:
    st.markdown("<h2>Analytics Dashboard</h2>", unsafe_allow_html=True)
    
    # KPIs
    total_tx = len(df)
    fraud_tx = len(df[df["label"] == "Suspicious"])
    fraud_rate = (fraud_tx / total_tx) * 100 if total_tx > 0 else 0
    total_vol = df["amount"].sum()
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    kpi1.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Total Volume</div>
            <div class="metric-value">₹{total_vol/1000000:.2f}M</div>
            <div class="metric-subtitle">Processed Transactions</div>
        </div>
    """, unsafe_allow_html=True)
    
    kpi2.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Total Transactions</div>
            <div class="metric-value">{total_tx:,}</div>
            <div class="metric-subtitle">Last 30 Days</div>
        </div>
    """, unsafe_allow_html=True)
    
    kpi3.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Fraud Flags</div>
            <div class="metric-value">{fraud_tx:,}</div>
            <div class="metric-subtitle">Suspicious Activities</div>
        </div>
    """, unsafe_allow_html=True)
    
    kpi4.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Fraud Rate</div>
            <div class="metric-value">{fraud_rate:.2f}%</div>
            <div class="metric-subtitle">Of total volume</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin: 2rem 0;'>", unsafe_allow_html=True)
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_bar = px.bar(
            df.groupby(["hour", "label"])["txn_count_1hr"].sum().reset_index(),
            x="hour", y="txn_count_1hr", color="label",
            title="Activity Volume by Hour",
            color_discrete_sequence=["#00b894", "#ff4b8b"]
        )
        st.plotly_chart(apply_plotly_layout(fig_bar), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        df_line = df.groupby("hour")["amount"].mean().reset_index()
        fig_line = px.line(
            df_line, x="hour", y="amount",
            title="Average Transaction Value Trend"
        )
        fig_line.update_traces(line_color="#ff4b8b", line_width=3, fill='tozeroy', fillcolor='rgba(255,75,139,0.1)')
        st.plotly_chart(apply_plotly_layout(fig_line), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Charts Row 2
    col3, col4 = st.columns([1, 1.5])
    
    with col3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_donut = px.pie(
            df, names="label", hole=0.6,
            title="Risk Distribution",
            color_discrete_sequence=["#00b894", "#ff4b8b"]
        )
        fig_donut.update_layout(annotations=[dict(text=f'{fraud_rate:.1f}%<br>Fraud', x=0.5, y=0.5, font_size=20, showarrow=False, font=dict(color=chart_font_color))])
        st.plotly_chart(apply_plotly_layout(fig_donut), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col4:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_sender = px.bar(
            df, x="sender_type", color="receiver_type",
            title="Entity Type Correlation Matrix", barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(apply_plotly_layout(fig_sender), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


elif "Analysis" in page:
    st.markdown("<h2>Data Intelligence Explorer</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("#### Transaction Registry")
    st.dataframe(df, use_container_width=True, height=400)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_hist = px.histogram(df, x="amount", color="label", nbins=40, title="Amount Distribution Density", color_discrete_sequence=["#00b894", "#ff4b8b"])
        st.plotly_chart(apply_plotly_layout(fig_hist), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_scatter = px.scatter(df, x="amount", y="txn_count_1hr", color="label", size="amount", hover_data=["hour"], title="Velocity vs Value Analysis", color_discrete_sequence=["#00b894", "#ff4b8b"])
        st.plotly_chart(apply_plotly_layout(fig_scatter), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif "Prediction" in page:
    st.markdown("<h2>Real-time Fraud Prediction Engine</h2>", unsafe_allow_html=True)
    st.markdown("<p style='opacity: 0.8;'>Submit transaction telemetry for instant ML inference.</p>", unsafe_allow_html=True)
    
    form_col, result_col = st.columns([1, 1.2])
    
    with form_col:
        st.markdown("<div class='glass-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("#### 🎙️ Voice Input")
        st.markdown("<p style='font-size: 0.9em; opacity: 0.7;'>Click mic to speak transaction details</p>", unsafe_allow_html=True)
        
        col_mic, col_del = st.columns([1, 1])
        with col_mic:
            audio_bytes = audio_recorder(text="", pause_threshold=2.0)
        with col_del:
            if st.button("🗑️ Reset", use_container_width=True):
                if audio_bytes:
                    st.session_state.last_audio = audio_bytes
                st.session_state.amount_val = 1500.0
                st.session_state.txn_val = 2
                st.session_state.hour_val = 14
                st.rerun()

        if audio_bytes and ("last_audio" not in st.session_state or st.session_state.last_audio != audio_bytes):
            st.session_state.last_audio = audio_bytes
            st.audio(audio_bytes, format="audio/wav")
            r = sr.Recognizer()
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio_data = r.record(source)
                try:
                    text = r.recognize_google(audio_data)
                    st.success(f"🗣️ '{text}'")
                    nums = [int(s) for s in re.findall(r'\d+', text)]
                    if len(nums) >= 1: st.session_state.amount_val = float(nums[0])
                    if len(nums) >= 2: st.session_state.txn_val = int(nums[1])
                    if len(nums) >= 3: st.session_state.hour_val = min(23, int(nums[2]))
                except sr.UnknownValueError:
                    st.warning("⚠️ Could not understand audio.")
                    tts = gTTS(text="Voice not heard properly, try again", lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    b64 = base64.b64encode(fp.read()).decode()
                    st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### ⌨️ Input Telemetry")
        amount = st.number_input("Transaction Value (₹)", min_value=0.0, value=st.session_state.amount_val, step=100.0)
        txn = st.number_input("Txn Velocity (Last 1hr)", min_value=0, value=st.session_state.txn_val, step=1)
        hour = st.slider("Hour of Day", 0, 23, value=st.session_state.hour_val)
        
        st.markdown("<br>", unsafe_allow_html=True)
        predict_btn = st.button("Initialize Inference", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with result_col:
        if predict_btn:
            # ── Hybrid fraud analysis via fraud_detector module ──
            result = analyze_transaction(
                amount=amount,
                txn_count=txn,
                hour=hour,
                model=model,
            )

            final_pred  = 1 if result["is_fraud"] else 0
            risk_score  = result["fraud_score"]          # real calculated score 0–100
            reason      = result["reason"]
            risk_level  = result["risk_label"]            # LOW / MEDIUM / HIGH / CRITICAL
            confidence  = result["ml_proba"] * 100        # actual ML fraud probability %
            rules_fired = result["triggered_rules"]

            card_class  = "result-danger" if final_pred == 1 else "result-success"
            icon        = "🚨" if final_pred == 1 else "✅"
            color       = "#ff1e56" if final_pred == 1 else "#00b894"
            display_verdict = "SUSPICIOUS" if final_pred == 1 else "SAFE"
            
            # Build triggered rules HTML
            rules_html = ""
            if rules_fired:
                rules_items = "".join(
                    f"<li style='margin-bottom:4px; font-size:0.85rem; opacity:0.85;'>{r}</li>"
                    for r in rules_fired
                )
                rules_html = f"""
                    <hr style="border:1px solid rgba(128,128,128,0.1); margin: 16px 0;">
                    <div style="font-size:0.8rem; font-weight:600; opacity:0.7; margin-bottom:8px;">TRIGGERED RULES</div>
                    <ul style="margin:0; padding-left:18px; list-style:disc;">{rules_items}</ul>
                """

            st.markdown(f"""
                <div class="{card_class}">
                    <h3 style="margin-top:0; color: {color} !important;">{icon} {display_verdict} — {risk_level} RISK</h3>
                    <p style="opacity:0.8; margin-bottom: 20px;">{reason}</p>

                    <div style="display:flex; justify-content:space-between; margin-bottom: 5px;">
                        <span style="font-size:0.9rem; font-weight:600;">ML Fraud Probability</span>
                        <span style="font-size:0.9rem; font-weight:600; color:{color};">{confidence:.1f}%</span>
                    </div>
                    <div class="progress-bg">
                        <div class="progress-fill" style="width: {min(confidence, 100):.1f}%; background: {color};"></div>
                    </div>

                    <hr style="border:1px solid rgba(128,128,128,0.1); margin: 20px 0;">

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div style="font-size:0.8rem; opacity:0.7;">Risk Score (Calculated)</div>
                            <div style="font-size:1.5rem; font-weight:700;">{risk_score}/100</div>
                        </div>
                        <div>
                            <div style="font-size:0.8rem; opacity:0.7;">Recommendation</div>
                            <div style="font-size:1.1rem; font-weight:600;">{result['recommendation'].replace('_', ' ')}</div>
                        </div>
                    </div>
                    </div>
                    {rules_html}
                </div>
            """, unsafe_allow_html=True)
            
            # AI Audio Alert for Fraud
            if final_pred == 1:
                try:
                    tts = gTTS(text="Warning: Fraudulent transaction detected. Please verify.", lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    b64 = base64.b64encode(fp.read()).decode()
                    st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                except Exception as e:
                    pass
        else:
            st.markdown("""
                <div style="height: 100%; display: flex; align-items: center; justify-content: center; opacity: 0.5; border: 2px dashed rgba(128,128,128,0.2); border-radius: 16px; padding: 50px; text-align: center;">
                    Waiting for telemetry input...<br>Enter parameters and click Initialize Inference.
                </div>
            """, unsafe_allow_html=True)

elif "About" in page:
    st.markdown("<h2>System Architecture & Intelligence</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <h4>UniPay FraudX</h4>
            <p style="opacity: 0.8; line-height: 1.6;">
                An enterprise-grade fraud detection platform engineered to process digital transactions in real-time. 
                Combining heuristic rule engines with advanced Machine Learning (Random Forest algorithms), FraudX isolates behavioral anomalies, high-velocity attacks, and unusual geographic footprints with millisecond latency.
            </p>
            <br>
            <h5>Technical Stack</h5>
            <ul style="opacity: 0.8; line-height: 1.6;">
                <li><b>Frontend Infrastructure:</b> Streamlit, Custom HTML/CSS (Glassmorphism), Plotly</li>
                <li><b>Inference Engine:</b> Scikit-Learn (Random Forest Classifier)</li>
                <li><b>Data Processing Pipeline:</b> Pandas, NumPy</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
 app
import os
import logging
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Configure logging to monitor file read occurrences
logging.basicConfig(level=logging.INFO)

DATA_PATH = "data.xlsx"

# Global cache variables
_cached_df = None
_last_modified_time = 0

def get_dataframe():
    """
    Helper function that reads the Excel file dynamically only if it has 
    been modified on disk. Otherwise, it serves data instantly from memory.
    """
    global _cached_df, _last_modified_time
    
    if not os.path.exists(DATA_PATH):
        logging.error(f"Database file '{DATA_PATH}' not found!")
        # Fallback: return empty dataframe with expected columns to prevent server crash
        return pd.DataFrame(columns=["label", "hour", "txn_count_1hr", "amount"])
    
    try:
        # Check the last modification timestamp of the file
        current_mtime = os.path.getmtime(DATA_PATH)
        
        # If file is updated or cache is completely empty, read from disk
        if _cached_df is None or current_mtime > _last_modified_time:
            logging.info("Reading Excel file from disk (Cache refresh)...")
            _cached_df = pd.read_excel(DATA_PATH, engine="openpyxl")
            _last_modified_time = current_mtime
            
        return _cached_df
    except Exception as e:
        logging.error(f"Error accessing or reading Excel data file: {e}")
        return pd.DataFrame(columns=["label", "hour", "txn_count_1hr", "amount"])


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    # Fetch optimized data through the helper cache function
    df = get_dataframe().copy()

    # Graceful fallback handler if dataframe contains no rows
    if df.empty:
        return render_template(
            "dashboard.html", 
            transactions=[], total_txn=0, suspicious_txn=0, normal_txn=0,
            hours=[], counts=[], amounts=[], txn_counts=[], labels=[]
        )

    # Convert DataFrame records cleanly to dictionaries for HTML rendering
    transactions = df.to_dict(orient="records")

    # Metrics Calculations
    total_txn = len(df)
    suspicious_txn = len(df[df["label"].str.lower() == "suspicious"])
    normal_txn = len(df[df["label"].str.lower() == "normal"])

    # Extract Chart Lists
    hours = df["hour"].tolist()
    counts = df["txn_count_1hr"].tolist()
    labels = df["label"].tolist()

    # FIX: Vectorized safe casting via Pandas to protect against type crashes (NaN strings)
    amounts = df["amount"].fillna(0).astype(int).tolist()
    txn_counts = df["txn_count_1hr"].fillna(0).astype(int).tolist()

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_txn=int(total_txn),
        suspicious_txn=int(suspicious_txn),
        normal_txn=int(normal_txn),
        hours=hours,
        counts=counts,
        amounts=amounts,
        txn_counts=txn_counts,
        labels=labels
    )


if __name__ == "__main__":
    app.run(debug=True)
import sys
import os
# Make models/ importable regardless of working directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"))

import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
import joblib
import plotly.graph_objects as go
from fraud_detector import analyze_transaction

st.set_page_config(page_title="UniPay FraudX", layout="wide", initial_sidebar_state="expanded")

# ================== CSS THEME INJECTION ==================
def inject_custom_css(theme):
    # Base Google Font
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            padding-top: 2rem;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Modern Metric Card */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }
        
        /* Metric Styling */
        .metric-title {
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            opacity: 0.8;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(90deg, #ff4b8b, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metric-subtitle {
            font-size: 0.85rem;
            opacity: 0.6;
            margin-top: 8px;
        }

        /* Gradient Button */
        .stButton > button {
            background: linear-gradient(135deg, #ff4b8b 0%, #ff1e56 100%);
            color: white !important;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            border: none;
            box-shadow: 0 4px 15px rgba(255, 75, 139, 0.3);
            transition: all 0.3s ease;
            font-weight: 600;
            width: 100%;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 75, 139, 0.4);
            background: linear-gradient(135deg, #ff1e56 0%, #ff4b8b 100%);
        }

        /* Probability Meter Animation */
        @keyframes fillBar {
            from { width: 0%; }
        }
        .progress-bg {
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            height: 12px;
            width: 100%;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            border-radius: 8px;
            animation: fillBar 1.5s cubic-bezier(0.1, 0.7, 0.1, 1) forwards;
        }

        /* Result Alert Boxes */
        .result-box {
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-top: 20px;
            border-left: 6px solid transparent;
        }
        .result-danger {
            background: linear-gradient(145deg, rgba(255, 30, 86, 0.1) 0%, rgba(255, 75, 139, 0.05) 100%);
            border-color: #ff1e56;
            border: 1px solid rgba(255, 30, 86, 0.2);
            border-left: 6px solid #ff1e56;
        }
        .result-success {
            background: linear-gradient(145deg, rgba(0, 184, 148, 0.1) 0%, rgba(54, 207, 201, 0.05) 100%);
            border-color: #00b894;
            border: 1px solid rgba(0, 184, 148, 0.2);
            border-left: 6px solid #00b894;
        }
        
        /* Top Spacing fix */
        .block-container {
            padding-top: 2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if theme == "Dark":
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] { background-color: #0b0f19; }
            [data-testid="stSidebar"] { background-color: #111827; }
            h1, h2, h3, h4, h5, h6, p, label, .metric-title, .metric-subtitle { color: #f3f4f6 !important; }
            .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255,255,255,0.05); }
            [data-testid="stDataFrame"] { background-color: #1f2937; border-radius: 12px; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] { background-color: #f8fafc; }
            [data-testid="stSidebar"] { background-color: #ffffff; }
            h1, h2, h3, h4, h5, h6, p, label, .metric-title, .metric-subtitle { color: #1e293b !important; }
            .glass-card { background: rgba(255, 255, 255, 1); border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 20px rgba(0,0,0,0.03); }
            .progress-bg { background: rgba(0,0,0,0.05); }
            [data-testid="stDataFrame"] { background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); }
            </style>
        """, unsafe_allow_html=True)

# ================== DATA LOADING ==================
@st.cache_data
def load_data():
    dataset_path = os.path.join("dataset", "data.xlsx")
    if not os.path.exists(dataset_path):
        st.error(f"Dataset not found at {dataset_path}. Please ensure the data file exists.")
        return pd.DataFrame()
    return pd.read_excel(dataset_path)

@st.cache_resource
def load_model():
    model_path = os.path.join("models", "fraud_model.pkl")
    if not os.path.exists(model_path):
        st.error(f"Model not found at {model_path}. Please train or place the model file.")
        return None
    try:
        return pickle.load(open(model_path, "rb"))
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

df = load_data()
model = load_model()

if df.empty or model is None:
    st.warning("⚠️ Application is running in limited mode due to missing data or model.")
    st.stop()

# ================== NAVIGATION & SIDEBAR ==================
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; font-weight: 700; background: linear-gradient(90deg, #ff4b8b, #ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;">UniPay FraudX</h1>
        <p style="font-size: 0.8rem; opacity: 0.7; margin-top: 0;">AI Fraud Intelligence</p>
    </div>
    """, unsafe_allow_html=True
)

st.sidebar.markdown("### Navigation")
page = st.sidebar.radio(
    label="Navigation", 
    options=[
        "🏠 Home", 
        "📊 Dashboard", 
        "🔍 Analysis", 
        "🔮 Prediction Engine", 
        "⚙️ About"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown("### Settings")
theme_choice = st.sidebar.radio("Theme Mode", ["🌙 Dark", "☀️ Light"])
theme = "Dark" if "Dark" in theme_choice else "Light"

inject_custom_css(theme)

# Plotly Theme Settings
chart_font_color = "#f3f4f6" if theme == "Dark" else "#1e293b"
chart_bg_color = "rgba(0,0,0,0)"

def apply_plotly_layout(fig):
    fig.update_layout(
        plot_bgcolor=chart_bg_color,
        paper_bgcolor=chart_bg_color,
        font=dict(family="Inter", color=chart_font_color),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.1)', zeroline=False)
    )
    return fig

# ================== PAGES ==================

if "Home" in page:
    st.markdown("""
        <style>
        .hero-container {
            height: 70vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: linear-gradient(135deg, rgba(255, 75, 139, 0.1) 0%, rgba(255, 30, 86, 0.05) 100%);
            border-radius: 24px;
            padding: 40px;
            border: 1px solid rgba(255, 75, 139, 0.2);
            position: relative;
            overflow: hidden;
        }
        .hero-container::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(255,75,139,0.1) 0%, transparent 50%);
            animation: pulse 15s infinite linear;
        }
        @keyframes pulse {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ff4b8b, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            z-index: 1;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            max-width: 600px;
            opacity: 0.8;
            margin-bottom: 40px;
            z-index: 1;
        }
        </style>
        
        <div class="hero-container">
            <div class="hero-title">Next-Gen Fraud Defense</div>
            <div class="hero-subtitle">
                Protect your digital ecosystem with real-time AI analytics, robust machine learning predictions, and enterprise-grade transaction intelligence.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown("<div class='glass-card'><h4>⚡ Real-Time ML</h4><p style='opacity:0.7; font-size:0.9rem;'>Millisecond inference times for active transaction streams.</p></div>", unsafe_allow_html=True)
    c2.markdown("<div class='glass-card'><h4>📊 Deep Analytics</h4><p style='opacity:0.7; font-size:0.9rem;'>Identify complex behavioral patterns and emerging threats.</p></div>", unsafe_allow_html=True)
    c3.markdown("<div class='glass-card'><h4>🛡️ Enterprise Scale</h4><p style='opacity:0.7; font-size:0.9rem;'>Designed for high-throughput fintech infrastructure.</p></div>", unsafe_allow_html=True)

elif "Dashboard" in page:
    st.markdown("<h2>Analytics Dashboard</h2>", unsafe_allow_html=True)
    
    # KPIs
    total_tx = len(df)
    fraud_tx = len(df[df["label"] == "Suspicious"])
    fraud_rate = (fraud_tx / total_tx) * 100 if total_tx > 0 else 0
    total_vol = df["amount"].sum()
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    kpi1.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Total Volume</div>
            <div class="metric-value">₹{total_vol/1000000:.2f}M</div>
            <div class="metric-subtitle">Processed Transactions</div>
        </div>
    """, unsafe_allow_html=True)
    
    kpi2.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Total Transactions</div>
            <div class="metric-value">{total_tx:,}</div>
            <div class="metric-subtitle">Last 30 Days</div>
        </div>
    """, unsafe_allow_html=True)
    
    kpi3.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Fraud Flags</div>
            <div class="metric-value">{fraud_tx:,}</div>
            <div class="metric-subtitle">Suspicious Activities</div>
        </div>
    """, unsafe_allow_html=True)
    
    kpi4.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Fraud Rate</div>
            <div class="metric-value">{fraud_rate:.2f}%</div>
            <div class="metric-subtitle">Of total volume</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin: 2rem 0;'>", unsafe_allow_html=True)
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_bar = px.bar(
            df.groupby(["hour", "label"])["txn_count_1hr"].sum().reset_index(),
            x="hour", y="txn_count_1hr", color="label",
            title="Activity Volume by Hour",
            color_discrete_sequence=["#00b894", "#ff4b8b"]
        )
        st.plotly_chart(apply_plotly_layout(fig_bar), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        df_line = df.groupby("hour")["amount"].mean().reset_index()
        fig_line = px.line(
            df_line, x="hour", y="amount",
            title="Average Transaction Value Trend"
        )
        fig_line.update_traces(line_color="#ff4b8b", line_width=3, fill='tozeroy', fillcolor='rgba(255,75,139,0.1)')
        st.plotly_chart(apply_plotly_layout(fig_line), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Charts Row 2
    col3, col4 = st.columns([1, 1.5])
    
    with col3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_donut = px.pie(
            df, names="label", hole=0.6,
            title="Risk Distribution",
            color_discrete_sequence=["#00b894", "#ff4b8b"]
        )
        fig_donut.update_layout(annotations=[dict(text=f'{fraud_rate:.1f}%<br>Fraud', x=0.5, y=0.5, font_size=20, showarrow=False, font=dict(color=chart_font_color))])
        st.plotly_chart(apply_plotly_layout(fig_donut), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col4:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_sender = px.bar(
            df, x="sender_type", color="receiver_type",
            title="Entity Type Correlation Matrix", barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(apply_plotly_layout(fig_sender), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


elif "Analysis" in page:
    st.markdown("<h2>Data Intelligence Explorer</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("#### Transaction Registry")
    st.dataframe(df, use_container_width=True, height=400)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_hist = px.histogram(df, x="amount", color="label", nbins=40, title="Amount Distribution Density", color_discrete_sequence=["#00b894", "#ff4b8b"])
        st.plotly_chart(apply_plotly_layout(fig_hist), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_scatter = px.scatter(df, x="amount", y="txn_count_1hr", color="label", size="amount", hover_data=["hour"], title="Velocity vs Value Analysis", color_discrete_sequence=["#00b894", "#ff4b8b"])
        st.plotly_chart(apply_plotly_layout(fig_scatter), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif "Prediction" in page:
    st.markdown("<h2>Real-time Fraud Prediction Engine</h2>", unsafe_allow_html=True)
    st.markdown("<p style='opacity: 0.8;'>Submit transaction telemetry for instant ML inference.</p>", unsafe_allow_html=True)
    
    form_col, result_col = st.columns([1, 1.2])
    
    with form_col:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Input Telemetry")
        amount = st.number_input("Transaction Value (₹)", min_value=0.0, value=1500.0, step=100.0)
        txn = st.number_input("Txn Velocity (Last 1hr)", min_value=0, value=2, step=1)
        hour = st.slider("Hour of Day", 0, 23, 14)
        
        st.markdown("<br>", unsafe_allow_html=True)
        predict_btn = st.button("Initialize Inference", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with result_col:
        if predict_btn:
            # ── Hybrid fraud analysis via fraud_detector module ──
            result = analyze_transaction(
                amount=amount,
                txn_count=txn,
                hour=hour,
                model=model,
            )

            final_pred  = 1 if result["is_fraud"] else 0
            risk_score  = result["fraud_score"]          # real calculated score 0–100
            reason      = result["reason"]
            risk_level  = result["risk_label"]            # LOW / MEDIUM / HIGH / CRITICAL
            confidence  = result["ml_proba"] * 100        # actual ML fraud probability %
            rules_fired = result["triggered_rules"]

            card_class  = "result-danger" if final_pred == 1 else "result-success"
            icon        = "🚨" if final_pred == 1 else "✅"
            color       = "#ff1e56" if final_pred == 1 else "#00b894"
            display_verdict = "SUSPICIOUS" if final_pred == 1 else "SAFE"
            
            # Build triggered rules HTML
            rules_html = ""
            if rules_fired:
                rules_items = "".join(
                    f"<li style='margin-bottom:4px; font-size:0.85rem; opacity:0.85;'>{r}</li>"
                    for r in rules_fired
                )
                rules_html = f"""
                    <hr style="border:1px solid rgba(128,128,128,0.1); margin: 16px 0;">
                    <div style="font-size:0.8rem; font-weight:600; opacity:0.7; margin-bottom:8px;">TRIGGERED RULES</div>
                    <ul style="margin:0; padding-left:18px; list-style:disc;">{rules_items}</ul>
                """

            st.markdown(f"""
                <div class="{card_class}">
                    <h3 style="margin-top:0; color: {color} !important;">{icon} {display_verdict} — {risk_level} RISK</h3>
                    <p style="opacity:0.8; margin-bottom: 20px;">{reason}</p>

                    <div style="display:flex; justify-content:space-between; margin-bottom: 5px;">
                        <span style="font-size:0.9rem; font-weight:600;">ML Fraud Probability</span>
                        <span style="font-size:0.9rem; font-weight:600; color:{color};">{confidence:.1f}%</span>
                    </div>
                    <div class="progress-bg">
                        <div class="progress-fill" style="width: {min(confidence, 100):.1f}%; background: {color};"></div>
                    </div>

                    <hr style="border:1px solid rgba(128,128,128,0.1); margin: 20px 0;">

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div style="font-size:0.8rem; opacity:0.7;">Risk Score (Calculated)</div>
                            <div style="font-size:1.5rem; font-weight:700;">{risk_score}/100</div>
                        </div>
                        <div>
                            <div style="font-size:0.8rem; opacity:0.7;">Recommendation</div>
                            <div style="font-size:1.1rem; font-weight:600;">{result['recommendation'].replace('_', ' ')}</div>
                        </div>
                    </div>
                    {rules_html}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="height: 100%; display: flex; align-items: center; justify-content: center; opacity: 0.5; border: 2px dashed rgba(128,128,128,0.2); border-radius: 16px; padding: 50px; text-align: center;">
                    Waiting for telemetry input...<br>Enter parameters and click Initialize Inference.
                </div>
            """, unsafe_allow_html=True)

elif "About" in page:
    st.markdown("<h2>System Architecture & Intelligence</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <h4>UniPay FraudX</h4>
            <p style="opacity: 0.8; line-height: 1.6;">
                An enterprise-grade fraud detection platform engineered to process digital transactions in real-time. 
                Combining heuristic rule engines with advanced Machine Learning (Random Forest algorithms), FraudX isolates behavioral anomalies, high-velocity attacks, and unusual geographic footprints with millisecond latency.
            </p>
            <br>
            <h5>Technical Stack</h5>
            <ul style="opacity: 0.8; line-height: 1.6;">
                <li><b>Frontend Infrastructure:</b> Streamlit, Custom HTML/CSS (Glassmorphism), Plotly</li>
                <li><b>Inference Engine:</b> Scikit-Learn (Random Forest Classifier)</li>
                <li><b>Data Processing Pipeline:</b> Pandas, NumPy</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
main
