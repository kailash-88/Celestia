"""
MediMitra Database Seeder - Multi-Role Healthcare System
Populates comprehensive demonstration data across all 4 roles:
1. Patient (Ramesh Sharma): profile, medicines, schedules, dose logs, queries
2. Doctor (Dr. Ananya Roy): verified cardiologist, assigned patients, pending prescription reviews, queries
3. Caregiver (Priya Sharma): linked to patient, adherence tracking, alerts
4. Admin (Admin User): verified doctor profiles, master medicine database, system logs
"""

import json
import os
import sys
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from database.db import get_connection, init_db


def seed():
    print("[Seed] Initializing database schema...")
    init_db()

    conn = get_connection()
    cur = conn.cursor()

    print("[Seed] Clearing old demo data...")
    tables = [
        "system_logs", "patient_queries", "patient_profiles", "medicine_database",
        "prescription_reviews", "prescriptions", "dose_logs", "schedules",
        "safety_alerts", "medicines", "caregiver_links", "doctor_profiles", "pharmacy_profiles", "users"
    ]
    for table in tables:
        try:
            cur.execute(f"DELETE FROM {table}")
        except Exception as e:
            pass

    print("[Seed] Creating demo users across all 4 roles...")
    password_hash = generate_password_hash("password123")

    # 1. Patient
    cur.execute(
        """INSERT INTO users (username, email, password_hash, full_name, role, phone, is_active)
           VALUES (?, ?, ?, ?, ?, ?, 1)""",
        ("patient_demo", "patient@example.com", password_hash, "Ramesh Sharma", "patient", "+91 98765 43210")
    )
    patient_id = cur.lastrowid

    # 2. Doctor
    cur.execute(
        """INSERT INTO users (username, email, password_hash, full_name, role, phone, is_active)
           VALUES (?, ?, ?, ?, ?, ?, 1)""",
        ("doctor_demo", "doctor@example.com", password_hash, "Dr. Ananya Roy", "doctor", "+91 98765 11223")
    )
    doctor_id = cur.lastrowid

    # Doctor Profile (Verified)
    cur.execute(
        """INSERT INTO doctor_profiles (user_id, specialty, license_number, qualifications, verification_status, verified_at)
           VALUES (?, ?, ?, ?, 'verified', CURRENT_TIMESTAMP)""",
        (doctor_id, "Cardiology & Internal Medicine", "MCI-2018-847291", "MBBS, MD (Medicine), DM (Cardiology)")
    )

    # 2b. Doctor 2 (Pending Verification for Admin demo)
    cur.execute(
        """INSERT INTO users (username, email, password_hash, full_name, role, phone, is_active)
           VALUES (?, ?, ?, ?, ?, ?, 1)""",
        ("dr_verma", "drverma@example.com", password_hash, "Dr. Rajesh Verma", "doctor", "+91 98765 99887")
    )
    dr_verma_id = cur.lastrowid
    cur.execute(
        """INSERT INTO doctor_profiles (user_id, specialty, license_number, qualifications, verification_status)
           VALUES (?, ?, ?, ?, 'pending')""",
        (dr_verma_id, "General Practice & Diabetology", "DMC-2021-394812", "MBBS, DNB (Family Medicine)")
    )

    # 3. Caregiver
    cur.execute(
        """INSERT INTO users (username, email, password_hash, full_name, role, phone, is_active)
           VALUES (?, ?, ?, ?, ?, ?, 1)""",
        ("caregiver_demo", "caregiver@example.com", password_hash, "Priya Sharma", "caregiver", "+91 98765 43211")
    )
    caregiver_id = cur.lastrowid

    # 4. Admin
    cur.execute(
        """INSERT INTO users (username, email, password_hash, full_name, role, phone, is_active)
           VALUES (?, ?, ?, ?, ?, ?, 1)""",
        ("admin_demo", "admin@example.com", password_hash, "MediMitra Administrator", "admin", "+91 98765 00001")
    )
    admin_id = cur.lastrowid

    print("[Seed] Linking caregiver to patient...")
    cur.execute(
        """INSERT INTO caregiver_links (caregiver_id, patient_id, status)
           VALUES (?, ?, 'active')""",
        (caregiver_id, patient_id)
    )

    print("[Seed] Adding patient profile (allergies, conditions, emergency contact)...")
    cur.execute(
        """INSERT INTO patient_profiles 
           (user_id, age, gender, blood_group, allergies, conditions, emergency_contact_name, emergency_contact_phone, emergency_contact_relation)
           VALUES (?, 64, 'Male', 'B+', 'Penicillin, Sulfa drugs', 'Type 2 Diabetes, Hypertension, Mild Coronary Artery Disease', 'Priya Sharma (Daughter)', '+91 98765 43211', 'Daughter')""",
        (patient_id,)
    )

    print("[Seed] Adding Master Medicine Knowledgebase...")
    master_medicines = [
        (
            "Metformin", "Metformin Hydrochloride", "Antidiabetic", "Tablet", "500mg, 850mg, 1000mg",
            "Take with or immediately after meals",
            "Controls blood glucose in type 2 diabetes by decreasing hepatic glucose production.",
            "Nausea, diarrhea, stomach upset, metallic taste.",
            "Risk of lactic acidosis; avoid excessive alcohol.",
            "Iodinated contrast media, alcohol, cimetidine"
        ),
        (
            "Ecosprin", "Aspirin", "Antiplatelet / NSAID", "Tablet", "75mg, 150mg",
            "Take strictly after food with plenty of water",
            "Prevents blood clots, heart attacks, and secondary cardiovascular events.",
            "Heartburn, nausea, gastric bleeding, bruising.",
            "Do not take with other blood thinners or NSAIDs without supervision.",
            "Warfarin, Ibuprofen, Heparin, SSRIs"
        ),
        (
            "Warfarin", "Warfarin Sodium", "Anticoagulant", "Tablet", "2mg, 5mg",
            "Take at the same time each evening with or without food",
            "Prevents blood clots in deep veins, pulmonary embolism, and atrial fibrillation.",
            "Excessive bleeding, prolonged bruising, red or dark brown urine.",
            "Requires routine INR blood monitoring. High vitamin K foods alter efficacy.",
            "Aspirin, Clopidogrel, NSAIDs, broad-spectrum antibiotics, St. John's wort"
        ),
        (
            "Telma 40", "Telmisartan", "Antihypertensive (ARB)", "Tablet", "40mg, 80mg",
            "Take with or without food, preferably same time every morning",
            "Lowers high blood pressure and protects kidneys in diabetic patients.",
            "Dizziness, lightheadedness, sinus pain, back pain.",
            "Do not use during pregnancy. Monitor serum potassium levels.",
            "Potassium supplements, ACE inhibitors, Lithium, NSAIDs"
        ),
        (
            "Amoxyclav 625", "Amoxicillin + Potassium Clavulanate", "Antibiotic", "Tablet", "625mg",
            "Take at the start of a meal to reduce gastrointestinal discomfort",
            "Treats bacterial infections of ear, nose, throat, respiratory tract, and skin.",
            "Diarrhea, skin rash, nausea, fungal overgrowth.",
            "Complete full prescribed course even if symptoms subside. Contraindicated in penicillin allergy.",
            "Methotrexate, Allopurinol, Oral contraceptives, Probenecid"
        ),
        (
            "Pantocid 40", "Pantoprazole", "Proton Pump Inhibitor (PPI)", "Tablet", "40mg",
            "Take 30-60 minutes before breakfast on an empty stomach",
            "Reduces stomach acid, treats GERD, acid reflux, and prevents gastric ulcers.",
            "Headache, mild diarrhea, flatulence, abdominal pain.",
            "Long-term use may reduce magnesium and vitamin B12 absorption.",
            "Atazanavir, Clopidogrel, Ketoconazole, Iron salts"
        ),
        (
            "Atorva 10", "Atorvastatin", "Statin / Lipid Lowering", "Tablet", "10mg, 20mg, 40mg",
            "Take once daily in the evening, with or without food",
            "Lowers LDL cholesterol and triglycerides to prevent heart attacks and strokes.",
            "Muscle aches, mild liver enzyme elevation, joint pain.",
            "Report unexplained muscle pain or weakness immediately. Avoid grapefruit juice.",
            "Clarithromycin, Cyclosporine, Gemfibrozil, Itraconazole"
        ),
        (
            "Dolo 650", "Paracetamol / Acetaminophen", "Analgesic & Antipyretic", "Tablet", "650mg",
            "Take after food with water",
            "Relieves mild to moderate pain and reduces fever.",
            "Rare when taken as directed. Overuse causes severe liver toxicity.",
            "Do not exceed 4,000mg per day. Check other combination cold medicines.",
            "Warfarin (chronic high dose), Alcohol, Isoniazid"
        ),
    ]

    cur.executemany(
        """INSERT INTO medicine_database 
           (name, generic_name, category, dosage_form, standard_strength, before_after_food, common_uses, side_effects, warnings, known_interactions)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        master_medicines
    )

    print("[Seed] Adding patient medicines...")
    sample_medicines = [
        (
            patient_id, "Metformin 500mg", "Metformin Hydrochloride", "500mg", "Tablet",
            "Sun Pharma", json.dumps(["metformin"]), "Type 2 Diabetes Blood Sugar Control",
            "Take with meals to reduce stomach upset.", "2028-12-31", 45, "manual", 1,
            "Take with meals"
        ),
        (
            patient_id, "Ecosprin 75", "Aspirin", "75mg", "Tablet",
            "USV", json.dumps(["aspirin"]), "Blood thinner & cardiovascular prevention",
            "Take after food. May cause mild gastric irritation.", "2027-10-15", 28, "manual", 1,
            "After food"
        ),
        (
            patient_id, "Warf 2mg", "Warfarin Sodium", "2mg", "Tablet",
            "Cipla", json.dumps(["warfarin"]), "Anticoagulant / Prevention of blood clots",
            "Strict dosage timing. Monitor INR levels regularly.", "2027-08-20", 14, "manual", 1,
            "Same time in evening"
        ),
        (
            patient_id, "Telma 40", "Telmisartan", "40mg", "Tablet",
            "Glenmark", json.dumps(["telmisartan"]), "Hypertension & Blood Pressure Control",
            "Take once daily at the same time every morning.", "2027-11-30", 3, "manual", 1,  # Low stock: 3 left!
            "Morning before/after food"
        ),
        (
            patient_id, "Amoxyclav 625", "Amoxicillin + Clavulanate", "625mg", "Tablet",
            "Abbott", json.dumps(["amoxicillin", "clavulanate"]), "Bacterial Infection Treatment",
            "Complete full course as prescribed.", "2023-05-10", 6, "scan", 1,  # Expired
            "Start of meal"
        ),
    ]

    cur.executemany(
        """INSERT INTO medicines 
           (user_id, name, generic_name, dosage, form, manufacturer, active_ingredients, 
            purpose, warnings, expiry_date, quantity, source, verified, before_after_food)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        sample_medicines
    )

    cur.execute("SELECT id, name FROM medicines WHERE user_id = ?", (patient_id,))
    med_rows = {row["name"]: row["id"] for row in cur.fetchall()}

    print("[Seed] Creating daily schedules...")
    schedules = [
        (patient_id, med_rows["Telma 40"], "morning", "08:00", "1 Tablet", "Before breakfast", date.today().isoformat(), None, 1),
        (patient_id, med_rows["Metformin 500mg"], "morning", "08:30", "1 Tablet", "With breakfast", date.today().isoformat(), None, 1),
        (patient_id, med_rows["Metformin 500mg"], "night", "20:30", "1 Tablet", "With dinner", date.today().isoformat(), None, 1),
        (patient_id, med_rows["Ecosprin 75"], "evening", "19:30", "1 Tablet", "After dinner", date.today().isoformat(), None, 1),
        (patient_id, med_rows["Warf 2mg"], "evening", "20:00", "1 Tablet", "Fixed time after meal", date.today().isoformat(), None, 1),
    ]

    schedule_ids = []
    for s in schedules:
        cur.execute(
            """INSERT INTO schedules 
               (user_id, medicine_id, time_of_day, scheduled_time, dosage_amount, instructions, start_date, end_date, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            s
        )
        schedule_ids.append(cur.lastrowid)

    print("[Seed] Generating past and current dose logs...")
    today = date.today()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    logs = [
        # Two days ago
        (schedule_ids[0], patient_id, "taken", f"{two_days_ago} 08:00:00", f"{two_days_ago} 08:05:00", None),
        (schedule_ids[1], patient_id, "taken", f"{two_days_ago} 08:30:00", f"{two_days_ago} 08:35:00", None),
        (schedule_ids[2], patient_id, "taken", f"{two_days_ago} 20:30:00", f"{two_days_ago} 20:40:00", None),
        # Yesterday
        (schedule_ids[0], patient_id, "taken", f"{yesterday} 08:00:00", f"{yesterday} 08:12:00", None),
        (schedule_ids[1], patient_id, "taken", f"{yesterday} 08:30:00", f"{yesterday} 08:32:00", None),
        (schedule_ids[2], patient_id, "missed", f"{yesterday} 20:30:00", None, "Fell asleep early"),
        (schedule_ids[3], patient_id, "taken", f"{yesterday} 19:30:00", f"{yesterday} 19:45:00", None),
        # Today
        (schedule_ids[0], patient_id, "taken", f"{today} 08:00:00", f"{today} 08:02:00", None),
        (schedule_ids[1], patient_id, "taken", f"{today} 08:30:00", f"{today} 08:31:00", None),
        (schedule_ids[2], patient_id, "pending", f"{today} 20:30:00", None, None),
        (schedule_ids[3], patient_id, "pending", f"{today} 19:30:00", None, None),
        (schedule_ids[4], patient_id, "pending", f"{today} 20:00:00", None, None),
    ]

    cur.executemany(
        """INSERT INTO dose_logs (schedule_id, user_id, status, scheduled_for, taken_at, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        logs
    )

    print("[Seed] Inserting safety alerts...")
    alerts = [
        (
            patient_id, "interaction", "high", "Drug Interaction: Warfarin + Aspirin",
            "Concurrent use of Warfarin and Aspirin significantly increases bleeding risks. Consult your physician immediately.",
            json.dumps(["Warf 2mg", "Ecosprin 75"]), 0
        ),
        (
            patient_id, "expiry", "medium", "Expired Medicine Detected: Amoxyclav 625",
            "Amoxyclav 625 expired on 2023-05-10. Do not consume expired antibiotics; dispose safely.",
            json.dumps(["Amoxyclav 625"]), 0
        ),
    ]

    cur.executemany(
        """INSERT INTO safety_alerts (user_id, alert_type, severity, title, description, medicine_ids, is_dismissed)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        alerts
    )

    print("[Seed] Creating sample prescription for Doctor Review & Approval workflow...")
    extracted_prescription_data = json.dumps({
        "doctor_name": "Dr. Ananya Roy",
        "hospital_name": "Apollo Heart Institute",
        "prescription_date": today.isoformat(),
        "medicines": [
            {
                "name": "Atorva 10",
                "dosage": "10mg",
                "form": "Tablet",
                "frequency": "Once daily at night",
                "instructions": "After dinner",
                "duration": "30 days"
            },
            {
                "name": "Pantocid 40",
                "dosage": "40mg",
                "form": "Tablet",
                "frequency": "Once daily in the morning",
                "instructions": "30 minutes before breakfast",
                "duration": "14 days"
            }
        ],
        "notes": "Patient reports mild chest discomfort and acidity. Cholesterol panel requested."
    })

    # Create dummy prescription image file if needed
    os.makedirs("d:/Celestia/MediMitra/uploads", exist_ok=True)
    sample_img_path = "d:/Celestia/MediMitra/uploads/sample_prescription.jpg"
    if not os.path.exists(sample_img_path):
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (600, 800), color=(250, 250, 250))
        d = ImageDraw.Draw(img)
        d.text((40, 40), "APOLLO HOSPITALS - PRESCRIPTION", fill=(20, 20, 20))
        d.text((40, 80), f"Doctor: Dr. Ananya Roy, MD Cardiology", fill=(50, 50, 50))
        d.text((40, 110), f"Patient: Ramesh Sharma (Age 64, Male)", fill=(50, 50, 50))
        d.text((40, 160), "Rx:", fill=(10, 10, 10))
        d.text((60, 200), "1. Tab. Atorva 10mg - 1 OD (Night) x 30 days", fill=(20, 20, 20))
        d.text((60, 240), "2. Tab. Pantocid 40mg - 1 OD (Empty stomach) x 14 days", fill=(20, 20, 20))
        d.text((40, 320), "Advice: Low salt diet, monitor lipid profile.", fill=(50, 50, 50))
        img.save(sample_img_path)

    cur.execute(
        """INSERT INTO prescriptions 
           (user_id, image_path, raw_ocr_text, extracted_data, doctor_name, hospital_name, 
            status, assigned_doctor_id, patient_confirmed_at)
           VALUES (?, ?, ?, ?, ?, ?, 'under_review', ?, CURRENT_TIMESTAMP)""",
        (
            patient_id, sample_img_path,
            "APOLLO HOSPITALS\nDr. Ananya Roy\nRx Atorva 10mg Pantocid 40mg",
            extracted_prescription_data, "Dr. Ananya Roy", "Apollo Heart Institute",
            doctor_id
        )
    )

    print("[Seed] Creating sample Patient Health Queries for Doctor...")
    cur.execute(
        """INSERT INTO patient_queries
           (patient_id, doctor_id, subject, question, status, escalated_from_ai, created_at)
           VALUES (?, ?, ?, ?, 'pending', 1, CURRENT_TIMESTAMP)""",
        (
            patient_id, doctor_id,
            "Dizziness after taking Telma 40",
            "Hello Doctor, I noticed mild dizziness about an hour after taking my Telma 40 morning tablet. Should I change the timing or continue?",
        )
    )
    cur.execute(
        """INSERT INTO patient_queries
           (patient_id, doctor_id, subject, question, status, doctor_response, answered_at, created_at)
           VALUES (?, ?, ?, ?, 'answered', ?, CURRENT_TIMESTAMP, datetime('now', '-2 days'))""",
        (
            patient_id, doctor_id,
            "Can I take Metformin before food?",
            "Can I take Metformin on an empty stomach if I am running late for breakfast?",
            "Always take Metformin with or immediately after food. Taking it on an empty stomach frequently triggers stomach cramps, nausea, or diarrhea. If you are delayed, take it with a light snack.",
        )
    )

    print("[Seed] Recording system audit logs...")
    cur.execute(
        """INSERT INTO system_logs (user_id, event_type, status, details)
           VALUES (?, 'system_init', 'success', 'MediMitra database initialized with multi-role demonstration dataset')""",
        (admin_id,)
    )

    conn.commit()
    conn.close()

    print("\n" + "="*50)
    print(" MediMitra Multi-Role Seed Complete!")
    print("="*50)
    print(" 1. Patient:   username='patient_demo',   password='password123'")
    print(" 2. Doctor:    username='doctor_demo',    password='password123'")
    print(" 3. Caregiver: username='caregiver_demo', password='password123'")
    print(" 4. Admin:     username='admin_demo',     password='password123'")
    print("="*50 + "\n")


if __name__ == "__main__":
    seed()
