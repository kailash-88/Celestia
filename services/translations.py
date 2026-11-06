"""
MediMitra Multilingual UI Translation Engine
Provides full English (en), Hindi (hi), and Tamil (ta) translations for the patient interface.
"""

TRANSLATIONS = {
    # =========================================================================
    # ENGLISH (en)
    # =========================================================================
    "en": {
        # App brand & generic
        "app_name": "MediMitra",
        "tagline": "Smart Medicine Companion",
        "patient_portal": "PATIENT WELLNESS PORTAL",
        "greeting_morning": "Good morning",
        "greeting_afternoon": "Good afternoon",
        "greeting_evening": "Good evening",
        "welcome_sub": "Your simple daily medicine companion. Scan tablets, check food timing, and stay healthy.",
        
        # Navigation
        "nav_overview": "Health Overview",
        "nav_scan_tablet": "Scan Tablet / Medicine",
        "nav_scan_prescription": "Scan Prescription",
        "nav_prescriptions": "My Prescriptions",
        "nav_medicines": "My Medicines",
        "nav_schedule": "Daily Schedule",
        "nav_settings": "Settings",
        "nav_logout": "Logout",
        
        # Auto-Camera Controls
        "auto_cam_title": "Auto-Open Camera on App Launch",
        "auto_cam_desc": "Automatically open camera to scan medicine strips as soon as you open MediMitra.",
        "auto_cam_badge_active": "ACTIVE",
        "auto_cam_badge_off": "OFF",
        "auto_cam_on": "Auto-Camera ON",
        "auto_cam_off": "Auto-Camera OFF",
        "open_camera_btn": "📸 Open Camera Scanner",
        "upload_prescription_btn": "📄 Upload Prescription",
        "launch_camera_pill": "Launch Camera",
        "lang_switch_label": "Language / भाषा / மொழி:",
        
        # Today's Schedule
        "today_schedule_title": "Today's Medicine Schedule",
        "today_schedule_sub": "Take your medicines on time as prescribed by your doctor.",
        "morning": "Morning (8:00 AM)",
        "afternoon": "Afternoon (1:00 PM)",
        "evening": "Evening (6:00 PM)",
        "night": "Night (9:00 PM)",
        "take_dose": "Take Medicine",
        "dose_taken": "Taken ✓",
        "skip_dose": "Skip",
        "take_after_food": "Take after meals with water",
        "take_before_food": "Take before meals on empty stomach",
        "no_meds_title": "No medicines scheduled for today!",
        "no_meds_desc": "Scan a tablet strip or doctor's prescription above to add your medications.",
        
        # Doctor's advice & Emergency
        "doctor_advice_title": "Doctor's Advice & Updates",
        "emergency_sos_title": "Emergency SOS",
        "emergency_sos_desc": "Alert your emergency contact or doctor with one tap.",
        "emergency_btn": "🚨 Send Emergency Alert",
        
        # Scanner Page
        "scanner_title": "AI Medicine & Tablet Scanner",
        "scanner_sub": "Point your camera at any tablet strip or blister pack. MediMitra detects the medicine, food timing, and what to avoid.",
        "live_camera_title": "Live Camera Feed",
        "camera_target_guide": "Align medicine strip or prescription inside the frame",
        "take_photo_btn": "📸 Take Photo & Scan",
        "switch_cam_btn": "🔄 Flip Camera",
        "choose_gallery_btn": "🖼️ Choose from Gallery",
        "open_phone_camera": "📸 Tap to Open Phone Camera",
        "back_to_dashboard": "⬅️ Back to Schedule",
        "analyzing_pill": "Analyzing medicine with AI...",
        "photo_ready": "Photo captured and ready for analysis",
        "analyze_btn": "Analyze Medicine Now",
        
        # Medical Results
        "med_identified": "Medicine Identified",
        "generic_name": "Generic Composition",
        "strength": "Dosage / Strength",
        "manufacturer": "Manufacturer",
        "prescribed_for_heading": "WHAT THIS MEDICINE IS PRESCRIBED FOR:",
        "food_timing_heading": "HOW & WHEN TO TAKE (FOOD TIMING):",
        "avoid_heading": "⚠️ WHAT NOT TO TAKE / THINGS TO AVOID:",
        "voice_companion_title": "AI Voice Companion 🔊",
        "voice_companion_desc": "Speaks the medicine details and avoidance instructions in your language.",
        "listen_voice": "Listen Aloud",
        "stop_voice": "Stop Voice",
        "auto_speak_label": "Auto-speak on scan",
        "speed": "Speed",
        "copied": "Copied to clipboard!",
    },

    # =========================================================================
    # HINDI (hi)
    # =========================================================================
    "hi": {
        # App brand & generic
        "app_name": "मेडि मित्र",
        "tagline": "आपका स्मार्ट दवा साथी",
        "patient_portal": "रोगी स्वास्थ्य सेवा पोर्टल",
        "greeting_morning": "शुभ प्रभात",
        "greeting_afternoon": "शुभ दोपहर",
        "greeting_evening": "शुभ संध्या",
        "welcome_sub": "आपका सरल दैनिक दवा साथी। टैबलेट स्कैन करें, भोजन का समय जानें और स्वस्थ रहें।",
        
        # Navigation
        "nav_overview": "स्वास्थ्य डैशबोर्ड",
        "nav_scan_tablet": "दवा / टैबलेट स्कैन करें",
        "nav_scan_prescription": "पर्ची स्कैन करें",
        "nav_prescriptions": "मेरी पर्चियां",
        "nav_medicines": "मेरी दवाएं",
        "nav_schedule": "दैनिक समय सारणी",
        "nav_settings": "सेटिंग्स",
        "nav_logout": "लॉग आउट",
        
        # Auto-Camera Controls
        "auto_cam_title": "ऐप खोलते ही कैमरा स्वचालित रूप से खोलें",
        "auto_cam_desc": "सक्रिय होने पर, मेडिमित्र ऐप खोलते ही सीधे टैबलेट स्कैन करने के लिए कैमरा खोलता है।",
        "auto_cam_badge_active": "चालू",
        "auto_cam_badge_off": "बंद",
        "auto_cam_on": "ऑटो कैमरा चालू",
        "auto_cam_off": "ऑटो कैमरा बंद",
        "open_camera_btn": "📸 कैमरा स्कैनर खोलें",
        "upload_prescription_btn": "📄 डॉक्टर की पर्ची स्कैन करें",
        "launch_camera_pill": "कैमरा शुरू करें",
        "lang_switch_label": "भाषा / Language:",
        
        # Today's Schedule
        "today_schedule_title": "आज की दवाएं और समय",
        "today_schedule_sub": "डॉक्टर द्वारा बताई गई दवाएं सही समय पर लें।",
        "morning": "सुबह (8:00 AM)",
        "afternoon": "दोपहर (1:00 PM)",
        "evening": "शाम (6:00 PM)",
        "night": "रात (9:00 PM)",
        "take_dose": "दवा ले ली ✓",
        "dose_taken": "ली गई ✓",
        "skip_dose": "छोड़ें",
        "take_after_food": "खाने के बाद पानी के साथ लें",
        "take_before_food": "खाने से पहले खाली पेट लें",
        "no_meds_title": "आज के लिए कोई दवा निर्धारित नहीं है!",
        "no_meds_desc": "दवा जोड़ने के लिए ऊपर कैमरा खोलें या डॉक्टर की पर्ची स्कैन करें।",
        
        # Doctor's advice & Emergency
        "doctor_advice_title": "डॉक्टर की सलाह और निर्देश",
        "emergency_sos_title": "आपातकालीन एसओएस (Emergency)",
        "emergency_sos_desc": "एक टैप में अपने परिवार या डॉक्टर को आपातकालीन अलर्ट भेजें।",
        "emergency_btn": "🚨 आपातकालीन अलर्ट भेजें",
        
        # Scanner Page
        "scanner_title": "एआई दवा और टैबलेट स्कैनर",
        "scanner_sub": "कैमरे को किसी भी टैबलेट स्ट्रिप या पैकेट के सामने रखें। मेडिमित्र दवा का नाम, खाने का समय और परहेज बताएगा।",
        "live_camera_title": "लाइव कैमरा",
        "camera_target_guide": "टैबलेट स्ट्रिप या पर्ची को फ्रेम के बीच में रखें",
        "take_photo_btn": "📸 फोटो खींचें और स्कैन करें",
        "switch_cam_btn": "🔄 कैमरा बदलें",
        "choose_gallery_btn": "🖼️ गैलरी से फोटो चुनें",
        "open_phone_camera": "📸 फोन का कैमरा खोलने के लिए यहां टैप करें",
        "back_to_dashboard": "⬅️ वापस समय सारणी पर जाएं",
        "analyzing_pill": "एआई से दवा की जांच हो रही है...",
        "photo_ready": "फोटो तैयार है, जांच के लिए बटन दबाएं",
        "analyze_btn": "दवा की पहचान करें",
        
        # Medical Results
        "med_identified": "पहचानी गई दवा",
        "generic_name": "मूल रासायनिक घटक (Generic)",
        "strength": "मात्रा / खुराक (Strength)",
        "manufacturer": "दवा निर्माता",
        "prescribed_for_heading": "यह दवा किस बीमारी / परेशानी के लिए है:",
        "food_timing_heading": "दवा कब और कैसे लें (भोजन का समय):",
        "avoid_heading": "⚠️ क्या न लें / क्या परहेज करें (सावधानी):",
        "voice_companion_title": "एआई आवाज़ साथी (Voice) 🔊",
        "voice_companion_desc": "दवा का नाम, लेने का सही समय और परहेज अपनी भाषा में सुनें।",
        "listen_voice": "आवाज़ में सुनें",
        "stop_voice": "आवाज़ रोकें",
        "auto_speak_label": "स्कैन होते ही आवाज़ में बोलें",
        "speed": "गति",
        "copied": "कॉपी हो गया!",
    },

    # =========================================================================
    # TAMIL (ta)
    # =========================================================================
    "ta": {
        # App brand & generic
        "app_name": "மெடிமித்ரா",
        "tagline": "உங்கள் ஸ்மார்ட் மருந்து உதவியாளர்",
        "patient_portal": "நோயாளி நல்வாழ்வு தளம்",
        "greeting_morning": "காலை வணக்கம்",
        "greeting_afternoon": "மதிய வணக்கம்",
        "greeting_evening": "மாலை வணக்கம்",
        "welcome_sub": "உங்கள் எளிய தினசரி மருந்து தோழன். மாத்திரைகளை ஸ்கேன் செய்யவும், நேரத்தைக் கண்காணிக்கவும், நலமுடன் வாழவும்.",
        
        # Navigation
        "nav_overview": "சுகாதார மேலோட்டம்",
        "nav_scan_tablet": "மாத்திரை ஸ்கேன் செய்க",
        "nav_scan_prescription": "மருந்து சீட்டு ஸ்கேன்",
        "nav_prescriptions": "எனது மருந்து சீட்டுகள்",
        "nav_medicines": "எனது மருந்துகள்",
        "nav_schedule": "தினசரி அட்டவணை",
        "nav_settings": "அமைப்புகள்",
        "nav_logout": "வெளியேறு",
        
        # Auto-Camera Controls
        "auto_cam_title": "செயலி திறக்கும் போதே கேமராவை தானாகத் திறக்கவும்",
        "auto_cam_desc": "செயலில் இருக்கும்போது, மாத்திரைகளை உடனடியாக ஸ்கேன் செய்ய மெடிமித்ரா நேரடியாக கேமராவைத் திறக்கும்.",
        "auto_cam_badge_active": "இயக்கத்தில்",
        "auto_cam_badge_off": "முடக்கம்",
        "auto_cam_on": "ஆட்டோ கேமரா ஆன்",
        "auto_cam_off": "ஆட்டோ கேமரா ஆஃப்",
        "open_camera_btn": "📸 கேமரா ஸ்கேனரைத் திறக்கவும்",
        "upload_prescription_btn": "📄 மருந்து சீட்டை ஸ்கேன் செய்க",
        "launch_camera_pill": "கேமராவைத் தொடங்கவும்",
        "lang_switch_label": "மொழி / Language:",
        
        # Today's Schedule
        "today_schedule_title": "இன்றைய மருந்து அட்டவணை",
        "today_schedule_sub": "மருத்துவர் பரிந்துரைத்தபடி மருந்துகளை சரியான நேரத்தில் உட்கொள்ளவும்.",
        "morning": "காலை (8:00 AM)",
        "afternoon": "மதியம் (1:00 PM)",
        "evening": "மாலை (6:00 PM)",
        "night": "இரவு (9:00 PM)",
        "take_dose": "மருந்து எடுத்தேன் ✓",
        "dose_taken": "எடுக்கப்பட்டது ✓",
        "skip_dose": "தவிர்",
        "take_after_food": "உணவுக்குப் பின் தண்ணீருடன் உட்கொள்ளவும்",
        "take_before_food": "உணவுக்கு முன் வெறும் வயிற்றில் உட்கொள்ளவும்",
        "no_meds_title": "இன்று எந்த மருந்துகளும் திட்டமிடப்படவில்லை!",
        "no_meds_desc": "மருந்துகளைச் சேர்க்க மேலே உள்ள கேமராவைத் திறந்து மாத்திரை அல்லது மருந்து சீட்டை ஸ்கேன் செய்யவும்.",
        
        # Doctor's advice & Emergency
        "doctor_advice_title": "மருத்துவரின் ஆலோசனை மற்றும் குறிப்புகள்",
        "emergency_sos_title": "அவசர உதவி (SOS)",
        "emergency_sos_desc": "ஒரே தட்டலில் உங்கள் குடும்பத்தினருக்கோ அல்லது மருத்துவருக்கோ அவசர எச்சரிக்கை அனுப்பவும்.",
        "emergency_btn": "🚨 அவசர எச்சரிக்கை அனுப்பு",
        
        # Scanner Page
        "scanner_title": "AI மாத்திரை மற்றும் மருந்து ஸ்கேனர்",
        "scanner_sub": "மாத்திரை அட்டை அல்லது மருந்து பாக்கெட்டை கேமராவில் காட்டவும். அதன் பயன்பாடு, உணவு நேரம் மற்றும் தவிர்க்க வேண்டியவற்றை மெடிமித்ரா கூறும்.",
        "live_camera_title": "நேரடி கேமரா காட்சி",
        "camera_target_guide": "மாத்திரை அல்லது மருந்து சீட்டை சட்டகத்திற்குள் சரியாக வைக்கவும்",
        "take_photo_btn": "📸 படம் எடுத்து ஸ்கேன் செய்",
        "switch_cam_btn": "🔄 கேமராவை மாற்று",
        "choose_gallery_btn": "🖼️ கேலரியில் இருந்து தேர்வு செய்",
        "open_phone_camera": "📸 போன் கேமராவைத் திறக்க இங்கே தட்டவும்",
        "back_to_dashboard": "⬅️ அட்டவணைக்குத் திரும்பு",
        "analyzing_pill": "AI மூலம் மருந்து பகுப்பாய்வு செய்யப்படுகிறது...",
        "photo_ready": "படம் தயாராக உள்ளது, பகுப்பாய்வு செய்ய கிளிக் செய்யவும்",
        "analyze_btn": "மருந்தை கண்டறியவும்",
        
        # Medical Results
        "med_identified": "கண்டறியப்பட்ட மருந்து",
        "generic_name": "மருந்தின் மூலக்கூறு (Generic)",
        "strength": "அளவு / வீரியம் (Strength)",
        "manufacturer": "உற்பத்தியாளர்",
        "prescribed_for_heading": "இந்த மருந்து எதற்காக பரிந்துரைக்கப்பட்டது:",
        "food_timing_heading": "எப்போது மற்றும் எப்படி உட்கொள்ள வேண்டும்:",
        "avoid_heading": "⚠️ எதை உட்கொள்ளக் கூடாது / தவிர்க்க வேண்டியவை:",
        "voice_companion_title": "AI குரல் உதவியாளர் (Voice) 🔊",
        "voice_companion_desc": "மருந்தின் விவரங்கள் மற்றும் எச்சரிக்கைகளை உங்கள் சொந்த மொழியிலேயே கேளுங்கள்.",
        "listen_voice": "குரலில் கேட்கவும்",
        "stop_voice": "குரலை நிறுத்து",
        "auto_speak_label": "தானாகக் குரலில் பேசவும்",
        "speed": "வேகம்",
        "copied": "நகலெடுக்கப்பட்டது!",
    }
}


def get_translation(key, lang="en", default=None):
    """Retrieve translated string for given key and language code (en, hi, ta)."""
    if not lang or lang not in TRANSLATIONS:
        lang = "en"
    
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    if key in lang_dict:
        return lang_dict[key]
    
    # Fallback to English
    return TRANSLATIONS["en"].get(key, default or key)
