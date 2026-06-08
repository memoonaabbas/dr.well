# ui_components.py
import streamlit as st
import random
from database import get_user_by_id, check_database

def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a2a33 0%, #0f3a45 50%, #0a2a33 100%);
            border-right: 1px solid rgba(255,215,0,0.2);
        }
        
        .sidebar-header {
            text-align: center;
            padding: 25px 15px 20px 15px;
            border-bottom: 2px solid rgba(255,215,0,0.3);
            margin-bottom: 20px;
        }
        
        .sidebar-header img {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
            padding: 8px;
            margin-bottom: 12px;
        }
        
        .sidebar-header h3 {
            color: #FFD700;
            font-size: 1.3rem;
            margin: 0;
            font-weight: 700;
        }
        
        .sidebar-header p {
            color: #90c9d9;
            font-size: 0.8rem;
            margin-top: 5px;
        }
        
        .user-info {
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            margin: 10px;
        }
        
        .user-name {
            color: #FFD700;
            font-size: 1rem;
            font-weight: 600;
        }
        
        .user-type {
            color: #90c9d9;
            font-size: 0.8rem;
            background: rgba(255,255,255,0.1);
            display: inline-block;
            padding: 2px 12px;
            border-radius: 20px;
            margin-top: 5px;
        }
        
        .stats-badge {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 10px;
            margin: 10px;
            text-align: center;
        }
        
        .stats-badge span {
            color: #FFD700;
            font-weight: bold;
        }
        
        /* Main Header */
        .main-header {
            background: linear-gradient(135deg, #1e5f6b 0%, #2c7a8a 100%);
            border-radius: 20px;
            padding: 32px;
            text-align: center;
            margin-bottom: 32px;
            color: white;
        }
        
        .main-header h1 {
            font-size: 2rem;
            margin-bottom: 8px;
            font-weight: 700;
        }
        
        .hero-banner {
            background: linear-gradient(135deg, #1e5f6b 0%, #2c7a8a 100%);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .hero-banner h1 {
            color: white;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .hero-banner p {
            color: rgba(255,255,255,0.9);
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 20px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        
        /* Stat Cards */
        .stat-card {
            background: white;
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #2c7a8a;
        }
        
        /* Doctor Card */
        .doctor-card {
            background: white;
            border-radius: 20px;
            padding: 24px;
            margin: 12px 0;
            border: 1px solid #e0e4e8;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            transition: all 0.3s ease;
        }
        
        .doctor-card:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
            transform: translateY(-2px);
        }
        
        .doctor-avatar {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #2c7a8a 0%, #1e5f6b 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
        }
        
        .grid-2 {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 16px;
        }
        
        .grid-col {
            flex: 1;
            min-width: 180px;
        }
        
        .grid-col p {
            margin: 6px 0;
            color: #4a5568;
            font-size: 0.9rem;
        }
        
        .grid-col strong {
            color: #1e5f6b;
        }
        
        .availability {
            background: #e8f4f0;
            padding: 10px 14px;
            border-radius: 10px;
            margin-bottom: 12px;
            font-size: 0.9rem;
        }
        
        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-green {
            background: #d4edda;
            color: #155724;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #2c7a8a 0%, #1e5f6b 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(44,122,138,0.4);
        }
        
        /* Chat Messages */
        .stChatMessage {
            background: white !important;
            border-radius: 16px !important;
            padding: 12px 16px !important;
            margin: 8px 0 !important;
            border: 1px solid #e0e4e8 !important;
        }
        
        .welcome-message {
            background: linear-gradient(135deg, #e8f4f0 0%, #d4e8e2 100%);
            border-radius: 16px;
            padding: 15px 20px;
            margin: 20px 0;
            border-left: 4px solid #2c7a8a;
        }
        
        /* Inline booking form */
        .booking-form-container {
            background: linear-gradient(135deg, #e8f4f0, #d4e8e2);
            border-radius: 16px;
            padding: 20px;
            margin: 0 0 20px 0;
            border-left: 4px solid #2c7a8a;
        }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #e0e4e8; border-radius: 10px; }
        ::-webkit-scrollbar-thumb { background: #2c7a8a; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)


# Images
IMAGES = {
    "hero": "https://cdn-icons-png.flaticon.com/512/4222/4222677.png",
    "consultation": "https://cdn-icons-png.flaticon.com/512/4222/4222677.png",
    "medication": "https://cdn-icons-png.flaticon.com/512/3096/3096600.png",
    "heart": "https://cdn-icons-png.flaticon.com/512/3028/3028751.png",
    "appointment": "https://cdn-icons-png.flaticon.com/512/3129/3129723.png",
    "stethoscope": "https://cdn-icons-png.flaticon.com/512/3049/3049575.png",
    "doctors": "https://cdn-icons-png.flaticon.com/512/2991/2991100.png",
    "health": "https://cdn-icons-png.flaticon.com/512/2972/2972654.png",
    "logo": "https://i.ibb.co/JwvqB1gC/file-00000000a21c90f54aa4611cd246.png",
}


def render_sidebar():
    """Render sidebar with logo, user info, stats, logout."""
    st.markdown("""
    <div class="sidebar-header">
        <img src="https://i.ibb.co/JwvqB1gC/file-00000000a21c90f54aa4611cd246.png" alt="Dr. Well">
        <h3>Dr. Well</h3>
        <p>AI Medical Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    if 'user_id' in st.session_state:
        try:
            user = get_user_by_id(st.session_state.user_id)
            if user:
                st.markdown(f"""
                <div class="user-info">
                    <div class="user-name">👋 {user.get('full_name', 'User')}</div>
                    <div class="user-type">{st.session_state.get('user_type', 'patient').title()}</div>
                </div>
                """, unsafe_allow_html=True)
        except:
            pass

    try:
        stats = check_database()
        st.markdown(f"""
        <div class="stats-badge">
            📊 <span>{stats['users']}</span> Users &nbsp;|&nbsp; <span>{stats['doctors']}</span> Doctors
        </div>
        """, unsafe_allow_html=True)
    except:
        pass

    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def show_hero_banner(username):
    st.markdown(f"""
    <div class="hero-banner">
        <img src="{IMAGES['hero']}" alt="Dr. Well" width="80">
        <h1>👋 Hello, {username}!</h1>
        <p>Your health is our priority. How can Dr. Well help you today?</p>
    </div>
    """, unsafe_allow_html=True)


def show_dashboard_stats():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="stat-card">
            <img src="{IMAGES['consultation']}" width="40">
            <div class="stat-number">24/7</div><p>AI Available</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-card">
            <img src="{IMAGES['doctors']}" width="40">
            <div class="stat-number">15+</div><p>Expert Doctors</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-card">
            <img src="{IMAGES['medication']}" width="40">
            <div class="stat-number">100%</div><p>Safe Meds</p>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="stat-card">
            <img src="{IMAGES['appointment']}" width="40">
            <div class="stat-number">500+</div><p>Patients Served</p>
        </div>""", unsafe_allow_html=True)


def show_chat_welcome():
    st.markdown(f"""
    <div class="welcome-message">
        <div style="display: flex; align-items: center; gap: 15px;">
            <img src="{IMAGES['consultation']}" width="50">
            <div>
                <strong>🤖 Dr. Well AI Assistant</strong><br>
                <small>Describe your symptoms. I'll analyze and provide treatment advice!</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_about_page():
    st.markdown(f"""
    <div class="hero-banner">
        <img src="{IMAGES['logo']}" alt="Dr. Well" width="90" style="border-radius: 50%;">
        <h1>🤖 Welcome to Dr. Well</h1>
        <p>Your AI-Powered Medical Assistant — Available 24/7</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h2 style="color: #1e5f6b;">🌟 About Dr. Well</h2>
            <p>Dr. Well is an advanced AI Medical Assistant that provides instant healthcare guidance.</p>
            <ul>
                <li>🤖 Smart Symptom Analysis</li>
                <li>💊 Auto Medication Prescriber</li>
                <li>👨‍⚕️ Doctor Referral System</li>
                <li>📅 Easy Appointment Booking</li>
                <li>🍎 Personalized Nutrition Advice</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card">
            <h2 style="color: #1e5f6b; text-align: center;">🎯 Key Features</h2>
            <div style="background: #e8f4f0; border-radius: 12px; padding: 16px; margin: 10px 0;">
                <img src="{IMAGES['stethoscope']}" width="35" style="float: left; margin-right: 12px;">
                <h3 style="color: #1e5f6b;">✓ 24/7 Availability</h3>
                <p>AI assistance anytime, anywhere</p>
            </div>
            <div style="background: #e8f4f0; border-radius: 12px; padding: 16px; margin: 10px 0;">
                <img src="{IMAGES['heart']}" width="35" style="float: left; margin-right: 12px;">
                <h3 style="color: #1e5f6b;">✓ Complete Care</h3>
                <p>Full healthcare management system</p>
            </div>
            <div style="background: #e8f4f0; border-radius: 12px; padding: 16px; margin: 10px 0;">
                <img src="{IMAGES['doctors']}" width="35" style="float: left; margin-right: 12px;">
                <h3 style="color: #1e5f6b;">✓ Expert Doctors</h3>
                <p>15+ verified medical specialists</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def show_login_ui():
    st.markdown(f'''
    <div class="card" style="max-width: 450px; margin: 0 auto;">
        <div style="text-align: center;">
            <img src="{IMAGES['logo']}" alt="Dr. Well" width="90" style="border-radius: 50%;">
            <h2 style="color: #1e5f6b; margin-top: 10px;">Welcome Back!</h2>
            <p>Login to continue</p>
        </div>
    ''', unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Username or Email", placeholder="Enter your username or email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.form_submit_button("Login", use_container_width=True):
            if username and password:
                return {"username": username, "password": password}
    st.markdown('</div>', unsafe_allow_html=True)
    return None


def show_signup_ui():
    st.markdown(f'''
    <div class="card" style="max-width: 500px; margin: 0 auto;">
        <div style="text-align: center;">
            <img src="{IMAGES['logo']}" alt="Dr. Well" width="90" style="border-radius: 50%;">
            <h2 style="color: #1e5f6b;">Create Account</h2>
            <p>Join Dr. Well today</p>
        </div>
    ''', unsafe_allow_html=True)
    with st.form("signup_form"):
        user_type = st.radio("I am a:", ["Patient", "Doctor"], horizontal=True)
        full_name = st.text_input("Full Name*", placeholder="Enter your full name")
        email = st.text_input("Email*", placeholder="Enter your email")
        username = st.text_input("Username*", placeholder="Choose a username")
        password = st.text_input("Password*", type="password", placeholder="Create a password")
        confirm = st.text_input("Confirm Password*", type="password", placeholder="Confirm your password")
        phone = st.text_input("Phone Number", placeholder="Optional")

        if st.form_submit_button("Sign Up", use_container_width=True):
            if all([full_name, email, username, password, confirm]):
                if password == confirm and len(password) >= 6:
                    return {"full_name": full_name, "email": email, "username": username,
                            "password": password, "user_type": user_type.lower(), "phone": phone}
                else:
                    st.error("Passwords must match and be at least 6 characters")
            else:
                st.error("Please fill all required fields")
    st.markdown('</div>', unsafe_allow_html=True)
    return None


def show_patient_info_form():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #1e5f6b;'>👤 Complete Your Profile</h2>", unsafe_allow_html=True)
    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1, value=70.0)
            height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0, step=0.1, value=170.0)
        with col2:
            blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            allergies = st.text_input("Allergies", placeholder="e.g., Penicillin, Peanuts")
        about = st.text_area("About Yourself", placeholder="Tell us about yourself...")
        if st.form_submit_button("Save Profile", use_container_width=True):
            return {"weight": weight, "height": height, "blood_group": blood_group,
                    "allergies": allergies, "about": about}
    st.markdown('</div>', unsafe_allow_html=True)
    return None


def show_doctor_info_form():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #1e5f6b;'>👨‍⚕️ Complete Your Profile</h2>", unsafe_allow_html=True)
    with st.form("doctor_form"):
        col1, col2 = st.columns(2)
        with col1:
            specialty = st.selectbox("Specialty*", [
                "Cardiologist", "Dermatologist", "Neurologist", "Orthopedic Surgeon",
                "Pediatrician", "General Physician", "ENT Specialist", "Ophthalmologist", "Gynecologist"
            ])
            qualification = st.text_input("Qualification*", placeholder="e.g., MBBS, MD")
            experience = st.number_input("Years of Experience*", min_value=0, max_value=50, step=1, value=10)
            fee = st.number_input("Consultation Fee ($)*", min_value=0, step=10, value=100)
        with col2:
            clinic_name = st.text_input("Clinic Name*")
            clinic_address = st.text_input("Clinic Address*")
            city = st.text_input("City*")
            state = st.text_input("State*")
            zip_code = st.text_input("ZIP Code*")
            phone = st.text_input("Clinic Phone*")

        days = st.multiselect("Available Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        col3, col4 = st.columns(2)
        with col3:
            start = st.time_input("From")
        with col4:
            end = st.time_input("To")
        about = st.text_area("About Yourself")

        if st.form_submit_button("Save Profile", use_container_width=True):
            if all([specialty, qualification, clinic_name, clinic_address, city, state, zip_code, phone, days]):
                return {"specialty": specialty, "qualification": qualification, "experience": experience,
                        "fee": fee, "clinic_name": clinic_name, "clinic_address": clinic_address,
                        "city": city, "state": state, "zip_code": zip_code, "phone": phone,
                        "days": ",".join(days), "start": start.strftime("%H:%M"),
                        "end": end.strftime("%H:%M"), "about": about}
            else:
                st.error("Please fill all required fields")
    st.markdown('</div>', unsafe_allow_html=True)
    return None


def show_doctor_card_ui(doctor: dict) -> bool:
    """
    Renders a doctor card and returns True if the Book button was clicked.
    This replaces show_doctor_card() to support inline booking in main.py.
    """
    def safe_get(value, default='N/A'):
        return str(value) if value else default

    rating_value = doctor.get('rating')
    try:
        rating_float = float(rating_value) if rating_value else 4.5
        rating_int = min(int(rating_float), 5)
    except (ValueError, TypeError):
        rating_int = 4
        rating_float = 4.5

    rating_stars = "⭐" * rating_int + "☆" * (5 - rating_int)
    doc_id = doctor['id']

    st.markdown(f"""
    <div class="doctor-card">
        <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px;
                    padding-bottom:12px; border-bottom:2px solid #e8f4f0;">
            <div class="doctor-avatar">👨‍⚕️</div>
            <div>
                <h3 style="margin:0; color:#1e5f6b;">Dr. {safe_get(doctor.get('full_name'))}</h3>
                <div style="color:#2c7a8a; font-weight:600;">{safe_get(doctor.get('specialty'))}</div>
                <div>{rating_stars} {rating_float} ({safe_get(doctor.get('total_reviews'), 0)} reviews)</div>
            </div>
        </div>
        <div class="grid-2">
            <div class="grid-col">
                <p><strong>📚 Qualification:</strong> {safe_get(doctor.get('qualification'))}</p>
                <p><strong>📅 Experience:</strong> {safe_get(doctor.get('experience_years'), 0)} years</p>
                <p><strong>💰 Fee:</strong> ${safe_get(doctor.get('consultation_fee'), 0)}</p>
                <p><strong>📞 Phone:</strong> {safe_get(doctor.get('phone'))}</p>
            </div>
            <div class="grid-col">
                <p><strong>🏥 Clinic:</strong> {safe_get(doctor.get('clinic_name'))}</p>
                <p><strong>📍 Address:</strong> {safe_get(doctor.get('clinic_address'))}</p>
                <p><strong>🌆 City:</strong> {safe_get(doctor.get('city'))}, {safe_get(doctor.get('state'))}</p>
                <p><strong>📧 Email:</strong> {safe_get(doctor.get('email'))}</p>
            </div>
        </div>
        <div class="availability">
            🕒 <strong>Available:</strong> {safe_get(doctor.get('available_days'))} &nbsp;|&nbsp;
            {safe_get(doctor.get('available_time_start'))} – {safe_get(doctor.get('available_time_end'))}
        </div>
        <p style="font-size:0.9rem; color:#4a5568;">
            📝 {safe_get(doctor.get('about', ''))[:200]}
        </p>
        <span class="badge badge-green">✓ Available for Consultation</span>
    </div>
    """, unsafe_allow_html=True)

    # The Book button — returns True when clicked
    btn_label = (
        "🔼 Close Booking Form"
        if st.session_state.get(f"booking_open_{doc_id}")
        else f"📅 Book Appointment with Dr. {safe_get(doctor.get('full_name'))}"
    )
    return st.button(btn_label, key=f"book_btn_{doc_id}", use_container_width=True)


# Keep show_doctor_card as alias for backward compatibility
def show_doctor_card(doctor: dict):
    """Legacy wrapper — use show_doctor_card_ui instead for inline booking."""
    clicked = show_doctor_card_ui(doctor)
    if clicked:
        return doctor
    return None