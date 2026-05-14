const API_BASE = "http://127.0.0.1:8000";

function getToken() {
    return localStorage.getItem("token");
}

function getUserRole() {
    return localStorage.getItem("userRole");
}

function getUserName() {
    return localStorage.getItem("userName") || "Kullanıcı";
}

function authHeaders() {
    const token = getToken();
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

async function apiFetch(path, options = {}) {
    const token = getToken();

    const headers = {
        ...(options.headers || {})
    };

    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers
    });

    const contentType = res.headers.get("content-type") || "";
    let data = null;

    if (contentType.includes("application/json")) {
        data = await res.json();
    } else {
        data = await res.text();
    }

    if (!res.ok) {
        const msg = data?.detail || data?.error || data || "İstek başarısız oldu.";
        throw new Error(msg);
    }

    return data;
}

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}

function requireAuth(expectedRole = null) {
    const token = getToken();
    const role = getUserRole();

    if (!token) {
        alert("Lütfen giriş yapın.");
        window.location.href = "login.html";
        return false;
    }

    if (expectedRole && role !== expectedRole) {
        alert("Bu sayfaya erişim yetkiniz yok.");
        window.location.href = "login.html";
        return false;
    }

    return true;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
