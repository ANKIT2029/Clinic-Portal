// API Base URL
const API_BASE = '';

// Utility Functions
function showMessage(elementId, message, type = 'success') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Patient Registration
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        name: document.getElementById('patientName').value,
        age: parseInt(document.getElementById('patientAge').value) || null,
        gender: document.getElementById('patientGender').value,
        phone: document.getElementById('patientPhone').value || null,
        email: document.getElementById('patientEmail').value || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/register_patient`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('registerResult', `✓ Patient registered successfully! ID: ${result.patient_id}`, 'success');
            document.getElementById('registerForm').reset();
            loadPatients(); // Refresh patient list
        } else {
            showMessage('registerResult', `✗ Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showMessage('registerResult', `✗ Network error: ${error.message}`, 'error');
    }
});

// Appointment Scheduling
document.getElementById('appointmentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        patient_id: parseInt(document.getElementById('apptPatientId').value),
        doctor: document.getElementById('apptDoctor').value || null,
        datetime: document.getElementById('apptDatetime').value,
        notes: document.getElementById('apptNotes').value || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/schedule_appointment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('apptResult', `✓ Appointment scheduled successfully! ID: ${result.appointment_id}`, 'success');
            document.getElementById('appointmentForm').reset();
            loadAppointments(); // Refresh appointments list
        } else {
            showMessage('apptResult', `✗ Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showMessage('apptResult', `✗ Network error: ${error.message}`, 'error');
    }
});

// Load Patients List
async function loadPatients() {
    const container = document.getElementById('patientsList');
    container.innerHTML = '<div class="loading">Loading patients...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/patients`);
        const patients = await response.json();
        
        if (patients.length === 0) {
            container.innerHTML = '<div class="empty-state">No patients registered yet</div>';
            return;
        }
        
        container.innerHTML = patients.map(patient => `
            <div class="data-item">
                <div class="data-item-header">
                    <span class="data-item-title">${patient.name}</span>
                    <span class="data-item-id">ID: ${patient.id}</span>
                </div>
                <div class="data-item-details">
                    <div><strong>Age:</strong> ${patient.age || 'N/A'} | <strong>Gender:</strong> ${patient.gender}</div>
                    <div><strong>Phone:</strong> ${patient.phone || 'N/A'}</div>
                    <div><strong>Email:</strong> ${patient.email || 'N/A'}</div>
                </div>
                <div class="data-item-meta">
                    Registered: ${formatDate(patient.created_at)}
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = `<div class="error">Error loading patients: ${error.message}</div>`;
    }
}

// Load Appointments List
async function loadAppointments() {
    const container = document.getElementById('appointmentsList');
    container.innerHTML = '<div class="loading">Loading appointments...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/appointments`);
        const appointments = await response.json();
        
        if (appointments.length === 0) {
            container.innerHTML = '<div class="empty-state">No appointments scheduled yet</div>';
            return;
        }
        
        container.innerHTML = appointments.map(appt => `
            <div class="data-item">
                <div class="data-item-header">
                    <span class="data-item-title">${appt.patient_name || 'Unknown Patient'}</span>
                    <span class="data-item-id">ID: ${appt.id}</span>
                </div>
                <div class="data-item-details">
                    <div><strong>Doctor:</strong> ${appt.doctor || 'Not assigned'}</div>
                    <div><strong>Date & Time:</strong> ${formatDate(appt.datetime)}</div>
                    <div><strong>Patient ID:</strong> ${appt.patient_id} | <strong>Phone:</strong> ${appt.patient_phone || 'N/A'}</div>
                    ${appt.notes ? `<div><strong>Notes:</strong> ${appt.notes}</div>` : ''}
                    <div><strong>Status:</strong> <span style="text-transform: capitalize;">${appt.status}</span></div>
                </div>
                <div class="data-item-meta">
                    Scheduled: ${formatDate(appt.created_at)}
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = `<div class="error">Error loading appointments: ${error.message}</div>`;
    }
}

// Chat Functionality
async function sendChatMessage() {
    const patientId = document.getElementById('chatPatientId').value;
    const message = document.getElementById('chatMessage').value;
    
    if (!message.trim()) {
        showMessage('chatResult', '✗ Please enter a message', 'error');
        return;
    }
    
    const data = {
        patient_id: patientId ? parseInt(patientId) : null,
        sender: 'patient',
        message: message
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('chatResult', `✓ Message sent! Reply: "${result.reply}"`, 'success');
            document.getElementById('chatMessage').value = '';
        } else {
            showMessage('chatResult', `✗ Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showMessage('chatResult', `✗ Network error: ${error.message}`, 'error');
    }
}

// Set default datetime to now
function setDefaultDateTime() {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('apptDatetime').value = now.toISOString().slice(0, 16);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPatients();
    loadAppointments();
    setDefaultDateTime();
});

// Auto-refresh every 30 seconds
setInterval(() => {
    loadPatients();
    loadAppointments();
}, 30000);