"""
MediMitra AI Health Assistant
Provides simple-language answers about prescribed medicines,
supports regional languages (Hindi, English), voice synthesis,
and clinical escalation to assigned doctors.
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from routes.auth import role_required, get_current_user
from database.db import query_db, execute_db

assistant_bp = Blueprint('assistant', __name__, url_prefix='/assistant')


@assistant_bp.route('', methods=['GET'])
@role_required('patient')
def index():
    user_id = session['user_id']
    # Fetch patient's active medicines to give context to assistant
    medicines = query_db(
        "SELECT name, generic_name, dosage, form, purpose, warnings, before_after_food FROM medicines WHERE user_id = ?",
        [user_id]
    )
    profile = query_db("SELECT * FROM patient_profiles WHERE user_id = ?", [user_id], one=True)
    return render_template('assistant.html', medicines=medicines, profile=profile)


@assistant_bp.route('/ask', methods=['POST'])
@role_required('patient')
def ask():
    user_id = session['user_id']
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    language = data.get('language', 'en')  # 'en' or 'hi'

    if not question:
        return jsonify({'error': 'Please provide a question.'}), 400

    # Retrieve patient's current medicines
    patient_meds = query_db("SELECT name, generic_name, dosage, purpose, before_after_food, warnings FROM medicines WHERE user_id = ?", [user_id])
    med_names = [m['name'].lower() for m in patient_meds] + [m['generic_name'].lower() for m in patient_meds if m['generic_name']]

    # Check verified medicine knowledgebase
    matched_db = None
    for m in patient_meds:
        # Search db by medicine name or generic
        matched = query_db(
            "SELECT * FROM medicine_database WHERE LOWER(name) LIKE ? OR LOWER(generic_name) LIKE ? LIMIT 1",
            [f"%{m['name'].split()[0].lower()}%", f"%{m['name'].split()[0].lower()}%"], one=True
        )
        if matched and (m['name'].lower() in question.lower() or (m['generic_name'] and m['generic_name'].lower() in question.lower())):
            matched_db = matched
            break

    if not matched_db:
        # Check if any master medicine is mentioned in question
        words = question.lower().split()
        for w in words:
            if len(w) > 3:
                res = query_db("SELECT * FROM medicine_database WHERE LOWER(name) LIKE ? OR LOWER(generic_name) LIKE ? LIMIT 1", [f"%{w}%", f"%{w}%"], one=True)
                if res:
                    matched_db = res
                    break

    # Build reliable, clinically guarded response
    is_hindi = (language == 'hi')
    q_lower = question.lower()
    spoken_answer = ""

    if matched_db:
        med_name = matched_db['name']
        timing = matched_db['before_after_food'] or "Follow your prescription instructions."
        uses = matched_db['common_uses'] or "Prescribed for your diagnosed medical condition."
        side_effects = matched_db['side_effects'] or "Mild stomach upset, nausea, headache."
        warnings = matched_db['warnings'] or "Do not alter dosage without physician consultation."

        if any(kw in q_lower for kw in ['food', 'before', 'after', 'eat', 'empty stomach', 'khana', 'khana khane', 'சாப்பாடு', 'உணவு', 'భోజనం']):
            if language == 'hi':
                answer = f"**{med_name} भोजन निर्देश:** {timing}। कृपया इसे समय पर पानी के साथ लें।"
                spoken_answer = f"{med_name} के भोजन निर्देश। {timing}। कृपया इसे समय पर पानी के साथ लें।"
            elif language == 'ta':
                answer = f"**{med_name} உணவு அறிவுரை:** {timing}। தயவுசெய்து இதை உணவு உண்ட பிறகு தண்ணீருடன் உட்கொள்ளவும்."
                spoken_answer = f"{med_name} உணவு அறிவுரை. தயவுசெய்து இதை உணவு உண்ட பிறகு தண்ணீருடன் உட்கொள்ளவும்."
            elif language == 'te':
                answer = f"**{med_name} ఆహార నియమం:** {timing}। దయచేసి దీనిని భోజనం చేసిన తర్వాత మాత్రమే నీటితో వేసుకోండి."
                spoken_answer = f"{med_name} ఆహార నియమం. దయచేసి దీనిని భోజనం చేసిన తర్వాత మాత్రమే నీటితో వేసుకోండి."
            else:
                answer = f"**Food Instructions for {med_name}:** {timing}. Taking it consistently helps prevent gastric discomfort."
                spoken_answer = f"Food instructions for {med_name}. {timing}. Taking it consistently helps prevent gastric discomfort."
        elif any(kw in q_lower for kw in ['side effect', 'side-effect', 'risk', 'nuksan', 'problem']):
            if language == 'hi':
                answer = f"**{med_name} के संभावित दुष्प्रभाव:** {side_effects}। चेतावनी: {warnings}।"
                spoken_answer = f"{med_name} के संभावित दुष्प्रभाव: {side_effects}। कृपया अधिक जानकारी के लिए डॉक्टर से परामर्श करें।"
            elif language == 'ta':
                answer = f"**{med_name} பக்க விளைவுகள்:** {side_effects}। எச்சரிக்கை: {warnings}।"
                spoken_answer = f"{med_name} பக்க விளைவுகள்: {side_effects}."
            elif language == 'te':
                answer = f"**{med_name} దుష్ప్రభావాలు:** {side_effects}। హెచ్చరిక: {warnings}।"
                spoken_answer = f"{med_name} దుష్ప్రభావాలు: {side_effects}."
            else:
                answer = f"**Possible Side Effects of {med_name}:** {side_effects}.\n\n*Important Clinical Warning:* {warnings}"
                spoken_answer = f"Possible side effects of {med_name} include {side_effects}. Please consult your doctor if symptoms persist."
        elif any(kw in q_lower for kw in ['why', 'use', 'purpose', 'kya kaam', 'kis liye', 'fayda']):
            if language == 'hi':
                answer = f"**{med_name} का उपयोग:** {uses}। इसे डॉक्टर द्वारा सुझाई गई खुराक में ही लें।"
                spoken_answer = f"{med_name} का उपयोग: {uses}। इसे डॉक्टर द्वारा निर्धारित खुराक में ही लें।"
            elif language == 'ta':
                answer = f"**{med_name} பயன்பாடு:** {uses}। மருத்துவர் பரிந்துரைத்த அளவில் மட்டுமே உட்கொள்ளவும்."
                spoken_answer = f"{med_name} பயன்பாடு: {uses}."
            elif language == 'te':
                answer = f"**{med_name} ఉపయోగాలు:** {uses}। డాక్టర్ సూచించిన మోతాదులో మాత్రమే వేసుకోండి."
                spoken_answer = f"{med_name} ఉపయోగాలు: {uses}."
            else:
                answer = f"**Clinical Purpose of {med_name}:** {uses}."
                spoken_answer = f"Clinical purpose of {med_name}: {uses}."
        else:
            if language == 'hi':
                answer = f"**{med_name} ({matched_db['generic_name'] or ''}):**\n• **उपयोग:** {uses}\n• **भोजन निर्देश:** {timing}\n• **सावधानी:** {warnings}"
                spoken_answer = f"{med_name}। इसका उपयोग {uses}। भोजन निर्देश: {timing}।"
            else:
                answer = f"**{med_name} Overview ({matched_db['generic_name'] or ''}):**\n• **Purpose:** {uses}\n• **Timing:** {timing}\n• **Key Safety Info:** {warnings}"
                spoken_answer = f"{med_name} overview. Prescribed for {uses}. {timing}."

    else:
        # General guidance
        if any(kw in q_lower for kw in ['missed', 'forgot', 'bhool gaya', 'chhoot']):
            if language == 'hi':
                answer = "यदि आप खुराक लेना भूल गए हैं, तो याद आते ही ले लें। यदि अगली खुराक का समय निकट है, तो छूटी हुई खुराक छोड़ दें। कभी भी दोहरी खुराक न लें।"
                spoken_answer = answer
            else:
                answer = "If you missed a dose, take it as soon as you remember. However, if it is almost time for your next scheduled dose, skip the missed dose and resume your normal schedule. Never take a double dose."
                spoken_answer = answer
        elif any(kw in q_lower for kw in ['pain', 'dard', 'fever', 'bukhar', 'headache', 'sir dard']):
            if language == 'hi':
                answer = "हल्के दर्द या बुखार के लिए डॉक्टर अक्सर पैरासिटामोल (Dolo 650) भोजन के बाद लेने की सलाह देते हैं। कृपया अधिक जानकारी के लिए अपने डॉक्टर से परामर्श करें।"
                spoken_answer = answer
            else:
                answer = "For mild fever or body aches, doctors commonly recommend Paracetamol (such as Dolo 650) taken after food. Please consult your physician if symptoms persist."
                spoken_answer = answer
        else:
            med_list = ', '.join([m['name'] for m in patient_meds]) or 'your medicines'
            if language == 'hi':
                answer = f"आपकी सक्रिय दवाओं ({med_list}) के अनुसार, कृपया डॉक्टर द्वारा निर्धारित समय और भोजन नियमों का पालन करें। किसी भी प्रश्न के लिए नीचे 'डॉक्टर से पूछें' बटन दबाएं।"
                spoken_answer = f"आपकी सक्रिय दवाओं के अनुसार, कृपया डॉक्टर द्वारा निर्धारित समय और भोजन नियमों का पालन करें।"
            else:
                answer = f"Based on your prescribed medications ({med_list}), please maintain consistent timing with meals as directed. For clinical advice, you can escalate this question directly to your doctor below."
                spoken_answer = "Based on your prescribed medications, please maintain consistent timing with meals as directed."

    # Clinical safety disclaimer
    disclaimer = " (नोट: यह AI सहायक केवल जानकारी के लिए है और चिकित्सा निदान नहीं देता।)" if is_hindi else " *(Note: MediMitra AI provides educational medicine guidance and does not replace professional medical diagnosis or dosage adjustments.)*"
    
    return jsonify({
        'answer': answer + "\n\n" + disclaimer,
        'spoken_text': spoken_answer or answer,
        'matched_medicine': matched_db['name'] if matched_db else None,
        'can_escalate': True
    })


@assistant_bp.route('/escalate', methods=['POST'])
@role_required('patient')
def escalate():
    user_id = session['user_id']
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    subject = data.get('subject', 'Question forwarded from AI Health Assistant').strip()

    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    # Assign to patient's verified doctor
    assigned = query_db(
        "SELECT assigned_doctor_id FROM prescriptions WHERE user_id=? AND assigned_doctor_id IS NOT NULL ORDER BY approved_at DESC LIMIT 1",
        [user_id], one=True
    )
    doctor_id = assigned['assigned_doctor_id'] if assigned else None
    if not doctor_id:
        doc = query_db("SELECT user_id FROM doctor_profiles WHERE verification_status='verified' LIMIT 1", one=True)
        doctor_id = doc['user_id'] if doc else None

    execute_db(
        """INSERT INTO patient_queries (patient_id, doctor_id, subject, question, status, escalated_from_ai)
           VALUES (?, ?, ?, ?, 'pending', 1)""",
        [user_id, doctor_id, subject, question]
    )

    return jsonify({
        'success': True,
        'message': 'Your question has been escalated directly to the doctor. You can track their response in the "Ask My Doctor" section.'
    })
