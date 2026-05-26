const API_URL = 'http://127.0.0.1:8000/api';

// Токены

function getAccessToken()  { return localStorage.getItem('access_token'); }
function getRefreshToken() { return localStorage.getItem('refresh_token'); }

function saveTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

// Базовый fetch с авто-обновлением токена

async function apiFetch(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };

    const token = getAccessToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    let res = await fetch(API_URL + path, { ...options, headers });

    // Токен истёк — пробуем обновить
    if (res.status === 401 && getRefreshToken()) {
        const refreshed = await tryRefresh();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${getAccessToken()}`;
            res = await fetch(API_URL + path, { ...options, headers });
        } else {
            clearTokens();
            window.location.href = 'index.html';
            return;
        }
    }

    return res;
}

async function tryRefresh() {
    try {
        const res = await fetch(API_URL + '/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: getRefreshToken() }),
        });
        if (!res.ok) return false;
        const data = await res.json();
        saveTokens(data.access_token, data.refresh_token);
        return true;
    } catch {
        return false;
    }
}

// Методы аутентификации

async function register(login, email, password) {
    const res = await fetch(API_URL + '/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login, email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Ошибка регистрации');
    return data;
}

async function login(loginOrEmail, password) {
    const res = await fetch(API_URL + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login_or_email: loginOrEmail, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Ошибка входа');
    saveTokens(data.access_token, data.refresh_token);
    return data;
}

async function getMe() {
    const res = await apiFetch('/auth/me');
    if (!res.ok) return null;
    return res.json();
}

function logout() {
    clearTokens();
    window.location.href = 'index.html';
}

// Редирект на главную если не авторизован
async function requireAuth() {
    const user = await getMe();
    if (!user) {
        clearTokens();
        window.location.href = 'index.html';
    }
    return user;
}
