const API_BASE = 'http://127.0.0.1:8000';

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-User-Token': getToken() || ''
  };
}

async function apiFetch(path, options = {}) {
  const opts = {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...(options.body ? {'Content-Type': 'application/json'} : {}),
      'X-User-Token': getToken() || ''
    }
  };
  const res = await fetch(`${API_BASE}${path}`, opts);
  let data = null;
  try { data = await res.json(); } catch (_) { data = {}; }
  if (!res.ok) {
    throw new Error(data.detail || data.error || `HTTP ${res.status}`);
  }
  return data;
}

function requireRole(role) {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('userRole');
  if (!token || userRole !== role) {
    alert('Bu sayfaya erişim yetkiniz yok.');
    window.location.href = 'login.html';
  }
}

function logout() {
  localStorage.clear();
  window.location.href = 'login.html';
}
