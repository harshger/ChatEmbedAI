import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Check, Lock, ArrowRight, Search, TrendingUp, PenTool, Share2, Shield, Tag, Mail, Rocket, Euro, Users, Lightbulb, Brain, Target, Crosshair } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import Header from '../components/Header';

const SCAN_MESSAGES = [
  'Lese Ihre Website...',
  'Prüfe SEO-Faktoren...',
  'Analysiere Ihre Texte...',
  'Prüfe DSGVO-Konformität...',
  'Erstelle Ihre Empfehlungen...',
];

const ICON_MAP = {
  'search': Search, 'trending-up': TrendingUp, 'pen-tool': PenTool, 'share-2': Share2,
  'shield': Shield, 'tag': Tag, 'mail': Mail, 'rocket': Rocket, 'euro': Euro,
  'users': Users, 'lightbulb': Lightbulb, 'brain': Brain, 'target': Target,
};

export default function Welcome() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [scan, setScan] = useState(null);
  const [scanMsg, setScanMsg] = useState(0);
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [scanConsent, setScanConsent] = useState(false);
  const [startingScan, setStartingScan] = useState(false);

  const hasWebsite = user?.website_url;

  // Poll for scan status
  useEffect(() => {
    let interval;
    const checkScan = async () => {
      try {
        const data = await api.getWebsiteScan();
        setScan(data);
        if (data.status === 'scanning') {
          if (!interval) {
            interval = setInterval(async () => {
              const updated = await api.getWebsiteScan();
              setScan(updated);
              if (updated.status !== 'scanning') clearInterval(interval);
            }, 3000);
          }
        }
      } catch {}
    };
    checkScan();
    return () => { if (interval) clearInterval(interval); };
  }, []);

  // Rotate loading messages
  useEffect(() => {
    if (scan?.status !== 'scanning') return;
    const interval = setInterval(() => {
      setScanMsg(prev => (prev + 1) % SCAN_MESSAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [scan?.status]);

  const handleStartScan = async () => {
    const url = websiteUrl.trim() || hasWebsite;
    if (!url || !scanConsent) return;
    setStartingScan(true);
    try {
      await api.startWebsiteScan({ url, consent: true });
      setScan({ status: 'scanning', url });
    } catch (err) {
      const d = await err.json?.().catch(() => null);
      alert(d?.detail || 'Fehler');
    }
    setStartingScan(false);
  };

  // ── STATE A: SCANNING ──
  if (scan?.status === 'scanning') {
    return (
      <div className="min-h-screen bg-[#F9FAFB]" data-testid="welcome-scanning">
        <Header />
        <div className="flex items-center justify-center pt-32 pb-32 px-6">
          <div className="max-w-lg w-full text-center">
            <div className="border-2 border-[#002FA7] bg-white p-12">
              <Search size={40} className="text-[#002FA7] mx-auto mb-6 animate-pulse" />
              <h2 className="font-clash text-2xl font-bold text-[#0A0A0A] mb-2">Wir analysieren Ihre Website...</h2>
              <p className="text-sm text-[#4B5563] mb-6 break-all">{scan.url}</p>
              <Progress value={Math.min((scanMsg + 1) / SCAN_MESSAGES.length * 100, 90)} className="h-2 rounded-none [&>div]:bg-[#002FA7] mb-4" />
              <p className="text-xs text-[#002FA7] animate-pulse">{SCAN_MESSAGES[scanMsg]}</p>
              <p className="text-xs text-[#9CA3AF] mt-4">Das dauert etwa 20-30 Sekunden.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── STATE B: RESULTS ──
  if (scan?.status === 'complete' && scan?.insights?.length) {
    return (
      <div className="min-h-screen bg-[#F9FAFB]" data-testid="welcome-results">
        <Header />
        <div className="max-w-4xl mx-auto pt-24 pb-16 px-6">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 bg-green-100 text-green-700 text-xs font-bold px-4 py-2 mb-4">
              <Check size={14} /> Analyse abgeschlossen!
            </div>
            <h1 className="font-clash text-3xl font-bold text-[#0A0A0A] mb-1">Wir haben 2 wichtige Punkte gefunden</h1>
            <p className="text-sm text-[#4B5563] break-all">für {scan.url}</p>
          </div>

          {/* 2 Free Insight Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {scan.insights.map((insight, idx) => {
              const Icon = ICON_MAP[insight.icon] || Crosshair;
              return (
                <div key={idx} className="border-2 border-[#002FA7] bg-white p-6" data-testid={`insight-${idx}`}>
                  <div className="flex items-center gap-2 mb-4">
                    <Icon size={20} className="text-[#002FA7]" />
                    <h3 className="font-bold text-sm text-[#0A0A0A]">{insight.label}</h3>
                  </div>
                  <div className="prose prose-xs max-w-none prose-headings:text-[#002FA7] prose-headings:text-sm prose-h2:text-sm prose-h2:mt-3 prose-h2:mb-1 prose-p:text-xs prose-p:text-[#4B5563] prose-p:leading-relaxed prose-li:text-xs prose-strong:text-[#0A0A0A]">
                    <ReactMarkdown>{insight.analysis?.slice(0, 600)}</ReactMarkdown>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Locked Skills */}
          <div className="border border-gray-200 bg-white p-6 mb-8">
            <div className="flex items-center gap-2 mb-4">
              <Lock size={16} className="text-[#4B5563]" />
              <h3 className="font-bold text-sm text-[#0A0A0A]">{scan.locked_skills_count} weitere Analysen für Sie bereit</h3>
            </div>
            <p className="text-xs text-[#4B5563] mb-4">Basierend auf Ihrer Website können diese Tools Ihnen konkret helfen:</p>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              {Object.entries(scan.teasers || {}).slice(0, 12).map(([skillKey, teaser]) => (
                <div key={skillKey} className="p-3 bg-[#F9FAFB] border border-gray-100 opacity-75">
                  <div className="flex items-center gap-1 mb-1">
                    <Lock size={10} className="text-[#9CA3AF]" />
                    <span className="text-xs font-bold text-[#4B5563] truncate">{skillKey.replace(/-/g, ' ')}</span>
                  </div>
                  <p className="text-[10px] text-[#9CA3AF] leading-snug line-clamp-2">{teaser}</p>
                </div>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div className="border-2 border-[#002FA7] bg-[#002FA7]/5 p-8 text-center">
            <Rocket size={28} className="text-[#002FA7] mx-auto mb-3" />
            <h3 className="font-clash text-xl font-bold text-[#0A0A0A] mb-1">Alle {scan.locked_skills_count} Analysen freischalten</h3>
            <p className="text-sm text-[#4B5563] mb-4">Growth-Plan — 99 EUR / Monat (zzgl. MwSt. · jederzeit kündbar)</p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button onClick={() => navigate('/dashboard/billing')} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-8 py-3 font-bold" data-testid="upgrade-cta">
                Jetzt freischalten
              </Button>
              <Button onClick={() => navigate('/dashboard')} variant="outline" className="rounded-none border-gray-300 font-bold" data-testid="go-dashboard">
                Zum Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── STATE C: NO WEBSITE / PROMPT TO SCAN ──
  return (
    <div className="min-h-screen bg-[#F9FAFB]" data-testid="welcome-no-scan">
      <Header />
      <div className="flex items-center justify-center pt-32 pb-32 px-6">
        <div className="max-w-lg w-full">
          <div className="border border-gray-200 bg-white p-8 text-center">
            <h1 className="font-clash text-3xl font-bold text-[#0A0A0A] mb-3">Willkommen bei ChatEmbed AI!</h1>

            {/* Quick start steps */}
            <div className="text-left space-y-3 mb-8">
              <p className="text-sm text-[#4B5563]">Starten Sie mit Schritt 1:</p>
              <div className="space-y-2">
                <div className="flex items-center gap-3 text-sm text-[#0A0A0A]">
                  <span className="w-6 h-6 bg-[#002FA7] text-white text-xs font-bold flex items-center justify-center flex-shrink-0">1</span>
                  Chatbot erstellen (5 Minuten)
                </div>
                <div className="flex items-center gap-3 text-sm text-[#4B5563]">
                  <span className="w-6 h-6 bg-gray-200 text-xs font-bold flex items-center justify-center flex-shrink-0">2</span>
                  Embed-Code kopieren
                </div>
                <div className="flex items-center gap-3 text-sm text-[#4B5563]">
                  <span className="w-6 h-6 bg-gray-200 text-xs font-bold flex items-center justify-center flex-shrink-0">3</span>
                  Website live testen
                </div>
              </div>
            </div>
            <Button onClick={() => navigate('/dashboard/new')} className="w-full bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none py-3 font-bold mb-6" data-testid="create-first-chatbot">
              Ersten Chatbot erstellen <ArrowRight size={16} className="ml-2" />
            </Button>

            {/* Free website analysis offer */}
            <div className="border-t border-gray-200 pt-6">
              <p className="text-xs font-bold text-[#4B5563] mb-3 flex items-center justify-center gap-1">
                <Lightbulb size={14} /> Möchten Sie auch Ihre Website kostenlos analysieren lassen?
              </p>
              <div className="space-y-3">
                <input
                  type="url"
                  value={websiteUrl}
                  onChange={e => setWebsiteUrl(e.target.value)}
                  placeholder="https://ihre-website.de"
                  className="w-full p-3 border border-gray-300 text-sm focus:border-[#002FA7] outline-none"
                  data-testid="welcome-url-input"
                />
                <label className="flex items-start gap-2 text-xs text-[#4B5563] cursor-pointer">
                  <input type="checkbox" checked={scanConsent} onChange={e => setScanConsent(e.target.checked)} className="mt-0.5" data-testid="welcome-scan-consent" />
                  Ich erlaube die einmalige Analyse meiner öffentlich zugänglichen Website (DSGVO-konform, keine Cookies, keine Speicherung personenbezogener Daten).
                </label>
                <Button
                  onClick={handleStartScan}
                  disabled={!websiteUrl.trim() || !scanConsent || startingScan}
                  variant="outline"
                  className="w-full rounded-none border-[#002FA7] text-[#002FA7] font-bold"
                  data-testid="welcome-start-scan"
                >
                  {startingScan ? 'Wird gestartet...' : 'Website analysieren'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
