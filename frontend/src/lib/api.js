const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => {
  const token = localStorage.getItem('session_token') || localStorage.getItem('auth_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  // Auth
  register: (data) => fetch(`${API}/auth/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  login: (data) => fetch(`${API}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  googleSession: (sessionId) => fetch(`${API}/auth/google-session`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: sessionId }) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getMe: () => fetch(`${API}/auth/me`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  logout: () => fetch(`${API}/auth/logout`, { method: 'POST', headers: { ...getAuthHeaders() } }),

  // Chatbots
  createChatbot: (data) => fetch(`${API}/chatbots`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getChatbots: () => fetch(`${API}/chatbots`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getChatbot: (id) => fetch(`${API}/chatbots/${id}`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  updateChatbot: (id, data) => fetch(`${API}/chatbots/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  deleteChatbot: (id) => fetch(`${API}/chatbots/${id}`, { method: 'DELETE', headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Chat
  sendChat: (data) => fetch(`${API}/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getPublicChatbot: (id) => fetch(`${API}/chatbot-public/${id}`).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Dashboard
  getStats: () => fetch(`${API}/dashboard/stats`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getAnalytics: () => fetch(`${API}/analytics`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getBilling: () => fetch(`${API}/billing`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Stripe
  createCheckout: (data) => fetch(`${API}/stripe/checkout`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  checkPaymentStatus: (sessionId) => fetch(`${API}/stripe/status/${sessionId}`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Consent
  logConsent: (data) => fetch(`${API}/consent`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }),

  // User data
  exportData: () => fetch(`${API}/user/export`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  deleteAccount: (confirmation) => fetch(`${API}/user/account`, { method: 'DELETE', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify({ confirmation }) }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Auth - Email Verification & Password Reset
  verifyEmail: (token) => fetch(`${API}/auth/verify-email`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token }) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  resendVerification: (email) => fetch(`${API}/auth/resend-verification`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  forgotPassword: (email) => fetch(`${API}/auth/forgot-password`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  resetPassword: (token, new_password) => fetch(`${API}/auth/reset-password`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token, new_password }) }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Templates
  getTemplates: () => fetch(`${API}/templates`).then(r => { if (!r.ok) throw r; return r.json(); }),
  createFromTemplate: (data) => fetch(`${API}/chatbots/from-template`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Team
  getTeam: () => fetch(`${API}/team`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  inviteTeamMember: (data) => fetch(`${API}/team/invite`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  removeTeamMember: (id) => fetch(`${API}/team/${id}`, { method: 'DELETE', headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // AI Config
  getAIConfig: () => fetch(`${API}/ai/config`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  updateAIConfig: (data) => fetch(`${API}/ai/config`, { method: 'PUT', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Conversations
  getConversations: (params) => fetch(`${API}/conversations?${params}`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getConversation: (sessionId) => fetch(`${API}/conversations/${sessionId}`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  exportConversations: (params) => fetch(`${API}/conversations/export?${params}`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.text(); }),

  // Domain Verification
  getDomainStatus: () => fetch(`${API}/domain/status`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  initDomainVerification: (data) => fetch(`${API}/domain/init`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  verifyDomain: (method) => fetch(`${API}/domain/verify`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify({ method }) }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Billing Management
  getPlans: () => fetch(`${API}/billing/plans`).then(r => { if (!r.ok) throw r; return r.json(); }),
  changePlan: (data) => fetch(`${API}/billing/change-plan`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Invoice PDF
  downloadInvoicePdf: (transactionId) => fetch(`${API}/billing/invoice/${transactionId}/pdf`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.blob(); }),

  // Analytics CSV Export
  exportAnalyticsCsv: () => fetch(`${API}/analytics/export/csv`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.text(); }),

  // Marketing Assistent
  getMarketingSkills: () => fetch(`${API}/marketing/skills`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getMarketingUsage: () => fetch(`${API}/marketing/usage`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  startMarketingTrial: () => fetch(`${API}/marketing/start-trial`, { method: 'POST', headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  runMarketingSkill: (data) => fetch(`${API}/marketing/run`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  saveMarketingResult: (data) => fetch(`${API}/marketing/save`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getMarketingHistory: () => fetch(`${API}/marketing/history`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  getMarketingProfile: () => fetch(`${API}/marketing/profile`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  saveMarketingProfile: (data) => fetch(`${API}/marketing/profile`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),

  // Website Scan
  getWebsiteScan: () => fetch(`${API}/marketing/website-scan`, { headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  startWebsiteScan: (data) => fetch(`${API}/marketing/website-scan/start`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw r; return r.json(); }),
  rescanWebsite: () => fetch(`${API}/marketing/rescan`, { method: 'POST', headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
  dismissScanBanner: () => fetch(`${API}/marketing/dismiss-banner`, { method: 'POST', headers: { ...getAuthHeaders() } }).then(r => { if (!r.ok) throw r; return r.json(); }),
};

export default api;
