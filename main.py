# main.py
import streamlit as st
from datetime import datetime
import time
import re
import uuid

from config import *
from database import *
from ui_components import *

st.set_page_config(
    page_title="Dr. Well - AI Medical Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_custom_css()


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def get_all_doctors_text() -> str:
    """Format all doctors as a readable string for the AI prompt."""
    all_doctors = get_all_doctors()
    lines = []
    for doc in all_doctors:
        lines.append(
            f"Dr. {doc.get('full_name')}|Specialty:{doc.get('specialty')}"
            f"|Clinic:{doc.get('clinic_name')}|City:{doc.get('city')}"
            f"|Fee:${doc.get('consultation_fee')}|Phone:{doc.get('phone')}"
            f"|Days:{doc.get('available_days')}"
            f"|Time:{doc.get('available_time_start')}-{doc.get('available_time_end')}"
        )
    return "\n".join(lines) if lines else "No doctors available"


def get_patient_info_text(user_id: int) -> str:
    """Format patient profile as a string for the AI prompt."""
    user = get_user_by_id(user_id)
    patient = get_patient_info(user_id)
    if not user:
        return "No patient profile"
    info = f"Name: {user.get('full_name', 'Unknown')}"
    if patient:
        info += (
            f" | Weight: {patient.get('weight', '?')}kg"
            f" | Height: {patient.get('height', '?')}cm"
            f" | Blood Group: {patient.get('blood_group', '?')}"
            f" | Allergies: {patient.get('allergies', 'None')}"
        )
    return info


def stream_response(response_text: str):
    """Stream response word by word for typing effect."""
    for word in response_text.split():
        yield word + " "
        time.sleep(0.02)


def get_ai_response(prompt: str, chat_history: list, session_id: str) -> dict:
    """Call the Dr. Well agent and return result dict."""
    from agent import run_agent

    doctors_info = get_all_doctors_text()
    patient_info = get_patient_info_text(st.session_state.user_id)

    result = run_agent(
        user_message=prompt,
        user_id=st.session_state.user_id,
        session_id=session_id,
        history=chat_history,
        doctors_info=doctors_info,
        patient_info=patient_info
    )

    # Auto-save extracted medications
    for med in result.get("extracted_meds", []):
        existing = get_medications(st.session_state.user_id)
        if not any(m['name'].lower() == med['name'].lower() for m in existing):
            save_medication(
                st.session_state.user_id,
                med['name'],
                med['dosage'],
                "As prescribed",
                med.get('timing', 'After food'),
                7,
                "Follow doctor's advice",
                "Dr. Well AI"
            )
            st.session_state[f"med_added_{med['name']}"] = True

    # Queue doctor recommendations if referral detected
    specialty = result.get("referred_specialty")
    if specialty:
        recommended = get_doctors_by_specialty(specialty)
        if recommended:
            st.session_state.show_doctor_recommendation = recommended[:3]

    return result


# ─────────────────────────────────────────────
# Inline Booking Form (shown right below doctor card)
# ─────────────────────────────────────────────

def show_inline_booking_form(doctor: dict, form_key: str):
    """Show booking form inline directly below the doctor card."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #e8f4f0, #d4e8e2);
                border-radius: 16px; padding: 20px; margin: 8px 0 16px 0;
                border-left: 4px solid #2c7a8a;">
        <h4 style="color:#1e5f6b; margin:0 0 12px 0;">
            📅 Book Appointment — Dr. {doctor.get('full_name', '')}
        </h4>
    </div>
    """, unsafe_allow_html=True)

    with st.form(key=form_key):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Select Date", min_value=datetime.now().date())
        with col2:
            time_slot = st.time_input("Select Time")
        symptoms = st.text_area("Describe your symptoms", height=80, placeholder="e.g., headache, fever since 2 days...")

        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            confirm = st.form_submit_button("✅ Confirm Booking", use_container_width=True)
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

    if confirm:
        save_appointment(
            st.session_state.user_id,
            doctor['id'],
            doctor['full_name'],
            doctor.get('specialty', ''),
            date.strftime("%Y-%m-%d"),
            time_slot.strftime("%H:%M"),
            symptoms,
            ""
        )
        st.success(f"✅ Appointment booked with Dr. {doctor['full_name']} on {date} at {time_slot.strftime('%H:%M')}!")
        # Clear the booking state for this doctor
        st.session_state.pop(f"booking_open_{doctor['id']}", None)
        st.rerun()

    if cancel:
        st.session_state.pop(f"booking_open_{doctor['id']}", None)
        st.rerun()


# ─────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────

def dashboard():
    user = get_user_by_id(st.session_state.user_id)
    show_hero_banner(user.get('full_name', 'User'))
    show_dashboard_stats()

    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🩺 **Consultations**\nChat with AI Doctor", use_container_width=True):
            st.session_state.page = "Consultations"; st.rerun()
    with col2:
        if st.button("🍎 **Nutrition**\nAI Diet Advice", use_container_width=True):
            st.session_state.page = "Nutrition"; st.rerun()
    with col3:
        if st.button("💊 **Medications**\nView prescriptions", use_container_width=True):
            st.session_state.page = "Medications"; st.rerun()
    with col4:
        if st.button("📅 **Appointments**\nSchedule visits", use_container_width=True):
            st.session_state.page = "Appointments"; st.rerun()

    col5, col6, col7 = st.columns(3)
    with col5:
        if st.button("👨‍⚕️ **Find Doctors**\nBrowse specialists", use_container_width=True):
            st.session_state.page = "Find Doctors"; st.rerun()
    with col6:
        if st.button("👤 **My Profile**\nUpdate information", use_container_width=True):
            st.session_state.page = "Profile"; st.rerun()
    with col7:
        if st.button("🚨 **Emergency**\nGet immediate help", use_container_width=True):
            st.error("🚨 **EMERGENCY!** Call 911 or 1122 immediately!")
            st.info("📞 Ambulance: 911/1122 | Poison Control: 1-800-222-1222")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card"><h3>💊 Recent Medications</h3>', unsafe_allow_html=True)
        meds = get_medications(st.session_state.user_id)
        if meds:
            for m in meds[:5]:
                st.write(f"• **{m['name']}** — {m['dosage']}")
        else:
            st.info("No active medications")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>📅 Upcoming Appointments</h3>', unsafe_allow_html=True)
        apts = get_appointments(st.session_state.user_id)
        upcoming = [a for a in apts if a['status'] != 'Completed'][:5]
        if upcoming:
            for a in upcoming:
                st.write(f"• **Dr. {a['doctor_name']}** — {a['date']}")
        else:
            st.info("No upcoming appointments")
        st.markdown('</div>', unsafe_allow_html=True)


def consultations():
    st.markdown(
        '<div class="main-header"><h1>🩺 AI Medical Consultation</h1>'
        '<p>Describe your symptoms — Dr. Well will analyze and treat you!</p></div>',
        unsafe_allow_html=True
    )
    show_chat_welcome()

    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"; st.rerun()

    # Session init
    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = create_chat_session(st.session_state.user_id)
        st.session_state.chat_messages = []

    if 'chat_messages' not in st.session_state or not st.session_state.chat_messages:
        saved = get_chat_history(st.session_state.user_id, st.session_state.chat_session_id)
        st.session_state.chat_messages = [
            {"role": m['role'], "content": m['content']} for m in saved
        ]

    # Sidebar chat history
    with st.sidebar:
        st.markdown("### 💬 Chat History")
        sessions = get_all_sessions(st.session_state.user_id)
        for sess in sessions[:5]:
            if st.button(f"📅 {sess['created_at'][:16]}", key=f"sess_{sess['id']}"):
                st.session_state.chat_session_id = sess['session_id']
                st.session_state.chat_messages = [
                    {"role": m['role'], "content": m['content']}
                    for m in get_chat_history(st.session_state.user_id, sess['session_id'])
                ]
                st.rerun()
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.chat_session_id = create_chat_session(st.session_state.user_id)
            st.session_state.chat_messages = []
            st.rerun()

    # Render chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Tell me your symptoms..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        save_chat_message(st.session_state.user_id, st.session_state.chat_session_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🩺 Dr. Well is analyzing..."):
                result = get_ai_response(prompt, st.session_state.chat_messages, st.session_state.chat_session_id)
                reply = result.get("response", "Please describe your symptoms so I can help!")

            placeholder = st.empty()
            full_reply = ""
            for chunk in stream_response(reply):
                full_reply += chunk
                placeholder.markdown(full_reply + "▌")
            placeholder.markdown(full_reply)

        st.session_state.chat_messages.append({"role": "assistant", "content": full_reply})
        save_chat_message(st.session_state.user_id, st.session_state.chat_session_id, "assistant", full_reply)

        # Show added medications
        for med in result.get("extracted_meds", []):
            if st.session_state.get(f"med_added_{med['name']}"):
                st.success(f"💊 **{med['name']}** added to your medications!")
                st.session_state.pop(f"med_added_{med['name']}", None)

        # Show doctor recommendations
        if st.session_state.get('show_doctor_recommendation'):
            st.markdown("### 👨‍⚕️ Recommended Specialists For You")
            for doc in st.session_state.show_doctor_recommendation:
                with st.expander(f"Dr. {doc.get('full_name')} — {doc.get('specialty')}"):
                    st.markdown(f"""
**🏥 Clinic:** {doc.get('clinic_name')}, {doc.get('city')}  
**💰 Fee:** ${doc.get('consultation_fee')}  
**📞 Phone:** {doc.get('phone')}  
**🕒 Available:** {doc.get('available_days')} | {doc.get('available_time_start')}–{doc.get('available_time_end')}
                    """)
                    if st.button(f"📅 Book with Dr. {doc.get('full_name')}", key=f"chat_rec_{doc['id']}"):
                        st.session_state[f"booking_open_{doc['id']}"] = True
                        st.rerun()

                # Show inline booking form if this doctor's button was clicked
                if st.session_state.get(f"booking_open_{doc['id']}"):
                    show_inline_booking_form(doc, f"chat_booking_form_{doc['id']}")

            st.session_state.show_doctor_recommendation = None

        st.rerun()


def nutrition():
    """Nutrition page — AI-powered."""
    st.markdown(
        '<div class="main-header"><h1>🍎 Smart Nutrition</h1>'
        '<p>Get personalized diet advice from NutriBot — powered by AI</p></div>',
        unsafe_allow_html=True
    )

    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"; st.rerun()

    if 'nutrition_messages' not in st.session_state:
        st.session_state.nutrition_messages = []

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    **🤖 NutriBot** — Tell me your health condition or ask any food/diet question!
    
    *Examples: "I have diabetes", "I want to lose weight", "What should I eat for high blood pressure?"*
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    for msg in st.session_state.nutrition_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if nutri_prompt := st.chat_input("Ask NutriBot about your diet..."):
        st.session_state.nutrition_messages.append({"role": "user", "content": nutri_prompt})
        with st.chat_message("user"):
            st.markdown(nutri_prompt)

        with st.chat_message("assistant"):
            with st.spinner("🥗 NutriBot is preparing your diet plan..."):
                from agent import run_agent
                result = run_agent(
                    user_message=nutri_prompt,
                    user_id=st.session_state.user_id,
                    session_id="nutrition",
                    history=st.session_state.nutrition_messages,
                    doctors_info="",
                    patient_info=get_patient_info_text(st.session_state.user_id)
                )
                reply = result.get("response", "Let me help you with your diet!")

            placeholder = st.empty()
            full_reply = ""
            for chunk in stream_response(reply):
                full_reply += chunk
                placeholder.markdown(full_reply + "▌")
            placeholder.markdown(full_reply)

        st.session_state.nutrition_messages.append({"role": "assistant", "content": full_reply})
        st.rerun()


def medications_page():
    st.markdown(
        '<div class="main-header"><h1>💊 My Medications</h1>'
        '<p>Auto-added from Dr. Well consultations</p></div>',
        unsafe_allow_html=True
    )
    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"; st.rerun()
    meds = get_medications(st.session_state.user_id)
    if meds:
        for m in meds:
            st.markdown(f"""
<div class="card">
    <h3 style="color:#1e5f6b;">💊 {m['name']}</h3>
    <p>
        <strong>Dosage:</strong> {m['dosage']}<br>
        <strong>Frequency:</strong> {m['frequency']}<br>
        <strong>Timing:</strong> {m['timing']}<br>
        <strong>Duration:</strong> {m['duration_days']} days<br>
        <strong>Food Advice:</strong> {m.get('food_restrictions', 'None')}<br>
        <strong>Prescribed by:</strong> {m['prescribed_by']}
    </p>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("No medications yet. Consult Dr. Well to get a prescription!")


def appointments_page():
    st.markdown(
        '<div class="main-header"><h1>📅 My Appointments</h1>'
        '<p>Your scheduled appointments</p></div>',
        unsafe_allow_html=True
    )
    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"; st.rerun()
    apts = get_appointments(st.session_state.user_id)
    if apts:
        for a in apts:
            status_color = "#27ae60" if a['status'] == 'Completed' else "#e67e22"
            st.markdown(f"""
<div class="card">
    <h3 style="color:#1e5f6b;">🏥 Dr. {a['doctor_name']}</h3>
    <p>
        <strong>Specialty:</strong> {a['specialty']}<br>
        <strong>Date:</strong> {a['date']} at {a['time']}<br>
        <strong>Status:</strong> <span style="color:{status_color}; font-weight:bold;">{a['status']}</span><br>
        <strong>Symptoms:</strong> {(a['symptoms'] or 'N/A')[:150]}
    </p>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("No appointments scheduled. Find a doctor and book one!")


def doctors_list_page():
    st.markdown(
        '<div class="main-header"><h1>👨‍⚕️ Find a Doctor</h1>'
        '<p>Browse verified specialists in our network</p></div>',
        unsafe_allow_html=True
    )
    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"; st.rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        specialty_filter = st.selectbox("Filter by Specialty", ["All"] + MEDICAL_SPECIALTIES)
    with col2:
        city_filter = st.text_input("Filter by City")
    with col3:
        sort_by = st.selectbox("Sort by", ["Rating", "Experience", "Fee"])

    doctors = get_all_doctors()
    if specialty_filter != "All":
        doctors = [d for d in doctors if d.get('specialty') == specialty_filter]
    if city_filter:
        doctors = [d for d in doctors if city_filter.lower() in d.get('city', '').lower()]
    if sort_by == "Rating":
        doctors.sort(key=lambda x: x.get('rating', 0), reverse=True)
    elif sort_by == "Experience":
        doctors.sort(key=lambda x: x.get('experience_years', 0), reverse=True)
    elif sort_by == "Fee":
        doctors.sort(key=lambda x: x.get('consultation_fee', 0))

    st.markdown(f"### Found {len(doctors)} Doctors")

    for doctor in doctors:
        # Show doctor card
        show_doctor_card_with_inline_booking(doctor)


def show_doctor_card_with_inline_booking(doctor: dict):
    """Show doctor card + inline booking form when book button is clicked."""
    from ui_components import show_doctor_card_ui

    doc_id = doctor['id']
    booking_key = f"booking_open_{doc_id}"

    # Render the card and get if book button was clicked
    book_clicked = show_doctor_card_ui(doctor)

    if book_clicked:
        # Toggle booking form
        if st.session_state.get(booking_key):
            st.session_state.pop(booking_key, None)
        else:
            st.session_state[booking_key] = True
        st.rerun()

    # Show inline booking form right below this card if toggled
    if st.session_state.get(booking_key):
        show_inline_booking_form(doctor, f"booking_form_{doc_id}")


def profile_page():
    user = get_user_by_id(st.session_state.user_id)
    st.markdown(
        '<div class="main-header"><h1>👤 My Profile</h1>'
        '<p>Update your information</p></div>',
        unsafe_allow_html=True
    )
    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"; st.rerun()
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", user.get('full_name', ''))
        email = st.text_input("Email", user.get('email', ''))
        phone = st.text_input("Phone", user.get('phone', ''))
    with col2:
        address = st.text_area("Address", user.get('address', ''))
        about = st.text_area("About", user.get('about', ''))
    if st.button("Update Profile", use_container_width=True):
        update_user_profile(st.session_state.user_id, full_name, phone, address, about)
        st.success("✅ Profile updated successfully!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────

def main():
    defaults = {
        'logged_in': False,
        'show_about': True,
        'page': "Dashboard",
        'show_doctor_recommendation': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if not st.session_state.logged_in:
        if st.session_state.show_about:
            show_about_page()
            _, col2, _ = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Get Started", use_container_width=True):
                    st.session_state.show_about = False; st.rerun()
            return

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        with tab1:
            result = show_login_ui()
            if result:
                user = authenticate_user(result['username'], result['password'])
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user['id']
                    st.session_state.user_type = user['user_type']
                    st.session_state.username = user['username']
                    st.rerun()
                else:
                    st.error("Invalid credentials. Try: test_patient / test123")
        with tab2:
            result = show_signup_ui()
            if result:
                uid = create_user(
                    result['username'], result['email'], result['password'],
                    result['user_type'], result['full_name'], result.get('phone', ''), '', ''
                )
                if uid:
                    st.success("Account created! Please login.")
                    st.rerun()
                else:
                    st.error("Username or email already exists.")
        return

    if not is_profile_complete(st.session_state.user_id):
        if st.session_state.user_type == 'doctor':
            result = show_doctor_info_form()
            if result:
                save_doctor_info(
                    st.session_state.user_id, result['specialty'], result['qualification'],
                    result['experience'], result['fee'], result['days'], result['start'],
                    result['end'], result['clinic_name'], result['clinic_address'],
                    result['city'], result['state'], result['zip_code'], result['phone'],
                    st.session_state.username, result['about']
                )
                st.success("Profile completed!"); st.rerun()
        else:
            result = show_patient_info_form()
            if result:
                save_patient_info(
                    st.session_state.user_id, result['weight'], result['height'],
                    result['allergies'], result['blood_group'], result['about']
                )
                st.success("Profile completed!"); st.rerun()
        return

    with st.sidebar:
        render_sidebar()

    page_map = {
        "Dashboard": dashboard,
        "Consultations": consultations,
        "Nutrition": nutrition,
        "Medications": medications_page,
        "Appointments": appointments_page,
        "Find Doctors": doctors_list_page,
        "Profile": profile_page,
    }
    page_fn = page_map.get(st.session_state.page, dashboard)
    page_fn()


if __name__ == "__main__":
    main()