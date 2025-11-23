import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "clinic_portal")
DB_USER = os.getenv("DB_USER", "clinic_app")
DB_PASS = os.getenv("DB_PASS", "change_this_password")
PORT = int(os.getenv("PORT", 5000))
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

frontend_folder = os.path.join(os.path.dirname(__file__), "frontend")
app = Flask(__name__, static_folder=frontend_folder, static_url_path="")
CORS(app)

def get_conn():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=True
    )

def query_all(q, params=None):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(q, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def query_one(q, params=None):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(q, params or ())
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def execute(q, params=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(q, params or ())
    last_id = cur.lastrowid
    cur.close()
    conn.close()
    return last_id

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(frontend_folder, "index.html")

@app.route("/api/register_patient", methods=["POST"])
def register_patient():
    data = request.get_json(force=True)
    name = data.get("name")
    if not name:
        return jsonify({"error": "name required"}), 400
    age = data.get("age")
    gender = data.get("gender") or "Other"
    phone = data.get("phone") or data.get("contact")
    email = data.get("email")
    external_id = data.get("external_id")
    q = """
    INSERT INTO patients (external_id, name, age, gender, phone, email)
    VALUES (%s,%s,%s,%s,%s,%s)
    """
    pid = execute(q, (external_id, name, age, gender, phone, email))
    return jsonify({"success": True, "patient_id": pid}), 201

@app.route("/api/patients", methods=["GET"])
def list_patients():
    q = "SELECT * FROM patients ORDER BY created_at DESC LIMIT 500"
    rows = query_all(q)
    return jsonify(rows)

@app.route("/api/schedule_appointment", methods=["POST"])
def schedule_appointment():
    data = request.get_json(force=True)
    patient_id = data.get("patient_id") or data.get("patientId")
    doctor = data.get("doctor")
    datetime_str = data.get("datetime")
    notes = data.get("notes")
    if not patient_id or not datetime_str:
        return jsonify({"error": "patient_id and datetime required"}), 400
    try:
        if isinstance(datetime_str, str):
            if "T" in datetime_str:
                dt = datetime.fromisoformat(datetime_str)
            else:
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime_str
    except Exception:
        dt = datetime_str
    q = """
    INSERT INTO appointments (patient_id, doctor, datetime, notes)
    VALUES (%s,%s,%s,%s)
    """
    appt_id = execute(q, (patient_id, doctor, dt, notes))
    return jsonify({"success": True, "appointment_id": appt_id}), 201

@app.route("/api/appointments", methods=["GET"])
def list_appointments():
    q = """SELECT a.*, p.name AS patient_name, p.phone AS patient_phone
           FROM appointments a LEFT JOIN patients p ON p.id = a.patient_id
           ORDER BY a.datetime DESC LIMIT 500"""
    rows = query_all(q)
    return jsonify(rows)

@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json(force=True)
    patient_id = body.get("patient_id")
    sender = body.get("sender") or "patient"
    message = body.get("message")
    if not message:
        return jsonify({"error": "message required"}), 400
    q_ins = "INSERT INTO chat_messages (patient_id, sender, message, metadata) VALUES (%s,%s,%s,%s)"
    execute(q_ins, (patient_id, sender, message, json.dumps({"source": "web"})))
    
    assistant_reply = None
    
    # FIXED: Updated to use new OpenAI API (v1.0+)
   if OPENAI_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}],
            max_tokens=400
        )
        assistant_reply = resp.choices[0].message.content.strip()
    except Exception as e:
        app.logger.warning("OpenAI call failed: %s", e)
        assistant_reply = None

    # Fallback to simple rule-based responses
    if not assistant_reply:
        m = message.lower()
        if "hello" in m or "hi" in m:
            assistant_reply = "Hello — how can I help you today?"
        elif "pain" in m or "hurt" in m:
            assistant_reply = "I'm sorry to hear that. Can you describe where it hurts and when it started?"
        elif "appointment" in m or "book" in m:
            assistant_reply = "I can help with appointments. Which date and time would you prefer?"
        else:
            assistant_reply = "Thanks for the message. A clinician will review and get back to you shortly."
    
    execute(q_ins, (patient_id, "system", assistant_reply, json.dumps({"source": "assistant"})))
    return jsonify({"reply": assistant_reply, "stored": True})

@app.route("/api/chats/<int:patient_id>", methods=["GET"])
def get_chats(patient_id):
    q = "SELECT * FROM chat_messages WHERE patient_id = %s ORDER BY created_at ASC"
    rows = query_all(q, (patient_id,))
    return jsonify(rows)

@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_conn()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=os.getenv("FLASK_DEBUG", "0") == "1")