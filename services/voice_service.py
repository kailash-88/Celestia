"""
Multilingual Voice Engine for MediMitra
Generates accurate, spoken audio transcripts for detected Indian medicines across 9 languages:
- English (en-IN)
- Hindi (hi-IN)
- Tamil (ta-IN)
- Telugu (te-IN)
- Bengali (bn-IN)
- Marathi (mr-IN)
- Gujarati (gu-IN)
- Kannada (kn-IN)
- Malayalam (ml-IN)
"""

import re

LANGUAGES = [
    {"code": "en", "locale": "en-IN", "name": "English", "flag": "🇬🇧"},
    {"code": "hi", "locale": "hi-IN", "name": "हिन्दी (Hindi)", "flag": "🇮🇳"},
    {"code": "ta", "locale": "ta-IN", "name": "தமிழ் (Tamil)", "flag": "🇮🇳"},
    {"code": "te", "locale": "te-IN", "name": "తెలుగు (Telugu)", "flag": "🇮🇳"},
    {"code": "bn", "locale": "bn-IN", "name": "বাংলা (Bengali)", "flag": "🇮🇳"},
    {"code": "mr", "locale": "mr-IN", "name": "मराठी (Marathi)", "flag": "🇮🇳"},
    {"code": "gu", "locale": "gu-IN", "name": "ગુજરાતી (Gujarati)", "flag": "🇮🇳"},
    {"code": "kn", "locale": "kn-IN", "name": "ಕನ್ನಡ (Kannada)", "flag": "🇮🇳"},
    {"code": "ml", "locale": "ml-IN", "name": "മലയാളം (Malayalam)", "flag": "🇮🇳"},
]


GENERIC_TRANSLATIONS = {
    "paracetamol": {
        "en": "Paracetamol", "hi": "पैरासिटामोल", "ta": "பாராசிட்டமால்", "te": "పారాసిటమాల్",
        "bn": "প্যারাসিটামল", "mr": "पॅरासिटामॉल", "gu": "પેરાસિટામોલ", "kn": "ಪ್ಯಾರಸಿಟಮಾಲ್", "ml": "പാരസെറ്റമോൾ"
    },
    "pantoprazole": {
        "en": "Pantoprazole", "hi": "पेंटोप्राजोल", "ta": "பான்டோபிரசோல்", "te": "పాంటోప్రజోల్",
        "bn": "প্যান্টোপ্রাজল", "mr": "पँटोप्राझोल", "gu": "પેન્ટોપ્રાઝોલ", "kn": "ಪ್ಯಾಂಟೊಪ್ರಜೋಲ್", "ml": "പാന്റോപ്രസോൾ"
    },
    "telmisartan": {
        "en": "Telmisartan", "hi": "टेलमिसार्टन", "ta": "டெல்மிசார்டன்", "te": "టెల్మిసార్టన్",
        "bn": "টেলমিসারটান", "mr": "टेल्मिसार्टन", "gu": "ટેલ્મિસારટન", "kn": "ಟೆಲ್ಮಿಸಾರ್ಟನ್", "ml": "ടെൽമിസാർട്ടൻ"
    },
    "atorvastatin": {
        "en": "Atorvastatin", "hi": "एटोरवास्टेटिन", "ta": "அடோர்வாஸ்டேடின்", "te": "అటోర్వాస్టాటిన్",
        "bn": "অ্যাটরভাস্ট্যাটিন", "mr": "अटोर्वास्टॅटिन", "gu": "એટોરવાસ્ટેટિન", "kn": "ಅಟೋರ್ವಾಸ್ಟಾಟಿನ್", "ml": "അറ്റോർവാസ്റ്റാറ്റിൻ"
    },
    "metformin": {
        "en": "Metformin", "hi": "मेटफॉर्मिन", "ta": "மெட்பார்மின்", "te": "మెట్‌ఫార్మిన్",
        "bn": "মেটফর্মিন", "mr": "मेटफॉर्मिन", "gu": "મેટફોર્મિન", "kn": "ಮೆಟ್‌ಫಾರ್ಮಿನ್", "ml": "മെറ്റ്ഫോർമിൻ"
    },
    "cetirizine": {
        "en": "Cetirizine", "hi": "सेटिरिज़िन", "ta": "செட்டிரிசைன்", "te": "సెటిరిజైన్",
        "bn": "সেটিরিজিন", "mr": "सिटिरिझिन", "gu": "સેટિરિઝિન", "kn": "ಸೆಟಿರಿಜಿನ್", "ml": "സെറ്റിറൈസിൻ"
    },
    "amoxicillin": {
        "en": "Amoxicillin", "hi": "अमोक्सिसिलिन", "ta": "அமோக்ஸிசிலின்", "te": "అమోక్సిసిలిన్",
        "bn": "অ্যামোক্সিসিলিন", "mr": "अमॉक्सिसिलिन", "gu": "એમોક્સિસિલિન", "kn": "ಅಮೋಕ್ಸಿಸಿಲಿನ್", "ml": "അമോക്സിസിലിൻ"
    },
    "caffeine": {
        "en": "Caffeine", "hi": "कैफीन", "ta": "காஃபின்", "te": "కెఫీన్",
        "bn": "ক্যাফেইন", "mr": "कॅफिन", "gu": "કેફીન", "kn": "ಕೆಫೀನ್", "ml": "കഫീൻ"
    },
    "ibuprofen": {
        "en": "Ibuprofen", "hi": "इबुप्रोफेन", "ta": "இபுபுரூஃபென்", "te": "ఇబుప్రోఫెన్",
        "bn": "আইবুপ্রোফেন", "mr": "इबुप्रोफेन", "gu": "ઇબુપ્રોફેન", "kn": "ಐಬುಪ್ರೊಫೇನ್", "ml": "ഐബുപ്രോഫെൻ"
    },
    "aspirin": {
        "en": "Aspirin", "hi": "एस्पिरिन", "ta": "ஆஸ்பிரின்", "te": "ఆస్ప్రిన్",
        "bn": "অ্যাসপিরিন", "mr": "अॅस्पिरिन", "gu": "એસ્પિરિન", "kn": "ಆಸ್ಪಿರಿನ್", "ml": "ആസ്പിരിൻ"
    }
}


def _get_natural_generic_name(raw_generic, lang_code, brand_name):
    """Translate clinical generic molecules into native Indic script terms."""
    if not raw_generic:
        return ""
    tokens = [t.strip().lower() for t in raw_generic.replace('/', '+').split('+')]
    translated = []
    for t in tokens:
        for k, v in GENERIC_TRANSLATIONS.items():
            if k in t and v.get(lang_code) not in translated:
                translated.append(v.get(lang_code))
                break
    if not translated:
        clean = raw_generic.split('/')[0].split('+')[0].strip()
        return clean if clean.lower() != (brand_name or "").lower() else ""
    if len(translated) == 1:
        return translated[0]
    joiners = {
        'en': ' and ', 'hi': ' और ', 'ta': ' மற்றும் ', 'te': ' మరియు ',
        'bn': ' এবং ', 'mr': ' आणि ', 'gu': ' અને ', 'kn': ' ಮತ್ತು ', 'ml': ' കൂടാതെ '
    }
    return joiners.get(lang_code, ' and ').join(translated[:2])


def _detect_food_timing_key(timing_str):
    """Classify timing text into standard categories."""
    t = (timing_str or "").lower()
    if any(k in t for k in ["empty stomach", "before breakfast", "before morning", "30-60 min", "before food"]):
        return "empty_stomach"
    elif any(k in t for k in ["strictly after", "after meals", "after food", "after dinner", "after lunch"]):
        return "after_food"
    elif any(k in t for k in ["with food", "with meals", "start of meal", "first bite", "during meal"]):
        return "with_meals"
    elif any(k in t for k in ["bedtime", "night", "sleeping", "evening"]):
        return "bedtime"
    elif any(k in t for k in ["weekly", "once weekly"]):
        return "weekly"
    return "general"


def _detect_purpose_key(uses_str, name_str, generic_str):
    """Classify clinical purpose into broad categories for natural speech."""
    corpus = f"{uses_str} {name_str} {generic_str}".lower()
    if any(k in corpus for k in ["fever", "paracetamol", "pain", "headache", "toothache", "dolo", "calpol", "crocin"]):
        return "fever_pain"
    elif any(k in corpus for k in ["acidity", "acid reflux", "gerd", "ulcer", "heartburn", "pantoprazole", "omeprazole", "pan-d"]):
        return "acidity_ulcer"
    elif any(k in corpus for k in ["blood pressure", "hypertension", "telmisartan", "amlodipine", "bp", "cardiac"]):
        return "blood_pressure"
    elif any(k in corpus for k in ["diabetes", "blood sugar", "metformin", "glycomet", "glucose", "insulin"]):
        return "diabetes"
    elif any(k in corpus for k in ["cholesterol", "statin", "atorvastatin", "blood thinner", "aspirin", "clopidogrel", "ecosprin"]):
        return "cholesterol_blood_thinner"
    elif any(k in corpus for k in ["antibiotic", "bacterial", "infection", "amoxicillin", "azithromycin", "augmentin"]):
        return "antibiotic"
    elif any(k in corpus for k in ["allergy", "sneezing", "cough", "cold", "antihistamine", "cetirizine", "montelukast"]):
        return "allergy_cough"
    elif any(k in corpus for k in ["vitamin", "calcium", "supplement", "fatigue", "immunity", "neurobion", "becosules"]):
        return "vitamins_minerals"
    elif any(k in corpus for k in ["thyroid", "hypothyroidism", "thyroxine", "thyronorm", "eltroxin"]):
        return "thyroid"
    elif any(k in corpus for k in ["anxiety", "nerve", "neuropathy", "sleep", "depression", "gabapentin", "pregabalin"]):
        return "nerve_anxiety"
    elif any(k in corpus for k in ["vomiting", "nausea", "motion sickness", "ondansetron", "ondem", "domperidone"]):
        return "nausea_vomiting"
    return "general"


def _detect_avoid_instructions(warnings_raw, interactions_raw, generic_raw, name_raw):
    """
    Determine what medicines, foods, or actions should NOT be taken or avoided.
    Returns localized guidance strings in English, Hindi, and Tamil (plus other Indic languages).
    """
    corpus = f"{warnings_raw or ''} {interactions_raw or ''} {generic_raw or ''} {name_raw or ''}".lower()
    
    avoid_en = []
    avoid_hi = []
    avoid_ta = []

    # 1. Alcohol
    if "alcohol" in corpus:
        avoid_en.append("Do not consume alcohol with this medicine.")
        avoid_hi.append("इसके साथ शराब का सेवन बिल्कुल न करें।")
        avoid_ta.append("இந்த மாத்திரையுடன் மது அருந்தக்கூடாது.")

    # 2. Duplicate paracetamol / Overdose
    if any(k in corpus for k in ["paracetamol", "dolo", "calpol", "crocin", "overdose"]):
        avoid_en.append("Do not take other paracetamol or cold medicines at the same time.")
        avoid_hi.append("इसके साथ कोई अन्य पैरासिटामोल या सर्दी की दवा न लें।")
        avoid_ta.append("இதனுடன் வேறு பாராசிட்டமால் அல்லது சளி மருந்துகளை சேர்த்து உட்கொள்ள வேண்டாம்.")

    # 3. Empty stomach / NSAID irritation
    if any(k in corpus for k in ["empty stomach", "ulcer", "ibuprofen", "combiflam", "flexon", "voveran", "diclofenac", "aceclofenac"]):
        avoid_en.append("Do not take on an empty stomach; avoid combining with other pain killers or aspirin.")
        avoid_hi.append("इसे खाली पेट न लें, और अन्य दर्द की दवा या एस्पिरिन के साथ लेने से बचें।")
        avoid_ta.append("இதை வெறும் வயிற்றில் உட்கொள்ளாதீர்கள், மேலும் பிற வலி நிவாரணிகள் அல்லது ஆஸ்பிரினுடன் சேர்ப்பதை தவிர்க்கவும்.")

    # 4. Antibiotics / Calcium / Milk / Antacids
    if any(k in corpus for k in ["antacid", "milk", "calcium", "tetracycline", "ciprofloxacin", "azithromycin", "doxycycline"]):
        avoid_en.append("Avoid taking with milk or antacids at the same time; keep at least a 2-hour gap.")
        avoid_hi.append("इसे दूध या एंटासिड के साथ न लें, कम से कम 2 घंटे का अंतर रखें।")
        avoid_ta.append("இதை பால் அல்லது அசிடிட்டி மருந்துகளுடன் ஒன்றாக எடுக்க வேண்டாம், 2 மணி நேரம் இடைவெளி விடவும்.")

    # 5. Blood thinners / Warfarin / Aspirin
    if any(k in corpus for k in ["warfarin", "blood thinner", "bleeding", "ecosprin", "clopidogrel"]):
        avoid_en.append("Avoid taking unprescribed pain relievers due to bleeding risks.")
        avoid_hi.append("रक्तस्राव के खतरे के कारण डॉक्टर की सलाह के बिना कोई दर्द निवारक न लें।")
        avoid_ta.append("இரத்தப்போக்கு ஆபத்து உள்ளதால் மருத்துவர் அனுமதியின்றி பிற வலி நிவாரணிகளை தவிர்க்கவும்.")

    # 6. Drowsiness / Driving
    if any(k in corpus for k in ["drowsy", "dizziness", "cetirizine", "montelukast", "sedat"]):
        avoid_en.append("Avoid driving or heavy machinery if you feel drowsy.")
        avoid_hi.append("नींद या चक्कर आने पर गाड़ी चलाने से बचें।")
        avoid_ta.append("தூக்கம் அல்லது மயக்கம் இருந்தால் வாகனம் ஓட்டுவதை தவிர்க்கவும்.")

    # Fallback if none specifically matched
    if not avoid_en:
        avoid_en.append("Avoid taking double doses or combining with unprescribed medications.")
        avoid_hi.append("दोगुनी खुराक न लें और बिना डॉक्टर की सलाह के कोई अन्य दवा साथ में न लें।")
        avoid_ta.append("இரட்டை அளவு எடுப்பதையோ அல்லது மருத்துவர் பரிந்துரைக்காத பிற மருந்துகளை சேர்ப்பதையோ தவிர்க்கவும்.")

    return {
        "en": " What to avoid: " + " ".join(avoid_en),
        "hi": " क्या न लें और परहेज करें: " + " ".join(avoid_hi),
        "ta": " என்ன தவிர்க்க வேண்டும்: " + " ".join(avoid_ta),
        "te": " నివారించవలసినవి: డబుల్ డోస్ తీసుకోకండి మరియు డాక్టర్ సలహా లేకుండా ఇతర మందులతో కలపకండి.",
        "bn": " যা এড়িয়ে চলবেন: অতিরিক্ত ডোজ নেবেন না এবং ডাক্তারের পরামর্শ ছাড়া অন্য ওষুধের সাথে খাবেন না।",
        "mr": " काय टाळावे: दुहेरी डोस घेऊ नका आणि डॉक्टरांच्या सल्ल्याशिवाय इतर औषधे एकत्र घेऊ नका.",
        "gu": " શું ટાળવું: બમણો ડોઝ ન લેશો અને ડૉક્ટરની સલાહ વિના અન્ય દવાઓ સાથે ન લેશો.",
        "kn": " ತಪ್ಪಿಸಬೇಕಾದದ್ದು: ಡಬಲ್ ಡೋಸ್ ತೆಗೆದುಕೊಳ್ಳಬೇಡಿ ಮತ್ತು ವೈದ್ಯರ ಸಲಹೆಯಿಲ್ಲದೆ ಇತರ ಔಷಧಿಗಳೊಂದಿಗೆ ತೆಗೆದುಕೊಳ್ಳಬೇಡಿ.",
        "ml": " ഒഴിവാക്കേണ്ടവ: ഇരട്ടി അളവിൽ കഴിക്കരുത്, ഡോക്ടറുടെ നിർദ്ദേശമില്ലാതെ മറ്റ് മരുന്നുകൾക്കൊപ്പം കഴിക്കരുത്.",
        "items": {
            "en": avoid_en,
            "hi": avoid_hi,
            "ta": avoid_ta
        }
    }


def generate_medicine_voice_scripts(facts):
    """
    Produce rich spoken text in 9 Indian languages for any scanned tablet/medicine.
    Includes medicine identification, clinical purpose, food timing, and what to avoid.
    """
    name = (facts.get("name") or "Medicine").strip()
    generic = (facts.get("generic_name") or facts.get("active_ingredient") or "").strip()
    dosage = (facts.get("dosage") or facts.get("strength") or "").strip()
    timing_raw = facts.get("before_after_food") or "Take as advised by your doctor."
    uses_raw = facts.get("common_uses") or facts.get("purpose") or "General therapeutic treatment."
    warnings_raw = facts.get("warnings") or ""
    interactions_raw = facts.get("known_interactions") or facts.get("side_effects") or ""

    form = facts.get("form") or "Tablet"
    if "cap" in form.lower():
        form_clean = "Capsule"
    elif "syrup" in form.lower():
        form_clean = "Syrup"
    else:
        form_clean = "Tablet"

    food_key = _detect_food_timing_key(timing_raw)
    purpose_key = _detect_purpose_key(uses_raw, name, generic)
    avoid_info = _detect_avoid_instructions(warnings_raw, interactions_raw, generic, name)

    # 1. Food timing translations
    timing_dict = {
        "after_food": {
            "en": "Please take it strictly after meals with plenty of water.",
            "hi": "कृपया इसे हमेशा खाना खाने के बाद ही भरपूर पानी के साथ लें।",
            "ta": "தயவுசெய்து இதை எப்போதும் உணவு உண்ட பிறகு தண்ணீருடன் உட்கொள்ளவும்.",
            "te": "దయచేసి దీనిని ఎల్లప్పుడూ భోజనం చేసిన తర్వాత మాత్రమే నీటితో వేసుకోండి.",
            "bn": "দয়া করে এটি সর্বদা খাবার খাওয়ার পর জল দিয়ে খাবেন।",
            "mr": "कृपया हे नेहमी जेवणानंतरच भरपूर पाण्यासोबत घ्यावे.",
            "gu": "કૃપા કરીને આ દવા હંમેશા જમ્યા પછી જ પાણી સાથે લેવી.",
            "kn": "ದಯವಿಟ್ಟು ಇದನ್ನು ಯಾವಾಗಲೂ ಊಟದ ನಂತರ ನೀರಿನೊಂದಿಗೆ ತೆಗೆದುಕೊಳ್ಳಿ.",
            "ml": "ദയവായി ഇത് എപ്പോഴും ആഹാരത്തിന് ശേഷം വെള്ളത്തോടൊപ്പം കഴിക്കുക."
        },
        "empty_stomach": {
            "en": "Please take it in the morning on an empty stomach, 30 to 60 minutes before breakfast.",
            "hi": "कृपया इसे सुबह नाश्ते से आधा घंटा पहले खाली पेट पानी के साथ लें।",
            "ta": "தயவுசெய்து இதை காலையில் உணவு உண்பதற்கு முன் வெறும் வயிற்றில் உட்கொள்ளவும்.",
            "te": "దయచేసి దీనిని ఉదయం అల్పాహారానికి ముందు ఖాళీ కడుపుతో మాత్రమే వేసుకోండి.",
            "bn": "দয়া করে এটি সকালে প্রাতঃরাশের আগে খালি পেটে জল দিয়ে খান।",
            "mr": "कृपया हे सकाळी नाश्त्याच्या ३० मिनिटे आधी रिकाम्या पोटी घ्यावे.",
            "gu": "કૃપા કરીને આ દવા સવારે નાસ્તા પહેલાં ખાલી પેટે પાણી સાથે લેવી.",
            "kn": "ದಯವಿಟ್ಟು ಇದನ್ನು ಬೆಳಿಗ್ಗೆ ಉಪಾಹಾರಕ್ಕಿಂತ ಮೊದಲು ಖಾಲಿ ಹೊಟ್ಟೆಯಲ್ಲಿ ತೆಗೆದುಕೊಳ್ಳಿ.",
            "ml": "ദയവായി ഇത് രാവിലെ പ്രാതലിന് മുൻപ് വെറും വയറ്റിൽ കഴിക്കുക."
        },
        "with_meals": {
            "en": "Please take it along with your meals or with the first bite of food.",
            "hi": "कृपया इसे भोजन के साथ या खाना खाते समय पहली बाइट के साथ लें।",
            "ta": "தயவுசெய்து இதை உணவு சாப்பிடும் போது அல்லது உணவின் தொடக்கத்தில் உட்கொள்ளவும்.",
            "te": "దయచేసి దీనిని భోజనంతో పాటు లేదా భోజనం ప్రారంభంలో వేసుకోండి.",
            "bn": "দয়া করে এটি খাবারের সাথে অথবা খাবারের শুরুতে খাবেন।",
            "mr": "कृपया हे जेवणासोबत किंवा जेवणाच्या सुरुवातीला घ्यावे.",
            "gu": "કૃપા કરીને આ દવા જમવાની સાથે અથવા જમવાની શરૂઆતમાં લેવી.",
            "kn": "ದಯವಿಟ್ಟು ಇದನ್ನು ಊಟದ ಜೊತೆಗೆ ಅಥವಾ ಊಟದ ಆರಂಭದಲ್ಲಿ ತೆಗೆದುಕೊಳ್ಳಿ.",
            "ml": "ദയവായി ഇത് ഭക്ഷണത്തോടൊപ്പം കഴിക്കുക."
        },
        "bedtime": {
            "en": "Please take it once daily at night before bedtime with water.",
            "hi": "कृपया इसे रात को सोने से पहले पानी के साथ लें।",
            "ta": "தயவுசெய்து இதை இரவு தூங்குவதற்கு முன் தண்ணீருடன் உட்கொள்ளவும்.",
            "te": "దయచేసి దీనిని రాత్రి పడుకునే ముందు నీటితో వేసుకోండి.",
            "bn": "দয়া করে এটি রাতে ঘুমানোর আগে জল দিয়ে খান।",
            "mr": "कृपया हे रात्री झोपण्यापूर्वी पाण्यासोबत घ्यावे.",
            "gu": "કૃપા કરીને આ દવા રાત્રે સૂતા પહેલાં પાણી સાથે લેવી.",
            "kn": "ದಯವಿಟ್ಟು ಇದನ್ನು ರಾತ್ರಿ ಮಲಗುವ ಮುನ್ನ ನೀರಿನೊಂದಿಗೆ ತೆಗೆದುಕೊಳ್ಳಿ.",
            "ml": "ദയവായി ഇത് രാത്രി ഉറങ്ങുന്നതിന് മുൻപ് വെള്ളത്തോടൊപ്പം കഴിക്കുക."
        },
        "weekly": {
            "en": "Important note: This is a once-weekly dose. Take strictly once a week with water or milk.",
            "hi": "विशेष सूचना: यह हफ्ते में केवल एक बार लेने वाली खुराक है। इसे सप्ताह में एक ही दिन लें।",
            "ta": "முக்கிய எச்சரிக்கை: இது வாரத்திற்கு ஒரு முறை மட்டுமே சாப்பிட வேண்டிய மாத்திரை.",
            "te": "ముఖ్య గమనిక: ఇది వారానికి ఒకసారి మాత్రమే వేసుకోవలసిన టాబ్లెట్.",
            "bn": "বিশেষ সতর্কতা: এটি সপ্তাহে শুধুমাত্র একবার খাওয়ার ওষুধ।",
            "mr": "विशेष सूचना: हे आठवड्यातून फक्त एकदाच घेण्याचे औषध आहे.",
            "gu": "ખાસ સૂચના: આ અઠવાડિયામાં ફક્ત એક જ વાર લેવાની દવા છે.",
            "kn": "ಮುಖ್ಯ ಸೂಚನೆ: ಇದು ವಾರಕ್ಕೆ ಒಂದು ಬಾರಿ ಮಾತ್ರ ತೆಗೆದುಕೊಳ್ಳಬೇಕಾದ ಮಾತ್ರೆ.",
            "ml": "പ്രത്യേക ശ്രദ്ധിക്കുക: ഇത് ആഴ്ചയിൽ ഒരിക്കൽ മാത്രം കഴിക്കേണ്ട ഗുളികയാണ്."
        },
        "general": {
            "en": timing_raw,
            "hi": "कृपया इसे अपने डॉक्टर की सलाह अनुसार समय पर लें।",
            "ta": "தயவுசெய்து மருத்துவரின் ஆலோசனைப்படி சரியான நேரத்தில் உட்கொள்ளவும்.",
            "te": "దయచేసి డాక్టర్ సలహా మేరకు సరైన సమయంలో వేసుకోండి.",
            "bn": "দয়া করে ডাক্তারের পরামর্শ অনুযায়ী নির্দিষ্ট সময়ে খান।",
            "mr": "कृपया डॉक्टरांच्या सल्ल्यानुसार योग्य वेळी औषध घ्यावे.",
            "gu": "કૃપા કરીને ડોક્ટરની સલાહ મુજબ નિયમિત સમયે લેવી.",
            "kn": "ದಯವಿಟ್ಟು ವೈದ್ಯರ ಸಲಹೆಯಂತೆ ಸರಿಯಾದ ಸಮಯಕ್ಕೆ ತೆಗೆದುಕೊಳ್ಳಿ.",
            "ml": "ദയവായി ഡോക്ടറുടെ നിർദ്ദേശപ്രകാരം കൃത്യസമയത്ത് കഴിക്കുക."
        }
    }

    # 2. Purpose translations
    purpose_dict = {
        "fever_pain": {
            "en": "relief of fever, headache, and body aches",
            "hi": "बुखार, सिरदर्द और शरीर के दर्द से राहत",
            "ta": "காய்ச்சல், தலைவலி மற்றும் உடல் வலியை குறைக்க",
            "te": "జ్వరం, తలనొప్పి మరియు ఒంటి నొప్పుల నివారణకు",
            "bn": "জ্বর, মাথাব্যথা এবং শরীরের ব্যথা কমাতে",
            "mr": "ताप, डोकेदुखी आणि अंगदुखी कमी करण्यासाठी",
            "gu": "તાવ, માથાનો દુખાવો અને શરીરના દુખાવામાં રાહત માટે",
            "kn": "ಜ್ವರ, ತಲೆನೋವು ಮತ್ತು ಮೈಕೈ ನೋವು ನಿವಾರಣೆಗೆ",
            "ml": "പനി, തലവേദന, ശരീരവേദന എന്നിവയ്ക്ക് ആശ്വാസം നൽകാൻ"
        },
        "acidity_ulcer": {
            "en": "treating stomach gas, acidity, heartburn, and ulcers",
            "hi": "पेट की गैस, एसिडिटी, सीने में जलन और पेट के अल्सर के इलाज",
            "ta": "நெஞ்செரிச்சல், அசிடிட்டி மற்றும் வயிற்றுப் புண் குணமாக",
            "te": "ఎసిడిటీ, గ్యాస్, గుండెల్లో మంట మరియు కడుపు పూతల నివారణకు",
            "bn": "গ্যাস্ট্রিক এসিডিটি, বুকজ্বালা এবং পেটের আলসার নিরাময়ে",
            "mr": "पोटातील ॲसिडिटी, छातीत जळजळ आणि अल्सरच्या उपचारासाठी",
            "gu": "ગેસ, એસિડિટી, છાતીમાં બળતરા અને અલ્સરની સારવાર માટે",
            "kn": "ಹೊಟ್ಟೆಯ ಗ್ಯಾಸ್, ಎಸಿಡಿಟಿ, ಎದೆಉರಿ ಮತ್ತು ಹುಣ್ಣುಗಳ ನಿವಾರಣೆಗೆ",
            "ml": "അസിഡിറ്റി, നെഞ്ചെരിച്ചിൽ, ഗ്യാസ്, അൾസർ എന്നിവയ്ക്ക്"
        },
        "blood_pressure": {
            "en": "controlling high blood pressure and protecting the heart",
            "hi": "हाई ब्लड प्रेशर को नियंत्रित करने और दिल की सुरक्षा",
            "ta": "இரத்த அழுத்தத்தை சீராக்கவும் இதயத்தை பாதுகாக்கவும்",
            "te": "రక్తపోటును నియంత్రించడానికి మరియు గుండె రక్షణకు",
            "bn": "উচ্চ রক্তচাপ নিয়ন্ত্রণ ও হৃদযন্ত্র সুরক্ষিত রাখতে",
            "mr": "उच्च रक्तदाब नियंत्रित करण्यासाठी आणि हृदयाच्या आरोग्यासाठी",
            "gu": "હાઈ બ્લડ પ્રેશરને નિયંત્રિત કરવા અને હૃદયની સુરક્ષા માટે",
            "kn": "ರಕ್ತದೊತ್ತಡ ನಿಯಂತ್ರಣ ಮತ್ತು ಹೃದಯದ ರಕ್ಷಣೆಗೆ",
            "ml": "രക്തസമ്മർദ്ദം നിയന്ത്രിക്കാനും ഹൃദയസംരക്ഷണത്തിനും"
        },
        "diabetes": {
            "en": "managing blood sugar levels in diabetes",
            "hi": "ब्लड शुगर (डायबिटीज) को नियंत्रित रखने",
            "ta": "இரத்த சர்க்கரை அளவை கட்டுப்பாட்டில் வைக்க",
            "te": "రక్తంలో చక్కెర స్థాయిని నియంత్రణలో ఉంచడానికి",
            "bn": "রক্তে সুগারের মাত্রা নিয়ন্ত্রণে রাখতে",
            "mr": "रक्तातील साखरेची पातळी नियंत्रित ठेवण्यासाठी",
            "gu": "બ્લડ શુગરનું સ્તર નિયંત્રણમાં રાખવા માટે",
            "kn": "ರಕ್ತದಲ್ಲಿನ ಸಕ್ಕರೆ ಮಟ್ಟವನ್ನು ನಿಯಂತ್ರಿಸಲು",
            "ml": "രക്തത്തിലെ പഞ്ചസാരയുടെ അളവ് നിയന്ത്രിച്ചു നിർത്താൻ"
        },
        "cholesterol_blood_thinner": {
            "en": "lowering bad cholesterol and preventing blood clots",
            "hi": "खराब कोलेस्ट्रॉल कम करने और खून के थक्के रोकने",
            "ta": "கொலஸ்ட்ராலை குறைக்கவும் இரத்தம் உறைவதை தடுக்கவும்",
            "te": "కొలెస్ట్రాల్ తగ్గించడానికి మరియు రక్తం గడ్డకట్టకుండా నిరోధించడానికి",
            "bn": "খারাপ কোলেস্টেরল কমাতে এবং রক্ত জমাট বাঁধা রোধ করতে",
            "mr": "कोलेस्टेरॉल कमी करण्यासाठी आणि रक्ताच्या गुठळ्या रोखण्यासाठी",
            "gu": "કોલેસ્ટ્રોલ ઘટાડવા અને લોહી ગંઠાઈ જતું અટકાવવા",
            "kn": "ಕೊಲೆಸ್ಟ್ರಾಲ್ ಕಡಿಮೆ ಮಾಡಲು ಮತ್ತು ರಕ್ತ ಹೆಪ್ಪುಗಟ್ಟುವುದನ್ನು ತಡೆಯಲು",
            "ml": "കൊളസ്ട്രോൾ കുറയ്ക്കാനും രക്തം കട്ടപിടിക്കുന്നത് തടയാനും"
        },
        "antibiotic": {
            "en": "treating bacterial infections",
            "hi": "बैक्टीरियल इन्फेक्शन को पूरी तरह खत्म करने",
            "ta": "பாக்டீரியா தொற்றுகளை குணப்படுத்த",
            "te": "బాక్టీరియల్ ఇన్ఫెక్షన్ల నివారణకు",
            "bn": "ব্যাকটেরিয়াজনিত সংক্রমণের চিকিৎসায়",
            "mr": "बॅक्टेरियाच्या संसर्गावर मात करण्यासाठी",
            "gu": "બેક્ટેરિયલ ઇન્ફેક્શનની સારવાર માટે",
            "kn": "ಬ್ಯಾಕ್ಟೀರಿಯಾದ ಸೋಂಕನ್ನು ಗುಣಪಡಿಸಲು",
            "ml": "ബാക്ടീരിയൽ അണുബാധകളെ സുഖപ്പെടുത്താൻ"
        },
        "allergy_cough": {
            "en": "relieving allergies, sneezing, runny nose, and cough",
            "hi": "एलर्जी, छींक, बहती नाक और खांसी से राहत",
            "ta": "ஒவ்வாமை, தும்மல், சளி மற்றும் இருமலில் இருந்து நிவாரணம்",
            "te": "అలెర్జీ, తుమ్ములు, జలుబు మరియు దగ్గు నుండి ఉపశమనం",
            "bn": "অ্যালার্জি, হাঁচি, সর্দি এবং কাশি থেকে মুক্তির জন্য",
            "mr": "ऍलर्जी, शिंका, सर्दी आणि खोकल्यापासून आराम",
            "gu": "એલર્જી, છીંક, શરદી અને ખાંસીમાં રાહત માટે",
            "kn": "ಅಲರ್ಜಿ, ಸೀನು, ನೆಗಡಿ ಮತ್ತು ಕೆಮ್ಮಿನಿಂದ ಉಪಶಮನಕ್ಕೆ",
            "ml": "അലർജി, തുമ്മൽ, ജലദോഷം, ചുമ എന്നിവയിൽ നിന്ന് ആശ്വാസം"
        },
        "vitamins_minerals": {
            "en": "boosting immunity, energy, and correcting nutrient deficiencies",
            "hi": "शारीरिक कमजोरी दूर करने, पोषण और रोग प्रतिरोधक क्षमता बढ़ाने",
            "ta": "உடல் சோர்வை போக்கவும் நோய் எதிர்ப்பு சக்தியை அதிகரிக்கவும்",
            "te": "శరీర నీరసం తగ్గించడానికి మరియు రోగనిರೋಧక శక్తిని పెంచడానికి",
            "bn": "শারীরিক দুর্বলতা দূর করতে ও রোগ প্রতিরোধ ক্ষমতা বাড়াতে",
            "mr": "शारीरिक थकवा दूर करून रोगप्रतिकारक शक्ती वाढवण्यासाठी",
            "gu": "શરીરની નબળાઈ દૂર કરવા અને રોગપ્રતિકારક શક્તિ વધારવા",
            "kn": "ಶಾರೀರಿಕ ದೌರ್ಬಲ್ಯ ನಿವಾರಿಸಿ ರೋಗನಿರೋಧಕ ಶಕ್ತಿ ಹೆಚ್ಚಿಸಲು",
            "ml": "ശരീരക്ഷീണം മാറ്റി പ്രതിരോധശേഷി വർദ്ധിപ്പിക്കാൻ"
        },
        "thyroid": {
            "en": "maintaining thyroid hormone balance and body metabolism",
            "hi": "थायराइड हार्मोन को संतुलित रखने और मेटाबॉलिज्म सुधारने",
            "ta": "தைராய்டு ஹார்மோன் அளவை சீராக்க",
            "te": "థైరాయిడ్ హార్మోన్ సమతుల్యతను కాపాడటానికి",
            "bn": "থাইরয়েড হরমোনের ভারসাম্য বজায় রাখতে",
            "mr": "थायरॉईड हार्मोन्स संतुलित ठेवण्यासाठी",
            "gu": "થાઇરોઇડ હોર્મોનને સંતુલિત રાખવા માટે",
            "kn": "ಥೈರಾಯ್ಡ್ ಹಾರ್ಮೋನ್ ಸಮತೋಲನ ಕಾಪಾಡಲು",
            "ml": "തൈറോയ്ഡ് ഹോർമോൺ സന്തുലിതാവസ്ഥ നിലനിർത്താൻ"
        },
        "nerve_anxiety": {
            "en": "relieving nerve pain, numbness, and reducing anxiety",
            "hi": "नसों के दर्द, झनझनाहट और तनाव को कम करने",
            "ta": "நரம்பு வலி, மரத்துப்போதல் மற்றும் பதட்டத்தை குறைக்க",
            "te": "నరాల నొప్పులు, తిమ్మిర్లు మరియు ఆందోళన తగ్గించడానికి",
            "bn": "স্নায়ুর ব্যথা, অসাড়তা এবং উদ্বেগ কমাতে",
            "mr": "मज्जातंतूंचे दुखणे, बधिरता आणि चिंता कमी करण्यासाठी",
            "gu": "નસોના દુખાવા, ખાલી ચડવી અને ચિંતા ઘટાડવા માટે",
            "kn": "ನರಗಳ ನೋವು, ಮರಗಟ್ಟುವಿಕೆ ಮತ್ತು ಆತಂಕ ಕಡಿಮೆ ಮಾಡಲು",
            "ml": "നാഡീവേദന, തരിപ്പ്, ഉത്കണ്ഠ എന്നിവ കുറയ്ക്കാൻ"
        },
        "nausea_vomiting": {
            "en": "preventing vomiting, nausea, and motion sickness",
            "hi": "उल्टी और जी मिचलाने से तुरंत राहत",
            "ta": "வாந்தி மற்றும் குமட்டலை உடனடியாக கட்டுப்படுத்த",
            "te": "వాంతులు మరియు వికారం నుండి తక్షణ ఉపశమనం",
            "bn": "বমি এবং বমি বমি ভাব প্রতিরোধে",
            "mr": "उलटी आणि मळमळ थांबवण्यासाठी",
            "gu": "ઊલટી અને ઉબકા રોકવા માટે",
            "kn": "ವಾಂತಿ ಮತ್ತು ವಾಕರಿಕೆಯನ್ನು ತಡೆಯಲು",
            "ml": "ഛർദ്ദിയും ഓക്കാനവും തടയാൻ"
        },
        "general": {
            "en": uses_raw,
            "hi": uses_raw,
            "ta": uses_raw,
            "te": uses_raw,
            "bn": uses_raw,
            "mr": uses_raw,
            "gu": uses_raw,
            "kn": uses_raw,
            "ml": uses_raw
        }
    }

    clean_name = re.sub(r'\(.*?\)', '', name).strip()
    has_num_in_name = bool(re.search(r'\d+', clean_name))

    # Avoid duplicate dosages like "Calpol 650 650mg"
    clean_dose = ""
    if dosage and not has_num_in_name and "+" not in dosage:
        clean_dose = dosage.strip()

    scripts = {}

    # 1. English (en-IN)
    gen_text_en = _get_natural_generic_name(generic, "en", clean_name)
    gen_clause_en = f" containing {gen_text_en}" if gen_text_en else ""
    dose_clause_en = f" {clean_dose}" if clean_dose else ""
    scripts["en"] = {
        "locale": "en-IN",
        "name": "English",
        "flag": "🇬🇧",
        "text": f"This is {clean_name}{dose_clause_en} {form_clean}{gen_clause_en}. It is prescribed for {purpose_dict[purpose_key]['en']}. {timing_dict[food_key]['en']}{avoid_info['en']}"
    }

    # 2. Hindi (hi-IN)
    gen_text_hi = _get_natural_generic_name(generic, "hi", clean_name)
    gen_clause_hi = f", जिसमें {gen_text_hi} मौजूद है।" if gen_text_hi else "।"
    dose_clause_hi = f" {clean_dose}" if clean_dose else ""
    scripts["hi"] = {
        "locale": "hi-IN",
        "name": "हिन्दी (Hindi)",
        "flag": "🇮🇳",
        "text": f"यह {clean_name}{dose_clause_hi} टैबलेट है{gen_clause_hi} इसका उपयोग {purpose_dict[purpose_key]['hi']} के लिए किया जाता है। {timing_dict[food_key]['hi']}{avoid_info['hi']}"
    }

    # 3. Tamil (ta-IN)
    gen_text_ta = _get_natural_generic_name(generic, "ta", clean_name)
    gen_clause_ta = f", இதில் {gen_text_ta} உள்ளது." if gen_text_ta else "."
    dose_clause_ta = f" {clean_dose}" if clean_dose else ""
    scripts["ta"] = {
        "locale": "ta-IN",
        "name": "தமிழ் (Tamil)",
        "flag": "🇮🇳",
        "text": f"இது {clean_name}{dose_clause_ta} மாத்திரை{gen_clause_ta} இது {purpose_dict[purpose_key]['ta']} பயன்படுகிறது. {timing_dict[food_key]['ta']}{avoid_info['ta']}"
    }

    # 4. Telugu (te-IN)
    gen_text_te = _get_natural_generic_name(generic, "te", clean_name)
    gen_clause_te = f", ఇందులో {gen_text_te} ఉంటుంది." if gen_text_te else "."
    dose_clause_te = f" {clean_dose}" if clean_dose else ""
    scripts["te"] = {
        "locale": "te-IN",
        "name": "తెలుగు (Telugu)",
        "flag": "🇮🇳",
        "text": f"ఇది {clean_name}{dose_clause_te} టాబ్లెట్{gen_clause_te} ఇది {purpose_dict[purpose_key]['te']} ఉపయోగపడుతుంది. {timing_dict[food_key]['te']}{avoid_info['te']}"
    }

    # 5. Bengali (bn-IN)
    gen_text_bn = _get_natural_generic_name(generic, "bn", clean_name)
    gen_clause_bn = f", যাতে {gen_text_bn} রয়েছে।" if gen_text_bn else "।"
    dose_clause_bn = f" {clean_dose}" if clean_dose else ""
    scripts["bn"] = {
        "locale": "bn-IN",
        "name": "বাংলা (Bengali)",
        "flag": "🇮🇳",
        "text": f"এটি {clean_name}{dose_clause_bn} ট্যাবলেট{gen_clause_bn} এটি {purpose_dict[purpose_key]['bn']} ব্যবহৃত হয়। {timing_dict[food_key]['bn']}{avoid_info['bn']}"
    }

    # 6. Marathi (mr-IN)
    gen_text_mr = _get_natural_generic_name(generic, "mr", clean_name)
    gen_clause_mr = f", यामध्ये {gen_text_mr} समाविष्ट आहे." if gen_text_mr else "."
    dose_clause_mr = f" {clean_dose}" if clean_dose else ""
    scripts["mr"] = {
        "locale": "mr-IN",
        "name": "मराठी (Marathi)",
        "flag": "🇮🇳",
        "text": f"हे {clean_name}{dose_clause_mr} टॅब्लेट आहे{gen_clause_mr} हे {purpose_dict[purpose_key]['mr']} वापरले जाते. {timing_dict[food_key]['mr']}{avoid_info['mr']}"
    }

    # 7. Gujarati (gu-IN)
    gen_text_gu = _get_natural_generic_name(generic, "gu", clean_name)
    gen_clause_gu = f", જેમાં {gen_text_gu} છે." if gen_text_gu else "."
    dose_clause_gu = f" {clean_dose}" if clean_dose else ""
    scripts["gu"] = {
        "locale": "gu-IN",
        "name": "ગુજરાતી (Gujarati)",
        "flag": "🇮🇳",
        "text": f"આ {clean_name}{dose_clause_gu} ટેબ્લેટ છે{gen_clause_gu} આ {purpose_dict[purpose_key]['gu']} માટે વપરાય છે. {timing_dict[food_key]['gu']}{avoid_info['gu']}"
    }

    # 8. Kannada (kn-IN)
    gen_text_kn = _get_natural_generic_name(generic, "kn", clean_name)
    gen_clause_kn = f", ಇದರಲ್ಲಿ {gen_text_kn} ಇರುತ್ತದೆ." if gen_text_kn else "."
    dose_clause_kn = f" {clean_dose}" if clean_dose else ""
    scripts["kn"] = {
        "locale": "kn-IN",
        "name": "ಕನ್ನಡ (Kannada)",
        "flag": "🇮🇳",
        "text": f"ಇದು {clean_name}{dose_clause_kn} ಮಾತ್ರೆ{gen_clause_kn} ಇದನ್ನು {purpose_dict[purpose_key]['kn']} ಬಳಸಲಾಗುತ್ತದೆ. {timing_dict[food_key]['kn']}{avoid_info['kn']}"
    }

    # 9. Malayalam (ml-IN)
    gen_text_ml = _get_natural_generic_name(generic, "ml", clean_name)
    gen_clause_ml = f", ഇതിൽ {gen_text_ml} അടങ്ങിയിരിക്കുന്നു." if gen_text_ml else "."
    dose_clause_ml = f" {clean_dose}" if clean_dose else ""
    scripts["ml"] = {
        "locale": "ml-IN",
        "name": "മലയാളം (Malayalam)",
        "flag": "🇮🇳",
        "text": f"ഇത് {clean_name}{dose_clause_ml} ഗുളികയാണ്{gen_clause_ml} ഇത് {purpose_dict[purpose_key]['ml']} ഉപയോഗിക്കുന്നു. {timing_dict[food_key]['ml']}{avoid_info['ml']}"
    }

    scripts["avoid_items"] = avoid_info["items"]
    return scripts
