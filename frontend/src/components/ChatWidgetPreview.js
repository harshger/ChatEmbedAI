import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from '../lib/i18n';
import { api } from '../lib/api';
import { MessageSquare, X, Send, Shield } from 'lucide-react';

export default function ChatWidgetPreview({ businessName, color = '#6366f1', showGdpr = true, chatbotId, interactive = false }) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [consented, setConsented] = useState(!showGdpr);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const messagesEnd = useRef(null);
  const sessionId = useRef(`preview_${Date.now()}`);

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !interactive || !chatbotId) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setTyping(true);

    try {
      const data = await api.sendChat({
        chatbot_id: chatbotId,
        message: userMsg,
        session_id: sessionId.current,
        history: messages.map(m => ({ role: m.role, content: m.content })),
        widget_consent: true,
      });
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Entschuldigung, ein Fehler ist aufgetreten.' }]);
    }
    setTyping(false);
  };

  return (
    <div className="relative" data-testid="chat-widget-preview">
      {/* Toggle button */}
      {!open && (
        <button onClick={() => setOpen(true)} className="w-14 h-14 flex items-center justify-center text-white shadow-lg transition-transform hover:scale-105" style={{ backgroundColor: color, borderRadius: '50%' }} data-testid="widget-toggle">
          <MessageSquare size={24} />
        </button>
      )}

      {/* Chat window */}
      {open && (
        <div className="w-[360px] h-[520px] bg-white border border-gray-200 shadow-[0_8px_32px_rgba(0,0,0,0.12)] flex flex-col overflow-hidden" data-testid="widget-window">
          {/* Header */}
          <div className="px-4 py-3 flex items-center justify-between text-white" style={{ backgroundColor: color }}>
            <div>
              <p className="font-bold text-sm">{businessName || 'Your Business'}</p>
              <p className="text-xs opacity-75">KI-Chat</p>
            </div>
            <button onClick={() => setOpen(false)} className="hover:opacity-75" data-testid="widget-close"><X size={18} /></button>
          </div>

          {/* GDPR notice */}
          {showGdpr && !consented && (
            <div className="p-4 bg-[#F9FAFB] border-b border-gray-200 flex-1 flex flex-col justify-center" data-testid="widget-gdpr">
              <Shield size={24} className="text-[#002FA7] mb-3" />
              <p className="text-xs text-[#0A0A0A] leading-relaxed mb-4">{t.widget.gdpr_notice} <a href="/datenschutz" className="text-[#002FA7] underline">{t.widget.privacy_link}</a></p>
              <button onClick={() => setConsented(true)} className="text-white text-xs font-bold px-4 py-2" style={{ backgroundColor: color }} data-testid="widget-consent-btn">{t.widget.consent_btn}</button>
            </div>
          )}

          {/* Messages */}
          {(consented || !showGdpr) && (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.length === 0 && (
                  <div className="text-center text-xs text-[#4B5563] py-8">
                    <MessageSquare size={24} className="mx-auto mb-2 opacity-30" />
                    <p>Send a message to start the conversation.</p>
                  </div>
                )}
                {messages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] px-3 py-2 text-sm ${msg.role === 'user' ? 'text-white' : 'bg-[#F3F4F6] text-[#0A0A0A]'}`} style={msg.role === 'user' ? { backgroundColor: color } : {}}>
                      {msg.content}
                    </div>
                  </div>
                ))}
                {typing && (
                  <div className="flex justify-start"><div className="bg-[#F3F4F6] px-4 py-2 text-sm"><span className="animate-pulse">...</span></div></div>
                )}
                <div ref={messagesEnd} />
              </div>

              {/* Input */}
              <div className="p-3 border-t border-gray-200">
                <div className="flex gap-2">
                  <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSend()} placeholder={t.widget.placeholder} className="flex-1 text-sm border border-gray-200 px-3 py-2 outline-none focus:border-[#002FA7]" disabled={!interactive} data-testid="widget-input" />
                  <button onClick={handleSend} className="px-3 py-2 text-white" style={{ backgroundColor: color }} disabled={!interactive} data-testid="widget-send"><Send size={16} /></button>
                </div>
              </div>

              {/* Footer */}
              <div className="px-3 py-2 border-t border-gray-100 flex items-center justify-between text-xs text-[#4B5563]">
                <span>{t.widget.powered}</span>
                <a href="/datenschutz" className="text-[#002FA7] hover:underline">{t.widget.privacy_link}</a>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
