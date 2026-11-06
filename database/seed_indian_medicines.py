"""
Indian Medicines Master Seed Data for MediMitra
Contains 130+ of the most commonly prescribed and OTC Indian tablets and formulations.
"""

import sqlite3
from pathlib import Path

INDIAN_MEDICINES = [
    # 1. ANALGESICS, ANTIPYRETICS & NSAIDs
    {
        "name": "Dolo 650",
        "generic_name": "Paracetamol / Acetaminophen",
        "category": "Antipyretic / Analgesic",
        "dosage_form": "Tablet",
        "standard_strength": "650mg",
        "before_after_food": "Take strictly after food with plenty of water.",
        "common_uses": "Relief of fever, headache, body aches, toothache, and mild-to-moderate pain.",
        "side_effects": "Mild nausea, rash, liver toxicity in overdose.",
        "warnings": "Do not exceed 4,000 mg (4 tablets) in 24 hours. Avoid alcohol. Maintain at least 4-6 hours between doses.",
        "known_interactions": "Warfarin (at high doses), Alcohol, Isoniazid"
    },
    {
        "name": "Calpol 500",
        "generic_name": "Paracetamol",
        "category": "Antipyretic / Analgesic",
        "dosage_form": "Tablet",
        "standard_strength": "500mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Reduces fever and relieves mild pain and headaches.",
        "side_effects": "Generally safe; rare allergic skin reactions.",
        "warnings": "Do not combine with other paracetamol-containing cold preparations.",
        "known_interactions": "Alcohol, Cholestyramine"
    },
    {
        "name": "Calpol 650",
        "generic_name": "Paracetamol",
        "category": "Antipyretic / Analgesic",
        "dosage_form": "Tablet",
        "standard_strength": "650mg",
        "before_after_food": "Take strictly after meals with water.",
        "common_uses": "Fast relief from high fever, post-vaccination fever, joint pain, and muscle soreness.",
        "side_effects": "Nausea, allergic reaction.",
        "warnings": "Do not exceed 4 tablets in 24 hours. Contraindicated in severe hepatic impairment.",
        "known_interactions": "Warfarin, Alcohol"
    },
    {
        "name": "Crocin Advance",
        "generic_name": "Paracetamol (Fast Release)",
        "category": "Antipyretic / Analgesic",
        "dosage_form": "Tablet",
        "standard_strength": "500mg",
        "before_after_food": "Take after food with water.",
        "common_uses": "Rapid release formula for headache, fever, toothache, and period pain.",
        "side_effects": "Rare mild stomach upset.",
        "warnings": "Keep 4 to 6 hours gap between doses. Do not exceed 4000mg per day.",
        "known_interactions": "Alcohol, Barbiturates"
    },
    {
        "name": "Crocin 650",
        "generic_name": "Paracetamol",
        "category": "Antipyretic / Analgesic",
        "dosage_form": "Tablet",
        "standard_strength": "650mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Effective for high viral fevers, dental pain, backache, and migraine.",
        "side_effects": "Mild nausea, rash.",
        "warnings": "Do not take along with Dolo, Sumo, or any other paracetamol tablet.",
        "known_interactions": "Alcohol, Warfarin"
    },
    {
        "name": "Pacimol 650",
        "generic_name": "Paracetamol",
        "category": "Antipyretic / Analgesic",
        "dosage_form": "Tablet",
        "standard_strength": "650mg",
        "before_after_food": "Take after food with water.",
        "common_uses": "Fever management and relief from chronic inflammatory or acute pain.",
        "side_effects": "Nausea, skin itching.",
        "warnings": "Caution in patients with liver or kidney disorders.",
        "known_interactions": "Alcohol, Isoniazid"
    },
    {
        "name": "Combiflam",
        "generic_name": "Ibuprofen + Paracetamol",
        "category": "NSAID Combination",
        "dosage_form": "Tablet",
        "standard_strength": "400mg + 325mg",
        "before_after_food": "Take strictly after meals with a full glass of water or milk.",
        "common_uses": "Relief of inflammatory pain, arthritis, dental pain, swelling, and fever.",
        "side_effects": "Acidity, heartburn, stomach ulceration, nausea.",
        "warnings": "Never take on an empty stomach. Contraindicated in active peptic ulcer disease and severe heart failure.",
        "known_interactions": "Aspirin, Blood thinners, ACE inhibitors, Methotrexate"
    },
    {
        "name": "Flexon",
        "generic_name": "Ibuprofen + Paracetamol",
        "category": "NSAID Combination",
        "dosage_form": "Tablet",
        "standard_strength": "400mg + 325mg",
        "before_after_food": "Take after meals to protect the stomach lining.",
        "common_uses": "Relieves muscular pain, joint pain, sprains, strains, and tooth extraction ache.",
        "side_effects": "Gastric irritation, indigestion, dizziness.",
        "warnings": "Avoid prolonged usage without gastric protective medicine like Pantoprazole.",
        "known_interactions": "Anticoagulants, Corticosteroids, Diuretics"
    },
    {
        "name": "Sumo",
        "generic_name": "Nimesulide + Paracetamol",
        "category": "NSAID Combination",
        "dosage_form": "Tablet",
        "standard_strength": "100mg + 325mg",
        "before_after_food": "Take strictly after meals.",
        "common_uses": "Rapid relief of severe pain, dysmenorrhea (period cramps), and fever.",
        "side_effects": "Nausea, epigastric discomfort, elevated liver enzymes.",
        "warnings": "Not recommended for children under 12 years or patients with active liver disease.",
        "known_interactions": "Alcohol, Methotrexate, Blood thinners"
    },
    {
        "name": "Zerodol-P",
        "generic_name": "Aceclofenac + Paracetamol",
        "category": "NSAID Combination",
        "dosage_form": "Tablet",
        "standard_strength": "100mg + 325mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Osteoarthritis, rheumatoid arthritis, ankylosing spondylitis, and acute musculoskeletal pain.",
        "side_effects": "Indigestion, abdominal pain, dizziness.",
        "warnings": "Avoid in patients with asthma, active gastrointestinal ulcers, or kidney impairment.",
        "known_interactions": "Warfarin, Lithium, Digoxin, Antihypertensives"
    },
    {
        "name": "Zerodol-SP",
        "generic_name": "Aceclofenac + Paracetamol + Serratiopeptidase",
        "category": "NSAID & Anti-inflammatory Enzyme",
        "dosage_form": "Tablet",
        "standard_strength": "100mg + 325mg + 15mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Post-surgical swelling, dental extraction inflammation, severe joint and wound pain.",
        "side_effects": "Gastric upset, diarrhea, rash.",
        "warnings": "Serratiopeptidase speeds clot breakdown; caution in patients on blood thinners.",
        "known_interactions": "Anticoagulants, Aspirin"
    },
    {
        "name": "Zerodol-TH 4",
        "generic_name": "Aceclofenac + Thiocolchicoside",
        "category": "NSAID + Muscle Relaxant",
        "dosage_form": "Tablet",
        "standard_strength": "100mg + 4mg",
        "before_after_food": "Take after food with water.",
        "common_uses": "Painful muscle spasms, low backache, cervical spondylosis, and sports injuries.",
        "side_effects": "Drowsiness, mild diarrhea, dizziness.",
        "warnings": "May cause sedation; avoid driving or operating heavy machinery.",
        "known_interactions": "Sedatives, CNS depressants"
    },
    {
        "name": "Voveran 50",
        "generic_name": "Diclofenac Sodium",
        "category": "NSAID",
        "dosage_form": "Tablet",
        "standard_strength": "50mg",
        "before_after_food": "Take immediately after food or with milk.",
        "common_uses": "Severe pain and inflammation in arthritis, gout, bursitis, and kidney stone colic.",
        "side_effects": "Epigastric burning, nausea, ulceration.",
        "warnings": "Take shortest duration necessary. High cardiovascular and renal caution.",
        "known_interactions": "Aspirin, Warfarin, ACE inhibitors"
    },
    {
        "name": "Voveran SR 100",
        "generic_name": "Diclofenac Sodium (Sustained Release)",
        "category": "NSAID Sustained Release",
        "dosage_form": "Tablet",
        "standard_strength": "100mg",
        "before_after_food": "Swallow whole after dinner; do not crush or chew.",
        "common_uses": "24-hour chronic pain relief for severe rheumatoid arthritis and spinal spondylitis.",
        "side_effects": "Stomach burning, bloating, headache.",
        "warnings": "Do not break or crush sustained release tablets.",
        "known_interactions": "Lithium, Methotrexate, Cyclosporine"
    },
    {
        "name": "Dynapar",
        "generic_name": "Diclofenac + Paracetamol",
        "category": "NSAID Combination",
        "dosage_form": "Tablet",
        "standard_strength": "50mg + 325mg",
        "before_after_food": "Take strictly after meals.",
        "common_uses": "Acute musculoskeletal trauma, fractures, dental pain, and post-operative pain.",
        "side_effects": "Stomach ache, nausea, dizziness.",
        "warnings": "Contraindicated in third-trimester pregnancy and bleeding disorders.",
        "known_interactions": "Anticoagulants, SSRIs"
    },
    {
        "name": "Meftal-Spas",
        "generic_name": "Dicyclomine + Mefenamic Acid",
        "category": "Antispasmodic & NSAID",
        "dosage_form": "Tablet",
        "standard_strength": "10mg + 250mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Spasmodic dysmenorrhea (menstrual cramps), intestinal colic, and biliary colic.",
        "side_effects": "Dry mouth, blurred vision, mild drowsiness, nausea.",
        "warnings": "Contraindicated in glaucoma, myasthenia gravis, and urinary retention.",
        "known_interactions": "Antihistamines, Anticholinergics, Blood thinners"
    },
    {
        "name": "Meftal 500",
        "generic_name": "Mefenamic Acid",
        "category": "NSAID",
        "dosage_form": "Tablet",
        "standard_strength": "500mg",
        "before_after_food": "Take with or after food with water.",
        "common_uses": "Heavy and painful menstrual bleeding (menorrhagia), headache, and dental pain.",
        "side_effects": "Diarrhea, indigestion, skin rash.",
        "warnings": "Do not take for more than 7 consecutive days without doctor consultation.",
        "known_interactions": "Warfarin, Antihypertensives, Lithium"
    },
    {
        "name": "Ultracet",
        "generic_name": "Tramadol Hydrochloride + Paracetamol",
        "category": "Opioid Analgesic Combination",
        "dosage_form": "Tablet",
        "standard_strength": "37.5mg + 325mg",
        "before_after_food": "Take with or without food as advised.",
        "common_uses": "Moderate to severe acute pain, post-surgical recovery, and severe joint pain.",
        "side_effects": "Drowsiness, constipation, nausea, dizziness, dry mouth.",
        "warnings": "Schedule H prescription drug. Risk of habituation. Do not drink alcohol. May cause drowsiness.",
        "known_interactions": "MAO inhibitors, SSRIs, Carbamazepine, Sedatives"
    },
    {
        "name": "Disprin",
        "generic_name": "Aspirin (Soluble)",
        "category": "Analgesic / Antiplatelet",
        "dosage_form": "Tablet",
        "standard_strength": "350mg",
        "before_after_food": "Dissolve in half a glass of water and drink immediately after food.",
        "common_uses": "Headache, migraine, toothache, acute emergency for suspected heart attack.",
        "side_effects": "Heartburn, gastric bleeding, tinnitus.",
        "warnings": "Never give to children under 16 years (risk of Reye's syndrome). Avoid on empty stomach.",
        "known_interactions": "Warfarin, Heparin, Methotrexate, Corticosteroids"
    },
    {
        "name": "Saridon",
        "generic_name": "Paracetamol + Propyphenazone + Caffeine",
        "category": "Analgesic & Antipyretic",
        "dosage_form": "Tablet",
        "standard_strength": "250mg + 150mg + 50mg",
        "before_after_food": "Take strictly after meals with plenty of water.",
        "common_uses": "Fast targeted relief from severe headache, migraine, toothache, and facial neuralgia.",
        "side_effects": "Restlessness, mild insomnia (from caffeine), nausea, gastric irritation.",
        "warnings": "Manufactured by Bayer. Contains caffeine; avoid taking late at night. Do not exceed 3 tablets in 24 hours. Not for children under 12.",
        "known_interactions": "Sedatives, Ephedrine, Other Paracetamol preparations"
    },
    {
        "name": "Paracetamol Tablets IP 650mg",
        "generic_name": "Paracetamol / Acetaminophen",
        "category": "Antipyretic / Analgesic",
        "dosage_form": "Tablet",
        "standard_strength": "650mg",
        "before_after_food": "Take strictly after food with water.",
        "common_uses": "Fever management and relief from mild to moderate pain.",
        "side_effects": "Rare mild stomach upset; liver toxicity only in overdose.",
        "warnings": "Do not exceed 4,000 mg in 24 hours. Maintain a minimum gap of 4 to 6 hours between doses.",
        "known_interactions": "Alcohol, Warfarin (chronic high dose)"
    },

    # 2. GASTROINTESTINAL & ACIDITY
    {
        "name": "Pantocid 40",
        "generic_name": "Pantoprazole",
        "category": "Proton Pump Inhibitor (PPI)",
        "dosage_form": "Tablet",
        "standard_strength": "40mg",
        "before_after_food": "Take 30-60 minutes before breakfast on an empty stomach.",
        "common_uses": "Gastric acidity, heartburn, gastroesophageal reflux disease (GERD), and peptic ulcers.",
        "side_effects": "Headache, mild diarrhea, flatulence, abdominal pain.",
        "warnings": "Swallow whole; do not chew or crush. Long-term use may cause magnesium deficiency.",
        "known_interactions": "Clopidogrel, Atazanavir, Iron supplements"
    },
    {
        "name": "Pan 40",
        "generic_name": "Pantoprazole",
        "category": "Proton Pump Inhibitor (PPI)",
        "dosage_form": "Tablet",
        "standard_strength": "40mg",
        "before_after_food": "Take once daily in morning, 30 minutes before first meal.",
        "common_uses": "Acid reflux, gastritis, gastric erosions, and prevention of NSAID-induced ulcers.",
        "side_effects": "Headache, nausea, dizziness.",
        "warnings": "Do not discontinue abruptly if on long term prescription.",
        "known_interactions": "Ketoconazole, Methotrexate, HIV protease inhibitors"
    },
    {
        "name": "Pan-D",
        "generic_name": "Pantoprazole + Domperidone",
        "category": "PPI + Prokinetic",
        "dosage_form": "Capsule",
        "standard_strength": "40mg + 30mg SR",
        "before_after_food": "Take strictly 30 minutes before breakfast on an empty stomach.",
        "common_uses": "Acid reflux accompanied by nausea, vomiting, fullness, and bloating.",
        "side_effects": "Dry mouth, headache, diarrhea.",
        "warnings": "Avoid in patients with cardiac conduction abnormalities (prolonged QT interval).",
        "known_interactions": "Amiodarone, Erythromycin, Ketoconazole"
    },
    {
        "name": "Pantocid-DSR",
        "generic_name": "Pantoprazole + Domperidone (Sustained Release)",
        "category": "PPI + Prokinetic",
        "dosage_form": "Capsule",
        "standard_strength": "40mg + 30mg SR",
        "before_after_food": "Take 30-60 minutes before morning breakfast with water.",
        "common_uses": "Severe acid reflux, dyspepsia, heartburn with persistent nausea and indigestion.",
        "side_effects": "Dry mouth, mild dizziness, abdominal cramps.",
        "warnings": "Do not open or chew the pellets inside the capsule.",
        "known_interactions": "Cardiac antiarrhythmics, Macrolide antibiotics"
    },
    {
        "name": "Omez 20",
        "generic_name": "Omeprazole",
        "category": "Proton Pump Inhibitor (PPI)",
        "dosage_form": "Capsule",
        "standard_strength": "20mg",
        "before_after_food": "Take 30 minutes before breakfast on an empty stomach.",
        "common_uses": "Stomach and duodenal ulcers, Zollinger-Ellison syndrome, and GERD.",
        "side_effects": "Stomach pain, gas, headache.",
        "warnings": "Long-term usage over 1 year requires bone density and vitamin B12 monitoring.",
        "known_interactions": "Clopidogrel (attenuates antiplatelet effect), Diazepam, Cilostazol"
    },
    {
        "name": "Omez-D",
        "generic_name": "Omeprazole + Domperidone",
        "category": "PPI + Antiemetic",
        "dosage_form": "Capsule",
        "standard_strength": "20mg + 10mg",
        "before_after_food": "Take 30 minutes before meal on empty stomach.",
        "common_uses": "Relief of acidity, nausea, vomiting, indigestion, and gas regurgitation.",
        "side_effects": "Dry mouth, headache, fatigue.",
        "warnings": "Do not take antacids simultaneously; maintain a 2-hour separation.",
        "known_interactions": "Clopidogrel, Digoxin"
    },
    {
        "name": "Rabekind-DSR",
        "generic_name": "Rabeprazole + Domperidone SR",
        "category": "PPI + Prokinetic",
        "dosage_form": "Capsule",
        "standard_strength": "20mg + 30mg SR",
        "before_after_food": "Take 30-45 minutes before morning breakfast.",
        "common_uses": "Rapid acid suppression, relief from gastric regurgitation and bloating.",
        "side_effects": "Mild diarrhea, headache, dry mouth.",
        "warnings": "Swallow capsule whole with water. Do not chew.",
        "known_interactions": "Atazanavir, Ketoconazole"
    },
    {
        "name": "Razo 20",
        "generic_name": "Rabeprazole Sodium",
        "category": "Proton Pump Inhibitor (PPI)",
        "dosage_form": "Tablet",
        "standard_strength": "20mg",
        "before_after_food": "Take 30 minutes before breakfast.",
        "common_uses": "Fast-acting relief from severe acidity, erosive esophagitis, and peptic ulcer.",
        "side_effects": "Headache, infection risk, constipation.",
        "warnings": "May decrease absorption of iron and vitamin B12 over prolonged use.",
        "known_interactions": "Warfarin, Digoxin, Methotrexate"
    },
    {
        "name": "Aciloc 150",
        "generic_name": "Ranitidine / Famotidine",
        "category": "H2 Receptor Blocker",
        "dosage_form": "Tablet",
        "standard_strength": "150mg",
        "before_after_food": "Take 30 minutes before meals or at bedtime.",
        "common_uses": "Reduces nighttime gastric acid secretion, heartburn, and sour burps.",
        "side_effects": "Drowsiness, headache, constipation.",
        "warnings": "Caution in patients with kidney dysfunction.",
        "known_interactions": "Antacids (reduce absorption), Theophylline"
    },
    {
        "name": "Aciloc 300",
        "generic_name": "Ranitidine / Famotidine",
        "category": "H2 Receptor Blocker",
        "dosage_form": "Tablet",
        "standard_strength": "300mg",
        "before_after_food": "Take once at bedtime or 30 minutes before evening meal.",
        "common_uses": "Healing active duodenal ulcers and Zollinger-Ellison syndrome.",
        "side_effects": "Headache, fatigue, mild diarrhea.",
        "warnings": "Dose adjustment required in renal insufficiency.",
        "known_interactions": "Ketoconazole, Warfarin"
    },
    {
        "name": "Digene",
        "generic_name": "Antacid (Magnesium + Aluminium Hydroxide + Simethicone)",
        "category": "Antacid & Antiflatulent",
        "dosage_form": "Tablet",
        "standard_strength": "Chewable",
        "before_after_food": "Chew 1-2 tablets thoroughly 30-60 minutes after meals or when acidity occurs.",
        "common_uses": "Immediate neutralization of stomach acid, heartburn, gas, and stomach heaviness.",
        "side_effects": "Constipation (from Aluminium) or mild laxative effect (from Magnesium).",
        "warnings": "Chew completely before swallowing. Do not take other oral medicines within 2 hours.",
        "known_interactions": "Tetracyclines, Ciprofloxacin, Iron supplements"
    },
    {
        "name": "Gelusil",
        "generic_name": "Aluminium Hydroxide + Magnesium Hydroxide + Dimethicone",
        "category": "Antacid & Antigas",
        "dosage_form": "Tablet",
        "standard_strength": "Chewable",
        "before_after_food": "Chew 1-2 tablets after meals and at bedtime.",
        "common_uses": "Fast soothing relief from acidity, heartburn, gas bubbles, and stomach bloating.",
        "side_effects": "Chalky taste, mild bowel habit changes.",
        "warnings": "Do not swallow whole; chew thoroughly for best efficacy.",
        "known_interactions": "Fluoroquinolones, Iron salts"
    },
    {
        "name": "Ondem 4",
        "generic_name": "Ondansetron",
        "category": "Antiemetic",
        "dosage_form": "Tablet",
        "standard_strength": "4mg",
        "before_after_food": "Take 30 minutes before food or before journey/chemotherapy.",
        "common_uses": "Prevents and treats nausea, vomiting due to gastroenteritis, food poisoning, or chemotherapy.",
        "side_effects": "Headache, constipation, sensation of warmth.",
        "warnings": "May dissolve rapidly on tongue (MD form). Caution in patients with electrolyte imbalances.",
        "known_interactions": "Amiodarone, Tramadol, Apomorphine"
    },
    {
        "name": "Vomikind 4",
        "generic_name": "Ondansetron (Fast Dissolving)",
        "category": "Antiemetic",
        "dosage_form": "Tablet",
        "standard_strength": "4mg",
        "before_after_food": "Place on tongue and allow to dissolve; take 30 mins before meals.",
        "common_uses": "Instant relief from vomiting and travel motion sickness.",
        "side_effects": "Headache, constipation, drowsiness.",
        "warnings": "Do not use with apomorphine.",
        "known_interactions": "Serotonergic drugs, Phenytoin"
    },
    {
        "name": "Domstal 10",
        "generic_name": "Domperidone",
        "category": "Prokinetic / Antiemetic",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take 15-30 minutes before meals with water.",
        "common_uses": "Relief from nausea, fullness, delayed gastric emptying, and regurgitation.",
        "side_effects": "Dry mouth, mild abdominal cramps.",
        "warnings": "Do not exceed recommended dose. Cardiac caution in patients over 60.",
        "known_interactions": "Ketoconazole, Erythromycin, QT-prolonging drugs"
    },
    {
        "name": "Eldoper",
        "generic_name": "Loperamide Hydrochloride",
        "category": "Antidiarrheal",
        "dosage_form": "Capsule",
        "standard_strength": "2mg",
        "before_after_food": "Take with water with or without food after each loose motion.",
        "common_uses": "Controls acute non-infectious diarrhea and chronic diarrhea.",
        "side_effects": "Constipation, abdominal cramps, dizziness.",
        "warnings": "Never take in bloody dysentery or high-fever bacterial diarrhea. Stop once stools become firm.",
        "known_interactions": "Ritonavir, Quinidine"
    },
    {
        "name": "Duphalac",
        "generic_name": "Lactulose",
        "category": "Osmotic Laxative",
        "dosage_form": "Syrup / Tablet",
        "standard_strength": "10g/15ml",
        "before_after_food": "Take preferably after breakfast or at bedtime with a full glass of water.",
        "common_uses": "Treats chronic constipation and prevents hepatic encephalopathy.",
        "side_effects": "Flatulence, bloating, mild cramps.",
        "warnings": "Drink plenty of water throughout the day. Diabetic patients should monitor blood sugar.",
        "known_interactions": "Antacids (reduce effect)"
    },

    # 3. ANTIHYPERTENSIVES & HEART MEDICINES
    {
        "name": "Telma 40",
        "generic_name": "Telmisartan",
        "category": "Antihypertensive (ARB)",
        "dosage_form": "Tablet",
        "standard_strength": "40mg",
        "before_after_food": "Take with or without food, preferably at the same time every morning.",
        "common_uses": "Controls high blood pressure (hypertension) and protects kidneys in diabetes.",
        "side_effects": "Dizziness, lightheadedness, sinus congestion, fatigue.",
        "warnings": "Contraindicated in pregnancy. Monitor blood pressure and serum potassium regularly.",
        "known_interactions": "Potassium supplements, ACE inhibitors, Lithium, NSAIDs"
    },
    {
        "name": "Telma 80",
        "generic_name": "Telmisartan",
        "category": "Antihypertensive (ARB)",
        "dosage_form": "Tablet",
        "standard_strength": "80mg",
        "before_after_food": "Take once daily in the morning with water.",
        "common_uses": "Management of moderate to severe hypertension and cardiovascular risk reduction.",
        "side_effects": "Low blood pressure upon standing, dizziness, back pain.",
        "warnings": "Do not skip doses. Stand up slowly from sitting or lying position.",
        "known_interactions": "Aliskiren, Spironolactone, Heparin"
    },
    {
        "name": "Telma-H",
        "generic_name": "Telmisartan + Hydrochlorothiazide",
        "category": "ARB + Thiazide Diuretic",
        "dosage_form": "Tablet",
        "standard_strength": "40mg + 12.5mg",
        "before_after_food": "Take in the morning with or after breakfast.",
        "common_uses": "Combined dual therapy for uncontrolled blood pressure.",
        "side_effects": "Increased urination, dizziness, dehydration, mild electrolyte shift.",
        "warnings": "Take in morning to avoid waking up at night to urinate. Monitor electrolytes.",
        "known_interactions": "Lithium, Digoxin, Diabetes medications"
    },
    {
        "name": "Telma-AM",
        "generic_name": "Telmisartan + Amlodipine",
        "category": "ARB + Calcium Channel Blocker",
        "dosage_form": "Tablet",
        "standard_strength": "40mg + 5mg",
        "before_after_food": "Take once daily at a fixed time with water.",
        "common_uses": "Synergistic control of stubborn high blood pressure and angina.",
        "side_effects": "Swelling in ankles/feet (peripheral edema), flushing, headache.",
        "warnings": "Report significant ankle swelling or persistent headache to doctor.",
        "known_interactions": "Simvastatin, Cyclosporine, Tacrolimus"
    },
    {
        "name": "Telmikem 40",
        "generic_name": "Telmisartan",
        "category": "Antihypertensive (ARB)",
        "dosage_form": "Tablet",
        "standard_strength": "40mg",
        "before_after_food": "Take once daily at the same time each day.",
        "common_uses": "Hypertension management and cardiovascular protection.",
        "side_effects": "Dizziness, fatigue, back pain.",
        "warnings": "Do not take potassium-based salt substitutes without consulting your physician.",
        "known_interactions": "NSAIDs, Lithium"
    },
    {
        "name": "Amlong 5",
        "generic_name": "Amlodipine Besylate",
        "category": "Calcium Channel Blocker",
        "dosage_form": "Tablet",
        "standard_strength": "5mg",
        "before_after_food": "Take with or without food at the same time every day.",
        "common_uses": "Lowers high blood pressure and prevents chest pain (angina pectoris).",
        "side_effects": "Swelling in feet/ankles, dizziness, facial flushing, palpitations.",
        "warnings": "Avoid grapefruit juice. Do not stop taking abruptly without medical advice.",
        "known_interactions": "Simvastatin (limit to 20mg), Diltiazem, Clarithromycin"
    },
    {
        "name": "Amlong 10",
        "generic_name": "Amlodipine Besylate",
        "category": "Calcium Channel Blocker",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take once daily with water.",
        "common_uses": "Targeted reduction of severe hypertension and chronic stable angina.",
        "side_effects": "Peripheral edema (ankle swelling), headache, fatigue.",
        "warnings": "Elevate feet while resting if mild ankle swelling occurs.",
        "known_interactions": "Cyclosporine, Dantrolene"
    },
    {
        "name": "Cilacar 10",
        "generic_name": "Cilnidipine",
        "category": "Dual L/N-type Calcium Channel Blocker",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Controls high blood pressure with lower risk of ankle swelling; renal protective.",
        "side_effects": "Mild headache, dizziness, flushing.",
        "warnings": "Good choice for hypertensive patients with kidney disease or diabetic nephropathy.",
        "known_interactions": "Rifampicin, Cimetidine"
    },
    {
        "name": "Cilacar 20",
        "generic_name": "Cilnidipine",
        "category": "Dual Calcium Channel Blocker",
        "dosage_form": "Tablet",
        "standard_strength": "20mg",
        "before_after_food": "Take once daily with water.",
        "common_uses": "Management of moderate to severe hypertension and reduction of proteinuria.",
        "side_effects": "Dizziness, palpitations, flushing.",
        "warnings": "Do not abruptly discontinue; taper dose under physician supervision.",
        "known_interactions": "Antihypertensives, Digoxin"
    },
    {
        "name": "Met XL 25",
        "generic_name": "Metoprolol Succinate (Extended Release)",
        "category": "Beta Blocker (Cardioselective)",
        "dosage_form": "Tablet",
        "standard_strength": "25mg",
        "before_after_food": "Take with or immediately after food.",
        "common_uses": "Slows rapid heart rate, manages hypertension, angina, and prevents heart failure.",
        "side_effects": "Slow heart rate (bradycardia), fatigue, cold hands/feet, dizziness.",
        "warnings": "Do not stop suddenly (may trigger rebound hypertension or heart attack). Avoid in severe asthma.",
        "known_interactions": "Verapamil, Diltiazem, Amiodarone, Clonidine"
    },
    {
        "name": "Met XL 50",
        "generic_name": "Metoprolol Succinate (Extended Release)",
        "category": "Beta Blocker (Cardioselective)",
        "dosage_form": "Tablet",
        "standard_strength": "50mg",
        "before_after_food": "Take once daily in morning with or after breakfast.",
        "common_uses": "Long-term control of high blood pressure, prevention of heart attack, and atrial fibrillation.",
        "side_effects": "Tiredness, low pulse rate, sleep disturbances.",
        "warnings": "Swallow tablet whole; do not chew or crush. Monitor resting heart rate.",
        "known_interactions": "Digoxin, Antiarrhythmics, Epinephrine"
    },
    {
        "name": "Betaloc 25",
        "generic_name": "Metoprolol Tartrate",
        "category": "Beta Blocker",
        "dosage_form": "Tablet",
        "standard_strength": "25mg",
        "before_after_food": "Take with meals or immediately after eating.",
        "common_uses": "Acute coronary syndrome, arrhythmia, and hypertension.",
        "side_effects": "Fatigue, slow heart rate, dizziness.",
        "warnings": "Check heart rate prior to taking. If pulse is under 55 bpm, consult doctor.",
        "known_interactions": "Fluoxetine, Paroxetine, Quinidine"
    },
    {
        "name": "Nebicard 5",
        "generic_name": "Nebivolol",
        "category": "Third-Generation Beta Blocker",
        "dosage_form": "Tablet",
        "standard_strength": "5mg",
        "before_after_food": "Take once daily at the same time, with or without food.",
        "common_uses": "Lowers blood pressure with nitric-oxide mediated vasodilation; lower erectile dysfunction risk.",
        "side_effects": "Headache, dizziness, tiredness, numbness in extremities.",
        "warnings": "Contraindicated in severe heart block or severe liver damage.",
        "known_interactions": "CYP2D6 inhibitors, Calcium channel blockers"
    },
    {
        "name": "Envas 5",
        "generic_name": "Enalapril Maleate",
        "category": "ACE Inhibitor",
        "dosage_form": "Tablet",
        "standard_strength": "5mg",
        "before_after_food": "Take with or without food at the same time each day.",
        "common_uses": "Hypertension, congestive heart failure, and prevention of left ventricular dysfunction.",
        "side_effects": "Dry persistent cough, dizziness, elevated potassium.",
        "warnings": "Dry cough is a common side effect. Contraindicated in pregnancy.",
        "known_interactions": "Potassium supplements, NSAIDs, Lithium"
    },
    {
        "name": "Losar 50",
        "generic_name": "Losartan Potassium",
        "category": "Antihypertensive (ARB)",
        "dosage_form": "Tablet",
        "standard_strength": "50mg",
        "before_after_food": "Take once daily with water.",
        "common_uses": "Lowers blood pressure, prevents stroke in patients with cardiomegaly, and treats diabetic kidney disease.",
        "side_effects": "Dizziness, nasal congestion, back pain.",
        "warnings": "Do not use during pregnancy. Keep hydrated.",
        "known_interactions": "Potassium-sparing diuretics, Fluconazole, Lithium"
    },
    {
        "name": "Lasix 40",
        "generic_name": "Furosemide",
        "category": "Loop Diuretic (Water Pill)",
        "dosage_form": "Tablet",
        "standard_strength": "40mg",
        "before_after_food": "Take in the morning after breakfast with a full glass of water.",
        "common_uses": "Rapid removal of excess fluid and swelling (edema) in heart failure, kidney disease, or liver cirrhosis.",
        "side_effects": "Frequent urination, dehydration, low potassium (hypokalemia), dizziness.",
        "warnings": "Never take at night to avoid sleep disruption. Doctor may prescribe potassium supplement alongside.",
        "known_interactions": "Digoxin, Aminoglycosides, NSAIDs, Lithium"
    },
    {
        "name": "Dytor 10",
        "generic_name": "Torsemide",
        "category": "Loop Diuretic",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take in the morning with water.",
        "common_uses": "Treats fluid retention and high blood pressure associated with heart failure.",
        "side_effects": "Frequent urination, weakness, thirst, muscle cramps.",
        "warnings": "Monitor weight, blood pressure, and electrolytes.",
        "known_interactions": "ACE inhibitors, Cholestyramine, Probenecid"
    },
    {
        "name": "Sorbitrate 5",
        "generic_name": "Isosorbide Dinitrate",
        "category": "Nitrate Vasodilator",
        "dosage_form": "Tablet",
        "standard_strength": "5mg (Sublingual)",
        "before_after_food": "Place tablet under the tongue (sublingual) during acute chest pain episodes.",
        "common_uses": "Immediate relief and prevention of angina pectoris (heart chest pain).",
        "side_effects": "Severe headache, facial flushing, sudden drop in blood pressure, dizziness.",
        "warnings": "ABSOLUTELY CONTRAINDICATED with Sildenafil (Viagra) or Tadalafil (leads to fatal drop in BP). Sit down while taking.",
        "known_interactions": "Sildenafil, Tadalafil, Vardenafil, Alcohol"
    },

    # 4. CHOLESTEROL & BLOOD THINNERS
    {
        "name": "Atorva 10",
        "generic_name": "Atorvastatin",
        "category": "Statin / Lipid Lowering",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take once daily in the evening/night, with or without food.",
        "common_uses": "Lowers bad cholesterol (LDL) and triglycerides, reduces risk of heart attack and stroke.",
        "side_effects": "Muscle aches, mild liver enzyme elevation, joint pain.",
        "warnings": "Report unexplained muscle pain or brown urine immediately. Avoid large amounts of grapefruit juice.",
        "known_interactions": "Clarithromycin, Cyclosporine, Gemfibrozil, Itraconazole"
    },
    {
        "name": "Atorva 20",
        "generic_name": "Atorvastatin",
        "category": "Statin / Lipid Lowering",
        "dosage_form": "Tablet",
        "standard_strength": "20mg",
        "before_after_food": "Take at night with water.",
        "common_uses": "Intensive cholesterol reduction in patients with coronary artery disease or past stent/bypass.",
        "side_effects": "Muscle stiffness, digestive upset, elevated blood sugar.",
        "warnings": "Periodic liver function testing (SGOT/SGPT) recommended.",
        "known_interactions": "Erythromycin, Diltiazem, Protease inhibitors"
    },
    {
        "name": "Atorva 40",
        "generic_name": "Atorvastatin",
        "category": "High-Intensity Statin",
        "dosage_form": "Tablet",
        "standard_strength": "40mg",
        "before_after_food": "Take once daily at night.",
        "common_uses": "High-intensity lipid lowering following acute coronary syndrome, heart attack, or ischemic stroke.",
        "side_effects": "Muscle soreness, fatigue, mild headache.",
        "warnings": "Do not skip doses. Strictly report any severe muscle tenderness.",
        "known_interactions": "Colchicine, Niacin, Fibrates"
    },
    {
        "name": "Rosuvas 10",
        "generic_name": "Rosuvastatin",
        "category": "Statin / Lipid Lowering",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take once daily at any time of day, with or without food.",
        "common_uses": "Potent reduction of LDL cholesterol and prevention of atherosclerotic cardiovascular events.",
        "side_effects": "Muscle ache, nausea, abdominal pain, headache.",
        "warnings": "Advise doctor if you have thyroid disorders or heavy alcohol history.",
        "known_interactions": "Antacids (take 2 hours apart), Cyclosporine, Warfarin"
    },
    {
        "name": "Rosuvas 20",
        "generic_name": "Rosuvastatin",
        "category": "High-Intensity Statin",
        "dosage_form": "Tablet",
        "standard_strength": "20mg",
        "before_after_food": "Take at a fixed time each day with water.",
        "common_uses": "Significant reduction of high cholesterol in familial hypercholesterolemia and vascular disease.",
        "side_effects": "Muscle weakness, joint aches, mild headache.",
        "warnings": "Do not use during pregnancy or breastfeeding.",
        "known_interactions": "Protease inhibitors, Gemfibrozil, Fenofibrate"
    },
    {
        "name": "Ecosprin 75",
        "generic_name": "Aspirin (Enteric Coated)",
        "category": "Antiplatelet / Blood Thinner",
        "dosage_form": "Tablet",
        "standard_strength": "75mg",
        "before_after_food": "Take strictly after meals with plenty of water.",
        "common_uses": "Prevents blood clots, secondary prevention of heart attacks and ischemic strokes.",
        "side_effects": "Indigestion, minor bruising, prolonged bleeding from cuts.",
        "warnings": "Enteric coating protects stomach. Swallow whole; do not crush. Consult surgeon before any dental extraction.",
        "known_interactions": "Warfarin, Heparin, Ibuprofen (blocks aspirin action), Methotrexate"
    },
    {
        "name": "Ecosprin 150",
        "generic_name": "Aspirin (Enteric Coated)",
        "category": "Antiplatelet / Blood Thinner",
        "dosage_form": "Tablet",
        "standard_strength": "150mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Blood thinner for patients with coronary stents, peripheral artery disease, or high stroke risk.",
        "side_effects": "Stomach irritation, increased bleeding tendency, acid reflux.",
        "warnings": "Do not take on an empty stomach. Watch for signs of dark black stools or unusual bleeding.",
        "known_interactions": "NSAIDs, Anticoagulants, Ginkgo Biloba"
    },
    {
        "name": "Clopilet 75",
        "generic_name": "Clopidogrel",
        "category": "Antiplatelet / Blood Thinner",
        "dosage_form": "Tablet",
        "standard_strength": "75mg",
        "before_after_food": "Take with or without food at the same time each day.",
        "common_uses": "Prevents blood clots inside coronary stents, prevents recurrent heart attack and stroke.",
        "side_effects": "Bruising, nosebleeds, mild diarrhea, bleeding.",
        "warnings": "Inform doctor before any surgery. Omeprazole may reduce its effectiveness; Pantoprazole is preferred.",
        "known_interactions": "Omeprazole, Warfarin, NSAIDs, SSRIs"
    },
    {
        "name": "Deplatt 75",
        "generic_name": "Clopidogrel",
        "category": "Antiplatelet / Blood Thinner",
        "dosage_form": "Tablet",
        "standard_strength": "75mg",
        "before_after_food": "Take once daily with water.",
        "common_uses": "Platelet inhibitor used post-angioplasty and in acute coronary syndromes.",
        "side_effects": "Easy bruising, bleeding.",
        "warnings": "Do not discontinue abruptly without cardiologist instructions.",
        "known_interactions": "Aspirin (synergistic bleeding), Dabigatran"
    },
    {
        "name": "Warf 2mg",
        "generic_name": "Warfarin Sodium",
        "category": "Anticoagulant (Vitamin K Antagonist)",
        "dosage_form": "Tablet",
        "standard_strength": "2mg",
        "before_after_food": "Take at the exact same time every evening with or without food.",
        "common_uses": "Prevents and treats deep vein thrombosis (DVT), pulmonary embolism, and stroke in atrial fibrillation/heart valves.",
        "side_effects": "Bleeding, bruising, dark urine, gum bleeding.",
        "warnings": "Requires regular INR blood test monitoring. Keep dietary green leafy vegetables (Vitamin K) intake consistent.",
        "known_interactions": "Aspirin, NSAIDs, Antibiotics, Alcohol, Vitamin K, Cranberry juice"
    },
    {
        "name": "Brilinta 90",
        "generic_name": "Ticagrelor",
        "category": "Antiplatelet Agent",
        "dosage_form": "Tablet",
        "standard_strength": "90mg",
        "before_after_food": "Take twice daily (morning & night), with or without food.",
        "common_uses": "Prevents stent thrombosis and heart attack in high-risk post-angioplasty patients.",
        "side_effects": "Shortness of breath (dyspnea), bleeding, bruising.",
        "warnings": "Do not skip doses due to twice-daily dosing requirement. Mild breathlessness often subsides.",
        "known_interactions": "High dose aspirin (>100mg), Strong CYP3A4 inhibitors, Ketoconazole"
    },

    # 5. DIABETES & BLOOD GLUCOSE MANAGEMENT
    {
        "name": "Glycomet 500",
        "generic_name": "Metformin Hydrochloride",
        "category": "Antidiabetic (Biguanide)",
        "dosage_form": "Tablet",
        "standard_strength": "500mg",
        "before_after_food": "Take with or immediately after meals with a glass of water.",
        "common_uses": "First-line medicine for type 2 diabetes; lowers insulin resistance and blood sugar.",
        "side_effects": "Nausea, flatulence, abdominal bloating, metallic taste, diarrhea.",
        "warnings": "Always take with food to minimize stomach upset. Avoid excess alcohol. Discontinue temporarily before CT scan contrast dye.",
        "known_interactions": "Alcohol (lactic acidosis risk), Iodinated contrast, Cimetidine"
    },
    {
        "name": "Glycomet 850",
        "generic_name": "Metformin Hydrochloride",
        "category": "Antidiabetic (Biguanide)",
        "dosage_form": "Tablet",
        "standard_strength": "850mg",
        "before_after_food": "Take with breakfast or dinner.",
        "common_uses": "Blood sugar regulation in type 2 diabetes mellitus and polycystic ovary syndrome (PCOS).",
        "side_effects": "Gastrointestinal discomfort, loose stools.",
        "warnings": "Monitor kidney function (eGFR). Do not take in severe renal failure.",
        "known_interactions": "Furosemide, Nifedipine, Topiramate"
    },
    {
        "name": "Glycomet-GP 1",
        "generic_name": "Glimepiride + Metformin SR",
        "category": "Sulfonylurea + Biguanide Combination",
        "dosage_form": "Tablet",
        "standard_strength": "1mg + 500mg SR",
        "before_after_food": "Take with breakfast or first main meal of the day.",
        "common_uses": "Dual action for type 2 diabetes: increases insulin secretion and improves insulin sensitivity.",
        "side_effects": "Low blood sugar (hypoglycemia), sweating, dizziness, stomach upset.",
        "warnings": "Never skip meals after taking this tablet. Always carry glucose sweets in case of shakiness or hypoglycemia.",
        "known_interactions": "Beta blockers (mask hypoglycemia signs), Fluconazole, Alcohol"
    },
    {
        "name": "Glycomet-GP 2",
        "generic_name": "Glimepiride + Metformin SR",
        "category": "Sulfonylurea + Biguanide Combination",
        "dosage_form": "Tablet",
        "standard_strength": "2mg + 500mg SR",
        "before_after_food": "Take immediately before or with breakfast.",
        "common_uses": "Advanced control of fasting and postprandial glucose levels in type 2 diabetes.",
        "side_effects": "Risk of low blood sugar (hypoglycemia), hunger, tremors, mild nausea.",
        "warnings": "Educate family members on hypoglycemia management. Swallow tablet whole.",
        "known_interactions": "Clarithromycin, Salicylates, Sulfonamides"
    },
    {
        "name": "Januvia 100",
        "generic_name": "Sitagliptin",
        "category": "DPP-4 Inhibitor",
        "dosage_form": "Tablet",
        "standard_strength": "100mg",
        "before_after_food": "Take once daily with or without food.",
        "common_uses": "Boosts natural incretin hormones to stimulate insulin when glucose is high; weight-neutral.",
        "side_effects": "Upper respiratory tract symptoms, headache, sore throat.",
        "warnings": "Low risk of hypoglycemia when used alone. Report persistent severe abdominal pain (pancreatitis).",
        "known_interactions": "Digoxin (slight concentration increase)"
    },
    {
        "name": "Janumet 50/500",
        "generic_name": "Sitagliptin + Metformin",
        "category": "DPP-4 Inhibitor + Biguanide",
        "dosage_form": "Tablet",
        "standard_strength": "50mg + 500mg",
        "before_after_food": "Take twice daily with meals.",
        "common_uses": "Effective dual blood sugar control with low hypoglycemia risk.",
        "side_effects": "Nausea, diarrhea, metallic taste.",
        "warnings": "Take strictly with food to protect stomach.",
        "known_interactions": "Alcohol, Carbonic anhydrase inhibitors"
    },
    {
        "name": "Galvus 50",
        "generic_name": "Vildagliptin",
        "category": "DPP-4 Inhibitor",
        "dosage_form": "Tablet",
        "standard_strength": "50mg",
        "before_after_food": "Take once or twice daily with or without food.",
        "common_uses": "Controls blood glucose spikes in adult type 2 diabetics.",
        "side_effects": "Headache, mild dizziness, constipation.",
        "warnings": "Routine liver function tests recommended during the first year of therapy.",
        "known_interactions": "ACE inhibitors (slight angioedema risk)"
    },
    {
        "name": "Galvus Met 50/500",
        "generic_name": "Vildagliptin + Metformin",
        "category": "DPP-4 + Biguanide",
        "dosage_form": "Tablet",
        "standard_strength": "50mg + 500mg",
        "before_after_food": "Take twice daily with breakfast and dinner.",
        "common_uses": "Comprehensive management of fasting and post-meal glucose.",
        "side_effects": "Stomach fullness, nausea, diarrhea.",
        "warnings": "Take during or after food. Stay well hydrated.",
        "known_interactions": "Alcohol, Diuretics"
    },
    {
        "name": "Jardiance 10",
        "generic_name": "Empagliflozin",
        "category": "SGLT2 Inhibitor",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take in the morning with or without food.",
        "common_uses": "Removes excess glucose through urine; protects heart and kidneys and aids weight loss.",
        "side_effects": "Increased urination, genital fungal infections, dehydration, thirst.",
        "warnings": "Maintain good intimate hygiene and drink ample water throughout the day.",
        "known_interactions": "Diuretics (additive dehydration), Insulin"
    },
    {
        "name": "Jardiance 25",
        "generic_name": "Empagliflozin",
        "category": "SGLT2 Inhibitor",
        "dosage_form": "Tablet",
        "standard_strength": "25mg",
        "before_after_food": "Take in the morning with water.",
        "common_uses": "Potent glycemic control, reduction of cardiovascular death in diabetic and heart failure patients.",
        "side_effects": "Frequent urination, dizziness, urinary tract infection.",
        "warnings": "Stop temporarily during acute illnesses or major surgery to avoid euglycemic ketoacidosis.",
        "known_interactions": "Sulfonylureas, Loop diuretics"
    },
    {
        "name": "Forxiga 10",
        "generic_name": "Dapagliflozin",
        "category": "SGLT2 Inhibitor",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take once daily in the morning with or without food.",
        "common_uses": "Lowers blood sugar, approved for heart failure (HFrEF) and chronic kidney disease (CKD).",
        "side_effects": "Increased urination, fungal infection, low blood pressure.",
        "warnings": "Drink plenty of water. Monitor blood pressure if on multiple BP medicines.",
        "known_interactions": "Thiazide diuretics, Glimepiride"
    },
    {
        "name": "Rybelsus 3",
        "generic_name": "Semaglutide (Oral GLP-1)",
        "category": "GLP-1 Receptor Agonist",
        "dosage_form": "Tablet",
        "standard_strength": "3mg",
        "before_after_food": "Take first thing in morning with no more than half a glass of plain water; wait 30 mins before eating or drinking.",
        "common_uses": "Type 2 diabetes glycemic control and significant weight loss.",
        "side_effects": "Nausea, vomiting, diarrhea, decreased appetite.",
        "warnings": "Strict absorption rule: must take on empty stomach with plain water only; wait 30 minutes before any food/tea/coffee.",
        "known_interactions": "Oral medications taken simultaneously (may delay absorption)"
    },
    {
        "name": "Rybelsus 7",
        "generic_name": "Semaglutide (Oral GLP-1)",
        "category": "GLP-1 Receptor Agonist",
        "dosage_form": "Tablet",
        "standard_strength": "7mg",
        "before_after_food": "Take first thing in the morning with sip of water, 30 minutes before breakfast.",
        "common_uses": "Advanced maintenance dose for blood sugar reduction and medical weight loss.",
        "side_effects": "Nausea, burping, constipation, heartburn.",
        "warnings": "Swallow tablet whole; do not cut, crush, or chew.",
        "known_interactions": "Insulin, Sulfonylureas"
    },
    {
        "name": "Amaryl 1",
        "generic_name": "Glimepiride",
        "category": "Sulfonylurea",
        "dosage_form": "Tablet",
        "standard_strength": "1mg",
        "before_after_food": "Take immediately before or with breakfast.",
        "common_uses": "Stimulates pancreatic beta cells to produce insulin in type 2 diabetes.",
        "side_effects": "Hypoglycemia (low blood sugar), hunger, sweating, weight gain.",
        "warnings": "Do not skip meals after taking this tablet. Carry candy or glucose packets.",
        "known_interactions": "Fluconazole, Miconazole, NSAIDs"
    },
    {
        "name": "Amaryl 2",
        "generic_name": "Glimepiride",
        "category": "Sulfonylurea",
        "dosage_form": "Tablet",
        "standard_strength": "2mg",
        "before_after_food": "Take with breakfast.",
        "common_uses": "Post-prandial and fasting blood sugar reduction in type 2 diabetes.",
        "side_effects": "Low blood sugar, shakiness, dizziness.",
        "warnings": "Elderly patients must be closely monitored for hypoglycemia.",
        "known_interactions": "Beta blockers, Clarithromycin"
    },
    {
        "name": "Teneliglip 20",
        "generic_name": "Teneligliptin",
        "category": "DPP-4 Inhibitor",
        "dosage_form": "Tablet",
        "standard_strength": "20mg",
        "before_after_food": "Take once daily with or without food.",
        "common_uses": "Affordable DPP-4 inhibitor safe in patients with renal impairment; controls glucose spikes.",
        "side_effects": "Hypoglycemia (if combined), constipation, nausea.",
        "warnings": "Safe to use without dose adjustment in renal disease.",
        "known_interactions": "Sulfonylureas"
    },
    {
        "name": "Volibo 0.2",
        "generic_name": "Voglibose",
        "category": "Alpha-Glucosidase Inhibitor",
        "dosage_form": "Tablet",
        "standard_strength": "0.2mg",
        "before_after_food": "Take strictly with the first bite of each main meal.",
        "common_uses": "Slows intestinal carbohydrate digestion to prevent sharp spikes in blood sugar right after eating.",
        "side_effects": "Flatulence, abdominal distension, soft stools.",
        "warnings": "Must be taken with the first bite of food to work. In case of hypoglycemia, use pure dextrose/glucose, not sucrose (table sugar).",
        "known_interactions": "Digestive enzymes, Antacids"
    },

    # 6. ANTIBIOTICS & ANTI-INFECTIVES
    {
        "name": "Augmentin 625",
        "generic_name": "Amoxicillin + Potassium Clavulanate",
        "category": "Broad-Spectrum Antibacterial",
        "dosage_form": "Tablet",
        "standard_strength": "625mg",
        "before_after_food": "Take at the start of a meal to optimize absorption and reduce stomach upset.",
        "common_uses": "Bacterial respiratory tract infections, sinusitis, bronchitis, skin infections, dental abscess, and UTI.",
        "side_effects": "Mild diarrhea, nausea, vomiting, candidiasis (yeast overgrowth).",
        "warnings": "Complete the full 5-7 day course even if feeling better. Strictly contraindicated in penicillin allergy.",
        "known_interactions": "Methotrexate, Oral contraceptives, Allopurinol, Warfarin"
    },
    {
        "name": "Amoxyclav 625",
        "generic_name": "Amoxicillin + Potassium Clavulanate",
        "category": "Broad-Spectrum Antibacterial",
        "dosage_form": "Tablet",
        "standard_strength": "625mg",
        "before_after_food": "Take at the beginning of a meal with water.",
        "common_uses": "Ear, nose, throat, lung, urinary, and skin bacterial infections.",
        "side_effects": "Diarrhea, loose motions, stomach ache.",
        "warnings": "Drink plenty of fluids. Consider taking a probiotic like Econorm to protect gut flora.",
        "known_interactions": "Probenecid, Oral Typhoid vaccine"
    },
    {
        "name": "Moxikind-CV 625",
        "generic_name": "Amoxicillin + Clavulanic Acid",
        "category": "Antibiotic",
        "dosage_form": "Tablet",
        "standard_strength": "625mg",
        "before_after_food": "Take with meals.",
        "common_uses": "Bacterial pneumonia, acute otitis media, tonsillitis, and post-surgical wound infections.",
        "side_effects": "Nausea, diarrhea, skin rash.",
        "warnings": "Do not skip doses. Never take for viral infections like common cold or flu.",
        "known_interactions": "Anticoagulants, Allopurinol"
    },
    {
        "name": "Novamox 500",
        "generic_name": "Amoxicillin",
        "category": "Penicillin Antibiotic",
        "dosage_form": "Capsule",
        "standard_strength": "500mg",
        "before_after_food": "Take every 8 hours with or without food.",
        "common_uses": "Streptococcal throat infection, mild pneumonia, dental infections, and ear infections.",
        "side_effects": "Skin rash, diarrhea, nausea.",
        "warnings": "Check for penicillin allergy before taking.",
        "known_interactions": "Methotrexate, Birth control pills"
    },
    {
        "name": "Azithral 500",
        "generic_name": "Azithromycin",
        "category": "Macrolide Antibiotic",
        "dosage_form": "Tablet",
        "standard_strength": "500mg",
        "before_after_food": "Take 1 hour before food or 2 hours after food with a full glass of water.",
        "common_uses": "Throat infections (pharyngitis/tonsillitis), typhoid, chest infections, sinusitis, and chlamydia.",
        "side_effects": "Nausea, diarrhea, abdominal cramps, mild headache.",
        "warnings": "Usually prescribed once daily for 3 or 5 days. Complete full course. Cardiac caution if history of arrhythmias.",
        "known_interactions": "Antacids (reduce absorption), Digoxin, Warfarin, Amiodarone"
    },
    {
        "name": "Azee 500",
        "generic_name": "Azithromycin",
        "category": "Macrolide Antibiotic",
        "dosage_form": "Tablet",
        "standard_strength": "500mg",
        "before_after_food": "Take once daily on an empty stomach (1 hr before or 2 hrs after meal).",
        "common_uses": "Bacterial throat infections, acute bronchitis, community-acquired pneumonia, and skin infections.",
        "side_effects": "Stomach upset, loose stools, nausea.",
        "warnings": "Do not take antacids containing aluminium or magnesium at the same time.",
        "known_interactions": "Pimozide, Astemizole, Ergot alkaloids"
    },
    {
        "name": "Cifran 500",
        "generic_name": "Ciprofloxacin",
        "category": "Fluoroquinolone Antibiotic",
        "dosage_form": "Tablet",
        "standard_strength": "500mg",
        "before_after_food": "Take with or without food. Avoid dairy products (milk, curd) within 2 hours of dose.",
        "common_uses": "Urinary tract infections (UTI), bacterial gastroenteritis, bone infections, and typhoid.",
        "side_effects": "Nausea, diarrhea, dizziness, tendon tenderness.",
        "warnings": "Do not take with milk, calcium, or antacids. Report tendon pain (especially Achilles tendon) immediately.",
        "known_interactions": "Theophylline, Tizanidine, Iron supplements, Antacids"
    },
    {
        "name": "Ciplox 500",
        "generic_name": "Ciprofloxacin",
        "category": "Fluoroquinolone Antibiotic",
        "dosage_form": "Tablet",
        "standard_strength": "500mg",
        "before_after_food": "Take every 12 hours with plenty of water. Avoid milk/calcium.",
        "common_uses": "Severe UTI, infectious diarrhea, respiratory infections, and pelvic infections.",
        "side_effects": "Headache, nausea, photosensitivity (sunburn).",
        "warnings": "Avoid excessive exposure to direct sunlight. Drink at least 8 glasses of water daily.",
        "known_interactions": "Warfarin, Methotrexate, Multivitamins with zinc"
    },
    {
        "name": "Taxim-O 200",
        "generic_name": "Cefixime",
        "category": "Third-Generation Cephalosporin",
        "dosage_form": "Tablet",
        "standard_strength": "200mg",
        "before_after_food": "Take with or after food with water.",
        "common_uses": "Typhoid fever, acute otitis media, urinary tract infections, and uncomplicated gonorrhea.",
        "side_effects": "Diarrhea, loose motions, gas, abdominal pain.",
        "warnings": "Effective against gram-negative bacteria. Complete prescribed duration.",
        "known_interactions": "Carbamazepine, Warfarin"
    },
    {
        "name": "Mahacef 200",
        "generic_name": "Cefixime",
        "category": "Cephalosporin Antibiotic",
        "dosage_form": "Tablet",
        "standard_strength": "200mg",
        "before_after_food": "Take twice daily after meals with water.",
        "common_uses": "Bacterial infections of the respiratory and urinary tracts, and enteric fever.",
        "side_effects": "Stomach upset, indigestion, rash.",
        "warnings": "Inform doctor if you have history of severe cephalosporin or penicillin allergy.",
        "known_interactions": "Probenecid, Anticoagulants"
    },
    {
        "name": "Monocef-O 200",
        "generic_name": "Cefpodoxime Proxetil",
        "category": "Third-Generation Cephalosporin",
        "dosage_form": "Tablet",
        "standard_strength": "200mg",
        "before_after_food": "Take strictly with or after meals to enhance absorption.",
        "common_uses": "Bacterial sinusitis, throat infections, community pneumonia, and skin infections.",
        "side_effects": "Diarrhea, nausea, fungal infection, headache.",
        "warnings": "Absorption is significantly higher when taken with food.",
        "known_interactions": "Antacids, H2 blockers (reduce absorption)"
    },
    {
        "name": "Gudcef 200",
        "generic_name": "Cefpodoxime Proxetil",
        "category": "Cephalosporin Antibiotic",
        "dosage_form": "Tablet",
        "standard_strength": "200mg",
        "before_after_food": "Take with meals with water.",
        "common_uses": "Ear infections, bronchitis, tonsillitis, and uncomplicated urinary infections.",
        "side_effects": "Loose stools, nausea, vaginal itching.",
        "warnings": "Complete the full antibiotic regimen.",
        "known_interactions": "PPIs, Antacids"
    },
    {
        "name": "Doxy-1 100",
        "generic_name": "Doxycycline",
        "category": "Tetracycline Antibiotic",
        "dosage_form": "Capsule",
        "standard_strength": "100mg",
        "before_after_food": "Take with a full glass of water while sitting or standing upright; do NOT lie down for 30 minutes.",
        "common_uses": "Acne vulgaris, scrub typhus, malaria prophylaxis, respiratory and sexually transmitted infections.",
        "side_effects": "Esophageal irritation/ulcer, photosensitivity, stomach ache.",
        "warnings": "NEVER lie down immediately after taking (causes severe throat/esophagus ulcers). Avoid milk and antacids within 2 hours. Not for pregnant women or children under 8.",
        "known_interactions": "Dairy products, Iron, Antacids, Isotretinoin, Penicillin"
    },
    {
        "name": "Zenflox 200",
        "generic_name": "Ofloxacin",
        "category": "Fluoroquinolone Antibiotic",
        "dosage_form": "Tablet",
        "standard_strength": "200mg",
        "before_after_food": "Take with or without food with plenty of water.",
        "common_uses": "Pelvic inflammatory disease, urinary infections, bronchitis, and diarrhea.",
        "side_effects": "Nausea, insomnia, headache, dizziness.",
        "warnings": "Avoid taking with magnesium/aluminium antacids or iron supplements.",
        "known_interactions": "Sucralfate, Theophylline, Didanosine"
    },
    {
        "name": "Oflox 200",
        "generic_name": "Ofloxacin",
        "category": "Fluoroquinolone Antibiotic",
        "dosage_form": "Tablet",
        "standard_strength": "200mg",
        "before_after_food": "Take twice daily with water.",
        "common_uses": "Infections of the skin, soft tissues, urinary tract, and respiratory tract.",
        "side_effects": "Dizziness, sleep disturbances, nausea.",
        "warnings": "Keep well hydrated throughout the day.",
        "known_interactions": "Caffeine, Glipizide"
    },
    {
        "name": "Norflox-TZ",
        "generic_name": "Norfloxacin + Tinidazole",
        "category": "Antibiotic + Antiprotozoal",
        "dosage_form": "Tablet",
        "standard_strength": "400mg + 600mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Acute infectious diarrhea, amoebiasis, giardiasis, and mixed bacterial-protozoal dysentery.",
        "side_effects": "Metallic taste in mouth, nausea, dark urine, headache.",
        "warnings": "ABSOLUTELY AVOID ALCOHOL during treatment and for 3 days after (triggers severe disulfiram-like vomiting/cramping reaction).",
        "known_interactions": "Alcohol, Warfarin, Cyclosporine"
    },
    {
        "name": "Metrogyl 400",
        "generic_name": "Metronidazole",
        "category": "Antiprotozoal & Anaerobic Antibacterial",
        "dosage_form": "Tablet",
        "standard_strength": "400mg",
        "before_after_food": "Take during or after meals with water.",
        "common_uses": "Amoebic dysentery, dental root infections, anaerobic pelvic infections, and H. pylori.",
        "side_effects": "Strong metallic taste, dark/reddish urine, nausea, coated tongue.",
        "warnings": "STRICTLY FORBIDDEN WITH ALCOHOL (causes severe flushing, tachycardia, and vomiting). Complete full course.",
        "known_interactions": "Alcohol, Warfarin, Phenobarbital, Busulfan"
    },

    # 7. ALLERGY, RESPIRATORY & COUGH
    {
        "name": "Montair-LC",
        "generic_name": "Montelukast Sodium + Levocetirizine",
        "category": "Antiallergic & Leukotriene Receptor Antagonist",
        "dosage_form": "Tablet",
        "standard_strength": "10mg + 5mg",
        "before_after_food": "Take once daily in the evening/night, with or without food.",
        "common_uses": "Allergic rhinitis, persistent sneezing, runny nose, hay fever, and asthma symptom control.",
        "side_effects": "Mild drowsiness, dry mouth, headache, fatigue.",
        "warnings": "Best taken at night. Avoid driving if drowsiness occurs. Report mood changes to doctor.",
        "known_interactions": "Phenobarbital, Phenytoin, Rifampicin"
    },
    {
        "name": "Montek-LC",
        "generic_name": "Montelukast + Levocetirizine",
        "category": "Antiallergic Combination",
        "dosage_form": "Tablet",
        "standard_strength": "10mg + 5mg",
        "before_after_food": "Take at bedtime with water.",
        "common_uses": "Relief of allergic asthma, perennial rhinitis, itchy eyes, and dust allergy.",
        "side_effects": "Sleepiness, dry mouth, dizziness.",
        "warnings": "Do not consume alcohol while taking this medicine.",
        "known_interactions": "CNS depressants, Alcohol"
    },
    {
        "name": "Allegra 120",
        "generic_name": "Fexofenadine Hydrochloride",
        "category": "Second-Generation Antihistamine (Non-Sedating)",
        "dosage_form": "Tablet",
        "standard_strength": "120mg",
        "before_after_food": "Take once daily with plain water; avoid fruit juices (orange, apple, grapefruit).",
        "common_uses": "Seasonal allergic rhinitis, sneezing, watery eyes, and runny nose without drowsiness.",
        "side_effects": "Headache, nausea, dry throat.",
        "warnings": "Do not take with fruit juices (reduces absorption by up to 50%). True non-drowsy antihistamine.",
        "known_interactions": "Fruit juices, Aluminium/Magnesium antacids, Erythromycin"
    },
    {
        "name": "Allegra 180",
        "generic_name": "Fexofenadine Hydrochloride",
        "category": "Non-Sedating Antihistamine",
        "dosage_form": "Tablet",
        "standard_strength": "180mg",
        "before_after_food": "Take once daily with water. Do not take with fruit juice.",
        "common_uses": "Chronic idiopathic urticaria (severe skin hives, wheals, and intense itching).",
        "side_effects": "Headache, mild dizziness, viral infection.",
        "warnings": "Take on an empty stomach or with plain water for maximum effectiveness.",
        "known_interactions": "Ketoconazole, Antacids"
    },
    {
        "name": "Cetzine 10",
        "generic_name": "Cetirizine Hydrochloride",
        "category": "Antihistamine",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take with or without food, preferably at bedtime.",
        "common_uses": "Relieves allergies, insect bites, sneezing, runny nose, and allergic conjunctivitis.",
        "side_effects": "Mild drowsiness, dry mouth, tiredness.",
        "warnings": "May cause mild drowsiness; avoid driving or operating machinery if affected.",
        "known_interactions": "Alcohol, Sedatives, Theophylline"
    },
    {
        "name": "Okacet",
        "generic_name": "Cetirizine",
        "category": "Antihistamine",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take once daily in the evening with water.",
        "common_uses": "Fast relief from common cold symptoms, dust allergy, and allergic skin rashes.",
        "side_effects": "Sleepiness, dry mouth, dizziness.",
        "warnings": "Do not mix with alcohol.",
        "known_interactions": "Sleeping pills, Tranquilizers"
    },
    {
        "name": "Levocet 5",
        "generic_name": "Levocetirizine",
        "category": "Antihistamine (Active Enantiomer)",
        "dosage_form": "Tablet",
        "standard_strength": "5mg",
        "before_after_food": "Take once daily in the evening with or without food.",
        "common_uses": "More potent relief of allergic rhinitis and chronic urticaria at lower doses than cetirizine.",
        "side_effects": "Dry mouth, fatigue, somnolence.",
        "warnings": "Avoid in patients with severe renal failure (CrCl < 10 ml/min).",
        "known_interactions": "Ritonavir, Alcohol"
    },
    {
        "name": "Avil 25",
        "generic_name": "Pheniramine Maleate",
        "category": "First-Generation Sedating Antihistamine",
        "dosage_form": "Tablet",
        "standard_strength": "25mg",
        "before_after_food": "Take with meals with water.",
        "common_uses": "Acute drug allergies, food allergy, insect stings, and travel sickness.",
        "side_effects": "Significant drowsiness, sedation, dry mouth, blurred vision.",
        "warnings": "Causes strong sedation. Do not drive or operate machines. Contraindicated in benign prostatic hyperplasia (BPH) and narrow-angle glaucoma.",
        "known_interactions": "Alcohol, Benzodiazepines, MAO inhibitors"
    },
    {
        "name": "Asthalin 4",
        "generic_name": "Salbutamol",
        "category": "Bronchodilator (Beta-2 Agonist)",
        "dosage_form": "Tablet",
        "standard_strength": "4mg",
        "before_after_food": "Take with water as prescribed by physician.",
        "common_uses": "Relief of bronchospasm in asthma, chronic obstructive pulmonary disease (COPD), and bronchitis.",
        "side_effects": "Fine tremors in hands, palpitations, rapid heart rate, nervousness.",
        "warnings": "Report severe rapid pulse or muscle cramps. Use inhaler route if rapid emergency relief is needed.",
        "known_interactions": "Beta blockers (e.g. Propranolol blocks its action), Diuretics"
    },

    # 8. VITAMINS, MINERALS & NUTRITIONAL SUPPLEMENTS
    {
        "name": "Becosules",
        "generic_name": "Vitamin B-Complex with Vitamin C",
        "category": "Nutritional Supplement",
        "dosage_form": "Capsule",
        "standard_strength": "Multivitamin",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Mouth ulcers, stomatitis, tongue inflammation, nerve weakness, and post-illness recovery.",
        "side_effects": "Bright yellow urine (harmless due to riboflavin), mild nausea.",
        "warnings": "Harmless bright yellow urine is completely normal while taking this supplement.",
        "known_interactions": "Levodopa (Vitamin B6 reduces its effect unless combined with carbidopa)"
    },
    {
        "name": "Neurobion Forte",
        "generic_name": "Vitamin B1 + B2 + B3 + B5 + B6 + B12",
        "category": "Neurotropic Vitamins",
        "dosage_form": "Tablet",
        "standard_strength": "High-Potency B-Vitamins",
        "before_after_food": "Take once daily after a meal.",
        "common_uses": "Diabetic neuropathy, nerve pain, tingling, numbness in fingers/toes, and chronic weakness.",
        "side_effects": "Mild stomach discomfort, sweating.",
        "warnings": "Consistent daily use is recommended for peripheral nerve health.",
        "known_interactions": "Isoniazid, Penicillamine"
    },
    {
        "name": "Shelcal 500",
        "generic_name": "Calcium 500mg + Vitamin D3 250 IU",
        "category": "Bone & Mineral Supplement",
        "dosage_form": "Tablet",
        "standard_strength": "500mg + 250 IU",
        "before_after_food": "Take after meals (preferably lunch or dinner) with a glass of water.",
        "common_uses": "Osteoporosis, weak bones, calcium deficiency in elderly, post-menopausal women, and fracture healing.",
        "side_effects": "Constipation, gas, bloating.",
        "warnings": "Drink sufficient water to avoid kidney stone formation. Avoid taking at the same time as thyroid or iron tablets.",
        "known_interactions": "Thyroxine (separate by 4 hrs), Tetracyclines, Ciprofloxacin, Iron"
    },
    {
        "name": "Supradyn Daily",
        "generic_name": "Essential Multivitamins & Minerals with Zinc",
        "category": "Daily Health Supplement",
        "dosage_form": "Tablet",
        "standard_strength": "Comprehensive Formula",
        "before_after_food": "Take once daily after breakfast or lunch.",
        "common_uses": "Daily energy, immunity support, combating fatigue, and correcting micronutrient deficiencies.",
        "side_effects": "Mild metallic taste, yellow discoloration of urine.",
        "warnings": "Take after a full meal to avoid mild nausea from zinc/iron.",
        "known_interactions": "Antacids (reduce absorption)"
    },
    {
        "name": "Limcee 500",
        "generic_name": "Vitamin C (Ascorbic Acid)",
        "category": "Vitamin / Antioxidant",
        "dosage_form": "Tablet",
        "standard_strength": "500mg (Chewable)",
        "before_after_food": "Chew thoroughly after meals at any time of day.",
        "common_uses": "Immunity booster, wound healing, collagen production, scurvy, and antioxidant protection.",
        "side_effects": "Mild stomach upset or diarrhea with excessive doses (>2000mg).",
        "warnings": "Chewable tablet; do not swallow whole. Safe for daily immune support.",
        "known_interactions": "Iron (enhances iron absorption positively), Deferoxamine"
    },
    {
        "name": "Zincovit",
        "generic_name": "Multivitamin + Multimineral with Grape Seed Extract",
        "category": "Antioxidant & Nutritional",
        "dosage_form": "Tablet",
        "standard_strength": "Multimineral + Zinc",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Boosts immunity, speeds convalescence after viral infections, and supports skin & hair health.",
        "side_effects": "Mild nausea if taken on empty stomach.",
        "warnings": "Always take after food.",
        "known_interactions": "Tetracycline antibiotics (space out by 2-3 hours)"
    },
    {
        "name": "Evion 400",
        "generic_name": "Vitamin E (Tocopheryl Acetate)",
        "category": "Lipid-Soluble Vitamin",
        "dosage_form": "Capsule",
        "standard_strength": "400mg",
        "before_after_food": "Take after meals with water.",
        "common_uses": "Nocturnal leg muscle cramps, antioxidant protection, skin and hair health, and fatty liver support.",
        "side_effects": "Nausea, fatigue with very high doses.",
        "warnings": "High doses may increase bleeding tendency in patients on blood thinners.",
        "known_interactions": "Warfarin, Aspirin, Orlistat"
    },
    {
        "name": "Uprise-D3 60K",
        "generic_name": "Cholecalciferol (Vitamin D3)",
        "category": "High-Dose Vitamin D3",
        "dosage_form": "Capsule",
        "standard_strength": "60,000 IU",
        "before_after_food": "Take once WEEKLY with a milk drink or fatty meal for optimal absorption.",
        "common_uses": "Severe Vitamin D deficiency, rickets, osteomalacia, muscle weakness, and bone density loss.",
        "side_effects": "Extremely well tolerated; hypercalcemia only in gross overuse.",
        "warnings": "THIS IS A WEEKLY DOSE, NOT A DAILY TABLET. Take strictly once a week as prescribed.",
        "known_interactions": "Thiazide diuretics, Digoxin"
    },
    {
        "name": "Tayo 60K",
        "generic_name": "Cholecalciferol (Vitamin D3)",
        "category": "Vitamin D3 Supplement",
        "dosage_form": "Tablet",
        "standard_strength": "60,000 IU (Chewable)",
        "before_after_food": "Chew once a week with or after meals.",
        "common_uses": "Corrects low vitamin D levels, strengthens bone structure and boosts immunity.",
        "side_effects": "Nausea only with chronic overdose.",
        "warnings": "Strictly once weekly dosing. Do not take daily.",
        "known_interactions": "Corticosteroids (reduce Vitamin D action)"
    },
    {
        "name": "Orofer-XT",
        "generic_name": "Ferrous Ascorbate + Folic Acid",
        "category": "Hematinic (Iron Supplement)",
        "dosage_form": "Tablet",
        "standard_strength": "Iron 100mg + Folic Acid 1.5mg",
        "before_after_food": "Take with meals or 1 hour after meals with water; avoid tea, coffee, or milk.",
        "common_uses": "Iron deficiency anemia, pregnancy-associated anemia, fatigue, and low hemoglobin.",
        "side_effects": "Harmless dark black stools, constipation, nausea, metallic taste.",
        "warnings": "Dark black stools are a normal, harmless effect of oral iron. Avoid tea/coffee within 1 hour.",
        "known_interactions": "Calcium supplements, Antacids, Levothyroxine, Fluoroquinolones"
    },

    # 9. MENTAL HEALTH, NEUROLOGY & SEDATIVES
    {
        "name": "Nexito 10",
        "generic_name": "Escitalopram",
        "category": "Antidepressant (SSRI)",
        "dosage_form": "Tablet",
        "standard_strength": "10mg",
        "before_after_food": "Take once daily in the morning or night, with or without food.",
        "common_uses": "Generalized anxiety disorder, panic attacks, depression, and social phobia.",
        "side_effects": "Nausea, insomnia or drowsiness, sexual dysfunction, dry mouth.",
        "warnings": "Takes 2-4 weeks for full therapeutic benefits. Never discontinue abruptly (risk of withdrawal symptoms).",
        "known_interactions": "MAO inhibitors, Tramadol, NSAIDs, Triptans"
    },
    {
        "name": "Clonafit 0.5",
        "generic_name": "Clonazepam",
        "category": "Benzodiazepine (Anxiolytic & Anticonvulsant)",
        "dosage_form": "Tablet",
        "standard_strength": "0.5mg",
        "before_after_food": "Take at night before bed with water.",
        "common_uses": "Panic attacks, severe anxiety, sleep disturbances, and seizure management.",
        "side_effects": "Drowsiness, ataxia, impaired coordination, memory changes.",
        "warnings": "Schedule H1 drug. Risk of tolerance and psychological dependence. Avoid alcohol completely.",
        "known_interactions": "Alcohol, Opioids, Sedatives, Antipsychotics"
    },
    {
        "name": "Restyl 0.25",
        "generic_name": "Alprazolam",
        "category": "Benzodiazepine",
        "dosage_form": "Tablet",
        "standard_strength": "0.25mg",
        "before_after_food": "Take with or without food as advised.",
        "common_uses": "Short-term relief of acute anxiety and panic disorders.",
        "side_effects": "Sedation, lightheadedness, dry mouth.",
        "warnings": "Short-term use only (2-4 weeks). Do not drive or drink alcohol.",
        "known_interactions": "Ketoconazole, Itraconazole, Central nervous system depressants"
    },
    {
        "name": "Gabapin-NT",
        "generic_name": "Gabapentin + Nortriptyline",
        "category": "Neuropathic Pain Combination",
        "dosage_form": "Tablet",
        "standard_strength": "400mg + 10mg",
        "before_after_food": "Take at bedtime with water.",
        "common_uses": "Diabetic peripheral neuropathy, post-herpetic neuralgia (shingles pain), and sciatica.",
        "side_effects": "Drowsiness, dizziness, dry mouth, blurred vision, weight gain.",
        "warnings": "Causes significant evening drowsiness. Rise slowly from bed. Do not discontinue abruptly.",
        "known_interactions": "Alcohol, Antacids (take 2 hours apart), Opioids"
    },
    {
        "name": "Pregabalin 75",
        "generic_name": "Pregabalin",
        "category": "Neuropathic Analgesic / Anticonvulsant",
        "dosage_form": "Capsule",
        "standard_strength": "75mg",
        "before_after_food": "Take once or twice daily with or without food.",
        "common_uses": "Fibromyalgia, diabetic nerve pain, spinal nerve compression, and anxiety.",
        "side_effects": "Dizziness, sleepiness, peripheral edema, weight gain.",
        "warnings": "Do not stop suddenly to prevent rebound insomnia or anxiety.",
        "known_interactions": "Lorazepam, Oxycodone, ACE inhibitors"
    },
    {
        "name": "Vertin 16",
        "generic_name": "Betahistine Hydrochloride",
        "category": "Antivertigo / Histamine Analogue",
        "dosage_form": "Tablet",
        "standard_strength": "16mg",
        "before_after_food": "Take strictly with or after meals to prevent stomach irritation.",
        "common_uses": "Meniere's disease, spinning sensation (vertigo), ringing in ears (tinnitus), and hearing loss.",
        "side_effects": "Mild stomach ache, headache, nausea.",
        "warnings": "Contraindicated in pheochromocytoma. Caution in bronchial asthma.",
        "known_interactions": "Antihistamines (counteract betahistine action)"
    },

    # 10. THYROID & HORMONAL
    {
        "name": "Thyronorm 25",
        "generic_name": "Thyroxine Sodium (Levothyroxine)",
        "category": "Thyroid Hormone Replacement",
        "dosage_form": "Tablet",
        "standard_strength": "25mcg",
        "before_after_food": "Take first thing in morning on an empty stomach with plain water, at least 30-45 minutes before breakfast, tea, or coffee.",
        "common_uses": "Hypothyroidism (underactive thyroid gland) and goiter prevention.",
        "side_effects": "Palpitations, weight loss, nervousness only if overdosed.",
        "warnings": "CRITICAL INSTRUCTION: Must be taken on an empty stomach with plain water. Wait 45 minutes before drinking tea, coffee, or eating.",
        "known_interactions": "Calcium supplements, Iron, Antacids, Soy products (must separate by 4 hours)"
    },
    {
        "name": "Thyronorm 50",
        "generic_name": "Thyroxine Sodium",
        "category": "Thyroid Hormone Replacement",
        "dosage_form": "Tablet",
        "standard_strength": "50mcg",
        "before_after_food": "Take first thing in the morning on an empty stomach with water.",
        "common_uses": "Maintains normal metabolism and thyroid hormone levels in hypothyroidism.",
        "side_effects": "Sweating, tremors, insomnia if dose is too high.",
        "warnings": "Take consistently at the same time every morning. Monitor TSH levels every 3 to 6 months.",
        "known_interactions": "Cholestyramine, Sucralfate, Warfarin"
    },
    {
        "name": "Thyronorm 100",
        "generic_name": "Thyroxine Sodium",
        "category": "Thyroid Hormone Replacement",
        "dosage_form": "Tablet",
        "standard_strength": "100mcg",
        "before_after_food": "Take strictly on an empty stomach with plain water, 45 minutes before breakfast.",
        "common_uses": "Full replacement therapy for total thyroidectomy or severe hypothyroidism.",
        "side_effects": "Fast pulse, heat intolerance if over-replaced.",
        "warnings": "Do not skip doses. Never take with calcium or iron tablets simultaneously.",
        "known_interactions": "Oral antidiabetic drugs (may require dose adjustment)"
    },
    {
        "name": "Eltroxin 50",
        "generic_name": "Thyroxine Sodium",
        "category": "Thyroid Hormone",
        "dosage_form": "Tablet",
        "standard_strength": "50mcg",
        "before_after_food": "Take on empty stomach 30-45 mins before morning tea/breakfast.",
        "common_uses": "Treats hypothyroidism, chronic fatigue, cold sensitivity, and weight gain from low thyroid.",
        "side_effects": "Well tolerated at physiological replacement doses.",
        "warnings": "Do not change brands without physician review.",
        "known_interactions": "Phenytoin, Carbamazepine, Rifampicin"
    },

    # 11. ANTIFUNGALS & STEROIDS
    {
        "name": "Forcan 150",
        "generic_name": "Fluconazole",
        "category": "Antifungal (Triazole)",
        "dosage_form": "Tablet",
        "standard_strength": "150mg",
        "before_after_food": "Take once with or after food with water.",
        "common_uses": "Vaginal yeast infections (candidiasis), fungal nail/skin infections, and oral thrush.",
        "side_effects": "Headache, nausea, abdominal discomfort.",
        "warnings": "Single dose for vaginal candidiasis. Inform doctor if you have liver disease.",
        "known_interactions": "Warfarin, Sulfonylureas, Phenytoin, Statins"
    },
    {
        "name": "Itrasys 200",
        "generic_name": "Itraconazole",
        "category": "Antifungal",
        "dosage_form": "Capsule",
        "standard_strength": "200mg",
        "before_after_food": "Take strictly immediately after a full meal for proper absorption.",
        "common_uses": "Stubborn ringworm (Tinea corporis/cruris), fungal nail infections (onychomycosis), and systemic fungal disease.",
        "side_effects": "Nausea, rash, elevated liver enzymes.",
        "warnings": "Requires stomach acid for absorption; do not take alongside antacids or PPIs. Take after a heavy meal.",
        "known_interactions": "Omeprazole, Pantoprazole, Statins, Digoxin"
    },
    {
        "name": "Omnacortil 5",
        "generic_name": "Prednisolone",
        "category": "Corticosteroid",
        "dosage_form": "Tablet",
        "standard_strength": "5mg",
        "before_after_food": "Take strictly with or immediately after food in the morning.",
        "common_uses": "Suppresses severe allergic reactions, asthma flare-ups, rheumatoid arthritis, and autoimmune diseases.",
        "side_effects": "Increased appetite, weight gain, insomnia, fluid retention.",
        "warnings": "Never stop taking steroid abruptly (must taper gradually). Take with food to protect stomach.",
        "known_interactions": "NSAIDs (increased ulcer risk), Diabetes medicines, Vaccines"
    },
    {
        "name": "Omnacortil 20",
        "generic_name": "Prednisolone",
        "category": "Corticosteroid",
        "dosage_form": "Tablet",
        "standard_strength": "20mg",
        "before_after_food": "Take with breakfast.",
        "common_uses": "Severe inflammatory conditions, severe allergic flare-ups, and skin dermatoses.",
        "side_effects": "Mood changes, increased blood sugar, gastric irritation.",
        "warnings": "Taper dose gradually as instructed by your doctor.",
        "known_interactions": "Live vaccines, Antidiabetic drugs"
    }
]


def seed_indian_medicines():
    """Populate sqlite database with 130+ Indian medicines."""
    db_path = Path(__file__).resolve().parents[1] / "medimitra.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    print(f"[Seed] Seeding {len(INDIAN_MEDICINES)} Indian medicines into {db_path}...")

    # Insert or update each medicine by name
    inserted = 0
    updated = 0
    for med in INDIAN_MEDICINES:
        cur.execute("SELECT id FROM medicine_database WHERE LOWER(name) = ?", (med["name"].lower(),))
        existing = cur.fetchone()
        if existing:
            cur.execute("""
                UPDATE medicine_database
                SET generic_name = ?, category = ?, dosage_form = ?, standard_strength = ?,
                    before_after_food = ?, common_uses = ?, side_effects = ?, warnings = ?,
                    known_interactions = ?
                WHERE id = ?
            """, (
                med["generic_name"], med["category"], med["dosage_form"], med["standard_strength"],
                med["before_after_food"], med["common_uses"], med["side_effects"], med["warnings"],
                med["known_interactions"], existing[0]
            ))
            updated += 1
        else:
            cur.execute("""
                INSERT INTO medicine_database
                (name, generic_name, category, dosage_form, standard_strength, before_after_food, common_uses, side_effects, warnings, known_interactions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                med["name"], med["generic_name"], med["category"], med["dosage_form"], med["standard_strength"],
                med["before_after_food"], med["common_uses"], med["side_effects"], med["warnings"],
                med["known_interactions"]
            ))
            inserted += 1

    conn.commit()

    # Get total count
    cur.execute("SELECT COUNT(*) FROM medicine_database")
    total = cur.fetchone()[0]
    conn.close()

    print(f"[Seed] Completed! Inserted: {inserted}, Updated: {updated}, Total Indian Medicines in Database: {total}")
    return total


if __name__ == "__main__":
    seed_indian_medicines()
