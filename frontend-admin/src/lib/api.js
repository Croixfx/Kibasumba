import axios from 'axios';

// Single base URL constant — comes from .env (VITE_API_URL); change there
// for production.
export const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

export const TOKEN_KEY = 'kibasumba_token';

export const api = axios.create({ baseURL: API_URL });

// Attach the stored token to every request automatically.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function hasToken() {
  return Boolean(localStorage.getItem(TOKEN_KEY));
}

// The backend reports errors as {"error": "..."} or as DRF field errors
// like {"age": ["msg"]}.
export function errorMessage(err, fallback = 'Habayeho ikibazo. Ongera ugerageze.') {
  const data = err?.response?.data;
  if (!data) return fallback;
  if (typeof data.error === 'string') return data.error;
  if (typeof data.detail === 'string') return data.detail;
  const messages = Object.values(data)
    .flatMap((v) => (Array.isArray(v) ? v : typeof v === 'string' ? [v] : []));
  return messages.length ? messages.join('\n') : fallback;
}
