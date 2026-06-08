# database.py
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = "drwell.db"

# Remove existing database to start fresh (optional - comment this out if you want to keep existing data)
if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                user_type TEXT CHECK(user_type IN ('patient', 'doctor')) NOT NULL,
                full_name TEXT,
                phone TEXT,
                address TEXT,
                about TEXT,
                medical_history TEXT,
                is_profile_complete BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Doctors info table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                specialty TEXT,
                qualification TEXT,
                experience_years INTEGER,
                consultation_fee REAL,
                available_days TEXT,
                available_time_start TEXT,
                available_time_end TEXT,
                clinic_name TEXT,
                clinic_address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                phone TEXT,
                email TEXT,
                rating REAL DEFAULT 4.5,
                total_reviews INTEGER DEFAULT 0,
                about TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Patients info
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                weight REAL,
                height REAL,
                allergies TEXT,
                blood_group TEXT,
                ongoing_conditions TEXT,
                current_medications TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Smart Medications table (auto-added)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                dosage TEXT,
                frequency TEXT,
                timing TEXT,
                duration_days INTEGER,
                food_restrictions TEXT,
                prescribed_by TEXT,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Chat Sessions (Memory)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Chat Memory (Full conversation history)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT,
                role TEXT,
                content TEXT,
                symptoms TEXT,
                diagnosis TEXT,
                medications TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Appointments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id INTEGER,
                doctor_name TEXT,
                specialty TEXT,
                date TEXT,
                time TEXT,
                status TEXT DEFAULT 'Pending',
                symptoms TEXT,
                diagnosis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Insert sample doctors
        doctors_data = [
            ("dr_smith", "smith@heartcare.com", "pass123", "doctor", "Sarah Smith", 
             "Cardiologist", "MBBS, MD Cardiology, FACC", 15, 250, 
             "Mon,Tue,Wed,Thu,Fri", "09:00", "17:00", 
             "Heart Care Clinic", "123 Medical Center", "New York", "NY", "10001",
             "+1 (212) 555-0100", "smith@heartcare.com", 4.9, 128,
             "Expert cardiologist. Specializes in heart attacks, chest pain, hypertension."),
            ("dr_khan", "khan@heart.com", "pass123", "doctor", "Ahmed Khan", 
             "Cardiologist", "MBBS, MD Cardiology", 12, 200, 
             "Mon,Tue,Wed,Thu,Fri,Sat", "10:00", "18:00", 
             "City Heart Institute", "456 Health Avenue", "Chicago", "IL", "60601",
             "+1 (312) 555-0200", "khan@heart.com", 4.8, 95,
             "Heart specialist. Expert in cardiac emergencies and preventive cardiology."),
            ("dr_johnson", "johnson@skin.com", "pass123", "doctor", "Michael Johnson", 
             "Dermatologist", "MBBS, MD Dermatology", 12, 180, 
             "Mon,Tue,Wed,Thu,Fri", "10:00", "18:00", 
             "Skin Care Center", "456 Health Ave", "Los Angeles", "CA", "90001",
             "+1 (310) 555-0300", "johnson@skin.com", 4.7, 87,
             "Skin specialist. Treats acne, eczema, psoriasis, and cosmetic issues."),
            ("dr_wilson", "wilson@neuro.com", "pass123", "doctor", "Emily Wilson", 
             "Neurologist", "MBBS, MD Neurology", 10, 220, 
             "Mon,Tue,Wed,Thu", "09:00", "16:00", 
             "Neuro Clinic", "789 Brain Street", "Chicago", "IL", "60001",
             "+1 (312) 555-0500", "wilson@neuro.com", 4.9, 203,
             "Brain specialist. Expert in headaches, migraines, epilepsy, stroke."),
            ("dr_patel", "patel@ortho.com", "pass123", "doctor", "Raj Patel", 
             "Orthopedic Surgeon", "MBBS, MS Orthopedics", 18, 300, 
             "Mon,Tue,Wed,Thu,Fri", "08:00", "15:00", 
             "Ortho Care", "321 Bone Road", "Houston", "TX", "77001",
             "+1 (713) 555-0700", "patel@ortho.com", 4.8, 312,
             "Bone and joint specialist. Expert in knee, back, and sports injuries."),
            ("dr_garcia", "garcia@pediatric.com", "pass123", "doctor", "Maria Garcia", 
             "Pediatrician", "MBBS, MD Pediatrics", 8, 150, 
             "Mon,Tue,Wed,Thu,Fri", "09:00", "17:00", 
             "Kids Care Clinic", "555 Children's Way", "Phoenix", "AZ", "85001",
             "+1 (602) 555-0900", "garcia@pediatric.com", 4.9, 234,
             "Child specialist. Expert in kids' health, vaccinations, development."),
            ("dr_ahmed", "ahmed@general.com", "pass123", "doctor", "Ahmed Hassan", 
             "General Physician", "MBBS", 20, 100, 
             "Mon,Tue,Wed,Thu,Fri,Sat", "09:00", "20:00", 
             "City Medical Center", "100 Main Street", "New York", "NY", "10001",
             "+1 (212) 555-1100", "ahmed@general.com", 4.6, 456,
             "Family doctor for all general health issues and routine checkups."),
        ]
        
        for doc in doctors_data:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password, user_type, full_name, about, is_profile_complete)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (doc[0], doc[1], doc[2], doc[3], doc[4], doc[18] if len(doc) > 18 else "Experienced doctor", 1))
            user_id = cursor.lastrowid
            
            if user_id:  # Only insert if user was created
                cursor.execute('''
                    INSERT OR IGNORE INTO doctors_info 
                    (user_id, specialty, qualification, experience_years, consultation_fee, 
                     available_days, available_time_start, available_time_end, 
                     clinic_name, clinic_address, city, state, zip_code, phone, email, rating, total_reviews, about)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, doc[5], doc[6], doc[7], doc[8], doc[9], doc[10], doc[11], 
                      doc[12], doc[13], doc[14], doc[15], doc[16], doc[17], doc[1], 
                      doc[19] if len(doc) > 19 else 4.8, doc[20] if len(doc) > 20 else 100, 
                      doc[21] if len(doc) > 21 else doc[18] if len(doc) > 18 else "Experienced medical professional"))
        
        # Test patient
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password, user_type, full_name, is_profile_complete)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("test_patient", "test@patient.com", "test123", "patient", "Test Patient", 1))

init_database()

# ========== USER FUNCTIONS ==========
def create_user(username, email, password, user_type, full_name=None, phone=None, address=None, about=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password, user_type, full_name, phone, address, about)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password, user_type, full_name, phone, address, about))
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

def authenticate_user(username, password):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?', 
                      (username, username, password))
        user = cursor.fetchone()
        return dict(user) if user else None

def get_user_by_id(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None

def update_user_profile(user_id, full_name, phone, address, about):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET full_name = ?, phone = ?, address = ?, about = ?, is_profile_complete = 1 WHERE id = ?
        ''', (full_name, phone, address, about, user_id))

def is_profile_complete(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT is_profile_complete FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        return result['is_profile_complete'] == 1 if result else False

# ========== DOCTOR FUNCTIONS ==========
def get_all_doctors():
    """Get all doctors with their complete information"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, d.* FROM users u
            JOIN doctors_info d ON u.id = d.user_id
            WHERE u.user_type = 'doctor'
            ORDER BY d.rating DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_doctors_by_specialty(specialty):
    """Get doctors filtered by specialty"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, d.* FROM users u
            JOIN doctors_info d ON u.id = d.user_id
            WHERE u.user_type = 'doctor' AND d.specialty = ?
            ORDER BY d.rating DESC
        ''', (specialty,))
        return [dict(row) for row in cursor.fetchall()]

def get_doctor_by_id(doctor_id):
    """Get single doctor by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, d.* FROM users u
            JOIN doctors_info d ON u.id = d.user_id
            WHERE u.user_type = 'doctor' AND u.id = ?
        ''', (doctor_id,))
        result = cursor.fetchone()
        return dict(result) if result else None

def save_doctor_info(user_id, specialty, qualification, experience, fee, days, time_start, time_end, 
                     clinic_name, clinic_address, city, state, zip_code, phone, email, about):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO doctors_info 
            (user_id, specialty, qualification, experience_years, consultation_fee, 
             available_days, available_time_start, available_time_end, 
             clinic_name, clinic_address, city, state, zip_code, phone, email, about)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, specialty, qualification, experience, fee, days, time_start, time_end, 
              clinic_name, clinic_address, city, state, zip_code, phone, email, about))
        cursor.execute('UPDATE users SET about = ?, is_profile_complete = 1 WHERE id = ?', (about, user_id))

# ========== CHAT MEMORY FUNCTIONS ==========
def create_chat_session(user_id):
    import uuid
    session_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_sessions (user_id, session_id)
            VALUES (?, ?)
        ''', (user_id, session_id))
    return session_id

def get_chat_history(user_id, session_id=None, limit=50):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if session_id:
            cursor.execute('''
                SELECT * FROM chat_memory 
                WHERE user_id = ? AND session_id = ?
                ORDER BY created_at ASC
                LIMIT ?
            ''', (user_id, session_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM chat_memory 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
        return [dict(row) for row in cursor.fetchall()]

def save_chat_message(user_id, session_id, role, content, symptoms=None, diagnosis=None, medications=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_memory (user_id, session_id, role, content, symptoms, diagnosis, medications)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, session_id, role, content, symptoms, diagnosis, medications))

def get_all_sessions(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, session_id, created_at FROM chat_sessions 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        return [dict(row) for row in cursor.fetchall()]

# ========== PATIENT FUNCTIONS ==========
def save_patient_info(user_id, weight, height, allergies, blood_group, about):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO patients_info (user_id, weight, height, allergies, blood_group)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, weight, height, allergies, blood_group))
        cursor.execute('UPDATE users SET about = ?, is_profile_complete = 1 WHERE id = ?', (about, user_id))

def get_patient_info(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients_info WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return dict(result) if result else None

# ========== SMART MEDICATION FUNCTIONS ==========
def save_medication(user_id, name, dosage, frequency, timing, duration_days, food_restrictions, prescribed_by):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medications (user_id, name, dosage, frequency, timing, duration_days, food_restrictions, prescribed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, dosage, frequency, timing, duration_days, food_restrictions, prescribed_by))
        return cursor.lastrowid

def get_medications(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM medications WHERE user_id = ? AND status = "Active" ORDER BY created_at DESC', (user_id,))
        return [dict(row) for row in cursor.fetchall()]

def update_medication_status(medication_id, status):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE medications SET status = ? WHERE id = ?', (status, medication_id))

# ========== APPOINTMENT FUNCTIONS ==========
def save_appointment(patient_id, doctor_id, doctor_name, specialty, date, time, symptoms, diagnosis):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, doctor_name, specialty, date, time, symptoms, diagnosis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, doctor_name, specialty, date, time, symptoms, diagnosis))
        return cursor.lastrowid

def get_appointments(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments WHERE patient_id = ? ORDER BY date DESC', (user_id,))
        return [dict(row) for row in cursor.fetchall()]

def update_appointment_status(appointment_id, status):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE appointments SET status = ? WHERE id = ?', (status, appointment_id))

# ========== UTILITY FUNCTIONS ==========
def check_database():
    """Get database statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM doctors_info")
        doctors = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM medications")
        medications = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM appointments")
        appointments = cursor.fetchone()[0]
        return {
            "users": users, 
            "doctors": doctors,
            "medications": medications,
            "appointments": appointments
        }

def search_doctors(query):
    """Search doctors by name, specialty, or city"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, d.* FROM users u
            JOIN doctors_info d ON u.id = d.user_id
            WHERE u.user_type = 'doctor' 
            AND (u.full_name LIKE ? OR d.specialty LIKE ? OR d.city LIKE ?)
            ORDER BY d.rating DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

# ========== EXPORT ALL FUNCTIONS ==========
__all__ = [
    'get_db_connection',
    'init_database',
    'create_user',
    'authenticate_user',
    'get_user_by_id',
    'update_user_profile',
    'is_profile_complete',
    'get_all_doctors',
    'get_doctors_by_specialty',
    'get_doctor_by_id',
    'save_doctor_info',
    'create_chat_session',
    'get_chat_history',
    'save_chat_message',
    'get_all_sessions',
    'save_patient_info',
    'get_patient_info',
    'save_medication',
    'get_medications',
    'update_medication_status',
    'save_appointment',
    'get_appointments',
    'update_appointment_status',
    'check_database',
    'search_doctors'
]