import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import re
from collections import Counter
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="SheSpeaks Pulse",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Firebase (only once)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    except:
        st.error("Firebase key not found. Please ensure firebase_key.json is in the project directory.")
        st.stop()

# Firestore DB
db = firestore.client()

# Modern Professional CSS with bright colors, animations, and gradients
st.markdown("""
<style>
    /* Modern Professional Theme */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Navbar Styling */
    .navbar {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        border-bottom: 2px solid #e91e63;
        padding: 1.5rem 0;
        margin-bottom: 3rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        animation: slideDown 0.8s ease-out;
    }
    
    @keyframes slideDown {
        from { transform: translateY(-100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .nav-item {
        display: inline-block;
        margin: 0 0.8rem;
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none;
        color: #333;
        font-weight: 600;
        font-size: 0.95rem;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .nav-item:hover {
        background: linear-gradient(45deg, #e91e63, #ff6b9d);
        color: white;
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(233, 30, 99, 0.4);
    }
    
    .nav-item.active {
        background: linear-gradient(45deg, #e91e63, #ff6b9d);
        color: white;
        box-shadow: 0 8px 25px rgba(233, 30, 99, 0.4);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 8px 25px rgba(233, 30, 99, 0.4); }
        50% { box-shadow: 0 8px 25px rgba(233, 30, 99, 0.6); }
        100% { box-shadow: 0 8px 25px rgba(233, 30, 99, 0.4); }
    }
    
    /* Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.9));
        border-radius: 25px;
        padding: 2rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        animation: fadeInScale 0.8s ease-out;
    }
    
    @keyframes fadeInScale {
        from { transform: scale(0.9); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #e91e63, #ff6b9d, #9c27b0, #673ab7);
        animation: gradientShift 3s ease-in-out infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
    }
    
    .metric-card:hover::before {
        animation: gradientShift 1s ease-in-out infinite;
    }
    
    /* Custom Streamlit Elements */
    .stButton > button {
        border-radius: 50px;
        background: linear-gradient(45deg, #e91e63, #ff6b9d);
        border: none;
        color: white;
        font-weight: 700;
        padding: 0.8rem 2.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 12px 30px rgba(233, 30, 99, 0.5);
        background: linear-gradient(45deg, #d81b60, #e91e63);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #e91e63, #ff6b9d);
        border-radius: 10px;
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #d81b60, #e91e63);
    }
    
    /* Custom headers */
    .hero-title {
        background: linear-gradient(45deg, #e91e63, #ff6b9d, #9c27b0, #673ab7, #3f51b5);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        animation: gradientFlow 3s ease-in-out infinite, slideInLeft 0.8s ease-out;
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .section-title {
        color: #2c3e50;
        font-weight: 700;
        font-size: 1.8rem;
        margin-bottom: 1rem;
        position: relative;
        padding-left: 1rem;
        animation: slideInLeft 0.8s ease-out;
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-30px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .section-title::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 2rem;
        background: linear-gradient(45deg, #e91e63, #ff6b9d);
        border-radius: 2px;
        animation: expandHeight 0.6s ease-out;
    }
    
    @keyframes expandHeight {
        from { height: 0; }
        to { height: 2rem; }
    }
    
    /* Filter styling */
    .stSelectbox > div > div {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8));
    }
    
    .stSelectbox > div > div:hover {
        border-color: #e91e63;
        box-shadow: 0 0 0 3px rgba(233, 30, 99, 0.1);
        transform: translateY(-2px);
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(45deg, #e91e63, #ff6b9d);
    }
    
    /* Metric styling */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #e91e63, #ff6b9d, #9c27b0);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientPulse 3s ease-in-out infinite;
    }
    
    @keyframes gradientPulse {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .metric-label {
        color: #34495e;
        font-weight: 600;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Quote card styling */
    .quote-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9));
        border-radius: 25px;
        padding: 2.5rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border-left: 6px solid #e91e63;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 1s ease-out;
        transition: all 0.4s ease;
    }
    
    .quote-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .quote-card::before {
        content: '"';
        position: absolute;
        top: -10px;
        left: 20px;
        font-size: 8rem;
        color: rgba(233, 30, 99, 0.1);
        font-family: serif;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Enhanced text colors */
    .text-primary { color: #e91e63; }
    .text-secondary { color: #ff6b9d; }
    .text-accent { color: #9c27b0; }
    .text-dark { color: #2c3e50; }
    .text-light { color: #7f8c8d; }
    
    /* Animated background elements */
    .animated-bg {
        position: relative;
        overflow: hidden;
    }
    
    .animated-bg::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(233, 30, 99, 0.05), transparent);
        animation: rotate 20s linear infinite;
        pointer-events: none;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Chart container animations */
    .chart-container {
        animation: fadeInScale 1s ease-out;
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        transform: scale(1.02);
    }
    
    /* Loading animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(233, 30, 99, 0.3);
        border-radius: 50%;
        border-top-color: #e91e63;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Success/Error messages */
    .success-message {
        background: linear-gradient(45deg, #27ae60, #2ecc71);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .error-message {
        background: linear-gradient(45deg, #e74c3c, #c0392b);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        animation: shake 0.5s ease-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_responses():
    """Fetch all responses from Firebase"""
    try:
        docs = db.collection("responses").stream()
        data = []
        for doc in docs:
            entry = doc.to_dict()
            entry["id"] = doc.id
            # Add timestamp if not present
            if "createdAt" not in entry:
                entry["createdAt"] = datetime.now()
            data.append(entry)
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def create_navbar(current_page):
    """Create modern navbar with routing using Streamlit buttons"""
    pages = [
        ("overview", "🏠 Pulse"),
        ("who-are-you", "👋 Who Are You?"),
        ("real-talk", "💬 Real Talk"),
        ("mood-check", "😊 Mood Check"),
        ("say-it", "☕ Tea Spill"),
        ("quick-picks", "🎯 Vibes Check"),
        ("parting-words", "💝 Parting Words")
    ]
    
    # Create navbar using Streamlit columns and buttons
    cols = st.columns(len(pages))
    
    for i, (page_id, page_name) in enumerate(pages):
        with cols[i]:
            if page_id == current_page:
                # Active page - show as selected
                st.markdown(f"""
                <div style="text-align: center; padding: 0.8rem; background: linear-gradient(45deg, #e91e63, #ff6b9d); 
                border-radius: 50px; color: white; font-weight: 700; box-shadow: 0 8px 25px rgba(233, 30, 99, 0.4); font-size: 0.95rem;">
                    {page_name}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Inactive page - show as button
                if st.button(page_name, key=f"nav_{page_id}", help=f"Go to {page_name}"):
                    st.query_params["page"] = page_id
                    st.rerun()

def overview_page(df):
    """Enhanced Overview page with Gen Z vibes and professional dashboard features"""
    
    # Hero Section with Gen Z messaging
    st.markdown("""
    <div class="animated-bg" style="text-align: center; margin-bottom: 3rem; padding: 3rem; border-radius: 25px; color: #2c3e50; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
        <h1 class="hero-title" style="font-size: 4.5rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">🌸 SheSpeaks Pulse</h1>
        <p style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; color: #34495e;">✨ Amplifying Women's Voices in Tech ✨</p>
        <p style="font-size: 1.2rem; margin-bottom: 1rem; color: #7f8c8d;">Real-time insights from the amazing women shaping the future of technology</p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1.5rem; flex-wrap: wrap;">
            <div style="background: linear-gradient(45deg, #e91e63, #ff6b9d); color: white; padding: 0.5rem 1rem; border-radius: 20px; box-shadow: 0 4px 15px rgba(233, 30, 99, 0.3);">
                <span style="font-size: 1.1rem;">🚀 Let's speak</span>
            </div>
            <div style="background: linear-gradient(45deg, #e91e63, #ff6b9d); color: white; padding: 0.5rem 1rem; border-radius: 20px; box-shadow: 0 4px 15px rgba(233, 30, 99, 0.3);">
                <span style="font-size: 1.1rem;">👂 Let's listen</span>
            </div>
            <div style="background: linear-gradient(45deg, #e91e63, #ff6b9d); color: white; padding: 0.5rem 1rem; border-radius: 20px; box-shadow: 0 4px 15px rgba(233, 30, 99, 0.3);">
                <span style="font-size: 1.1rem;">💫 Let's change</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 4rem; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); border: 3px solid #ff6b9d;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📭</div>
            <h2 class="text-dark" style="margin-bottom: 1rem; font-size: 2rem;">No Responses Yet</h2>
            <p class="text-light" style="font-size: 1.2rem; margin-bottom: 1rem;">✨ The dashboard is ready to shine once responses start coming in! ✨</p>
            <p class="text-light" style="font-size: 1rem; margin-bottom: 1.5rem;">Share the survey link to start collecting insights and making waves! 🌊</p>
            <div style="font-size: 2rem; margin-top: 1rem;">💫 🌟 ✨ 🎀</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Enhanced Key Metrics Cards with Gen Z messaging
    st.markdown('<h2 class="section-title">📊 Key Insights at a Glance</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total Responses with Gen Z flair
        response_count = len(df)
        response_emoji = "🔥" if response_count > 100 else "✨" if response_count > 50 else "🌟"
        response_message = "Absolutely crushing it!" if response_count > 100 else "Making waves!" if response_count > 50 else "Getting started!"
        
        st.markdown(f"""
        <div class="metric-card animated-bg">
            <div class="metric-label">{response_emoji} Total Responses</div>
            <div class="metric-value">{response_count}</div>
            <div class="text-light" style="font-size: 0.9rem; margin-top: 0.5rem;">{response_message}</div>
            <div class="text-light" style="font-size: 0.8rem; margin-top: 0.3rem;">Voices heard & amplified</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Enhanced Mood Score with context
        mood_questions = ['boys-club', 'equal-chances', 'safe-supported', 'held-back', 'women-mentors']
        mood_scores = []
        for q in mood_questions:
            if q in df.columns:
                numeric_values = pd.to_numeric(df[q], errors='coerce')
                if not numeric_values.isna().all():
                    mood_scores.append(numeric_values.mean())
        
        avg_mood = np.mean(mood_scores) if mood_scores else 0
        mood_emoji = "😊" if avg_mood >= 3.5 else "😐" if avg_mood >= 2.5 else "😔"
        mood_message = "Feeling the vibes!" if avg_mood >= 3.5 else "Room for growth!" if avg_mood >= 2.5 else "Need support!"
        
        st.markdown(f"""
        <div class="metric-card animated-bg">
            <div class="metric-label">{mood_emoji} Community Mood</div>
            <div class="metric-value">{avg_mood:.1f}/5</div>
            <div class="text-light" style="font-size: 0.9rem; margin-top: 0.5rem;">{mood_message}</div>
            <div class="text-light" style="font-size: 0.8rem; margin-top: 0.3rem;">Average sentiment score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Top Request with better presentation
        top_request = "N/A"
        if 'help' in df.columns and not df['help'].isna().all():
            help_responses = []
            for response in df['help'].dropna():
                if isinstance(response, list):
                    help_responses.extend(response)
                elif isinstance(response, str):
                    help_responses.extend(response.split(','))
            
            if help_responses:
                help_counts = Counter(help_responses)
                top_request = help_counts.most_common(1)[0][0] if help_counts else "N/A"
        
        st.markdown(f"""
        <div class="metric-card animated-bg">
            <div class="metric-label">🔥 Top Community Ask</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #2c3e50; margin: 0.5rem 0; line-height: 1.3;">{top_request[:25]}{'...' if len(top_request) > 25 else ''}</div>
            <div class="text-light" style="font-size: 0.9rem;">Most requested change</div>
            <div class="text-light" style="font-size: 0.8rem; margin-top: 0.3rem;">What the community wants</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Enhanced Judged Percentage with action items
        judged_pct = 0
        if 'judged' in df.columns and not df['judged'].isna().all():
            judged_responses = df['judged'].dropna()
            if len(judged_responses) > 0:
                judged_pct = len(judged_responses[judged_responses.isin(['multiple', 'sometimes'])]) / len(judged_responses) * 100
        
        judged_emoji = "⚠️" if judged_pct > 50 else "💪" if judged_pct > 25 else "✨"
        judged_message = "Action needed!" if judged_pct > 50 else "Room to improve!" if judged_pct > 25 else "Great vibes!"
        
        st.markdown(f"""
        <div class="metric-card animated-bg">
            <div class="metric-label">{judged_emoji} Felt Judged</div>
            <div class="metric-value">{judged_pct:.1f}%</div>
            <div class="text-light" style="font-size: 0.9rem; margin-top: 0.5rem;">{judged_message}</div>
            <div class="text-light" style="font-size: 0.8rem; margin-top: 0.3rem;">Need support & allyship</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # New Section: Quick Stats with Gen Z vibes
    st.markdown('<h2 class="section-title">⚡ Quick Stats & Vibes</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Recent Activity
        recent_count = len(df) if len(df) > 0 else 0
        recent_emoji = "🚀" if recent_count > 0 else "⏳"
        st.markdown(f"""
        <div class="metric-card animated-bg" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{recent_emoji}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #2c3e50;">{recent_count}</div>
                <div style="font-size: 1rem; color: #34495e; margin-top: 0.3rem;">Total Responses</div>
                <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 0.2rem;">✨ Every voice counts ✨</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Year Distribution
        if 'year' in df.columns and not df['year'].isna().all():
            year_counts = df['year'].dropna().value_counts()
            most_common_year = year_counts.index[0] if len(year_counts) > 0 else "N/A"
        else:
            most_common_year = "N/A"
        
        st.markdown(f"""
        <div class="metric-card animated-bg" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎓</div>
                <div style="font-size: 1.5rem; font-weight: 700;">{most_common_year}</div>
                <div style="font-size: 1rem; margin-top: 0.3rem;">Most Active Year</div>
                <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.2rem;">🌟 Leading the charge 🌟</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Course Diversity
        if 'course' in df.columns and not df['course'].isna().all():
            course_counts = df['course'].dropna().value_counts()
            unique_courses = len(course_counts)
        else:
            unique_courses = 0
        
        st.markdown(f"""
        <div class="metric-card animated-bg" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📚</div>
                <div style="font-size: 1.5rem; font-weight: 700;">{unique_courses}</div>
                <div style="font-size: 1rem; margin-top: 0.3rem;">Different Courses</div>
                <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.2rem;">💫 Diverse perspectives 💫</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Enhanced Filters Section with Gen Z messaging
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; color: white; box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔍</div>
            <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">Filter & Explore Your Data ✨</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        year_options = ["All Years"]
        if 'year' in df.columns and not df['year'].isna().all():
            year_options.extend(list(df['year'].dropna().unique()))
        year_filter = st.selectbox("🎓 Filter by Year", year_options)
    
    with col2:
        mood_range = st.slider("😊 Mood Score Range", 1.0, 5.0, (1.0, 5.0), 0.5)
    
    with col3:
        judged_options = ["All"]
        if 'judged' in df.columns and not df['judged'].isna().all():
            judged_options.extend(list(df['judged'].dropna().unique()))
        judged_filter = st.selectbox("🤔 Felt Judged?", judged_options)
    
    with col4:
        course_options = ["All Courses"]
        if 'course' in df.columns and not df['course'].isna().all():
            course_options.extend(list(df['course'].dropna().unique()))
        course_filter = st.selectbox("📚 Filter by Course", course_options)
    
    # Apply filters
    filtered_df = df.copy()
    if year_filter != "All Years":
        filtered_df = filtered_df[filtered_df['year'] == year_filter]
    if judged_filter != "All":
        filtered_df = filtered_df[filtered_df['judged'] == judged_filter]
    if course_filter != "All Courses":
        filtered_df = filtered_df[filtered_df['course'] == course_filter]
    
    # Show filtered results
    if len(filtered_df) != len(df):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; border: 2px solid #ff6b9d; box-shadow: 0 8px 20px rgba(255, 107, 157, 0.15);">
            <div style="text-align: center;">
                <p style="margin: 0; color: #2c3e50; font-size: 1rem; font-weight: 600;">
                    🔍 Showing <span style="color: #e91e63; font-weight: 700;">{len(filtered_df)}</span> of <span style="color: #e91e63; font-weight: 700;">{len(df)}</span> responses
                </p>
                <div style="margin-top: 0.3rem; font-size: 0.8rem; color: #7f8c8d;">✨ Filtered just for you ✨</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Quick Actions with Gen Z messaging
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; border: 2px solid #ff6b9d; box-shadow: 0 10px 25px rgba(255, 107, 157, 0.15);">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚡</div>
            <p style="margin: 0; font-weight: 600; font-size: 1.1rem; color: #2c3e50;">Quick Actions & Downloads 🚀</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📥 Download CSV", key="download_csv", help="Export filtered data as CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button("Download CSV", csv, "she_speaks_responses.csv", "text/csv")
    
    with col2:
        if st.button("📊 Export Excel", key="export_excel", help="Export as Excel file"):
            st.info("✨ Excel export feature coming soon! ✨")
    
    with col3:
        if st.button("🔄 Refresh Data", key="refresh", help="Reload latest data"):
            st.rerun()
    
    with col4:
        if st.button("📈 View Trends", key="view_trends", help="See time-based trends"):
            st.info("🚀 Trends analysis coming soon! 🚀")
    
    # New Section: Community Insights with Gen Z vibes
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">💫 Community Insights & Vibes</h2>', unsafe_allow_html=True)
    
    # Add descriptive text about the insights
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; color: white; box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💡</div>
            <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">✨ AI-Powered Insights & Community Vibes ✨</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Our smart analysis digs deep into your responses to uncover meaningful patterns and trends that help us understand the real challenges and opportunities for women in tech.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add Gen Z Insights Section
    insights = create_genz_insights(df)
    if insights:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; border: 2px solid #ff6b9d; box-shadow: 0 10px 25px rgba(255, 107, 157, 0.15);">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💡</div>
                <p style="margin: 0; font-weight: 600; font-size: 1.1rem; color: #2c3e50;">✨ Key Insights & Vibes ✨</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display insights in a Gen Z style
        for i, insight in enumerate(insights, 1):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8)); 
            padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; border-left: 4px solid #e91e63; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">#{i}</span>
                    <span style="font-size: 1rem; color: #2c3e50; font-weight: 500;">{insight}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Top Courses Chart
    st.markdown('<h2 class="section-title">📚 Community Representation</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Overview page - Top Courses Chart
        if 'course' in df.columns and not df['course'].isna().all():
            course_counts = df['course'].dropna().value_counts().head(5)
            if len(course_counts) > 0:
                fig = px.bar(x=course_counts.values, y=course_counts.index, orientation='h',
                            title="📚 Top 5 Courses Represented",
                            color_discrete_sequence=['#ff6b9d'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=14), 
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Number of Students",
                    yaxis_title="Course/Program"
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">📚</div>
                    <p class="text-light">No course data available yet</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📚</div>
                <p class="text-light">No course data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Professional Features Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🚀 Professional Dashboard Features</h2>', unsafe_allow_html=True)
    
    genz_messages = get_genz_messages()
    professional_features = genz_messages['professional_features']
    
    # Display professional features in a grid
    cols = st.columns(4)
    for i, feature in enumerate(professional_features):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9)); 
            padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 1rem; 
            border: 2px solid #e91e63; box-shadow: 0 8px 20px rgba(233, 30, 99, 0.15);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{feature.split()[0]}</div>
                <div style="font-size: 0.9rem; color: #2c3e50; font-weight: 600;">{' '.join(feature.split()[1:])}</div>
            </div>
            """, unsafe_allow_html=True)
    

    
    # Final Call-to-Action with Gen Z vibes
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); border-radius: 25px; color: white; box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);">
        <div style="font-size: 3rem; margin-bottom: 1rem;">💫</div>
        <p style="margin: 0; font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">
            Ready to dive deeper into the data? ✨
        </p>
        <p style="margin: 0; font-size: 1rem; opacity: 0.9; margin-bottom: 1.5rem;">
            Explore different sections to uncover more insights and stories from our amazing community!
        </p>
        <div style="font-size: 1.5rem; margin-top: 1rem;">🚀 💫 ✨ 🌟</div>
    </div>
    """, unsafe_allow_html=True)

def who_are_you_page(df):
    """Section 1: Who Are You? - Basic demographics"""
    st.markdown("""
    <div class="animated-bg" style="text-align: center; margin-bottom: 3rem;">
        <h1 class="hero-title" style="font-size: 3.5rem;">👋 Who Are You?</h1>
        <p class="text-dark" style="font-size: 1.2rem; font-weight: 500;">Getting to know our amazing community</p>
        <p class="text-light" style="font-size: 1rem; margin-top: 1rem;">Understanding the diverse backgrounds and experiences of women in tech helps us create more inclusive and supportive environments. Let's explore the demographics of our community!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 4rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <h2 class="text-dark" style="margin-bottom: 1rem;">No Responses Yet</h2>
            <p class="text-light" style="font-size: 1.1rem;">The dashboard will populate once responses start coming in!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Year Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h2 class="section-title">🎓 Year-wise Breakdown</h2>', unsafe_allow_html=True)
        if 'year' in df.columns and not df['year'].isna().all():
            year_counts = df['year'].dropna().value_counts()
            if len(year_counts) > 0:
                fig = px.bar(x=year_counts.index, y=year_counts.values,
                            title="📊 Student Distribution by Academic Year",
                            color_discrete_sequence=['#e91e63'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=14), 
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Academic Year",
                    yaxis_title="Number of Students"
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                    <p class="text-light">No year data available yet</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <p class="text-light">No year data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<h2 class="section-title">📚 Course Analysis</h2>', unsafe_allow_html=True)
        if 'course' in df.columns and not df['course'].isna().all():
            course_counts = df['course'].dropna().value_counts().head(10)
            if len(course_counts) > 0:
                fig = px.bar(x=course_counts.values, y=course_counts.index, orientation='h',
                            title="📚 Top 10 Courses by Student Count",
                            color_discrete_sequence=['#ff6b9d'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=14), 
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Number of Students",
                    yaxis_title="Course/Program"
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">📚</div>
                    <p class="text-light">No course data available yet</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📚</div>
                <p class="text-light">No course data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Ever felt judged in tech spaces?
    st.markdown('<h2 class="section-title">🤔 Ever Felt Judged in Tech Spaces?</h2>', unsafe_allow_html=True)
    if 'judged' in df.columns and not df['judged'].isna().all():
        judged_counts = df['judged'].dropna().value_counts()
        if len(judged_counts) > 0:
            fig = px.pie(values=judged_counts.values, names=judged_counts.index,
                        title="🤔 Experience of Judgment in Tech Spaces",
                        color_discrete_sequence=['#e91e63', '#ff6b9d', '#9c27b0', '#673ab7'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=14), 
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🤔</div>
                <p class="text-light">No judgment data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🤔</div>
            <p class="text-light">No judgment data available yet</p>
        </div>
        """, unsafe_allow_html=True)

def real_talk_page(df):
    """Section 2: Real Talk - Group dynamics and experiences"""
    st.markdown("""
    <div class="animated-bg" style="text-align: center; margin-bottom: 3rem;">
        <h1 class="hero-title" style="font-size: 3.5rem;">💬 Real Talk</h1>
        <p class="text-dark" style="font-size: 1.2rem; font-weight: 500;">The real deal about group projects & gender dynamics</p>
        <p class="text-light" style="font-size: 1rem; margin-top: 1rem;">Group projects and collaborative work are fundamental to tech education and careers. Understanding how women navigate these spaces helps us identify barriers and create better support systems.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 4rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <h2 class="text-dark" style="margin-bottom: 1rem;">No Responses Yet</h2>
            <p class="text-light" style="font-size: 1.1rem;">The dashboard will populate once responses start coming in!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Voice in group projects
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h2 class="section-title">🎙️ Voice in Group Projects</h2>', unsafe_allow_html=True)
        if 'voice' in df.columns and not df['voice'].isna().all():
            voice_counts = df['voice'].dropna().value_counts()
            if len(voice_counts) > 0:
                fig = px.bar(x=voice_counts.index, y=voice_counts.values,
                            title="🎙️ Comfort Level Speaking Up in Group Projects",
                            color_discrete_sequence=['#e91e63'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=14), 
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Response Category",
                    yaxis_title="Number of Students"
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">🎙️</div>
                    <p class="text-light">No voice data available yet</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🎙️</div>
                <p class="text-light">No voice data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<h2 class="section-title">🚶‍♀️ Stepped Back from Tech?</h2>', unsafe_allow_html=True)
        if 'stepped-back' in df.columns and not df['stepped-back'].isna().all():
            stepped_counts = df['stepped-back'].dropna().value_counts()
            if len(stepped_counts) > 0:
                fig = px.pie(values=stepped_counts.values, names=stepped_counts.index,
                            title="🚶‍♀️ Experience of Stepping Back from Tech Opportunities",
                            color_discrete_sequence=['#ff6b9d', '#e91e63', '#9c27b0', '#673ab7'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=14), 
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">🚶‍♀️</div>
                    <p class="text-light">No stepped back data available yet</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🚶‍♀️</div>
                <p class="text-light">No stepped back data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Hostel curfews impact
    st.markdown('<h2 class="section-title">🕒 Hostel Curfews Impacting Participation?</h2>', unsafe_allow_html=True)
    if 'curfews' in df.columns and not df['curfews'].isna().all():
        curfew_counts = df['curfews'].dropna().value_counts()
        if len(curfew_counts) > 0:
            fig = px.bar(x=curfew_counts.index, y=curfew_counts.values,
                        title="🕒 Impact of Hostel Curfews on Tech Participation",
                        color_discrete_sequence=['#9c27b0'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=14), 
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="Response Category",
                yaxis_title="Number of Students"
            )
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🕒</div>
                <p class="text-light">No curfew data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🕒</div>
            <p class="text-light">No curfew data available yet</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Correlation Analysis
    st.markdown('<h2 class="section-title">🔗 Correlation Analysis</h2>', unsafe_allow_html=True)
    if all(col in df.columns for col in ['year', 'curfews', 'judged']) and not df[['year', 'curfews']].isna().all().all():
        # Do final year students report more curfew frustration?
        final_year_data = df[df['year'] == 'Final']['curfews'].dropna()
        other_years_data = df[df['year'] != 'Final']['curfews'].dropna()
        
        if len(final_year_data) > 0 or len(other_years_data) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class="metric-card animated-bg">
                    <h3 class="text-primary" style="margin-bottom: 1rem;">Final Year Students - Curfew Impact</h3>
                </div>
                """, unsafe_allow_html=True)
                if len(final_year_data) > 0:
                    final_year_curfews = final_year_data.value_counts()
                    st.write(final_year_curfews)
                else:
                    st.markdown('<p class="text-light">No final year data available</p>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card animated-bg">
                    <h3 class="text-primary" style="margin-bottom: 1rem;">Other Years - Curfew Impact</h3>
                </div>
                """, unsafe_allow_html=True)
                if len(other_years_data) > 0:
                    other_years_curfews = other_years_data.value_counts()
                    st.write(other_years_curfews)
                else:
                    st.markdown('<p class="text-light">No other years data available</p>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🔗</div>
                <p class="text-light">No correlation data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🔗</div>
            <p class="text-light">No correlation data available yet</p>
        </div>
        """, unsafe_allow_html=True)

def mood_check_page(df):
    """Section 3: Mood Check - 5-point scale analysis"""
    st.markdown("""
    <div class="animated-bg" style="text-align: center; margin-bottom: 3rem;">
        <h1 class="hero-title" style="font-size: 3.5rem;">😊 Mood Check</h1>
        <p class="text-dark" style="font-size: 1.2rem; font-weight: 500;">How are we really feeling about tech spaces?</p>
        <p class="text-light" style="font-size: 1rem; margin-top: 1rem;">Sentiment analysis helps us understand the emotional landscape of women in tech. These insights guide us in creating more supportive and inclusive environments where everyone can thrive.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 4rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <h2 class="text-dark" style="margin-bottom: 1rem;">No Responses Yet</h2>
            <p class="text-light" style="font-size: 1.1rem;">The dashboard will populate once responses start coming in!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 5-Point Scale Questions
    scale_questions = {
        'boys-club': 'Engineering feels like boys\' club',
        'equal-chances': 'Equal opportunity',
        'safe-supported': 'Feeling safe and supported',
        'held-back': 'Held back from speaking',
        'women-mentors': 'Wish for more women mentors'
    }
    
    available_questions = {k: v for k, v in scale_questions.items() if k in df.columns}
    
    if available_questions:
        # Calculate averages
        averages = []
        question_names = []
        for question, name in available_questions.items():
            numeric_values = pd.to_numeric(df[question], errors='coerce')
            avg = numeric_values.mean() if not numeric_values.isna().all() else 0
            averages.append(avg)
            question_names.append(name)
        
        # Check if we have meaningful data
        if any(avg > 0 for avg in averages):
            # Radar Chart
            st.markdown('<h2 class="section-title">📊 Overall Sentiment Radar</h2>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=averages,
                theta=question_names,
                fill='toself',
                name='Average Response',
                line_color='#e91e63',
                fillcolor='rgba(233, 30, 99, 0.3)'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5],
                        tickfont=dict(size=12)
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=11)
                    )
                ),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=14),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Individual Score Bars
            st.markdown('<h2 class="section-title">📈 Individual Question Scores</h2>', unsafe_allow_html=True)
            fig = px.bar(x=question_names, y=averages,
                        title="📊 Average Scores by Question (1-5 Scale)",
                        color_discrete_sequence=['#ff6b9d'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=14), 
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="Survey Questions",
                yaxis_title="Average Score (1-5 Scale)"
            )
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Overall sentiment index
            overall_sentiment = np.mean(averages)
            st.markdown('<h2 class="section-title">💫 Overall Sentiment Index</h2>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div class="metric-card animated-bg" style="text-align: center;">
                    <div class="metric-value">{overall_sentiment:.2f}/5</div>
                    <div class="text-dark" style="font-size: 1.2rem; margin-top: 0.5rem;">Average Mood Score</div>
                    <div class="text-light" style="font-size: 1rem; margin-top: 0.5rem;">{'😊' if overall_sentiment >= 3 else '😔'}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 4rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">😊</div>
                <h2 class="text-dark" style="margin-bottom: 1rem;">No Mood Data Yet</h2>
                <p class="text-light" style="font-size: 1.1rem;">5-point scale responses will appear here once available!</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 4rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">😊</div>
            <h2 class="text-dark" style="margin-bottom: 1rem;">No Mood Data Yet</h2>
            <p class="text-light" style="font-size: 1.1rem;">5-point scale responses will appear here once available!</p>
        </div>
        """, unsafe_allow_html=True)

def say_it_page(df):
    """Section 4: Tea Spill - Text analysis with Gen Z vibes"""
    st.markdown("""
    <div class="animated-bg" style="text-align: center; margin-bottom: 3rem; padding: 3rem; border-radius: 25px; color: #2c3e50; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
        <h1 class="hero-title" style="font-size: 3.5rem;">☕ Tea Spill</h1>
        <p style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem; color: #34495e;">✨ Unfiltered Voices & Real Talk ✨</p>
        <p style="font-size: 1.1rem; margin-bottom: 1rem; color: #7f8c8d;">Raw insights, honest feedback, and the real stories behind the data</p>
    </div>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 4rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <h2 class="text-dark" style="margin-bottom: 1rem;">No Responses Yet</h2>
            <p class="text-light" style="font-size: 1.1rem;">The dashboard will populate once responses start coming in!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Interactive filters
    st.markdown('<h2 class="section-title">🔍 Filter Your Tea</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filter by year
        if 'year' in df.columns:
            years = sorted(df['year'].dropna().unique())
            selected_year = st.selectbox("📅 Filter by Year", ["All Years"] + list(years))
        else:
            selected_year = "All Years"
    
    with col2:
        # Filter by course
        if 'course' in df.columns:
            courses = sorted(df['course'].dropna().unique())
            selected_course = st.selectbox("🎓 Filter by Course", ["All Courses"] + list(courses))
        else:
            selected_course = "All Courses"
    
    with col3:
        # Filter by judgment experience
        if 'judged' in df.columns:
            judged_options = sorted(df['judged'].dropna().unique())
            selected_judged = st.selectbox("⚖️ Filter by Judgment Experience", ["All"] + list(judged_options))
        else:
            selected_judged = "All"
    
    # Apply filters
    filtered_df = df.copy()
    if selected_year != "All Years":
        filtered_df = filtered_df[filtered_df['year'] == selected_year]
    if selected_course != "All Courses":
        filtered_df = filtered_df[filtered_df['course'] == selected_course]
    if selected_judged != "All":
        filtered_df = filtered_df[filtered_df['judged'] == selected_judged]
    
    # Show filter summary
    if len(filtered_df) != len(df):
        st.markdown(f"""
        <div class="metric-card animated-bg" style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 1.2rem; font-weight: 600; color: #e91e63;">🔍 Filtered Results</div>
            <div style="font-size: 1rem; color: #7f8c8d;">Showing {len(filtered_df)} out of {len(df)} responses</div>
        </div>
        """, unsafe_allow_html=True)
    
    # What held you back from reporting?
    st.markdown('<h2 class="section-title">🤐 What Held You Back from Reporting?</h2>', unsafe_allow_html=True)
    if 'held-back-report' in filtered_df.columns and not filtered_df['held-back-report'].isna().all():
        # Simple word frequency analysis
        all_text = ' '.join(filtered_df['held-back-report'].dropna().astype(str))
        if all_text.strip():
            words = re.findall(r'\b\w+\b', all_text.lower())
            word_counts = Counter(words)
            
            # Remove common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'should', 'would', 'could', 'may', 'might', 'must', 'can'}
            filtered_words = {word: count for word, count in word_counts.items() if word not in common_words and len(word) > 2}
            
            if filtered_words:
                top_words = dict(sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:10])
                
                # Create two columns for chart and analysis
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig = px.bar(x=list(top_words.values()), y=list(top_words.keys()), orientation='h',
                                title="🤐 Most Common Words in Reporting Barriers",
                                color_discrete_sequence=['#e91e63'])
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=14), 
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis_title="Word Frequency",
                        yaxis_title="Common Words"
                    )
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    # Analysis insights
                    st.markdown("""
                    <div class="metric-card animated-bg" style="padding: 1.5rem;">
                        <h3 style="color: #e91e63; margin-bottom: 1rem;">🔍 Text Analysis</h3>
                    """, unsafe_allow_html=True)
                    
                    # Calculate insights
                    total_responses = len(filtered_df['held-back-report'].dropna())
                    most_common_word = list(top_words.keys())[0] if top_words else "N/A"
                    most_common_count = list(top_words.values())[0] if top_words else 0
                    
                    # Identify themes with more comprehensive word lists
                    fear_words = ['fear', 'afraid', 'scared', 'worried', 'anxiety', 'nervous', 'worried', 'backlash', 'blamed', 'judged']
                    confidence_words = ['confidence', 'sure', 'certain', 'confident', 'doubt', 'unsure', 'minor', 'normal']
                    support_words = ['support', 'help', 'guidance', 'mentor', 'procedure', 'evidence', 'proof']
                    safety_words = ['safe', 'safety', 'isolation', 'trouble', 'career', 'opportunities']
                    
                    fear_count = sum(count for word, count in top_words.items() if word in fear_words)
                    confidence_count = sum(count for word, count in top_words.items() if word in confidence_words)
                    support_count = sum(count for word, count in top_words.items() if word in support_words)
                    safety_count = sum(count for word, count in top_words.items() if word in safety_words)
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">📊 Total Responses</div>
                        <div style="color: #7f8c8d;">{total_responses} students</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">🔥 Most Common Word</div>
                        <div style="color: #7f8c8d;">"{most_common_word}" ({most_common_count} mentions)</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">😰 Fear/Safety Concerns</div>
                        <div style="color: #7f8c8d;">{fear_count + safety_count} mentions</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">💪 Confidence/Self-doubt</div>
                        <div style="color: #7f8c8d;">{confidence_count} mentions</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">🤝 Support/Procedure Issues</div>
                        <div style="color: #7f8c8d;">{support_count} mentions</div>
                    </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Deep dive analysis
                st.markdown('<h3 class="section-title">💭 What This Tells Us</h3>', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if fear_count > 0:
                        st.markdown(f"""
                        <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">😰</div>
                            <div style="font-weight: 600; color: #e91e63;">Fear & Safety</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{fear_count} mentions</div>
                            <div style="color: #2c3e50; font-size: 0.8rem; margin-top: 0.5rem;">Students fear consequences</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    if safety_count > 0:
                        st.markdown(f"""
                        <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🛡️</div>
                            <div style="font-weight: 600; color: #e91e63;">Safety Concerns</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{safety_count} mentions</div>
                            <div style="color: #2c3e50; font-size: 0.8rem; margin-top: 0.5rem;">Career & isolation fears</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col3:
                    if confidence_count > 0:
                        st.markdown(f"""
                        <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💪</div>
                            <div style="font-weight: 600; color: #e91e63;">Confidence Issues</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{confidence_count} mentions</div>
                            <div style="color: #2c3e50; font-size: 0.8rem; margin-top: 0.5rem;">Self-doubt & uncertainty</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col4:
                    if support_count > 0:
                        st.markdown(f"""
                        <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤝</div>
                            <div style="font-weight: 600; color: #e91e63;">Support Gaps</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{support_count} mentions</div>
                            <div style="color: #2c3e50; font-size: 0.8rem; margin-top: 0.5rem;">Need better procedures</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">🤐</div>
                    <p class="text-light">No meaningful text data available yet</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🤐</div>
                <p class="text-light">No reporting data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🤐</div>
            <p class="text-light">No reporting data available yet</p>
        </div>
        """, unsafe_allow_html=True)
    
    # One thing you'd change
    st.markdown('<h2 class="section-title">✨ One Thing You\'d Change</h2>', unsafe_allow_html=True)
    if 'one-change' in filtered_df.columns and not filtered_df['one-change'].isna().all():
        # Simple word frequency analysis
        all_text = ' '.join(filtered_df['one-change'].dropna().astype(str))
        if all_text.strip():
            words = re.findall(r'\b\w+\b', all_text.lower())
            word_counts = Counter(words)
            
            # Remove common words
            filtered_words = {word: count for word, count in word_counts.items() if word not in common_words and len(word) > 2}
            
            if filtered_words:
                top_words = dict(sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:10])
                
                # Create two columns for chart and analysis
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig = px.bar(x=list(top_words.values()), y=list(top_words.keys()), orientation='h',
                                title="✨ Most Common Words in Desired Changes",
                                color_discrete_sequence=['#ff6b9d'])
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=14), 
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis_title="Word Frequency",
                        yaxis_title="Common Words"
                    )
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    # Analysis insights
                    st.markdown("""
                    <div class="metric-card animated-bg" style="padding: 1.5rem;">
                        <h3 style="color: #ff6b9d; margin-bottom: 1rem;">🔍 Change Analysis</h3>
                    """, unsafe_allow_html=True)
                    
                    # Calculate insights
                    total_responses = len(filtered_df['one-change'].dropna())
                    most_common_word = list(top_words.keys())[0] if top_words else "N/A"
                    most_common_count = list(top_words.values())[0] if top_words else 0
                    
                    # Identify themes
                    culture_words = ['culture', 'environment', 'atmosphere', 'community', 'inclusive']
                    support_words = ['support', 'help', 'mentorship', 'guidance', 'resources']
                    policy_words = ['policy', 'rules', 'regulations', 'curfew', 'restrictions']
                    education_words = ['education', 'training', 'workshop', 'course', 'learning']
                    
                    culture_count = sum(count for word, count in top_words.items() if word in culture_words)
                    support_count = sum(count for word, count in top_words.items() if word in support_words)
                    policy_count = sum(count for word, count in top_words.items() if word in policy_words)
                    education_count = sum(count for word, count in top_words.items() if word in education_words)
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">📊 Total Responses</div>
                        <div style="color: #7f8c8d;">{total_responses} students</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">🔥 Top Request</div>
                        <div style="color: #7f8c8d;">"{most_common_word}" ({most_common_count} mentions)</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">🌍 Culture/Environment</div>
                        <div style="color: #7f8c8d;">{culture_count} mentions</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">🤝 Support Systems</div>
                        <div style="color: #7f8c8d;">{support_count} mentions</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">📋 Policy Changes</div>
                        <div style="color: #7f8c8d;">{policy_count} mentions</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #2c3e50;">📚 Education</div>
                        <div style="color: #7f8c8d;">{education_count} mentions</div>
                    </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Actionable insights
                st.markdown('<h3 class="section-title">💡 Actionable Insights</h3>', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if culture_count > 0:
                        st.markdown(f"""
                        <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌍</div>
                            <div style="font-weight: 600; color: #ff6b9d;">Culture Shift</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{culture_count} mentions</div>
                            <div style="color: #2c3e50; font-size: 0.8rem; margin-top: 0.5rem;">Focus on inclusive environment</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    if support_count > 0:
                        st.markdown(f"""
                        <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤝</div>
                            <div style="font-weight: 600; color: #ff6b9d;">Support Systems</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{support_count} mentions</div>
                            <div style="color: #2c3e50; font-size: 0.8rem; margin-top: 0.5rem;">Build mentorship programs</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col3:
                    if policy_count > 0:
                        st.markdown(f"""
                        <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
                            <div style="font-weight: 600; color: #ff6b9d;">Policy Review</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{policy_count} mentions</div>
                            <div style="color: #2c3e50; font-size: 0.8rem; margin-top: 0.5rem;">Revisit restrictive policies</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col4:
                    if education_count > 0:
                        st.markdown(f"""
                        <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📚</div>
                            <div style="font-weight: 600; color: #ff6b9d;">Education Focus</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{education_count} mentions</div>
                            <div style="color: #2c3e50; font-size: 0.8rem; margin-top: 0.5rem;">Enhance learning opportunities</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">✨</div>
                    <p class="text-light">No meaningful change data available yet</p>
                </div>
                """, unsafe_allow_html=True)
            '''else:
                st.markdown("""
                <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">✨</div>
                    <p class="text-light">No change data available yet</p>
                </div>
                """, unsafe_allow_html=True)'''
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">✨</div>
                <p class="text-light">No change data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">✨</div>
            <p class="text-light">No change data available yet</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Summary insights for Tea Spill
    if not filtered_df.empty:
        st.markdown('<h2 class="section-title">💡 Tea Spill Summary</h2>', unsafe_allow_html=True)
        
        # Calculate overall insights
        total_responses = len(filtered_df)
        
        # Reporting barriers analysis
        reporting_data = filtered_df['held-back-report'].dropna() if 'held-back-report' in filtered_df.columns else []
        change_data = filtered_df['one-change'].dropna() if 'one-change' in filtered_df.columns else []
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-weight: 600; color: #e91e63;">Total Responses</div>
                <div style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">
                    {total_responses} students
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤐</div>
                <div style="font-weight: 600; color: #e91e63;">Reporting Barriers</div>
                <div style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">
                    {len(reporting_data)} responses
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">✨</div>
                <div style="font-weight: 600; color: #e91e63;">Desired Changes</div>
                <div style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">
                    {len(change_data)} responses
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Key insights
        st.markdown('<h3 class="section-title">🔍 Key Insights</h3>', unsafe_allow_html=True)
        
        if len(reporting_data) > 0 or len(change_data) > 0:
            insights = []
            
            if len(reporting_data) > 0:
                insights.append("Students face multiple barriers to reporting issues")
            
            if len(change_data) > 0:
                insights.append("Clear patterns emerge in desired improvements")
            
            if len(reporting_data) > len(change_data):
                insights.append("More students shared barriers than suggestions")
            elif len(change_data) > len(reporting_data):
                insights.append("More students shared suggestions than barriers")
            
            for i, insight in enumerate(insights):
                st.markdown(f"""
                <div class="metric-card animated-bg" style="padding: 1rem; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 1.5rem; margin-right: 1rem;">💭</div>
                        <div style="color: #2c3e50; font-weight: 500;">{insight}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Action recommendations
        st.markdown('<h3 class="section-title">🚀 Action Recommendations</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card animated-bg" style="padding: 2rem;">
            <h4 style="color: #e91e63; margin-bottom: 1rem;">🎯 Based on Tea Spill Analysis</h4>
            <div style="color: #2c3e50; margin-bottom: 1rem;">
                <p><strong>1. Address Reporting Barriers:</strong> Focus on creating safe, confidential reporting mechanisms</p>
                <p><strong>2. Implement Suggested Changes:</strong> Prioritize the most frequently mentioned improvements</p>
                <p><strong>3. Build Trust:</strong> Create an environment where students feel comfortable sharing concerns</p>
            </div>
            <div style="background: linear-gradient(45deg, #e91e63, #ff6b9d); padding: 1rem; border-radius: 10px; color: white;">
                <strong>Next Steps:</strong> Use these insights to develop targeted interventions and support systems.
            </div>
        </div>
        """, unsafe_allow_html=True)

def quick_picks_page(df):
    """Section 5: Vibes Check - Multi-select analysis with Gen Z flair"""
    st.markdown("""
    <div class="animated-bg" style="text-align: center; margin-bottom: 3rem; padding: 3rem; border-radius: 25px; color: #2c3e50; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
        <h1 class="hero-title" style="font-size: 3.5rem;">🎯 Vibes Check</h1>
        <p style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem; color: #34495e;">✨ Community Priorities & Support Needs ✨</p>
        <p style="font-size: 1.1rem; margin-bottom: 1rem; color: #7f8c8d;">What would help girls in tech? Let's see what the community really wants!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 4rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <h2 class="text-dark" style="margin-bottom: 1rem;">No Responses Yet</h2>
            <p class="text-light" style="font-size: 1.1rem;">The dashboard will populate once responses start coming in!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Interactive filters
    st.markdown('<h2 class="section-title">🔍 Filter Your Vibes</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filter by year
        if 'year' in df.columns:
            years = sorted(df['year'].dropna().unique())
            selected_year = st.selectbox("📅 Filter by Year", ["All Years"] + list(years))
        else:
            selected_year = "All Years"
    
    with col2:
        # Filter by course
        if 'course' in df.columns:
            courses = sorted(df['course'].dropna().unique())
            selected_course = st.selectbox("🎓 Filter by Course", ["All Courses"] + list(courses))
        else:
            selected_course = "All Courses"
    
    with col3:
        # Filter by voice comfort
        if 'voice' in df.columns:
            voice_options = sorted(df['voice'].dropna().unique())
            selected_voice = st.selectbox("🗣️ Filter by Voice Comfort", ["All"] + list(voice_options))
        else:
            selected_voice = "All"
    
    # Apply filters
    filtered_df = df.copy()
    if selected_year != "All Years":
        filtered_df = filtered_df[filtered_df['year'] == selected_year]
    if selected_course != "All Courses":
        filtered_df = filtered_df[filtered_df['course'] == selected_course]
    if selected_voice != "All":
        filtered_df = filtered_df[filtered_df['voice'] == selected_voice]
    
    # Show filter summary
    if len(filtered_df) != len(df):
        st.markdown(f"""
        <div class="metric-card animated-bg" style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 1.2rem; font-weight: 600; color: #e91e63;">🔍 Filtered Results</div>
            <div style="font-size: 1rem; color: #7f8c8d;">Showing {len(filtered_df)} out of {len(df)} responses</div>
        </div>
        """, unsafe_allow_html=True)
    
    # What would help girls in tech?
    st.markdown('<h2 class="section-title">🚀 What Would Help Girls in Tech?</h2>', unsafe_allow_html=True)
    if 'help' in filtered_df.columns and not filtered_df['help'].isna().all():
        # Parse help responses
        help_responses = []
        for response in filtered_df['help'].dropna():
            if isinstance(response, list):
                help_responses.extend(response)
            elif isinstance(response, str):
                help_responses.extend(response.split(','))
        
        if help_responses:
            help_counts = Counter(help_responses)
            # Calculate percentages
            total_responses = len(filtered_df)
            help_percentages = {item: (count / total_responses) * 100 for item, count in help_counts.items()}
            
            # Sort by percentage
            sorted_help = dict(sorted(help_percentages.items(), key=lambda x: x[1], reverse=True))
            
            # Create two columns for chart and analysis
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(x=list(sorted_help.values()), y=list(sorted_help.keys()), orientation='h',
                            title="🚀 Community Priorities: What Would Help Girls in Tech?",
                            color_discrete_sequence=['#e91e63'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=14), 
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Percentage of Students (%)",
                    yaxis_title="Support Categories"
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Analysis insights
                st.markdown("""
                <div class="metric-card animated-bg" style="padding: 1.5rem;">
                    <h3 style="color: #e91e63; margin-bottom: 1rem;">🔍 Priority Analysis</h3>
                """, unsafe_allow_html=True)
                
                # Calculate insights
                top_priority = list(sorted_help.keys())[0] if sorted_help else "N/A"
                top_percentage = list(sorted_help.values())[0] if sorted_help else 0
                
                # Show all available options and their percentages
                all_options = {
                    'all-girls-teams': 'All-girls tech teams',
                    'women-mentors': 'Women tech mentors/speakers', 
                    'late-night-access': 'Late-night lab/hackathon access',
                    'transparent-selections': 'Transparent team selections',
                    'anonymous-reporting': 'Anonymous reporting system',
                    'not-sure': 'Not sure yet'
                }
                
                # Calculate percentages for all options
                all_percentages = {}
                for option in all_options.keys():
                    count = help_counts.get(option, 0)
                    all_percentages[option] = (count / total_responses) * 100 if total_responses > 0 else 0
                
                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: #2c3e50;">📊 Total Responses</div>
                    <div style="color: #7f8c8d;">{total_responses} students</div>
                </div>
                <div style="margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: #2c3e50;">🔥 Top Priority</div>
                    <div style="color: #7f8c8d;">"{all_options.get(top_priority, top_priority)}" ({top_percentage:.1f}%)</div>
                </div>
                <div style="margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: #2c3e50;">📋 All Options Breakdown</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show all options with their percentages
                for option_key, option_name in all_options.items():
                    percentage = all_percentages[option_key]
                    count = help_counts.get(option_key, 0)
                    st.markdown(f"""
                    <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: rgba(233, 30, 99, 0.1); border-radius: 5px;">
                        <div style="font-weight: 600; color: #2c3e50; font-size: 0.9rem;">{option_name}</div>
                        <div style="color: #7f8c8d; font-size: 0.8rem;">{count} students ({percentage:.1f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # All options breakdown
            st.markdown('<h3 class="section-title">📋 Complete Options Breakdown</h3>', unsafe_allow_html=True)
            
            # Create a proper breakdown showing all options
            all_options_display = {
                'all-girls-teams': 'All-girls tech teams',
                'women-mentors': 'Women tech mentors/speakers', 
                'late-night-access': 'Late-night lab/hackathon access',
                'transparent-selections': 'Transparent team selections',
                'anonymous-reporting': 'Anonymous reporting system',
                'not-sure': 'Not sure yet'
            }
            
            # Sort by percentage
            sorted_all_options = sorted(all_percentages.items(), key=lambda x: x[1], reverse=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="metric-card animated-bg" style="padding: 1.5rem;">
                    <h4 style="color: #e91e63; margin-bottom: 1rem;">🏆 Top 3 Priorities</h4>
                """, unsafe_allow_html=True)
                
                for i, (option_key, percentage) in enumerate(sorted_all_options[:3]):
                    option_name = all_options_display[option_key]
                    count = help_counts.get(option_key, 0)
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem; padding: 1rem; background: linear-gradient(45deg, #e91e63, #ff6b9d); border-radius: 10px; color: white;">
                        <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem;">#{i+1} {option_name}</div>
                        <div style="font-size: 1rem;">{count} students ({percentage:.1f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card animated-bg" style="padding: 1.5rem;">
                    <h4 style="color: #e91e63; margin-bottom: 1rem;">📊 Other Options</h4>
                """, unsafe_allow_html=True)
                
                for option_key, percentage in sorted_all_options[3:]:
                    option_name = all_options_display[option_key]
                    count = help_counts.get(option_key, 0)
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(233, 30, 99, 0.1); border-radius: 10px;">
                        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;">{option_name}</div>
                        <div style="color: #7f8c8d;">{count} students ({percentage:.1f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Cross-analysis with other factors
            st.markdown('<h3 class="section-title">🔗 Cross-Analysis Insights</h3>', unsafe_allow_html=True)
            
            # Analyze by voice comfort level
            if 'voice' in filtered_df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div class="metric-card animated-bg" style="padding: 1.5rem;">
                        <h4 style="color: #e91e63; margin-bottom: 1rem;">🗣️ Voice Comfort vs Priorities</h4>
                    """, unsafe_allow_html=True)
                    
                    # Group by voice comfort and analyze help priorities
                    voice_groups = filtered_df.groupby('voice')['help'].apply(lambda x: [item for sublist in x.dropna() for item in (sublist if isinstance(sublist, list) else sublist.split(','))]).to_dict()
                    
                    voice_labels = {
                        'heard': 'Voice Heard',
                        'ignored': 'Voice Ignored', 
                        'talked-over': 'Talked Over',
                        'depends': 'Depends on Situation'
                    }
                    
                    for voice_level, help_items in voice_groups.items():
                        if help_items:
                            help_counter = Counter(help_items)
                            top_help = help_counter.most_common(1)[0] if help_counter else ("N/A", 0)
                            top_help_name = all_options_display.get(top_help[0], top_help[0])
                            voice_label = voice_labels.get(voice_level, voice_level)
                            st.markdown(f"""
                            <div style="margin-bottom: 1rem; padding: 0.5rem; background: rgba(233, 30, 99, 0.1); border-radius: 5px;">
                                <div style="font-weight: 600; color: #2c3e50;">{voice_label}</div>
                                <div style="color: #7f8c8d; font-size: 0.9rem;">Top need: {top_help_name}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card animated-bg" style="padding: 1.5rem;">
                        <h4 style="color: #e91e63; margin-bottom: 1rem;">🔍 What This Data Reveals</h4>
                    """, unsafe_allow_html=True)
                    
                    # Generate deeper insights based on data patterns
                    insights = []
                    
                    # Analyze mentorship needs
                    if 'women-mentors' in help_counts and help_counts['women-mentors'] > 0:
                        mentor_percentage = (help_counts['women-mentors'] / total_responses) * 100
                        if mentor_percentage > 40:
                            insights.append("👩‍🏫 <strong>Strong Role Model Need:</strong> High demand for women mentors suggests students lack visible female leadership in tech")
                        elif mentor_percentage > 20:
                            insights.append("👩‍🏫 <strong>Role Model Gap:</strong> Students want more women to look up to in tech")
                    
                    # Analyze access issues
                    if 'late-night-access' in help_counts and help_counts['late-night-access'] > 0:
                        access_percentage = (help_counts['late-night-access'] / total_responses) * 100
                        if access_percentage > 30:
                            insights.append("🌙 <strong>Access Inequality:</strong> Curfew restrictions are significantly limiting tech participation")
                        elif access_percentage > 15:
                            insights.append("🌙 <strong>Time Constraints:</strong> Students need more flexible lab access for tech activities")
                    
                    # Analyze team preferences
                    if 'all-girls-teams' in help_counts and help_counts['all-girls-teams'] > 0:
                        teams_percentage = (help_counts['all-girls-teams'] / total_responses) * 100
                        if teams_percentage > 25:
                            insights.append("👭 <strong>Safe Spaces Needed:</strong> Students prefer all-girls teams, indicating discomfort in mixed environments")
                        elif teams_percentage > 10:
                            insights.append("👭 <strong>Comfort Zones:</strong> Some students feel more comfortable in women-only tech teams")
                    
                    # Analyze reporting concerns
                    if 'anonymous-reporting' in help_counts and help_counts['anonymous-reporting'] > 0:
                        reporting_percentage = (help_counts['anonymous-reporting'] / total_responses) * 100
                        if reporting_percentage > 20:
                            insights.append("🔒 <strong>Safety Concerns:</strong> High demand for anonymous reporting suggests fear of retaliation")
                        elif reporting_percentage > 10:
                            insights.append("🔒 <strong>Reporting Barriers:</strong> Students need safer ways to report issues")
                    
                    # Analyze transparency needs
                    if 'transparent-selections' in help_counts and help_counts['transparent-selections'] > 0:
                        selection_percentage = (help_counts['transparent-selections'] / total_responses) * 100
                        if selection_percentage > 15:
                            insights.append("📋 <strong>Trust Issues:</strong> Students want transparent selection processes, indicating current opacity")
                    
                    # Overall pattern analysis
                    total_selected = sum(help_counts.values())
                    avg_selections = total_selected / total_responses if total_responses > 0 else 0
                    if avg_selections > 1.5:
                        insights.append("📊 <strong>Multiple Needs:</strong> Students have diverse needs, suggesting systemic issues across multiple areas")
                    
                    for insight in insights:
                        st.markdown(f"""
                        <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: rgba(255, 107, 157, 0.1); border-radius: 5px;">
                            <div style="color: #2c3e50; font-size: 0.9rem;">{insight}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🚀</div>
                <p class="text-light">No help data available yet</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card animated-bg" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🚀</div>
            <p class="text-light">No help data available yet</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Summary insights
    if not filtered_df.empty and 'help' in filtered_df.columns and not filtered_df['help'].isna().all():
        st.markdown('<h2 class="section-title">💡 Key Takeaways</h2>', unsafe_allow_html=True)
        
        # Calculate overall insights
        total_responses = len(filtered_df)
        help_responses = []
        for response in filtered_df['help'].dropna():
            if isinstance(response, list):
                help_responses.extend(response)
            elif isinstance(response, str):
                help_responses.extend(response.split(','))
        
        if help_responses:
            help_counts = Counter(help_responses)
            help_percentages = {item: (count / total_responses) * 100 for item, count in help_counts.items()}
            sorted_help = dict(sorted(help_percentages.items(), key=lambda x: x[1], reverse=True))
            
            # Generate insights
            top_3_priorities = list(sorted_help.keys())[:3]
            top_priority_percentage = list(sorted_help.values())[0] if sorted_help else 0
            
            # Check if there's a clear winner
            has_clear_winner = top_priority_percentage > 30
            
            # Check diversity of needs
            diverse_needs = len(sorted_help) > 5
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                    <div style="font-weight: 600; color: #e91e63;">Community Focus</div>
                    <div style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">
                        {'Clear priority identified' if has_clear_winner else 'Diverse needs across community'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-weight: 600; color: #e91e63;">Response Rate</div>
                    <div style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">
                        {len(filtered_df['help'].dropna())} out of {total_responses} students
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card animated-bg" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">💭</div>
                    <div style="font-weight: 600; color: #e91e63;">Need Diversity</div>
                    <div style="color: #7f8c8d; font-size: 0.9rem; margin-top: 0.5rem;">
                        {len(sorted_help)} different support categories identified
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Action recommendations
            st.markdown('<h3 class="section-title">🚀 Recommended Actions</h3>', unsafe_allow_html=True)
            
            # Generate specific recommendations based on the actual data
            recommendations = []
            
            # Check each option and provide specific recommendations
            if 'women-mentors' in help_counts and help_counts['women-mentors'] > 0:
                mentor_percentage = (help_counts['women-mentors'] / total_responses) * 100
                if mentor_percentage > 30:
                    recommendations.append("👩‍🏫 <strong>High Priority:</strong> Launch women mentorship program with industry professionals")
                else:
                    recommendations.append("👩‍🏫 <strong>Consider:</strong> Develop women mentorship initiatives")
            
            if 'late-night-access' in help_counts and help_counts['late-night-access'] > 0:
                access_percentage = (help_counts['late-night-access'] / total_responses) * 100
                if access_percentage > 25:
                    recommendations.append("🌙 <strong>High Priority:</strong> Negotiate extended lab hours for tech activities")
                else:
                    recommendations.append("🌙 <strong>Consider:</strong> Review lab access policies")
            
            if 'all-girls-teams' in help_counts and help_counts['all-girls-teams'] > 0:
                teams_percentage = (help_counts['all-girls-teams'] / total_responses) * 100
                if teams_percentage > 20:
                    recommendations.append("👭 <strong>High Priority:</strong> Create all-girls tech teams and hackathon groups")
                else:
                    recommendations.append("👭 <strong>Consider:</strong> Support women-only tech initiatives")
            
            if 'anonymous-reporting' in help_counts and help_counts['anonymous-reporting'] > 0:
                reporting_percentage = (help_counts['anonymous-reporting'] / total_responses) * 100
                if reporting_percentage > 15:
                    recommendations.append("🔒 <strong>High Priority:</strong> Implement anonymous reporting system")
                else:
                    recommendations.append("🔒 <strong>Consider:</strong> Develop safe reporting mechanisms")
            
            if 'transparent-selections' in help_counts and help_counts['transparent-selections'] > 0:
                selection_percentage = (help_counts['transparent-selections'] / total_responses) * 100
                if selection_percentage > 15:
                    recommendations.append("📋 <strong>High Priority:</strong> Make team selection processes transparent")
                else:
                    recommendations.append("📋 <strong>Consider:</strong> Review selection criteria transparency")
            
            if not recommendations:
                recommendations.append("📊 <strong>Monitor:</strong> Continue collecting data to identify clear priorities")
            
            st.markdown(f"""
            <div class="metric-card animated-bg" style="padding: 2rem;">
                <h4 style="color: #e91e63; margin-bottom: 1rem;">🎯 Data-Driven Recommendations</h4>
                <p style="color: #2c3e50; margin-bottom: 1rem;">
                    Based on responses from <strong>{total_responses} students</strong>, here are the specific actions needed:
                </p>
                <div style="background: linear-gradient(45deg, #e91e63, #ff6b9d); padding: 1rem; border-radius: 10px; color: white;">
                    <strong>Priority Actions:</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display recommendations
            for recommendation in recommendations:
                st.markdown(f"""
                <div class="metric-card animated-bg" style="padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #2c3e50; font-size: 1rem;">{recommendation}</div>
                </div>
                """, unsafe_allow_html=True)

def parting_words_page(df):
    """Section 6: Parting Words - Gen Z Vibes ✨"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 2rem; border-radius: 20px; color: white; box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);">
        <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">💝 Parting Words</h1>
        <p style="font-size: 1.3rem; margin-bottom: 0; opacity: 0.95; font-weight: 500;">✨ Messages to inspire the next generation ✨</p>
        <div style="margin-top: 1rem; font-size: 1rem; opacity: 0.8;">Because every voice matters 💫</div>
    </div>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown("""
        <div style="text-align: center; padding: 4rem; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); border-radius: 20px; border: 3px solid #ff6b9d; box-shadow: 0 15px 35px rgba(255, 107, 157, 0.2);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📭</div>
            <h2 style="color: #2c3e50; margin-bottom: 1rem; font-weight: 700; font-size: 2rem;">No Responses Yet</h2>
            <p style="color: #34495e; font-size: 1.2rem; font-weight: 500;">The dashboard will populate once responses start coming in! 🚀</p>
            <div style="margin-top: 2rem; font-size: 1.5rem;">✨ 💫 🌟</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Get all advice messages from database
    if 'advice' in df.columns and not df['advice'].isna().all():
        messages = df['advice'].dropna().tolist()
        
        if messages:
            # Add context about the advice section
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; color: white; box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💌</div>
                    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">✨ Wisdom from the Community ✨</p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">These messages represent the collective wisdom, experiences, and hopes of women in tech. Each piece of advice is a gift to the next generation.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Clean and get ALL unique messages (no limit)
            unique_messages = []
            seen_messages = set()
            
            for msg in messages:
                cleaned_msg = msg.strip()
                if cleaned_msg and len(cleaned_msg) > 5:  # Include more messages
                    normalized = cleaned_msg.lower().strip()
                    if normalized not in seen_messages:
                        seen_messages.add(normalized)
                        unique_messages.append(cleaned_msg)
            
            # Show statistics with Gen Z vibes
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; border: 2px solid #ff6b9d; box-shadow: 0 10px 25px rgba(255, 107, 157, 0.15);">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <p style="margin: 0; color: #2c3e50; font-weight: 700; font-size: 1.1rem;">
                        Found <span style="color: #e91e63; font-size: 1.3rem;">{len(unique_messages)} unique messages</span> from {len(messages)} total responses
                    </p>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #7f8c8d;">✨ Each one is special ✨</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gen Z search and sort controls
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; color: white; box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔍</div>
                    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">Find Your Perfect Message ✨</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                search_term = st.text_input("🔍 Search advice messages", placeholder="Type keywords to filter...", key="search_advice")
            
            with col2:
                sort_option = st.selectbox("🔄 Sort by", ["Original Order", "Length", "Alphabetical"], key="sort_advice")
            
            # Apply search filter
            filtered_messages = unique_messages.copy()
            if search_term:
                filtered_messages = [msg for msg in filtered_messages if search_term.lower() in msg.lower()]
            
            # Apply sorting
            if sort_option == "Length":
                filtered_messages.sort(key=len)
            elif sort_option == "Alphabetical":
                filtered_messages.sort()
            
            # Show filter results if any with Gen Z style
            if len(filtered_messages) != len(unique_messages):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; border: 2px solid #ff6b9d; box-shadow: 0 8px 20px rgba(255, 107, 157, 0.15);">
                    <div style="text-align: center;">
                        <p style="margin: 0; color: #2c3e50; font-size: 1rem; font-weight: 600;">
                            🔍 Showing <span style="color: #e91e63; font-weight: 700;">{len(filtered_messages)}</span> of <span style="color: #e91e63; font-weight: 700;">{len(unique_messages)}</span> messages
                        </p>
                        <div style="margin-top: 0.3rem; font-size: 0.8rem; color: #7f8c8d;">✨ Filtered just for you ✨</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            # Display messages in an improved grid layout
            if filtered_messages:
                st.markdown("""
                <div style="margin-top: 2rem; text-align: center;">
                    <h3 style="color: #2c3e50; font-size: 1.8rem; margin-bottom: 1.5rem; font-weight: 700; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">💌 Community Wisdom</h3>
                    <p style="color: #7f8c8d; font-size: 1rem; margin-bottom: 2rem;">✨ Scroll through the wisdom ✨</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a 2-column grid layout for better organization
                cols = st.columns(2)
                for i, message in enumerate(filtered_messages, 1):
                    col_idx = (i - 1) % 2
                    
                    # Different card styles based on position
                    if i % 6 == 0:
                        # Special highlight card
                        card_style = f"""
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; 
                            border-radius: 20px; 
                            padding: 1.5rem; 
                            margin-bottom: 1.5rem;
                            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
                            border: 3px solid rgba(255,255,255,0.2);
                            position: relative;
                            overflow: hidden;
                        ">
                            <div style="position: absolute; top: -10px; right: -10px; font-size: 2rem; opacity: 0.1;">💫</div>
                            <div style="text-align: center;">
                                <div style="font-size: 1.5rem; margin-bottom: 0.8rem;">🌟</div>
                                <p style="margin: 0; font-size: 1rem; line-height: 1.5; font-style: italic; font-weight: 500;">
                                    "{message}"
                                </p>
                                <div style="margin-top: 0.8rem; font-size: 0.8rem; opacity: 0.8;">
                                    #{i}
                                </div>
                            </div>
                        </div>
                        """
                    elif i % 6 == 1:
                        # Glassmorphism card
                        card_style = f"""
                        <div style="
                            background: rgba(255, 255, 255, 0.1); 
                            backdrop-filter: blur(10px); 
                            border: 2px solid rgba(255, 255, 255, 0.2); 
                            color: #2c3e50; 
                            border-radius: 20px; 
                            padding: 1.5rem; 
                            margin-bottom: 1.5rem;
                            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                        ">
                            <div style="text-align: center;">
                                <div style="font-size: 1.5rem; margin-bottom: 0.8rem;">✨</div>
                                <p style="margin: 0; font-size: 1rem; line-height: 1.5; font-style: italic; font-weight: 500;">
                                    "{message}"
                                </p>
                                <div style="margin-top: 0.8rem; font-size: 0.8rem; color: #7f8c8d;">
                                    #{i}
                                </div>
                            </div>
                        </div>
                        """
                    elif i % 6 == 2:
                        # Pink gradient card
                        card_style = f"""
                        <div style="
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            color: white; 
                            border-radius: 20px; 
                            padding: 1.5rem; 
                            margin-bottom: 1.5rem;
                            box-shadow: 0 15px 35px rgba(240, 147, 251, 0.3);
                            border: 3px solid rgba(255,255,255,0.2);
                        ">
                            <div style="text-align: center;">
                                <div style="font-size: 1.5rem; margin-bottom: 0.8rem;">💝</div>
                                <p style="margin: 0; font-size: 1rem; line-height: 1.5; font-style: italic; font-weight: 500;">
                                    "{message}"
                                </p>
                                <div style="margin-top: 0.8rem; font-size: 0.8rem; opacity: 0.8;">
                                    #{i}
                                </div>
                            </div>
                        </div>
                        """
                    elif i % 6 == 3:
                        # Pastel gradient card
                        card_style = f"""
                        <div style="
                            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                            color: #2c3e50; 
                            border-radius: 20px; 
                            padding: 1.5rem; 
                            margin-bottom: 1.5rem;
                            box-shadow: 0 15px 35px rgba(168, 237, 234, 0.3);
                            border: 3px solid rgba(255,255,255,0.3);
                        ">
                            <div style="text-align: center;">
                                <div style="font-size: 1.5rem; margin-bottom: 0.8rem;">🎀</div>
                                <p style="margin: 0; font-size: 1rem; line-height: 1.5; font-style: italic; font-weight: 500;">
                                    "{message}"
                                </p>
                                <div style="margin-top: 0.8rem; font-size: 0.8rem; color: #7f8c8d;">
                                    #{i}
                                </div>
                            </div>
                        </div>
                        """
                    elif i % 6 == 4:
                        # Purple gradient card
                        card_style = f"""
                        <div style="
                            background: linear-gradient(135deg, #9c27b0 0%, #673ab7 100%); 
                            color: white; 
                            border-radius: 20px; 
                            padding: 1.5rem; 
                            margin-bottom: 1.5rem;
                            box-shadow: 0 15px 35px rgba(156, 39, 176, 0.3);
                            border: 3px solid rgba(255,255,255,0.2);
                        ">
                            <div style="text-align: center;">
                                <div style="font-size: 1.5rem; margin-bottom: 0.8rem;">💜</div>
                                <p style="margin: 0; font-size: 1rem; line-height: 1.5; font-style: italic; font-weight: 500;">
                                    "{message}"
                                </p>
                                <div style="margin-top: 0.8rem; font-size: 0.8rem; opacity: 0.8;">
                                    #{i}
                                </div>
                            </div>
                        </div>
                        """
                    else:
                        # Orange gradient card
                        card_style = f"""
                        <div style="
                            background: linear-gradient(135deg, #ff9800 0%, #ff5722 100%); 
                            color: white; 
                            border-radius: 20px; 
                            padding: 1.5rem; 
                            margin-bottom: 1.5rem;
                            box-shadow: 0 15px 35px rgba(255, 152, 0, 0.3);
                            border: 3px solid rgba(255,255,255,0.2);
                        ">
                            <div style="text-align: center;">
                                <div style="font-size: 1.5rem; margin-bottom: 0.8rem;">🔥</div>
                                <p style="margin: 0; font-size: 1rem; line-height: 1.5; font-style: italic; font-weight: 500;">
                                    "{message}"
                                </p>
                                <div style="margin-top: 0.8rem; font-size: 0.8rem; opacity: 0.8;">
                                    #{i}
                                </div>
                            </div>
                        </div>
                        """
                    
                    with cols[col_idx]:
                        st.markdown(card_style, unsafe_allow_html=True)
                
                # Add a Gen Z style summary footer
                st.markdown("""
                <div style="text-align: center; margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); border-radius: 25px; color: white; box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">💝</div>
                    <p style="margin: 0; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
                        Every piece of advice matters ✨
                    </p>
                    <p style="margin: 0; font-size: 1rem; opacity: 0.9;">
                        These messages represent the collective wisdom of women in tech 💫
                    </p>
                    <div style="margin-top: 1.5rem; font-size: 1.5rem;">🌟 💫 ✨ 🎀</div>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.markdown("""
                <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); border-radius: 20px; border: 3px solid #ff6b9d; box-shadow: 0 15px 35px rgba(255, 107, 157, 0.2);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">💌</div>
                    <p style="color: #2c3e50; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">No meaningful advice messages available yet</p>
                    <p style="color: #7f8c8d; font-size: 1rem;">✨ But they're coming soon! ✨</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); border-radius: 20px; border: 3px solid #ff6b9d; box-shadow: 0 15px 35px rgba(255, 107, 157, 0.2);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">💌</div>
                <p style="color: #2c3e50; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">No advice messages available yet</p>
                <p style="color: #7f8c8d; font-size: 1rem;">🌟 Stay tuned for wisdom! 🌟</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; border: 3px solid #ff6b9d; box-shadow: 0 15px 35px rgba(255, 107, 157, 0.2); color: white;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">💌</div>
            <p style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">No advice messages available yet</p>
            <p style="font-size: 1rem; opacity: 0.9;">💫 The wisdom is coming! 💫</p>
        </div>
        """, unsafe_allow_html=True)

def get_genz_messages():
    """Collection of Gen Z messages and one-liners for the dashboard"""
    return {
        'hero_messages': [
            "✨ Amplifying Women's Voices in Tech ✨",
            "🚀 Making waves in the tech world 🚀", 
            "💫 Every voice matters, every story counts 💫",
            "🌟 Empowering the next generation of tech leaders 🌟",
            "🎀 Breaking barriers, building bridges 🎀"
        ],
        'metric_messages': {
            'high_response': [
                "Absolutely crushing it! 🔥",
                "Making waves and breaking records! 🌊",
                "The community is thriving! ✨",
                "Incredible engagement! 🚀"
            ],
            'medium_response': [
                "Building momentum! 💪",
                "Growing stronger every day! 🌱",
                "Making progress! 📈",
                "On the rise! ⬆️"
            ],
            'low_response': [
                "Getting started! 🌟",
                "Every journey begins with a step! 👣",
                "The beginning of something amazing! ✨",
                "Ready to grow! 🌱"
            ]
        },
        'mood_messages': {
            'positive': [
                "Feeling the vibes! 😊",
                "Positive energy all around! ✨",
                "Great community spirit! 💫",
                "Amazing vibes! 🌟"
            ],
            'neutral': [
                "Room for growth! 📈",
                "Building better spaces! 🏗️",
                "Working on improvements! 🔧",
                "On the right track! 🎯"
            ],
            'negative': [
                "Need support & allyship! 🤝",
                "Time for positive change! 💪",
                "Building better vibes! 🌈",
                "Creating safe spaces! 🛡️"
            ]
        },
        'call_to_action': [
            "Ready to dive deeper? Let's explore! 🚀",
            "Curious about the data? Let's discover! 🔍",
            "Want to see more insights? Let's go! 💫",
            "Ready for the full story? Let's uncover! ✨"
        ],
        'professional_features': [
            "📊 Real-time Analytics",
            "📈 Trend Analysis", 
            "🎯 Actionable Insights",
            "📋 Export Capabilities",
            "🔄 Live Data Updates",
            "📱 Mobile Responsive",
            "🎨 Modern UI/UX",
            "🔒 Secure Data Handling"
        ]
    }

def create_professional_metrics(df):
    """Create professional dashboard metrics with Gen Z flair"""
    metrics = {}
    
    # Basic counts
    metrics['total_responses'] = len(df)
    metrics['unique_courses'] = len(df['course'].dropna().unique()) if 'course' in df.columns else 0
    metrics['unique_years'] = len(df['year'].dropna().unique()) if 'year' in df.columns else 0
    
    # Response rate (if we had total population)
    metrics['response_rate'] = "N/A"  # Would need total population data
    
    # Sentiment analysis
    mood_questions = ['boys-club', 'equal-chances', 'safe-supported', 'held-back', 'women-mentors']
    mood_scores = []
    for q in mood_questions:
        if q in df.columns:
            numeric_values = pd.to_numeric(df[q], errors='coerce')
            if not numeric_values.isna().all():
                mood_scores.append(numeric_values.mean())
    
    metrics['avg_sentiment'] = np.mean(mood_scores) if mood_scores else 0
    metrics['sentiment_trend'] = "Stable"  # Would need historical data
    
    # Issues identification
    if 'judged' in df.columns and not df['judged'].isna().all():
        judged_responses = df['judged'].dropna()
        if len(judged_responses) > 0:
            metrics['judged_percentage'] = len(judged_responses[judged_responses.isin(['multiple', 'sometimes'])]) / len(judged_responses) * 100
        else:
            metrics['judged_percentage'] = 0
    else:
        metrics['judged_percentage'] = 0
    
    # Top concerns
    if 'help' in df.columns and not df['help'].isna().all():
        help_responses = []
        for response in df['help'].dropna():
            if isinstance(response, list):
                help_responses.extend(response)
            elif isinstance(response, str):
                help_responses.extend(response.split(','))
        
        if help_responses:
            help_counts = Counter(help_responses)
            metrics['top_concern'] = help_counts.most_common(1)[0][0] if help_counts else "N/A"
        else:
            metrics['top_concern'] = "N/A"
    else:
        metrics['top_concern'] = "N/A"
    
    return metrics

def create_genz_insights(df):
    """Generate comprehensive Gen Z style insights from the data"""
    insights = []
    
    total_responses = len(df)
    
    # Response volume insights
    if total_responses > 100:
        insights.append("🔥 The community is absolutely thriving with over 100 voices heard!")
    elif total_responses > 50:
        insights.append("✨ Making waves with 50+ amazing responses!")
    elif total_responses > 10:
        insights.append("🌟 Building momentum with growing community engagement!")
    else:
        insights.append("💫 Every voice matters - the journey has begun!")
    
    # Sentiment insights
    mood_questions = ['boys-club', 'equal-chances', 'safe-supported', 'held-back', 'women-mentors']
    mood_scores = []
    for q in mood_questions:
        if q in df.columns:
            numeric_values = pd.to_numeric(df[q], errors='coerce')
            if not numeric_values.isna().all():
                mood_scores.append(numeric_values.mean())
    
    avg_mood = np.mean(mood_scores) if mood_scores else 0
    
    if avg_mood >= 3.5:
        insights.append("😊 The community is feeling positive and supported!")
    elif avg_mood >= 2.5:
        insights.append("📈 There's room for growth and improvement!")
    else:
        insights.append("💪 Time to build stronger support systems!")
    
    # Course diversity insights
    if 'course' in df.columns and not df['course'].isna().all():
        unique_courses = len(df['course'].dropna().unique())
        if unique_courses > 10:
            insights.append("📚 Amazing diversity across 10+ different courses!")
        elif unique_courses > 5:
            insights.append("🎓 Great representation from multiple disciplines!")
        else:
            insights.append("🌟 Building representation across different fields!")
    
    # Year distribution insights
    if 'year' in df.columns and not df['year'].isna().all():
        year_counts = df['year'].dropna().value_counts()
        if len(year_counts) > 0:
            most_common_year = year_counts.index[0]
            insights.append(f"🎓 {most_common_year} students are leading the charge!")
    
    # Judgment insights
    if 'judged' in df.columns and not df['judged'].isna().all():
        judged_responses = df['judged'].dropna()
        judged_pct = len(judged_responses[judged_responses.isin(['multiple', 'sometimes'])]) / len(judged_responses) * 100
        if judged_pct > 50:
            insights.append("⚠️ High judgment rates detected - urgent need for allyship and support!")
        elif judged_pct > 25:
            insights.append("🤔 Moderate judgment experiences - work needed on creating safer spaces!")
        else:
            insights.append("💪 Low judgment rates - great progress in building inclusive environments!")
    
    # Voice insights
    if 'voice' in df.columns and not df['voice'].isna().all():
        voice_counts = df['voice'].dropna().value_counts()
        if 'comfortable' in voice_counts.index and voice_counts['comfortable'] > voice_counts.sum() * 0.5:
            insights.append("🎙️ Most students feel comfortable speaking up - positive group dynamics!")
        elif 'uncomfortable' in voice_counts.index and voice_counts['uncomfortable'] > voice_counts.sum() * 0.3:
            insights.append("🤐 Many students feel uncomfortable speaking up - need safer spaces!")
    
    # Help priorities insights
    if 'help' in df.columns and not df['help'].isna().all():
        help_responses = []
        for response in df['help'].dropna():
            if isinstance(response, list):
                help_responses.extend(response)
            elif isinstance(response, str):
                help_responses.extend(response.split(','))
        
        if help_responses:
            help_counts = Counter(help_responses)
            top_help = help_counts.most_common(1)[0][0] if help_counts else ""
            if 'mentor' in top_help.lower():
                insights.append("👩‍🏫 Mentorship is the top priority - women want role models and guidance!")
            elif 'support' in top_help.lower():
                insights.append("🤝 Support systems are key - community and allyship matter most!")
            elif 'opportunity' in top_help.lower():
                insights.append("🚀 Opportunities are in demand - women want chances to grow and excel!")
    
    # Activity insights
    if 'createdAt' in df.columns and not df['createdAt'].isna().all():
        try:
            df['date'] = pd.to_datetime(df['createdAt']).dt.date
            recent_activity = df['date'].value_counts().sort_index().tail(3)
            if recent_activity.sum() > 10:
                insights.append("📈 High recent engagement - community is actively participating and growing!")
            elif recent_activity.sum() > 5:
                insights.append("📊 Steady participation - consistent engagement shows sustained interest!")
        except:
            pass
    
    # Gender dynamics insights
    if 'stepped-back' in df.columns and not df['stepped-back'].isna().all():
        stepped_counts = df['stepped-back'].dropna().value_counts()
        if 'yes' in stepped_counts.index and stepped_counts['yes'] > stepped_counts.sum() * 0.3:
            insights.append("🚶‍♀️ Many women have stepped back from opportunities - need to address barriers!")
        elif 'no' in stepped_counts.index and stepped_counts['no'] > stepped_counts.sum() * 0.7:
            insights.append("💪 Most women are staying engaged - great resilience and determination!")
    
    # Curfew impact insights
    if 'curfews' in df.columns and not df['curfews'].isna().all():
        curfew_counts = df['curfews'].dropna().value_counts()
        if 'yes' in curfew_counts.index and curfew_counts['yes'] > curfew_counts.sum() * 0.4:
            insights.append("🕒 Curfews are significantly impacting participation - need flexible solutions!")
        elif 'no' in curfew_counts.index and curfew_counts['no'] > curfew_counts.sum() * 0.6:
            insights.append("✅ Curfews aren't a major barrier - other factors may be more important!")
    
    return insights

# Main app logic
def main():
    # Get current page from URL parameters
    current_page = st.query_params.get("page", "overview")
    
    # Create navbar
    create_navbar(current_page)
    
    # Fetch data
    df = fetch_responses()
    
    # Route to appropriate page
    if current_page == "overview":
        overview_page(df)
    elif current_page == "who-are-you":
        who_are_you_page(df)
    elif current_page == "real-talk":
        real_talk_page(df)
    elif current_page == "mood-check":
        mood_check_page(df)
    elif current_page == "say-it":
        say_it_page(df)
    elif current_page == "quick-picks":
        quick_picks_page(df)
    elif current_page == "parting-words":
        parting_words_page(df)
    else:
        st.error(f"Unknown page: {current_page}")
        overview_page(df)

if __name__ == "__main__":
    main()
