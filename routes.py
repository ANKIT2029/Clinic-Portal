import json
from datetime import datetime
from flask import request, jsonify, send_from_directory
from database import query_all, query_one, execute_query
from config import Config

def register_routes(app):
    """Register all application routes."""
    
    @app.route("/", methods=["GET"])
    def index():
        """Serve the frontend application."""
        return send_from_directory(Config.FRONTEND_FOLDER, "index.html")

    @app.route("/api/register_patient", methods=["POST"])
    def register_patient():
        """Register a new patient."""
        data = request.get_json(force=True)
        name = data.get("name")
        
        if not name:
            return jsonify({"error": "name required"}), 400
        
        age = data.get("age")
        gender = data.get("gender") or "Other"
        phone = data.get("phone") or data.get("contact")
        email = data.get("email")
        external_id = data.get("external_id")
        
        query = """
        INSERT INTO patients (external_id, name, age, gender, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        patient_id = execute_query(query, (external_id, name, age, gender, phone, email))
        
        return jsonify({"success": True, "patient_id": patient_id}), 201

    @app.route("/api/patients", methods=["GET"])
    def list_patients():
        """Get list of all patients."""
        query = "SELECT * FROM patients ORDER BY created_at DESC LIMIT 500"
        rows = query_all(query)
        return jsonify(rows)

    @app.route("/api/schedule_appointment", methods=["POST"])
    def schedule_appointment():
        """Schedule a new appointment."""
        data = request.get_json(force=True)
        patient_id = data.get("patient_id") or data.get("patientId")
        doctor = data.get("doctor")
        datetime_str = data.get("datetime")
        notes = data.get("notes")
        
        if not patient_id or not datetime_str:
            return jsonify({"error": "patient_id and datetime required"}), 400
        
        # Parse datetime
        try:
            if isinstance(datetime_str, str):
                if "T" in datetime_str:
                    dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            else:
                dt = datetime_str
        except Exception:
            dt = datetime_str
        
        query = """
        INSERT INTO appointments (patient_id, doctor, datetime, notes)
        VALUES (%s, %s, %s, %s)
        """
        appointment_id = execute_query(query, (patient_id, doctor, dt, notes))
        
        return jsonify({"success": True, "appointment_id": appointment_id}), 201

    @app.route("/api/appointments", methods=["GET"])
    def list_appointments():
        """Get list of all appointments."""
        query = """
        SELECT a.*, p.name AS patient_name, p.phone AS patient_phone
        FROM appointments a 
        LEFT JOIN patients p ON p.id = a.patient_id
        ORDER BY a.datetime DESC 
        LIMIT 500
        """
        rows = query_all(query)
        return jsonify(rows)

    @app.route("/api/chat", methods=["POST"])
    def chat():
        """Handle chat messages."""
        from services import get_ai_response
        
        body = request.get_json(force=True)
        patient_id = body.get("patient_id")
        sender = body.get("sender") or "patient"
        message = body.get("message")
        
        if not message:
            return jsonify({"error": "message required"}), 400
        
        # Store patient message
        query = """
        INSERT INTO chat_messages (patient_id, sender, message, metadata) 
        VALUES (%s, %s, %s, %s)
        """
        execute_query(query, (patient_id, sender, message, json.dumps({"source": "web"})))
        
        # Get AI response
        assistant_reply = get_ai_response(message, app.logger)
        
        # Store assistant response
        execute_query(query, (patient_id, "system", assistant_reply, json.dumps({"source": "assistant"})))
        
        return jsonify({"reply": assistant_reply, "stored": True})

    @app.route("/api/chats/<int:patient_id>", methods=["GET"])
    def get_chats(patient_id):
        """Get chat history for a patient."""
        query = "SELECT * FROM chat_messages WHERE patient_id = %s ORDER BY created_at ASC"
        rows = query_all(query, (patient_id,))
        return jsonify(rows)

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        try:
            from database import get_connection
            conn = get_connection()
            conn.close()
            return jsonify({"status": "ok"})
        except Exception as e:
            return jsonify({"status": "error", "detail": str(e)}), 500