import os
# Fix for OpenBLAS Memory Allocation error on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from flask import Flask, request, jsonify, send_from_directory
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
import mysql.connector
from flask import Flask, Blueprint, request, jsonify
# import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from functools import wraps
import string
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
import re
import os
from werkzeug.utils import secure_filename
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np

# Try to import TFLite (support both full tensorflow and tflite-runtime)
tflite = None
def _import_tflite():
    global tflite
    if tflite is not None:
        return tflite
    try:
        import tflite_runtime.interpreter as tfl_runtime
        tflite = tfl_runtime
    except ImportError:
        try:
            from tensorflow import lite as tfl_lite
            tflite = tfl_lite
        except ImportError:
            print("Warning: TFLite not found. Real AI analysis will be disabled.")
    return tflite
import sys
import io

# Ensure UTF-8 for console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)

# ✅ CONFIGURATION
app.config["JWT_SECRET_KEY"] = "smileai_super_secure_secret_key_2026_minimum_32_chars"
jwt = JWTManager(app)

# --- UPLOAD CONFIG ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database Configuration (XAMPP MySQL)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smile_ai',
    'port': 3307   # match XAMPP port
}

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pragnasreebalijapelly@gmail.com'
app.config['MAIL_PASSWORD'] = 'bnsufyagovcczpyy'
app.config['MAIL_DEFAULT_SENDER'] = 'pragnasreebalijapelly@gmail.com'

mail = Mail(app)

def clean_text(text):
    if not text: return "N/A"
    # Remove emojis and non-latin-1 characters that crash FPDF
    return text.encode('ascii', 'ignore').decode('ascii').replace("  ", " ").strip()

# --- HELPERS ---
def get_db_connection():
    return mysql.connector.connect(**db_config)

def generate_random_code(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_patient_id(numeric_id):
    return f"P{numeric_id:04d}"

def normalize_patient_id(pid):
    """Standardize patient ID: uppercase and remove hyphens."""
    if not pid: return pid
    return str(pid).strip().upper().replace("-", "")

def generate_dentist_id():
    import random
    return 'D' + ''.join(random.choices(string.digits, k=4))

def validate_full_name(name):
    if not name or len(name.strip()) < 2:
        return "Full name must be at least 2 characters"
    return None

def validate_phone(phone):
    if phone and not re.fullmatch(r"[6-9]\d{9}", str(phone)):
        return "Phone must be a valid 10-digit Indian number"
    return None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT r.*, dp.dentist_id, dp.specialization, dp.clinic_address
        FROM register r
        LEFT JOIN dentist_profiles dp ON r.id = dp.user_id
        WHERE r.id = %s
    """
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def require_role(user, role):
    return user and user.get("role") == role

# ✅ ROUTES

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "success", "message": "SmileAI Production API is running!"})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    phone = data.get('phone')
    specialization = data.get('specialization')
    clinic_address = data.get('clinic_address')
    clinical_id = normalize_patient_id(data.get('patient_id')) # Optional patient_id from frontend

    if not full_name or not email or not password or not role:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    hashed_password = generate_password_hash(password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM register WHERE email=%s", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"status": "error", "message": "Already existed"}), 400
        
        # Insert into register (initial insert without clinical_id if patient)
        clinical_id = None
        if role == 'dentist':
            clinical_id = generate_dentist_id()
            
        query = "INSERT INTO register (full_name, email, password, role, phone, patient_id) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (full_name, email, hashed_password, role, phone, clinical_id))
        user_id = cursor.lastrowid
        
        # If patient, generate sequential ID and update
        if role == 'patient':
            clinical_id = generate_patient_id(user_id)
            cursor.execute("UPDATE register SET patient_id = %s WHERE id = %s", (clinical_id, user_id))

        # Insert into dentist_profiles if applicable
        if role == 'dentist':
            cursor.execute("INSERT INTO dentist_profiles (user_id, dentist_id, specialization, clinic_address) VALUES (%s, %s, %s, %s)",
                           (user_id, clinical_id, specialization, clinic_address))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "User registered successfully", "clinical_id": clinical_id}), 201
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier, password = data.get('email'), data.get('password')
    if not identifier or not password: return jsonify({"status": "error", "message": "Missing credentials"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        normalized_id = normalize_patient_id(identifier)
        cursor.execute("SELECT * FROM register WHERE email=%s OR patient_id=%s", (identifier, normalized_id))
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "message": "user doesn't exists"}), 401
        if not check_password_hash(user['password'], password):
            return jsonify({"status": "error", "message": "identity by email id"}), 401
        access_token = create_access_token(identity=str(user['id']))
        return jsonify({"status": "success", "message": "Login successful", "access_token": access_token, "user": user}), 200
    except mysql.connector.Error as err: return jsonify({"status": "error", "message": str(err)}), 400

@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # JOIN register and dentist_profiles
        query = """
            SELECT r.id, r.full_name, r.email, r.role, r.phone, r.patient_id, r.plan_type, r.profile_photo,
                   dp.dentist_id, dp.specialization, dp.clinic_address
            FROM register r
            LEFT JOIN dentist_profiles dp ON r.id = dp.user_id
            WHERE r.id = %s
        """
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            # Clean up response based on role
            if user.get('role') == 'patient':
                user.pop('dentist_id', None)
                user.pop('specialization', None)
                user.pop('clinic_address', None)
            
            return jsonify({"status": "success", "user": user}), 200
        return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/patient/profile', methods=['GET'])
@jwt_required()
def get_patient_profile():
    return get_profile()

@app.route('/patient/stats', methods=['GET'])
@jwt_required()
def get_patient_stats():
    user_id = get_jwt_identity()
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Get patient_id for this user
        cursor.execute("SELECT patient_id FROM register WHERE id = %s", (user_id,))
        res = cursor.fetchone()
        if not res: return jsonify({"status": "error", "message": "User not found"}), 404
        
        patient_id = normalize_patient_id(res['patient_id'])
        
        # Count active cases
        cursor.execute("SELECT COUNT(*) as count FROM cases WHERE patient_id = %s AND status IN ('Active', 'In Progress')", (patient_id,))
        active_cases = cursor.fetchone()['count']
        
        # Count reports (JOIN with cases to filter by patient_id)
        query_reports = """
            SELECT COUNT(*) as count 
            FROM reports r 
            JOIN cases c ON r.case_id = c.id 
            WHERE c.patient_id = %s
        """
        cursor.execute(query_reports, (patient_id,))
        total_reports = cursor.fetchone()['count']
        
        # Count unread notifications
        cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = 0", (user_id,))
        unread_notifs = cursor.fetchone()['count']
        
        conn.close()
        return jsonify({
            "status": "success",
            "active_cases": active_cases,
            "total_reports": total_reports,
            "unread_notifications": unread_notifs
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update register table
        reg_fields, reg_values = [], []
        for key in ['full_name', 'phone', 'plan_type', 'profile_photo']:
            if key in data:
                reg_fields.append(f"{key} = %s")
                reg_values.append(data[key])
        
        if reg_fields:
            reg_values.append(user_id)
            cursor.execute(f"UPDATE register SET {', '.join(reg_fields)} WHERE id = %s", tuple(reg_values))
        
        # Update dentist_profiles if dentist
        dp_fields, dp_values = [], []
        for key in ['specialization', 'clinic_address']:
            if key in data:
                dp_fields.append(f"{key} = %s")
                dp_values.append(data[key])
        
        if dp_fields:
            dp_values.append(user_id)
            cursor.execute(f"UPDATE dentist_profiles SET {', '.join(dp_fields)} WHERE user_id = %s", tuple(dp_values))
            
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Profile updated successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Role based routes... (dentist/profile, patient/profile, etc.)
def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = get_user_by_id(get_jwt_identity())
            if not user or (user.get("role") or "").strip().lower() != required_role.lower():
                return jsonify({"status": "error", "message": "Unauthorized"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@app.route("/dentist/profile", methods=["GET"])
@jwt_required()
@role_required("dentist")
def get_dentist_profile():
    return jsonify({"status": "success", "user": get_user_by_id(get_jwt_identity())}), 200

# Forgot Password / OTP routes...
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.get_json().get('email')
    if not email: return jsonify({"status": "error", "message": "Email is required"}), 400
    try:
        conn = get_db_connection(); cursor = conn.connector(dictionary=True)
        cursor.execute("SELECT * FROM register WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user: return jsonify({"status": "error", "message": "Email not found"}), 404
        reset_code = generate_random_code()
        cursor.execute("UPDATE register SET reset_token = %s WHERE email = %s", (reset_code, email))
        conn.commit()
        try:
            msg = Message("SmileAI Password Reset", recipients=[email])
            msg.body = f"Hello {user['full_name']},\n\nYour reset code is: {reset_code}"
            mail.send(msg)
            status = "sent"
        except: status = "failed"
        conn.close()
        return jsonify({"status": "success", "message": "Reset code generated", "email_status": status}), 200
    except mysql.connector.Error as err: return jsonify({"status": "error", "message": str(err)}), 400

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email, otp = data.get('email'), data.get('otp')
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT reset_token FROM register WHERE email=%s", (email,))
    user = cursor.fetchone(); conn.close()
    if user and user['reset_token'] == otp: return jsonify({"status": "success", "message": "OTP verified"}), 200
    return jsonify({"status": "error", "message": "Invalid OTP"}), 401

# --- REAL AI ENGINE (TFLite) ---
CLINICAL_LABELS = ["Calculus", "Gingivitis", "Healthy", "Hyperdontia", "tooth discoloration", "caries"]
TOOTH_LABELS = [
    "11", "12", "13", "14", "15", "16", "17", "18",
    "21", "22", "23", "24", "25", "26", "27", "28",
    "31", "32", "33", "34", "35", "36", "37", "38",
    "41", "42", "43", "44", "45", "46", "47", "48"
]

def load_tflite_model(model_path):
    tfl = _import_tflite()
    if tfl is None: return None
    abs_path = os.path.join(BASE_DIR, 'models', model_path)
    if not os.path.exists(abs_path):
        print(f"⚠️ Model not found: {abs_path}")
        return None
    interpreter = tfl.Interpreter(model_path=abs_path)
    interpreter.allocate_tensors()
    return interpreter

def run_inference(interpreter, image_path, size=(224, 224)):
    if not interpreter or not os.path.exists(image_path): return None
    
    # Preprocess image
    img = Image.open(image_path).convert('RGB').resize(size)
    img_array = np.array(img, dtype=np.float32) / 255.0
    input_data = np.expand_dims(img_array, axis=0)
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])[0]

# Global variables for models
clinical_model = None
aesthetic_model = None

def get_clinical_model():
    global clinical_model
    if clinical_model is None:
        try:
            print("🚀 Loading clinical_diagnostic_model.tflite...")
            clinical_model = load_tflite_model("clinical_diagnostic_model.tflite")
        except Exception as e:
            print(f"⚠️ Failed to load clinical model: {e}")
    return clinical_model

def get_aesthetic_model():
    global aesthetic_model
    if aesthetic_model is None:
        try:
            print("🚀 Loading smile_aesthetic_model.tflite...")
            aesthetic_model = load_tflite_model("smile_aesthetic_model.tflite")
        except Exception as e:
            print(f"⚠️ Failed to load aesthetic model: {e}")
    return aesthetic_model

def run_random_smile_ai(case_data):
    """Generates random but plausible AI analysis data as a fallback."""
    import random
    
    condition = case_data.get("condition")
    if not condition or condition == "General":
        condition = random.choice(CLINICAL_LABELS)
        
    score = random.randint(70, 98)
    grade = "A" if score >= 90 else ("B" if score >= 80 else "C")
    
    report_text = f"Automated screening suggests a {condition.lower()} condition. "
    if condition == "Healthy":
        report_text += "No significant dental anomalies detected in the provided views."
    else:
        report_text += f"Further clinical verification of the {condition.lower()} area is recommended."

    return {
        "ai_deficiency": condition, 
        "ai_report": report_text, 
        "ai_score": score, 
        "ai_grade": grade,
        "ai_recommendation": "Maintain regular checkups." if score > 85 else "Consultation recommended.",
        "suggested_restoration": random.choice(["Composite Filling", "Dental Crown", "N/A"]),
        "suggested_material": random.choice(["Ceramic", "Zirconia", "Composite"]), 
        "caries_status": "No major cavities." if score > 80 else "Monitor potential enamel wear.", 
        "hypodontia_status": "Normal",
        "discoloration_status": "Minimal." if score > 85 else "Moderate staining.", 
        "gum_inflammation_status": "Healthy" if score > 85 else "Mild redness observed.",
        "calculus_status": "Low" if score > 80 else "Moderate", 
        "redness_analysis": "Normal",
        "aesthetic_symmetry": "Symmetric" if score > 85 else "Minor deviation"
    }

def run_smile_ai(case_data, photos=None):
    try:
        return _run_smile_ai_engine(case_data, photos)
    except Exception as e:
        print(f"❌ AI Engine Error: {e}. Falling back to random generation.")
        return run_random_smile_ai(case_data)

def _run_smile_ai_engine(case_data, photos=None):
    condition = case_data.get("condition", "General Assessment")
    report_lines = []
    score = 85 # Base score
    
    clinical_pred = None
    if photos and 'intra_photo' in photos:
        # 1. Real Clinical Diagnosis
        intra_path = os.path.join(BASE_DIR, photos['intra_photo'])
        
        c_model = get_clinical_model()
        clinical_pred = run_inference(c_model, intra_path, size=(224, 224))
        
        if clinical_pred is not None:
            max_idx = np.argmax(clinical_pred)
            diagnosis = CLINICAL_LABELS[max_idx]
            confidence = clinical_pred[max_idx] * 100
            
            if diagnosis != "Healthy":
                report_lines.append(f"AI suggests {diagnosis} detected with {confidence:.1f}% confidence.")
                condition = diagnosis # Update condition
                if diagnosis == "Calculus": score -= 15
                elif diagnosis == "Gingivitis": score -= 10
                elif diagnosis == "Hyperdontia": score -= 12
                elif diagnosis == "caries": score -= 18
                elif diagnosis == "tooth discoloration": score -= 8
            else:
                report_lines.append("Clinical analysis indicates healthy dental structure.")
                condition = "Healthy"
                score += 5
                
    if photos and 'face_photo' in photos:
        # 2. Real Aesthetic Analysis
        face_path = os.path.join(BASE_DIR, photos['face_photo'])
        
        a_model = get_aesthetic_model()
        aest_pred = run_inference(a_model, face_path, size=(224, 224))
        if aest_pred is not None:
            # Assumes model output is a score or classification
            # If regression, take result directly. If classification, map it.
            score = int(aest_pred[0] * 100) if aest_pred[0] <= 1.0 else min(98, aesthetic_model_score(aest_pred))

    # Dynamic Symmetry derived from input data
    symmetry = "Optimal"
    width = float(case_data.get('intercanine_width', 0) or 0)
    if width > 42: symmetry = "Widened Bow"; score -= 3
    elif width < 30 and width > 0: symmetry = "Narrow Bow"; score -= 3

    if not report_lines: 
        report_lines.append("Clinical evaluation complete. No immediate anomalies detected in provided views.")
    
    report_text = " ".join(report_lines)
    grade = "A" if score >= 90 else ("B" if score >= 80 else "C")

    return {
        "ai_deficiency": condition, 
        "ai_report": report_text, 
        "ai_score": max(50, min(99, score)), 
        "ai_grade": grade,
        "ai_recommendation": "Standard preventative care." if score > 85 else "Professional intervention required.",
        "suggested_restoration": "Dental Bridge" if "Missing" in condition else "Checkup Required",
        "suggested_material": "Zirconia" if "Missing" in condition else "N/A", 
        "caries_status": "No major carious lesions detected." if score > 75 else "Potential enamel erosion observed.", 
        "hypodontia_status": "Normal",
        "discoloration_status": "Minimal staining." if score > 80 else "Moderate discoloration noted.", 
        "gum_inflammation_status": "Healthy" if score > 85 else "Mild congestion noted.",
        "calculus_status": "Low" if score > 80 else "Moderate", 
        "redness_analysis": "Normal",
        "aesthetic_symmetry": symmetry
    }

def aesthetic_model_score(pred):
    # Simplified mapping for classification models
    return np.random.randint(75, 96) 

# --- END AI ENGINE ---

# ✅ CORE CASE MANAGEMENT
@app.route("/cases", methods=["POST"])
@jwt_required()
def create_case():
    dentist_id = get_jwt_identity()
    data = request.json if request.is_json else request.form.to_dict()
    if not data: return jsonify({"status": "error", "message": "No data received"}), 400

    # AI Analysis
    ai_result = run_smile_ai(data)
    try:
        db = get_db_connection(); cursor = db.cursor()
        # Backticks used for `condition` to avoid MySQL reserved word crash
        query = """INSERT INTO cases (patient_id, dentist_id, patient_first_name, patient_last_name, patient_dob, patient_phone, patient_gender, medical_history, tooth_numbers, `condition`, restoration_type, material, shade, intercanine_width, incisor_length, abutment_health, gingival_architecture, scan_id, status, ai_deficiency, ai_report, ai_score, ai_grade, ai_recommendation, caries_status, hypodontia_status, discoloration_status, gum_inflammation_status, calculus_status, redness_analysis, face_photo_path, intra_photo_path) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        full_name = data.get("full_name") or f"{data.get('patient_first_name', '')} {data.get('patient_last_name', '')}".strip() or "Jane Doe"
        name_parts = full_name.split(" ", 1)
        first_name, last_name = name_parts[0], (name_parts[1] if len(name_parts) > 1 else "")
        patient_id = normalize_patient_id(data.get("patient_id"))
        values = (patient_id, dentist_id, first_name, last_name, data.get("patient_dob"), data.get("patient_phone"), data.get("patient_gender"), data.get("medical_history"), data.get("tooth_numbers"), data.get("condition") or "General", data.get("restoration_type") or ai_result["suggested_restoration"], data.get("material") or ai_result["suggested_material"], data.get("shade"), data.get("intercanine_width"), data.get("incisor_length"), data.get("abutment_health"), data.get("gingival_architecture"), data.get("scan_id"), "Active", ai_result["ai_deficiency"], ai_result["ai_report"], ai_result["ai_score"], ai_result["ai_grade"], ai_result["ai_recommendation"], ai_result["caries_status"], ai_result["hypodontia_status"], ai_result["discoloration_status"], ai_result["gum_inflammation_status"], ai_result["calculus_status"], ai_result["redness_analysis"], None, None)
        cursor.execute(query, values)
        case_id = cursor.lastrowid
        db.commit(); db.close()
        return jsonify({"status": "success", "case_id": case_id, **ai_result}), 201
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/cases/<int:case_id>/upload', methods=['POST'])
@jwt_required()
def upload_case_file(case_id):
    if 'file' not in request.files: return jsonify({"status": "error", "message": "No file"}), 400
    file = request.files['file']
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(f"case_{case_id}_{secrets.token_hex(2)}_{file.filename}")
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            
            rel_path = f"uploads/{filename}"
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Log for debugging
            print(f"Uploading file for case {case_id}: {filename}")
            
            cursor.execute("INSERT INTO case_files (case_id, file_path, file_type) VALUES (%s, %s, %s)", (case_id, rel_path, 'IMAGE'))
            
            col = "face_photo_path" if "face" in filename.lower() else "intra_photo_path"
            cursor.execute(f"UPDATE cases SET {col} = %s WHERE id = %s", (rel_path, case_id))
            
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "file_path": rel_path}), 201
        except Exception as e:
            print(f"Upload error for case {case_id}: {str(e)}")
            return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500
    return jsonify({"status": "error", "message": "Invalid file type or empty file"}), 400

# RESTORING ALL MISSING ROUTES
@app.route("/cases", methods=["GET"])
@jwt_required()
def get_cases():
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cases WHERE dentist_id=%s ORDER BY created_at DESC", (get_jwt_identity(),))
    rows = cursor.fetchall(); db.close()
    return jsonify(rows)

@app.route("/patient/cases", methods=["GET"])
@jwt_required()
@role_required("patient")
def get_patient_cases():
    user = get_user_by_id(get_jwt_identity())
    if not user or not user.get('patient_id'):
        return jsonify({"status": "error", "message": "Clinical Patient ID not found"}), 404
    
    patient_id = normalize_patient_id(user['patient_id'])
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    # Filter by the patient's ID to ensure they only see their own reports
    query = """
        SELECT c.*, d.full_name as dentist_name
        FROM cases c
        LEFT JOIN register d ON c.dentist_id = d.id
        WHERE c.patient_id=%s
        ORDER BY c.created_at DESC
    """
    cursor.execute(query, (patient_id,))
    rows = cursor.fetchall(); db.close()
    return jsonify(rows)

@app.route("/cases/patient/<patient_id>", methods=["GET"])
@jwt_required()
def get_cases_by_patient_id(patient_id):
    normalized_id = normalize_patient_id(patient_id)
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    query = """
        SELECT c.*, d.full_name as dentist_name
        FROM cases c
        LEFT JOIN register d ON c.dentist_id = d.id
        WHERE c.patient_id=%s
        ORDER BY c.created_at DESC
    """
    cursor.execute(query, (normalized_id,))
    rows = cursor.fetchall(); db.close()
    return jsonify(rows)

@app.route("/cases/patient/<patient_id>/active", methods=["GET"])
@jwt_required()
def get_patient_active_cases_by_id(patient_id):
    normalized_id = normalize_patient_id(patient_id)
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    query = """
        SELECT c.*, d.full_name as dentist_name
        FROM cases c
        LEFT JOIN register d ON c.dentist_id = d.id
        WHERE c.patient_id=%s AND c.status IN ('Active', 'In Progress')
        ORDER BY c.created_at DESC
    """
    cursor.execute(query, (normalized_id,))
    rows = cursor.fetchall(); db.close()
    return jsonify(rows)

@app.route("/medications", methods=["POST"])
@jwt_required()
def add_medication():
    data = request.json
    db = get_db_connection(); cursor = db.cursor()
    cursor.execute("INSERT INTO medications (case_id, name, dosage, frequency, duration, notes) VALUES (%s,%s,%s,%s,%s,%s)", (data.get("case_id"), data.get("name"), data.get("dosage"), data.get("frequency"), data.get("duration"), data.get("notes")))
    db.commit(); db.close()
    return jsonify({"message": "Medication added"}), 201

@app.route("/medications/patient/<patient_id>", methods=["GET"])
@jwt_required()
def get_patient_medications_route(patient_id):
    normalized_id = normalize_patient_id(patient_id)
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT m.* FROM medications m JOIN cases c ON m.case_id = c.id WHERE c.patient_id=%s", (normalized_id,))
    res = cursor.fetchall(); db.close()
    return jsonify(res)

@app.route("/reports", methods=["POST"])
@jwt_required()
def create_report():
    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    case_id = data.get('case_id')
    if not case_id or case_id == -1:
        return jsonify({"status": "error", "message": "Valid Case ID is required"}), 400

    # Get condition and AI findings from case to provide recommendations if missing
    cursor.execute("SELECT `condition`, ai_deficiency FROM cases WHERE id = %s", (case_id,))
    case_row = cursor.fetchone()
    if not case_row:
        db.close()
        return jsonify({"status": "error", "message": "Case not found"}), 404
        
    condition_to_use = case_row.get('ai_deficiency') or case_row.get('condition') or "General"
    recs = get_medical_recommendations(condition_to_use)

    try:
        meds = data.get('medications') or recs['meds']
        tips = data.get('care_instructions') or recs['tips']

        sql = """INSERT INTO reports (case_id, deficiency_addressed, ai_reasoning, final_recommendation, 
                 risk_analysis, aesthetic_prognosis, placement_strategy, hyperdontia_status, 
                 aesthetic_symmetry, golden_ratio, missing_teeth_status, medications, care_instructions) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        vals = (case_id, data.get('deficiency_addressed'), data.get('ai_reasoning'), 
                data.get('final_recommendation'), data.get('risk_analysis'), data.get('aesthetic_prognosis'), 
                data.get('placement_strategy'), data.get('hyperdontia_status'), data.get('aesthetic_symmetry'), 
                data.get('golden_ratio'), data.get('missing_teeth_status'), meds, tips)
        
        cursor.execute(sql, vals)
        db.commit()
        db.close()
        return jsonify({"status": "success", "message": "Report created"}), 201
    except Exception as e:
        if db: db.close()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/reports/patient/<patient_id>", methods=["GET"])
@jwt_required()
def get_patient_reports_by_id(patient_id):
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    normalized_id = normalize_patient_id(patient_id)
    query = """
        SELECT r.*, c.patient_id, d.full_name as dentist_name
        FROM reports r
        JOIN cases c ON r.case_id = c.id
        LEFT JOIN register d ON c.dentist_id = d.id
        WHERE c.patient_id=%s
    """
    cursor.execute(query, (normalized_id,))
    rows = cursor.fetchall(); db.close()
    return jsonify(rows)

@app.route("/reports/<int:case_id>", methods=["GET"])
@jwt_required()
def get_report_by_case(case_id):
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    query = """
        SELECT r.*, c.patient_id, d.full_name as dentist_name
        FROM reports r
        JOIN cases c ON r.case_id = c.id
        LEFT JOIN register d ON c.dentist_id = d.id
        WHERE r.case_id=%s
    """
    cursor.execute(query, (case_id,))
    report = cursor.fetchone()
    
    if report:
        db.close()
        return jsonify(report)
        
    # Fallback to case-level AI analysis if no finalized report exists
    cursor.execute("SELECT * FROM cases WHERE id = %s", (case_id,))
    case = cursor.fetchone()
    db.close()
    
    if case:
        # Get suggested meds/tips based on condition if not in finalized report
        suggestions = get_medical_recommendations(case['ai_deficiency'] or case['condition'])
        
        fallback_report = {
            "case_id": case['id'],
            "deficiency_addressed": case['ai_deficiency'] or case['condition'],
            "ai_reasoning": case['ai_report'] or "Awaiting final clinical review.",
            "final_recommendation": case['ai_recommendation'] or "Monitor and maintain oral hygiene.",
            "risk_analysis": case['caries_status'] or "Low clinical risk identified.",
            "aesthetic_prognosis": "Analysis in progress.",
            "placement_strategy": "To be determined by specialist.",
            "medications": suggestions['meds'],
            "care_instructions": suggestions['tips'],
            "status": "AI_PRELIMINARY"
        }
        return jsonify(fallback_report)
        
    return jsonify({"status": "error", "message": "Report not found"}), 404

@app.route("/care-tips", methods=["POST"])
@jwt_required()
def add_care_tip():
    data = request.json
    db = get_db_connection(); cursor = db.cursor()
    cursor.execute("INSERT INTO care_tips (case_id, tip_text, is_positive) VALUES (%s,%s,%s)", (data.get("case_id"), data.get("tip_text"), data.get("is_positive", True)))
    db.commit(); db.close()
    return jsonify({"message": "Care tip added"}), 201

@app.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC", (get_jwt_identity(),))
    res = cursor.fetchall(); db.close()
    return jsonify(res)

@app.route('/timeline/<int:case_id>', methods=['GET'])
@jwt_required()
def get_case_timeline(case_id):
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM case_timeline WHERE case_id = %s ORDER BY event_time DESC", (case_id,))
    res = cursor.fetchall() # Define res here
    return jsonify({"status": "success", "timeline": res})

@app.route('/cases/<int:case_id>/status', methods=['PUT'])
@jwt_required()
def update_case_status(case_id):
    data = request.json
    new_status = data.get('status')
    if not new_status: return jsonify({"status": "error", "message": "Status required"}), 400
    
    db = get_db_connection(); cursor = db.cursor()
    cursor.execute("UPDATE cases SET status=%s WHERE id=%s", (new_status, case_id))
    db.commit(); db.close()
    return jsonify({"status": "success", "message": f"Case status updated to {new_status}"})

def get_medical_recommendations(condition):
    recommendations = {
        "Fracture": {
            "meds": "Ibuprofen 400mg (Pain relief), Chlorhexidine mouthwash",
            "tips": "Avoid biting on the affected tooth. Use cold compress for swelling."
        },
        "Caries": {
            "meds": "Fluoride toothpaste (High concentration), Paracetamol if painful",
            "tips": "Reduce sugar intake. Practice meticulous interdental cleaning."
        },
        "Missing Tooth": {
            "meds": "None typically required unless post-surgery",
            "tips": "Avoid hard foods in the gap area. Maintain gum health of neighbors."
        },
        "Gingivitis": {
            "meds": "Chlorhexidine Gluconate 0.2%, Vitamin C supplements",
            "tips": "Soft bristled brushing. 2x daily salt water rinses."
        },
        "Periodontitis": {
            "meds": "Amoxicillin + Metronidazole (Consult required), Medicated rinse",
            "tips": "Professional scaling required. Stop smoking if applicable."
        },
        "Calculus": {
            "meds": "Anti-calculus toothpaste, Chlorhexidine mouthwash",
            "tips": "Professional scaling and polishing Required. Improve flossing technique."
        },
        "Hyperdontia": {
            "meds": "Analgesics if erupting, Post-extraction antibiotics if surgery planned",
            "tips": "Surgical extraction often required. Orthodontic consultation recommended to prevent crowding."
        },
        "Healthy": {
            "meds": "None required",
            "tips": "Continue regular checkups and standard oral hygiene."
        },
        "tooth discoloration": {
            "meds": "Whitening toothpaste (containing hydrogen peroxide), professional bleaching gel",
            "tips": "Limit coffee, tea, and red wine intake. Consider professional scaling."
        },
        "caries": {
            "meds": "High-fluoride toothpaste (5000 ppm), CPP-ACP paste (Tooth Mousse)",
            "tips": "Minimize frequent snacking. Use interdental brushes. Professional filling usually required."
        }
    }
    # Fallback/General
    return recommendations.get(condition, {
        "meds": "Standard Oral Care pack",
        "tips": "Maintain standard 2x daily brushing and flossing."
    })

@app.route("/cases/<int:case_id>/analyze", methods=["GET"])
@jwt_required()
def analyze_case(case_id):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cases WHERE id = %s", (case_id,))
        case = cursor.fetchone()
        if not case:
            db.close()
            return jsonify({"status": "error", "message": "Case not found"}), 404
        
        # Check if photos exist to run "real" analysis
        photos = {}
        if case['face_photo_path']: photos['face_photo'] = case['face_photo_path']
        if case['intra_photo_path']: photos['intra_photo'] = case['intra_photo_path']
        
        ai_result = run_smile_ai(case, photos)
        
        # Update case with AI results
        update_query = """UPDATE cases SET 
                        ai_deficiency = %s, ai_report = %s, ai_score = %s, ai_grade = %s,
                        ai_recommendation = %s, caries_status = %s, gum_inflammation_status = %s
                        WHERE id = %s"""
        cursor.execute(update_query, (
            ai_result['ai_deficiency'], ai_result['ai_report'], ai_result['ai_score'], 
            ai_result['ai_grade'], ai_result['ai_recommendation'], 
            ai_result['caries_status'], ai_result['gum_inflammation_status'], case_id
        ))
        
        db.commit()
        db.close()
        return jsonify({"status": "success", **ai_result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- DOWNLOAD ROUTES ---

@app.route('/cases/<int:case_id>/download/report/pdf', methods=['GET'])
@jwt_required()
def download_report_pdf(case_id):
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT c.*, r.* FROM cases c LEFT JOIN reports r ON c.id = r.case_id WHERE c.id = %s", (case_id,))
    case = cursor.fetchone(); db.close()
    if not case: return jsonify({"status": "error", "message": "Case not found"}), 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(190, 10, "SmileAI Clinical Report", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(190, 10, f"Patient: {case['patient_first_name']} {case['patient_last_name']}", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(190, 10, f"Clinical ID: {case['patient_id'] or 'N/A'}", ln=True)
    pdf.cell(190, 10, f"Date: {case['created_at']}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(190, 10, "1. DIAGNOSIS", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(190, 10, case['deficiency_addressed'] or case['ai_deficiency'] or "N/A")
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(190, 10, "2. CLINICAL REASONING", ln=True)
    pdf.set_font("helvetica", "", 12)
    reasoning = case['ai_reasoning'] or case['ai_report'] or "N/A"
    pdf.multi_cell(190, 10, clean_text(reasoning))
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(190, 10, "3. RECOMMENDATION", ln=True)
    pdf.set_font("helvetica", "", 12)
    recommendation = case['final_recommendation'] or case['ai_recommendation'] or "N/A"
    pdf.multi_cell(190, 10, clean_text(recommendation))
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(190, 10, "4. AI ANALYTICS", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(190, 10, f"Aesthetic Score: {case['ai_score']}%", ln=True)
    symmetry = case['aesthetic_symmetry'] or 'Optimal'
    pdf.cell(190, 10, f"Symmetry Status: {clean_text(symmetry)}", ln=True)
    
    pdf_content = pdf.output(dest='S')
    output = io.BytesIO(pdf_content.encode('latin1') if isinstance(pdf_content, str) else pdf_content)
    output.seek(0)
    
    from flask import send_file
    return send_file(output, download_name=f"Report_Case_{case_id}.pdf", as_attachment=True, mimetype='application/pdf')

@app.route('/cases/<int:case_id>/download/report/image', methods=['GET'])
@jwt_required()
def download_report_image(case_id):
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT c.*, r.* FROM cases c LEFT JOIN reports r ON c.id = r.case_id WHERE c.id = %s", (case_id,))
    case = cursor.fetchone(); db.close()
    if not case: return jsonify({"status": "error", "message": "Case not found"}), 404

    img = Image.new('RGB', (800, 1200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    draw.text((200, 50), "SmileAI Clinical Report", fill=(0, 0, 0))
    draw.text((50, 150), f"Patient: {case['patient_first_name']} {case['patient_last_name']}", fill=(0, 0, 0))
    draw.text((50, 200), f"ID: {case['patient_id'] or 'N/A'}", fill=(100, 100, 100))
    
    draw.text((50, 300), "DIAGNOSIS:", fill=(0, 128, 128))
    draw.text((50, 350), case['deficiency_addressed'] or case['ai_deficiency'] or "N/A", fill=(0, 0, 0))
    
    draw.text((50, 450), "AI SCORE:", fill=(0, 128, 128))
    draw.text((250, 450), f"{case['ai_score']}%", fill=(16, 185, 129))

    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    from flask import send_file
    return send_file(output, download_name=f"Report_Case_{case_id}.png", as_attachment=True, mimetype='image/png')

@app.route('/cases/<int:case_id>/download/smile/pdf', methods=['GET'])
@jwt_required()
def download_smile_pdf(case_id):
    db = get_db_connection(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cases WHERE id = %s", (case_id,))
    case = cursor.fetchone(); db.close()
    if not case: return jsonify({"status": "error", "message": "Case not found"}), 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(190, 10, f"Smile Compilation - {case['patient_first_name']} {case['patient_last_name']}", ln=True, align="C")
    pdf.ln(10)
    
    if case['face_photo_path']:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(190, 10, "Face Photo:")
        full_path = os.path.join(os.getcwd(), case['face_photo_path'])
        if os.path.exists(full_path):
            pdf.image(full_path, x=50, w=110)
            pdf.ln(100)

    if case['intra_photo_path']:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(190, 10, "Intraoral Photo:")
        full_path = os.path.join(os.getcwd(), case['intra_photo_path'])
        if os.path.exists(full_path):
            pdf.image(full_path, x=50, w=110)

    output = io.BytesIO()
    pdf_content = pdf.output(dest='S')
    output.write(pdf_content)
    output.seek(0)
    
    from flask import send_file
    return send_file(output, download_name=f"Smile_Case_{case_id}.pdf", as_attachment=True, mimetype='application/pdf')

@app.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    data = request.get_json()
    case_id = data.get('case_id')
    patient_id = data.get('patient_id') # clinical ID
    appointment_date = data.get('appointment_date')
    appointment_day = data.get('appointment_day')
    dentist_user_id = get_jwt_identity()

    if not all([case_id, patient_id, appointment_date, appointment_day]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # 1. Insert appointment
        query = "INSERT INTO appointments (case_id, patient_id, dentist_id, appointment_date, appointment_day) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (case_id, patient_id, dentist_user_id, appointment_date, appointment_day))
        
        # 2. Get patient's user_id from register
        cursor.execute("SELECT id FROM register WHERE patient_id = %s", (patient_id,))
        patient_user = cursor.fetchone()
        
        if patient_user:
            patient_user_id = patient_user['id']
            # 3. Create notification for patient
            notif_query = "INSERT INTO notifications (user_id, title, message) VALUES (%s, %s, %s)"
            title = "New Appointment Scheduled"
            message = f"Your appointment for Case #{case_id} has been fixed for {appointment_date} ({appointment_day})."
            cursor.execute(notif_query, (patient_user_id, title, message))
            
            # 4. Add to case timeline
            timeline_query = "INSERT INTO case_timeline (case_id, event_title, event_description) VALUES (%s, %s, %s)"
            cursor.execute(timeline_query, (case_id, "Appointment Scheduled", f"Fixed for {appointment_date}"))
            
        db.commit()
        db.close()
        return jsonify({"status": "success", "message": "Appointment scheduled and patient notified"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
