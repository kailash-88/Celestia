-- MediMitra Database Schema
-- Users table for authentication

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'patient',  -- 'patient', 'doctor', 'caregiver', 'admin', 'pharmacist'
    phone TEXT,
    language TEXT DEFAULT 'en',
    auto_camera INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Caregiver-patient relationships
CREATE TABLE IF NOT EXISTS caregiver_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caregiver_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'active', 'revoked'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (caregiver_id) REFERENCES users(id),
    FOREIGN KEY (patient_id) REFERENCES users(id),
    UNIQUE(caregiver_id, patient_id)
);

-- Professional accounts remain unable to review until an administrator verifies them.
CREATE TABLE IF NOT EXISTS doctor_profiles (
    user_id INTEGER PRIMARY KEY,
    specialty TEXT NOT NULL,
    license_number TEXT NOT NULL,
    qualifications TEXT,
    verification_status TEXT NOT NULL DEFAULT 'pending',
    verified_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS pharmacy_profiles (
    user_id INTEGER PRIMARY KEY,
    pharmacy_name TEXT NOT NULL,
    license_number TEXT NOT NULL,
    verification_status TEXT NOT NULL DEFAULT 'pending',
    verified_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Medicines added by users
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    generic_name TEXT,
    dosage TEXT,
    form TEXT,           -- tablet, capsule, syrup, injection, etc.
    manufacturer TEXT,
    batch_number TEXT,
    manufacturing_date DATE,
    active_ingredients TEXT,  -- JSON array
    purpose TEXT,
    side_effects TEXT,        -- JSON array
    warnings TEXT,
    expiry_date DATE,
    quantity INTEGER DEFAULT 0,
    image_path TEXT,
    prescription_id INTEGER,
    source TEXT DEFAULT 'manual',  -- 'manual', 'scan', 'prescription'
    verified INTEGER DEFAULT 0,    -- human-confirmed flag
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
);

-- Prescription scans
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    raw_ocr_text TEXT,
    extracted_data TEXT,    -- JSON of parsed prescription
    doctor_name TEXT,
    hospital_name TEXT,
    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'uploaded',
    assigned_doctor_id INTEGER,
    patient_confirmed_at TIMESTAMP,
    approved_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS prescription_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    comments TEXT,
    extracted_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);

-- Medicine schedules
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    time_of_day TEXT NOT NULL,       -- 'morning', 'afternoon', 'evening', 'night'
    scheduled_time TIME NOT NULL,
    dosage_amount TEXT,
    instructions TEXT,               -- 'before food', 'after food', etc.
    start_date DATE NOT NULL,
    end_date DATE,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);

-- Dose tracking / adherence log
CREATE TABLE IF NOT EXISTS dose_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'taken', 'missed', 'skipped', 'pending'
    scheduled_for TIMESTAMP NOT NULL,
    taken_at TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (schedule_id) REFERENCES schedules(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Safety alerts (interaction warnings, duplicates, expiry)
CREATE TABLE IF NOT EXISTS safety_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,    -- 'interaction', 'duplicate', 'expiry', 'allergy'
    severity TEXT NOT NULL,      -- 'low', 'medium', 'high', 'critical'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    medicine_ids TEXT,           -- JSON array of related medicine IDs
    is_dismissed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


-- Patient health profiles (allergies, conditions, emergency contact)
CREATE TABLE IF NOT EXISTS patient_profiles (
    user_id INTEGER PRIMARY KEY,
    age INTEGER,
    gender TEXT,
    blood_group TEXT,
    allergies TEXT,
    conditions TEXT,
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    emergency_contact_relation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Patient Health Queries (Patient to Doctor communication & AI Escalations)
CREATE TABLE IF NOT EXISTS patient_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER,
    subject TEXT NOT NULL,
    question TEXT NOT NULL,
    image_path TEXT,
    prescription_id INTEGER,
    status TEXT DEFAULT 'pending',
    doctor_response TEXT,
    doctor_notes TEXT,
    escalated_from_ai INTEGER DEFAULT 0,
    answered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);

-- Master Verified Medicine Knowledgebase (for Indian & Global medicines)
CREATE TABLE IF NOT EXISTS medicine_database (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    generic_name TEXT,
    category TEXT,
    dosage_form TEXT,
    standard_strength TEXT,
    before_after_food TEXT,
    common_uses TEXT,
    side_effects TEXT,
    warnings TEXT,
    known_interactions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System & AI Security Audit Logs
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


-- App Releases and In-App / SMS Update Broadcasts
CREATE TABLE IF NOT EXISTS app_releases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_code INTEGER NOT NULL,
    version_name TEXT NOT NULL,
    release_notes TEXT NOT NULL,
    force_update INTEGER DEFAULT 0,
    download_url TEXT,
    released_by INTEGER,
    sms_broadcast_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (released_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    notification_type TEXT DEFAULT 'system',
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
