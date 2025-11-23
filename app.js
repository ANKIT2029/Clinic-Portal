// app.js - Clinic Portal frontend
// When deploying to Netlify, set the backend URL in Netlify UI as BACKEND_URL
// If BACKEND_URL is not set, client will assume no backend (static-only).

const BACKEND_URL = (function() {
  // Netlify exposes env vars at build time. Replace this during build or set it in Netlify UI.
  // If you built with a bundler, you could inject at build time; for plain static, edit this string.
  return window.__BACKEND_URL__ || ""; // set this by editing index.html at deploy, or replace with actual URL
})();

const API_BASE = BACKEND_URL ? `${BACKEND_URL.replace(/\/$/, '')}/api` : '/api';

function showMessage(elementId, message, type='success') {
    const element = document.getElementById(elementId);
    if(!element) return;
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
    setTimeout(()=>{ element.style.display='none'; }, 5000);
}

async function loadPatients() {
    if (!API_BASE || API_BASE === '/api') return; // no backend configured
    try {
        const res = await fetch(`${API_BASE}/patients`);
        const data = await res.json();
        const list = document.getElementById('patientsList');
        if (list) {
            list.innerHTML = data.map(p => `<li>${p.id || p.patient_id || ''} — ${p.name || 'No name'}</li>`).join('');
        }
    } catch (err) {
        console.error('loadPatients error', err);
    }
}

async function loadAppointments() {
    if (!API_BASE || API_BASE === '/api') return;
    try {
        const res = await fetch(`${API_BASE}/appointments`);
        const data = await res.json();
        const list = document.getElementById('appointmentsList');
        if (list) {
            list.innerHTML = data.map(a => `<li>${a.appointment_datetime} — ${a.doctor || ''}</li>`).join('');
        }
    } catch (err) {
        console.error('loadAppointments error', err);
    }
}

async function registerPatient() {
    if (!API_BASE || API_BASE === '/api') {
        showMessage('messageBox', 'No backend configured. Patient saved locally (demo).', 'error');
        return;
    }
    const name = document.getElementById('patientName').value;
    const email = document.getElementById('patientEmail').value;
    const phone = document.getElementById('patientPhone').value;
    const res = await fetch(`${API_BASE}/register_patient`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, email, phone})
    });
    const data = await res.json();
    if (res.ok) {
        showMessage('messageBox', 'Patient registered successfully');
        loadPatients();
    } else {
        showMessage('messageBox', data.error || 'Error registering patient', 'error');
    }
}

function setDefaultDateTime() {
    const el = document.getElementById('apptDatetime');
    if (!el) return;
    const now = new Date();
    const iso = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0,16);
    el.value = iso;
}

document.addEventListener('DOMContentLoaded', () => {
    loadPatients();
    loadAppointments();
    setDefaultDateTime();
});
