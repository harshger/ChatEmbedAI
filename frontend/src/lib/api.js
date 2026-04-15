const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => {
  const token = localStorage.getItem('session_token') || localStorage.getItem('auth_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  // Auth
  register: (data) => fetch(`${API}/auth/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data), credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  login: (data) => fetch(`${API}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data), credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  googleSession: (sessionId) => fetch(`${API}/auth/google-session`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: sessionId }), credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getMe: () => fetch(`${API}/auth/me`, { headers: { ...getAuthHeaders() }, credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  logout: () => fetch(`${API}/auth/logout`, { method: 'POST', headers: { ...getAuthHeaders() }, credentials: 'include' }),

  // Chatbots
  createChatbot: (data) => fetch(`${API}/chatbots`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data), credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getChatbots: () => fetch(`${API}/chatbots`, { headers: { ...getAuthHeaders() }, credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getChatbot: (id) => fetch(`${API}/chatbots/${id}`, { headers: { ...getAuthHeaders() }, credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  updateChatbot: (id, data) => fetch(`${API}/chatbots/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data), credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  deleteChatbot: (id) => fetch(`${API}/chatbots/${id}`, { method: 'DELETE', headers: { ...getAuthHeaders() }, credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Chat
  sendChat: (data) => fetch(`${API}/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getPublicChatbot: (id) => fetch(`${API}/chatbot-public/${id}`).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Dashboard
  getStats: () => fetch(`${API}/dashboard/stats`, { headers: { ...getAuthHeaders() }, credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getAnalytics: () => fetch(`${API}/analytics`, { headers: { ...getAuthHeaders() }, credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getBilling: () => fetch(`${API}/billing`, { headers: { ...getAuthHeaders() }, credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Stripe
  createCheckout: (data) => fetch(`${API}/stripe/checkout`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data), credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  checkPaymentStatus: (sessionId) => fetch(`${API}/stripe/status/${sessionId}`, { headers: { ...getAuthHeaders() }, credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Consent
  logConsent: (data) => fetch(`${API}/consent`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }),

  // User data
  exportData: () => fetch(`${API}/user/export`, { headers: { ...getAuthHeaders() }, credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
  deleteAccount: (confirmation) => fetch(`${API}/user/account`, { method: 'DELETE', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify({ confirmation }), credentials: 'include' }).then(r => { if (!r.ok) throw r; return r.json(); }),
};

export default api;
