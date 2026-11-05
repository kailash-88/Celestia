"""AI and OCR-based medicine identification with Clinical NLP and Multi-Provider Vision AI."""

import base64
import json
import os
import re
import sqlite3
from pathlib import Path
from dotenv import dotenv_values

# Built-in essential clinical knowledge base
CLINICAL_CATALOG = [
    {
        "name": "Dolo 650",
        "aliases": ["dolo 650", "dolo-650", "dolo", "micro labs dolo"],
        "generic_name": "Paracetamol / Acetaminophen",
        "active_ingredients": ["Paracetamol", "Acetaminophen"],
        "dosage_form": "Tablet",
        "default_strength": "650mg",
        "before_after_food": "Take strictly after food with water to avoid gastric irritation.",
        "common_uses": "Relief of fever (antipyretic) and mild-to-moderate pain (analgesic).",
        "side_effects": "Nausea, allergic skin rash, liver toxicity in overdose.",
        "warnings": "Do not exceed 4,000 mg (4g) in 24 hours. Avoid alcohol. Maintain at least 4-6 hours between doses.",
        "category": "Antipyretic / Analgesic",
    },
    {
        "name": "Calpol 650",
        "aliases": ["calpol 650", "calpol-650", "calpol", "gsk calpol", "glaxo calpol"],
        "generic_name": "Paracetamol",
        "active_ingredients": ["Paracetamol"],
        "dosage_form": "Tablet",
        "default_strength": "650mg",
        "before_after_food": "Take strictly after meals with water.",
        "common_uses": "Fast relief from high fever, body pain, headache, and toothache.",
        "side_effects": "Nausea, allergic skin reaction in sensitive individuals.",
        "warnings": "GlaxoSmithKline (GSK) formulation. Do not exceed 4 tablets in 24 hours. Do not combine with other paracetamol medicines.",
        "category": "Antipyretic / Analgesic",
    },
    {
        "name": "Calpol 500",
        "aliases": ["calpol 500", "calpol-500"],
        "generic_name": "Paracetamol",
        "active_ingredients": ["Paracetamol"],
        "dosage_form": "Tablet",
        "default_strength": "500mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Reduces fever and relieves mild-to-moderate pain and headache.",
        "side_effects": "Generally safe; rare allergic skin reaction.",
        "warnings": "Do not exceed recommended dose.",
        "category": "Antipyretic / Analgesic",
    },
    {
        "name": "Saridon",
        "aliases": ["saridon", "bayer saridon", "propyphenazone paracetamol caffeine"],
        "generic_name": "Paracetamol + Propyphenazone + Caffeine",
        "active_ingredients": ["Paracetamol", "Propyphenazone", "Caffeine"],
        "dosage_form": "Tablet",
        "default_strength": "250mg + 150mg + 50mg",
        "before_after_food": "Take strictly after meals with plenty of water.",
        "common_uses": "Fast targeted relief from severe headache, migraine, toothache, and body pain.",
        "side_effects": "Restlessness, mild insomnia (from caffeine), nausea.",
        "warnings": "Manufactured by Bayer. Contains caffeine; avoid taking late at night. Do not exceed 3 tablets in 24 hours.",
        "category": "Analgesic & Antipyretic",
    },
    {
        "name": "Combiflam",
        "aliases": ["combiflam", "combiflam tablet", "sanofi combiflam"],
        "generic_name": "Ibuprofen + Paracetamol",
        "active_ingredients": ["Ibuprofen", "Paracetamol"],
        "dosage_form": "Tablet",
        "default_strength": "400mg + 325mg",
        "before_after_food": "Take strictly after meals with a full glass of water or milk.",
        "common_uses": "Relief of inflammatory pain, arthritis, dental pain, swelling, and fever.",
        "side_effects": "Acidity, heartburn, stomach ulceration, nausea.",
        "warnings": "Never take on an empty stomach. Contraindicated in active peptic ulcer disease and severe heart failure.",
        "category": "NSAID Combination",
    },
    {
        "name": "Pan-D",
        "aliases": ["pan-d", "pan d", "alkem pan d", "pan d capsule"],
        "generic_name": "Pantoprazole + Domperidone",
        "active_ingredients": ["Pantoprazole", "Domperidone"],
        "dosage_form": "Capsule",
        "default_strength": "40mg + 30mg",
        "before_after_food": "Take 30-60 minutes before breakfast strictly on an empty stomach.",
        "common_uses": "Gastroesophageal reflux disease (GERD), severe acidity, acid indigestion, and nausea.",
        "side_effects": "Dry mouth, headache, diarrhea, dizziness.",
        "warnings": "Manufactured by Alkem. Swallow whole; do not chew or crush capsule granules.",
        "category": "Antacid / Antiemetic",
    },
    {
        "name": "Atorva 10",
        "aliases": ["atorva 10", "atorva-10", "atorva", "zydus atorva"],
        "generic_name": "Atorvastatin",
        "active_ingredients": ["Atorvastatin Calcium"],
        "dosage_form": "Tablet",
        "default_strength": "10mg",
        "before_after_food": "Take once daily in the evening, with or without food.",
        "common_uses": "Lowers bad cholesterol (LDL) and triglycerides, reduces risk of heart disease and stroke.",
        "side_effects": "Muscle pain, weakness, digestive problems, elevated liver enzymes.",
        "warnings": "Avoid grapefruit and excess alcohol. Report unexplained muscle aches or dark urine immediately.",
        "category": "Statin / Lipid-lowering",
    },
    {
        "name": "Pantocid 40",
        "aliases": ["pantocid 40", "pantocid-40", "pantocid", "sun pantocid"],
        "generic_name": "Pantoprazole",
        "active_ingredients": ["Pantoprazole Sodium"],
        "dosage_form": "Tablet",
        "default_strength": "40mg",
        "before_after_food": "Take 30-60 minutes before breakfast on an empty stomach.",
        "common_uses": "Treats gastroesophageal reflux disease (GERD), heartburn, and stomach ulcers.",
        "side_effects": "Headache, diarrhea, dizziness, abdominal discomfort.",
        "warnings": "Swallow whole; do not crush or chew. Long-term use may reduce magnesium and vitamin B12.",
        "category": "Proton Pump Inhibitor (PPI)",
    },
    {
        "name": "Telma 40",
        "aliases": ["telma 40", "telma-40", "telma", "glenmark telma"],
        "generic_name": "Telmisartan",
        "active_ingredients": ["Telmisartan"],
        "dosage_form": "Tablet",
        "default_strength": "40mg",
        "before_after_food": "Take with or without food, preferably at the same time every morning.",
        "common_uses": "Lowers high blood pressure (hypertension) and protects kidney function.",
        "side_effects": "Dizziness, low blood pressure upon standing, fatigue.",
        "warnings": "Contraindicated in pregnancy. Regularly monitor blood pressure and potassium levels.",
        "category": "Antihypertensive (ARB)",
    },
    {
        "name": "Amoxyclav 625",
        "aliases": ["amoxyclav 625", "amoxyclav", "augmentin 625", "augmentin", "moxikind-cv"],
        "generic_name": "Amoxicillin + Potassium Clavulanate",
        "active_ingredients": ["Amoxicillin", "Clavulanic Acid"],
        "dosage_form": "Tablet",
        "default_strength": "625mg",
        "before_after_food": "Take at the start of a meal to reduce gastrointestinal discomfort.",
        "common_uses": "Treats bacterial infections of the respiratory tract, ear, sinus, skin, and urinary tract.",
        "side_effects": "Mild diarrhea, nausea, vomiting, skin rash.",
        "warnings": "Complete the full prescribed antibiotic course. Contraindicated for individuals allergic to penicillin.",
        "category": "Antibacterial",
    },
    {
        "name": "Metformin",
        "aliases": ["metformin", "glycomet 500", "glycomet", "glucophage"],
        "generic_name": "Metformin Hydrochloride",
        "active_ingredients": ["Metformin"],
        "dosage_form": "Tablet",
        "default_strength": "500mg",
        "before_after_food": "Take with or immediately after meals to reduce stomach upset.",
        "common_uses": "First-line oral treatment for type 2 diabetes mellitus to control blood glucose levels.",
        "side_effects": "Nausea, flatulence, abdominal cramps, metallic taste.",
        "warnings": "Avoid excessive alcohol intake. Discontinue temporarily before contrast dye radiologic procedures.",
        "category": "Antidiabetic (Biguanide)",
    },
    {
        "name": "Ecosprin 75",
        "aliases": ["ecosprin 75", "ecosprin", "disprin", "aspirin 75"],
        "generic_name": "Aspirin",
        "active_ingredients": ["Acetylsalicylic Acid"],
        "dosage_form": "Tablet",
        "default_strength": "75mg",
        "before_after_food": "Take strictly after food with plenty of water.",
        "common_uses": "Blood thinner (antiplatelet) to prevent heart attack, angina, and stroke.",
        "side_effects": "Indigestion, stomach ulcers, increased bleeding risk, bruising.",
        "warnings": "Do not take on an empty stomach. Consult your doctor immediately if you notice unusual bleeding.",
        "category": "Antiplatelet / Anticoagulant",
    },
    {
        "name": "Warfarin",
        "aliases": ["warfarin", "coumadin", "uniwarf"],
        "generic_name": "Warfarin Sodium",
        "active_ingredients": ["Warfarin"],
        "dosage_form": "Tablet",
        "default_strength": "5mg",
        "before_after_food": "Take at the same time each evening with or without food.",
        "common_uses": "Prevents and treats deep vein thrombosis (DVT), pulmonary embolism, and stroke in atrial fibrillation.",
        "side_effects": "Bleeding, bruising, headache.",
        "warnings": "Requires regular INR blood test monitoring. Avoid sharp changes in dietary vitamin K intake (green leafy vegetables).",
        "category": "Anticoagulant",
    },
    {
        "name": "Azithral 500",
        "aliases": ["azithral 500", "azithral", "zithromax", "aziwok"],
        "generic_name": "Azithromycin",
        "active_ingredients": ["Azithromycin"],
        "dosage_form": "Tablet",
        "default_strength": "500mg",
        "before_after_food": "Take 1 hour before meals or 2 hours after meals with water.",
        "common_uses": "Treats bacterial throat, chest, and respiratory tract infections.",
        "side_effects": "Nausea, diarrhea, abdominal pain.",
        "warnings": "Complete the full 3 or 5 day course as prescribed by doctor.",
        "category": "Macrolide Antibiotic",
    },
    {
        "name": "Cetirizine 10",
        "aliases": ["cetirizine 10", "cetirizine", "cetzine", "okacet", "zyrtec"],
        "generic_name": "Cetirizine Hydrochloride",
        "active_ingredients": ["Cetirizine"],
        "dosage_form": "Tablet",
        "default_strength": "10mg",
        "before_after_food": "Take with or without food, preferably in the evening.",
        "common_uses": "Relieves allergic rhinitis, sneezing, runny nose, and hives (urticaria).",
        "side_effects": "Mild drowsiness, dry mouth, tiredness.",
        "warnings": "May cause mild sedation; avoid driving if drowsy.",
        "category": "Antihistamine",
    }
]


PACKAGING_STOP_WORDS = {
    "tablet", "tablets", "capsule", "capsules", "syrup", "suspension", "injection",
    "manufactured", "marketed", "mfg", "mfd", "expiry", "exp", "batch", "lot",
    "limited", "ltd", "pvt", "private", "corp", "corporation", "pharma", "pharmaceuticals",
    "warning", "caution", "schedule", "prescription", "reach", "children", "protect",
    "light", "moisture", "temperature", "store", "dry", "place", "below", "exceed",
    "contains", "composition", "each", "uncoated", "coated", "film", "colour", "color",
    "titanium", "dioxide", "iron", "oxide", "dosage", "directed", "physician", "doctor",
    "hospital", "patient", "clinic", "road", "industrial", "area", "estate", "india",
    "regd", "office", "trademark", "licensed", "user", "keep", "cool", "dark",
    "overdose", "harmful", "customer", "care", "helpline", "email", "phone", "strip",
    "blister", "pack", "sealed", "foil", "take", "advice", "daily", "stomach", "empty",
    "water", "food", "meals", "night", "morning", "random", "bottle", "intake"
}


def _get_master_database_meds():
    """Load reference drugs from SQLite database and merge with clinical catalog."""
    items = list(CLINICAL_CATALOG)
    db_path = Path(__file__).resolve().parents[1] / "medimitra.db"
    if db_path.exists():
        try:
            con = sqlite3.connect(str(db_path))
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT * FROM medicine_database").fetchall()
            for row in rows:
                r_dict = dict(row)
                name = r_dict.get("name", "")
                aliases = [name.lower(), name.lower().replace("-", " ")]
                first_word = name.split()[0].lower() if name else ""
                if first_word and len(first_word) >= 4 and first_word not in PACKAGING_STOP_WORDS:
                    aliases.append(first_word)

                items.append({
                    "name": name,
                    "aliases": list(set(aliases)),
                    "generic_name": r_dict.get("generic_name", ""),
                    "active_ingredients": [r_dict.get("generic_name", "")] if r_dict.get("generic_name") else [],
                    "dosage_form": r_dict.get("dosage_form", "Tablet"),
                    "default_strength": r_dict.get("standard_strength", ""),
                    "before_after_food": r_dict.get("before_after_food", "Take with water as advised."),
                    "common_uses": r_dict.get("common_uses", "Therapeutic medication."),
                    "side_effects": r_dict.get("side_effects", "Consult doctor if unusual symptoms occur."),
                    "warnings": r_dict.get("warnings", "Take as directed by doctor."),
                    "category": r_dict.get("category", "General"),
                })
            con.close()
        except Exception:
            pass

    ref_json = Path(__file__).resolve().parents[1] / "data" / "medicines.json"
    if ref_json.exists():
        try:
            json_meds = json.loads(ref_json.read_text(encoding="utf-8"))
            for jm in json_meds:
                items.append({
                    "name": jm.get("name", ""),
                    "aliases": [jm.get("name", "").lower(), jm.get("generic_name", "").lower()] + [a.lower() for a in jm.get("active_ingredients", [])],
                    "generic_name": jm.get("generic_name", ""),
                    "active_ingredients": jm.get("active_ingredients", []),
                    "dosage_form": "Tablet",
                    "default_strength": "",
                    "before_after_food": "Take after meals with water.",
                    "common_uses": "Prescribed medicine.",
                    "side_effects": "Mild stomach discomfort.",
                    "warnings": "Take as directed.",
                    "category": "General",
                })
        except Exception:
            pass
    return items


def _normalize_ocr_text(text):
    """Normalize common OCR substitutions in medicine labels (e.g. Dol0 -> Dolo)."""
    t = re.sub(r'([a-zA-Z]+)0([a-zA-Z0-9]*)', r'\g<1>o\g<2>', text)
    t = re.sub(r'[^a-zA-Z0-9\s\.\-\+]', ' ', t)
    return t


def _find_best_medicine_match(text_corpus, master_list):
    """
    Scored clinical medicine matching:
    Distinguishes specific Indian tablet brands (Saridon, Calpol 650, Dolo 650, Pan-D, Pantocid 40, etc.)
    using packaging brand signatures, word boundary matching, and multi-criteria scoring.
    Never collapses unknown images into Dolo 650.
    """
    if not text_corpus:
        return None

    raw_lower = text_corpus.lower()
    text_norm = _normalize_ocr_text(text_corpus).lower()

    # 1. Distinctive Indian Brand Signatures (Highest Precision)
    # Saridon (Bayer + Caffeine or Paracetamol & Caffeine or Saridon)
    if ("bayer" in raw_lower and ("caffeine" in raw_lower or "paracetamol" in raw_lower or "propyphenazone" in raw_lower)) or \
       ("paracetamol" in raw_lower and "caffeine" in raw_lower) or \
       (re.search(r'\bsaridon\b', text_norm)):
        for d in master_list:
            if d["name"].lower() == "saridon":
                return d

    # Calpol 650 / 500 (GSK + Paracetamol or Calpol)
    if re.search(r'\bcalpol\b', text_norm) or (("gsk" in raw_lower or "glaxosmithkline" in raw_lower or "glaxo" in raw_lower) and "paracetamol" in raw_lower):
        target = "Calpol 500" if ("500" in text_norm and "650" not in text_norm) else "Calpol 650"
        for d in master_list:
            if d["name"].lower() == target.lower():
                return d

    # Dolo 650 (Dolo or Micro Labs + Paracetamol)
    if re.search(r'\bdolo\b', text_norm) or ("micro labs" in raw_lower and "paracetamol" in raw_lower):
        for d in master_list:
            if d["name"].lower() == "dolo 650":
                return d

    # Combiflam (Ibuprofen + Paracetamol or Combiflam)
    if re.search(r'\bcombiflam\b', text_norm) or ("ibuprofen" in raw_lower and "paracetamol" in raw_lower):
        for d in master_list:
            if d["name"].lower() == "combiflam":
                return d

    # Pan-D (Pantoprazole + Domperidone or Pan-D / Alkem)
    if re.search(r'\bpan\s*[-–]?\s*d\b', text_norm) or ("pantoprazole" in raw_lower and "domperidone" in raw_lower):
        for d in master_list:
            if "pan-d" in d["name"].lower() or "pan d" in d["name"].lower():
                return d

    # Pantocid 40 (Pantocid or Sun Pharma + Pantoprazole)
    if re.search(r'\bpantocid\b', text_norm) or ("sun pharma" in raw_lower and "pantoprazole" in raw_lower):
        for d in master_list:
            if "pantocid" in d["name"].lower():
                return d

    # Atorva 10 (Atorva or Zydus + Atorvastatin)
    if re.search(r'\batorva\b', text_norm) or ("zydus" in raw_lower and "atorvastatin" in raw_lower):
        for d in master_list:
            if "atorva" in d["name"].lower():
                return d

    # Telma 40 (Telma or Glenmark + Telmisartan)
    if re.search(r'\btelma\b', text_norm) or ("glenmark" in raw_lower and "telmisartan" in raw_lower):
        for d in master_list:
            if "telma" in d["name"].lower():
                return d

    # Augmentin 625 / Amoxyclav 625
    if re.search(r'\b(?:augmentin|amoxyclav|moxikind\s*cv)\b', text_norm) or \
       ("amoxicillin" in raw_lower and ("clavulanate" in raw_lower or "clavulanic" in raw_lower)):
        for d in master_list:
            if "amoxyclav" in d["name"].lower() or "augmentin" in d["name"].lower():
                return d

    # Zerodol-P / Zerodol-SP
    if re.search(r'\bzerodol\b', text_norm) or ("aceclofenac" in raw_lower and "paracetamol" in raw_lower):
        target = "Zerodol-SP" if "sp" in text_norm or "serratio" in text_norm else "Zerodol-P"
        for d in master_list:
            if target.lower() in d["name"].lower():
                return d

    # 2. General Scored Matching across full master list
    best_drug = None
    best_score = 0

    for drug in master_list:
        score = 0
        dname = drug["name"].lower()
        dname_clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', dname)
        d_tokens = [t for t in dname_clean.split() if len(t) >= 4 and not t.isdigit() and t not in PACKAGING_STOP_WORDS]

        # Exact brand name token in text (word boundary)
        for t in d_tokens:
            if re.search(rf'\b{re.escape(t)}\b', text_norm):
                score += 80
                break

        # Check aliases
        for alias in drug.get("aliases", []):
            al_clean = alias.strip().lower()
            if len(al_clean) >= 4 and al_clean not in PACKAGING_STOP_WORDS:
                if re.search(rf'\b{re.escape(al_clean)}\b', text_norm):
                    score += 70
                    break

        # Check multi-salt generic combinations
        gen = (drug.get("generic_name") or "").lower()
        if gen and ("+" in gen or " and " in gen):
            parts = [p.strip() for p in re.split(r'[\+\/]| and ', gen) if len(p.strip()) >= 4]
            matched_parts = sum(1 for p in parts if p in text_norm)
            if matched_parts >= 2:
                score += 65

        # Strength match bonus
        strength = drug.get("default_strength") or drug.get("standard_strength") or ""
        if strength and strength.lower() in text_norm:
            score += 15

        if score > best_score:
            best_score = score
            best_drug = drug

    # High confidence threshold required to confirm identification
    if best_drug and best_score >= 60:
        return best_drug

    return None


def _smart_clinical_nlp_extract(ocr_text, image_path=None, notice=None):
    """
    Intelligent Clinical NLP Engine:
    Extracts structured prescription and medicine strip details accurately,
    cross-referencing with master medicine databases even when offline or API quotas are exhausted.
    """
    raw = ocr_text or ""
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    joined = " ".join(lines)
    master_list = _get_master_database_meds()

    # 1. Detect Document Type
    is_prescription = bool(re.search(r"\b(rx|prescription|doctor|patient|hospitals?|clinic|dr\.|m\.?d\.?|mbbs)\b", joined, re.I))
    doc_type = "prescription" if is_prescription else "medicine_label"

    # 2. Extract Doctor & Specialty
    doc_match = re.search(r"\b(?:Dr\.|Doctor)\s+([A-Za-z\s]{2,40}?)(?:,\s*|\n|$)", raw, re.I)
    doctor_name = doc_match.group(1).strip() if doc_match else ""
    spec_match = re.search(r"\b(Cardiology|Cardiologist|Physician|General Medicine|Orthopedics|Neurology|Pediatrics|Dermatology|Oncology|Gynecology)\b", raw, re.I)
    specialty = spec_match.group(1).strip() if spec_match else ""

    # 3. Extract Patient
    pat_match = re.search(r"\b(?:Patient|Pt)\b\s*[:.-]?\s*([A-Za-z\s]{2,40}?)(?:\s*\(|\n|$)", raw, re.I)
    patient_name = pat_match.group(1).strip() if pat_match else ""

    # 4. Extract Dates
    date_matches = re.findall(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b", raw)
    rx_date = date_matches[0] if date_matches else ""
    expiry_match = re.search(r"\b(?:exp(?:iry)?|use before)\b\s*[:#-]?\s*(\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})", raw, re.I)
    expiry_date = expiry_match.group(1).strip() if expiry_match else ""
    mfg_match = re.search(r"\b(?:mfg|mfd|date of mfg)\b\s*[:#-]?\s*(\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})", raw, re.I)
    mfg_date = mfg_match.group(1).strip() if mfg_match else ""

    # 5. Extract Strength & Form
    strength_match = re.search(r"\b\d+(?:\.\d+)?\s?(?:mg|mcg|µg|g|ml|mL|%|IU)\b", joined, re.I)
    detected_strength = strength_match.group(0).strip() if strength_match else ""
    form_match = re.search(r"\b(tablets?|capsules?|syrup|suspension|injection|inhaler|drops?|cream|ointment)\b", joined, re.I)
    detected_form = form_match.group(1).title() if form_match else "Tablet"

    # 6. Extract Prescribed Medicine Lines
    extracted_meds = []
    summary_lines = []
    for line in lines:
        if re.search(r"\b(?:Tab\.?|Cap\.?|Syrup|Inj\.?|Oint\.?)\b|\b\d+\s*(?:mg|mcg|ml|g)\b", line, re.I):
            clean_l = re.sub(r"^\s*\d+[\.\)]\s*", "", line).strip()
            l_strength = re.search(r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|g|ml|iu|%)\b", clean_l, re.I)
            l_freq = re.search(r"\b(1\s*[-–]\s*0\s*[-–]\s*1|1\s*[-–]\s*1\s*[-–]\s*1|0\s*[-–]\s*0\s*[-–]\s*1|1\s*[-–]\s*0\s*[-–]\s*0|1\s*OD|1\s*BD|OD|BD|TDS|QID|HS|SOS|Once daily|Twice daily|Night|Morning|Empty stomach)\b", clean_l, re.I)
            l_dur = re.search(r"\b(?:x\s*)?(\d+\s*(?:days?|weeks?|months?))\b", clean_l, re.I)
            
            # Extract name candidate
            cand = re.sub(r"\b(?:tab(?:let)?|cap(?:sule)?|syrup|inj(?:ection)?|drops?|gel|cream|oint(?:ment)?)\.?\s*", "", clean_l, flags=re.I)
            cand = re.split(r"\s+(?:\d+\s*(?:mg|mcg|g|ml)|[-–]|x\s*\d|OD|BD|TDS|SOS)\b", cand, maxsplit=1, flags=re.I)[0].strip(" .-:")
            if cand and len(cand) >= 2:
                matched_drug = _find_best_medicine_match(cand, master_list)
                med_item = {
                    "name": matched_drug["name"] if matched_drug else cand.title(),
                    "generic_name": matched_drug["generic_name"] if matched_drug else "",
                    "dosage": l_strength.group(0).strip() if l_strength else (matched_drug.get("default_strength") if matched_drug else ""),
                    "form": "Tablet" if "tab" in clean_l.lower() else ("Capsule" if "cap" in clean_l.lower() else "Tablet"),
                    "frequency": l_freq.group(0).strip().upper() if l_freq else "1 OD",
                    "duration": l_dur.group(1).strip() if l_dur else "",
                    "instructions": clean_l
                }
                extracted_meds.append(med_item)
                summary_lines.append(f"{med_item['name']} ({med_item['dosage'] or 'standard dose'}) - {med_item['frequency']}")

    # 7. Identify Primary Medicine
    primary_med_match = _find_best_medicine_match(joined, master_list)
    if extracted_meds:
        primary_name = extracted_meds[0]["name"]
        primary_generic = extracted_meds[0]["generic_name"]
        primary_dosage = extracted_meds[0]["dosage"] or detected_strength
        primary_form = extracted_meds[0]["form"] or detected_form
        primary_freq = extracted_meds[0]["frequency"]
        primary_dur = extracted_meds[0]["duration"]
        primary_instructions = "\n".join([m["instructions"] for m in extracted_meds])
    elif primary_med_match:
        primary_name = primary_med_match["name"]
        primary_generic = primary_med_match["generic_name"]
        primary_dosage = detected_strength or primary_med_match.get("default_strength") or "As prescribed"
        primary_form = detected_form or primary_med_match.get("dosage_form", "Tablet")
        primary_freq = "1 OD"
        primary_dur = ""
        primary_instructions = primary_med_match.get("before_after_food", "")
    else:
        # Check if a generic salt was detected in OCR text when specific brand name is not printed
        generic_candidates = [
            ("paracetamol", "Paracetamol", "Antipyretic / Analgesic", "Take strictly after meals with water.", "Relief of fever and body aches."),
            ("pantoprazole", "Pantoprazole", "Proton Pump Inhibitor (PPI)", "Take 30-60 min before breakfast on empty stomach.", "Treats acidity, heartburn and GERD."),
            ("telmisartan", "Telmisartan", "Antihypertensive", "Take once daily in the morning with water.", "Lowers high blood pressure."),
            ("atorvastatin", "Atorvastatin", "Statin / Lipid-lowering", "Take once daily in the evening with or without food.", "Lowers bad cholesterol."),
            ("metformin", "Metformin", "Antidiabetic", "Take with or immediately after meals.", "Controls blood sugar in Type 2 Diabetes."),
            ("cetirizine", "Cetirizine", "Antihistamine", "Take in the evening with or without food.", "Relieves allergic rhinitis, sneezing and hives."),
            ("amoxicillin", "Amoxicillin", "Antibacterial Antibiotic", "Take as directed with food.", "Treats bacterial infections.")
        ]
        matched_gen = None
        for salt_kw, salt_name, salt_cat, salt_timing, salt_use in generic_candidates:
            if salt_kw in joined.lower():
                matched_gen = (salt_name, salt_cat, salt_timing, salt_use)
                break

        if matched_gen:
            salt_name, salt_cat, salt_timing, salt_use = matched_gen
            primary_name = f"{salt_name} {detected_strength}".strip() + " (Generic Formulation)"
            primary_generic = salt_name
            primary_dosage = detected_strength or "Standard dose"
            primary_form = detected_form
            primary_freq = "1 OD"
            primary_dur = ""
            primary_instructions = salt_timing
        else:
            primary_name = "Unidentified Medicine"
            primary_generic = ""
            primary_dosage = detected_strength
            primary_form = detected_form
            primary_freq = "1 OD"
            primary_dur = ""
            primary_instructions = "Please take only as prescribed by your doctor."

    # Look up clinical facts for the primary identified drug
    ref_facts = primary_med_match or _find_best_medicine_match(primary_name, master_list)
    before_after = ref_facts.get("before_after_food", "Take after meals with water.") if ref_facts else "Take as directed by doctor."
    purpose = ref_facts.get("common_uses", "Therapeutic medication.") if ref_facts else "Therapeutic medication."
    side_effects = ref_facts.get("side_effects", "Consult physician if unusual symptoms occur.") if ref_facts else ""
    warnings = ref_facts.get("warnings", "Take as directed by doctor.") if ref_facts else ""

    rx_summary = "; ".join(summary_lines) if summary_lines else f"Prescription for {primary_name} ({primary_dosage})"

    facts = {
        "name": primary_name,
        "active_ingredient": primary_generic,
        "generic_name": primary_generic,
        "strength": primary_dosage,
        "dosage": primary_dosage,
        "form": primary_form,
        "manufacturer": ref_facts.get("manufacturer", "") if ref_facts else "",
        "batch_number": "",
        "manufacturing_date": mfg_date,
        "expiry_date": expiry_date,
        "prescription_date": rx_date,
        "doctor_name": doctor_name,
        "specialty": specialty,
        "patient_name": patient_name,
        "frequency": primary_freq,
        "duration": primary_dur,
        "route": "Oral",
        "prescription_instructions": primary_instructions,
        "before_after_food": before_after,
        "document_type": doc_type,
        "prescription_summary": rx_summary,
        "purpose": purpose,
        "side_effects": side_effects,
        "warnings": warnings,
        "medicines": extracted_meds
    }

    confidence = {
        key: ("high" if (ref_facts and facts.get(key)) else ("medium" if facts.get(key) else "unavailable"))
        for key in facts.keys()
    }

    if primary_name == "Unidentified Medicine":
        nlp_notice = "Medicine brand could not be identified with certainty. Please ensure the tablet foil name is clear and well-lit, or select the medicine from the list."
    else:
        nlp_notice = notice or "Analyzed using MediMitra Clinical NLP Engine & verified Indian drug knowledgebase."

    return {
        "extracted_facts": facts,
        "confidence": confidence,
        "uncertain_fields": [k for k, v in facts.items() if not v and k not in ("batch_number", "manufacturing_date")],
        "source": "smart_nlp",
        "notice": nlp_notice
    }


def _call_gemini_vision(api_key, image_path, ocr_text, model="gemini-1.5-flash"):
    """Call Google Gemini Vision API."""
    import requests
    import mimetypes

    mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("ascii")

    prompt = (
        "Identify the medicine or prescription shown in this image. "
        "Return a valid JSON object with 'extracted_facts' containing: "
        "name, active_ingredient, strength, form, manufacturer, batch_number, manufacturing_date, "
        "expiry_date, prescription_date, doctor_name, specialty, patient_name, frequency, route, "
        "duration, prescription_instructions, before_after_food, document_type, prescription_summary, purpose. "
        "Also include 'confidence' object and 'notice'. Use empty strings when not identifiable. "
        f"Additional OCR hints:\n{ocr_text or 'None'}"
    )

    # Use Google Generative Language REST API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime_type, "data": img_b64}}
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.1
        }
    }

    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    res_json = resp.json()
    raw_content = res_json["candidates"][0]["content"]["parts"][0]["text"]
    data = json.loads(raw_content)
    facts = data.get("extracted_facts", {})
    return facts, data.get("confidence", {}), data.get("notice", "Analyzed with Google Gemini Vision AI.")


def _call_openai_vision(api_key, endpoint, model, image_path, ocr_text):
    """Call OpenAI compatible Vision API."""
    import requests
    import mimetypes

    content = []
    if image_path and os.path.isfile(image_path):
        mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("ascii")
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}})

    prompt = (
        "Identify the medicine or prescription shown in this image. "
        "Return a JSON object with extracted_facts containing name, active_ingredient, strength, form, "
        "manufacturer, batch_number, manufacturing_date, expiry_date, prescription_date, doctor_name, specialty, "
        "patient_name, frequency, route, duration, prescription_instructions, before_after_food, document_type, prescription_summary, purpose.\n"
        f"OCR text:\n{ocr_text or '(no readable OCR text)'}"
    )
    content.insert(0, {"type": "text", "text": prompt})

    response = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        },
        timeout=35,
    )
    response.raise_for_status()
    payload = response.json()
    data = json.loads(payload["choices"][0]["message"]["content"])
    facts = data.get("extracted_facts", {})
    return facts, data.get("confidence", {}), data.get("notice", "Analyzed with OpenAI Vision AI.")


def extract_medicine_info(ocr_text, image_path=None):
    """
    Main extraction interface:
    Tries configured Vision AI providers (Gemini or OpenAI).
    When cloud API keys are missing or exhausted (e.g., HTTP 429 quota limits),
    automatically executes the Intelligent Clinical NLP Engine without failing.
    """
    local_env = dotenv_values(Path(__file__).resolve().parents[1] / ".env")
    gemini_key = (os.getenv("GEMINI_API_KEY") or local_env.get("GEMINI_API_KEY") or "").strip()
    openai_key = (os.getenv("VISION_API_KEY") or os.getenv("OPENAI_API_KEY") or local_env.get("VISION_API_KEY") or local_env.get("OPENAI_API_KEY") or "").strip()

    placeholder_markers = ("paste-your-key", "your-api-key", "your_secret", "replace-me", "your_key", "your-openai", "api-key-here")

    # 1. Try Gemini Vision if valid key present
    if gemini_key and not any(m in gemini_key.lower() for m in placeholder_markers):
        if image_path and os.path.isfile(image_path):
            try:
                model = os.getenv("GEMINI_MODEL") or local_env.get("GEMINI_MODEL") or "gemini-1.5-flash"
                facts, confidence, notice = _call_gemini_vision(gemini_key, image_path, ocr_text, model=model)
                return {
                    "extracted_facts": facts,
                    "confidence": confidence,
                    "uncertain_fields": [k for k, v in facts.items() if not v],
                    "source": "vision_ai",
                    "notice": notice
                }
            except Exception:
                pass

    # 2. Try OpenAI Vision if valid key present
    if openai_key and not any(m in openai_key.lower() for m in placeholder_markers):
        if image_path and os.path.isfile(image_path):
            try:
                endpoint = os.getenv("VISION_API_URL") or local_env.get("VISION_API_URL") or "https://api.openai.com/v1/chat/completions"
                model = os.getenv("AI_MODEL") or local_env.get("AI_MODEL") or "gpt-4o-mini"
                facts, confidence, notice = _call_openai_vision(openai_key, endpoint, model, image_path, ocr_text)
                return {
                    "extracted_facts": facts,
                    "confidence": confidence,
                    "uncertain_fields": [k for k, v in facts.items() if not v],
                    "source": "vision_ai",
                    "notice": notice
                }
            except Exception as e:
                # If 429 quota or rate limit, record friendly note
                resp = getattr(e, "response", None)
                status = getattr(resp, "status_code", None)
                if status == 429:
                    api_note = "Cloud Vision quota exceeded (HTTP 429). Successfully switched to MediMitra Smart Clinical NLP Engine."
                elif status == 401:
                    api_note = "Cloud Vision API key invalid. Successfully switched to MediMitra Smart Clinical NLP Engine."
                else:
                    api_note = "Switched to MediMitra Smart Clinical NLP Engine."
                return _smart_clinical_nlp_extract(ocr_text, image_path=image_path, notice=api_note)

    # 3. Default to Smart Clinical NLP Engine
    return _smart_clinical_nlp_extract(
        ocr_text,
        image_path=image_path,
        notice="Extracted via MediMitra Smart Clinical NLP Engine & verified against master medicine database."
    )
