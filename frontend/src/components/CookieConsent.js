import React, { useState, useEffect } from 'react';
import { useTranslation } from '../lib/i18n';
import { api } from '../lib/api';
import { Switch } from '../components/ui/switch';
import { X } from 'lucide-react';

export default function CookieConsent() {
  const { t } = useTranslation();
  const [visible, setVisible] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [analytics, setAnalytics] = useState(false);
  const [marketing, setMarketing] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookie_consent');
    if (!consent) setVisible(true);
  }, []);

  const saveConsent = (type) => {
    const consent = {
      necessary: true,
      analytics: type === 'all' ? true : analytics,
      marketing: type === 'all' ? true : marketing,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('cookie_consent', JSON.stringify(consent));
    setVisible(false);

    // Log consent
    try {
      api.logConsent({ consent_type: 'cookie_analytics', granted: consent.analytics, session_id: `anon_${Date.now()}` });
      api.logConsent({ consent_type: 'cookie_marketing', granted: consent.marketing, session_id: `anon_${Date.now()}` });
    } catch {}
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[100]" data-testid="cookie-banner">
      <div className="bg-[#0A0A0A] text-white">
        {!showSettings ? (
          <div className="max-w-7xl mx-auto px-6 md:px-12 py-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <p className="text-sm leading-relaxed max-w-2xl">{t.cookie.text}</p>
            <div className="flex items-center gap-3 flex-shrink-0">
              <button onClick={() => saveConsent('all')} className="bg-[#002FA7] text-white px-5 py-2 text-sm font-bold hover:bg-[#0040D6] transition-colors" data-testid="cookie-accept-all">{t.cookie.acceptAll}</button>
              <button onClick={() => saveConsent('necessary')} className="border border-gray-500 text-white px-5 py-2 text-sm font-bold hover:bg-white/10 transition-colors" data-testid="cookie-reject">{t.cookie.rejectAll}</button>
              <button onClick={() => setShowSettings(true)} className="text-gray-400 text-sm underline hover:text-white transition-colors" data-testid="cookie-settings-btn">{t.cookie.settings}</button>
            </div>
          </div>
        ) : (
          <div className="max-w-7xl mx-auto px-6 md:px-12 py-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-bold uppercase tracking-wider">Cookie-Einstellungen</h3>
              <button onClick={() => setShowSettings(false)} className="text-gray-400 hover:text-white"><X size={18} /></button>
            </div>
            <div className="space-y-4 mb-6">
              <div className="flex items-center justify-between py-3 border-b border-gray-700">
                <div>
                  <p className="text-sm font-bold">{t.cookie.necessary}</p>
                  <p className="text-xs text-gray-400">{t.cookie.alwaysOn}</p>
                </div>
                <Switch checked disabled className="opacity-50" />
              </div>
              <div className="flex items-center justify-between py-3 border-b border-gray-700">
                <div>
                  <p className="text-sm font-bold">{t.cookie.analytics}</p>
                  <p className="text-xs text-gray-400">Performance & analytics cookies</p>
                </div>
                <Switch checked={analytics} onCheckedChange={setAnalytics} data-testid="cookie-analytics-toggle" />
              </div>
              <div className="flex items-center justify-between py-3 border-b border-gray-700">
                <div>
                  <p className="text-sm font-bold">{t.cookie.marketing}</p>
                  <p className="text-xs text-gray-400">Marketing & advertising cookies</p>
                </div>
                <Switch checked={marketing} onCheckedChange={setMarketing} data-testid="cookie-marketing-toggle" />
              </div>
            </div>
            <button onClick={() => saveConsent('custom')} className="bg-[#002FA7] text-white px-6 py-2 text-sm font-bold hover:bg-[#0040D6] transition-colors" data-testid="cookie-save-settings">{t.cookie.save}</button>
          </div>
        )}
      </div>
    </div>
  );
}
