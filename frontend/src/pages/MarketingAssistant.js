import React, { useState, useEffect } from 'react';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { ArrowLeft, Copy, Save, RefreshCw, Check, Lock, PenTool, Mail, TrendingUp, Euro, MailPlus, Search, Share2, Rocket, Shield, Users, ChevronDown, ChevronUp, Crosshair } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import ReactMarkdown from 'react-markdown';

const SKILL_ICONS = {
  'pen-tool': PenTool, 'mail': Mail, 'trending-up': TrendingUp, 'euro': Euro,
  'mail-plus': MailPlus, 'search': Search, 'share-2': Share2, 'rocket': Rocket,
  'shield': Shield, 'users': Users,
};

const LOADING_MESSAGES = [
  'Analysiere Ihren Kontext...',
  'Wende deutsche Markt-Regeln an...',
  'Erstelle Empfehlungen...',
  'Fast fertig...',
];

export default function MarketingAssistant() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [view, setView] = useState('grid');
  const [skills, setSkills] = useState({});
  const [usage, setUsage] = useState({ used: 0, limit: 50 });
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [message, setMessage] = useState('');
  const [additionalContext, setAdditionalContext] = useState('');
  const [showContext, setShowContext] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState(0);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [saved, setSaved] = useState(false);
  const [history, setHistory] = useState([]);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [trialStarting, setTrialStarting] = useState(false);
  const [businessContext, setBusinessContext] = useState(null);

  const plan = user?.plan || 'free';
  const hasAccess = ['growth', 'agency'].includes(plan) || usage.trial_active;

  useEffect(() => {
    api.getMarketingSkills().then(setSkills).catch(() => {});
    api.getMarketingUsage().then(setUsage).catch(() => {});
    api.getChatbots().then(bots => {
      if (bots?.length > 0) setBusinessContext(bots[0]);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setLoadingMsg(prev => (prev + 1) % LOADING_MESSAGES.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [loading]);

  const handleSelectSkill = (skillName) => {
    if (!hasAccess) { setShowUpgrade(true); return; }
    setSelectedSkill(skillName);
    setMessage('');
    setAdditionalContext('');
    setView('input');
  };

  const handleRun = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setLoadingMsg(0);
    try {
      const data = await api.runMarketingSkill({ skillName: selectedSkill, message, additionalContext });
      setResult(data);
      setUsage(prev => ({ ...prev, used: data.used }));
      setView('result');
    } catch (err) {
      const errorData = await err.json?.().catch(() => null);
      alert(errorData?.detail || 'Fehler bei der Verarbeitung');
    }
    setLoading(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(result?.result || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = async () => {
    try {
      await api.saveMarketingResult({ skillName: selectedSkill, prompt: message, result: result?.result || '' });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      api.getMarketingHistory().then(setHistory).catch(() => {});
    } catch {}
  };

  const handleStartTrial = async () => {
    setTrialStarting(true);
    try {
      await api.startMarketingTrial();
      const u = await api.getMarketingUsage();
      setUsage(u);
      setShowUpgrade(false);
    } catch (err) {
      const errorData = await err.json?.().catch(() => null);
      alert(errorData?.detail || 'Fehler');
    }
    setTrialStarting(false);
  };

  const handleBack = () => {
    setView('grid');
    setSelectedSkill(null);
    setResult(null);
  };

  // NON-GROWTH USERS: show upgrade prompt
  if (!hasAccess && view === 'grid') {
    return (
      <DashboardLayout>
        <div className="space-y-8" data-testid="marketing-locked">
          <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">{t.marketing.title}</h1>
          <div className="border-2 border-[#002FA7] bg-white p-12 text-center max-w-2xl mx-auto">
            <Crosshair size={48} className="text-[#002FA7] mx-auto mb-6" />
            <h2 className="font-clash text-2xl font-bold text-[#0A0A0A] mb-3">{t.marketing.unlock_title}</h2>
            <p className="text-[#4B5563] mb-8">{t.marketing.unlock_subtitle}</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left mb-8 max-w-md mx-auto">
              {t.marketing.unlock_features.map((f, i) => (
                <p key={i} className="flex items-center gap-2 text-sm text-[#0A0A0A]"><Check size={14} className="text-green-600 flex-shrink-0" />{f}</p>
              ))}
            </div>
            <p className="text-2xl font-black text-[#0A0A0A] mb-2">{t.marketing.unlock_price}</p>
            <p className="text-xs text-[#4B5563] mb-6">{t.marketing.unlock_trial}</p>
            <div className="flex flex-col gap-3 items-center">
              <Button onClick={handleStartTrial} disabled={trialStarting} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-8 py-3 font-bold" data-testid="start-trial-btn">
                {trialStarting ? '...' : t.marketing.start_trial}
              </Button>
              <p className="text-xs text-[#4B5563]">{t.marketing.cancel_policy}</p>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="marketing-page">
        {/* VIEW 1: SKILL GRID */}
        {view === 'grid' && (
          <>
            <div className="flex items-center justify-between">
              <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">{t.marketing.title}</h1>
              {usage.trial_active && (
                <span className="text-xs bg-green-100 text-green-700 px-3 py-1 font-bold" data-testid="trial-badge">
                  {t.marketing.trial_active} — {t.marketing.trial_until} {usage.trial_end?.slice(0, 10)}
                </span>
              )}
            </div>

            {/* Usage Bar */}
            <div className={`border p-4 ${usage.used / usage.limit >= 0.8 ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 bg-white'}`} data-testid="marketing-usage-bar">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-bold text-[#0A0A0A]">{usage.used} / {usage.limit} {t.marketing.usage_label}</p>
                <span className="text-xs font-bold text-[#4B5563]">{Math.round(usage.used / usage.limit * 100)}%</span>
              </div>
              <Progress value={Math.min(usage.used / usage.limit * 100, 100)} className={`h-2 rounded-none ${usage.used / usage.limit >= 0.8 ? '[&>div]:bg-yellow-500' : '[&>div]:bg-[#002FA7]'}`} />
            </div>

            {/* Skill Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border border-gray-200" data-testid="skill-grid">
              {Object.entries(skills).map(([key, skill]) => {
                const Icon = SKILL_ICONS[skill.icon] || Crosshair;
                return (
                  <button key={key} onClick={() => handleSelectSkill(key)} className="p-6 bg-white border border-gray-200 text-left hover:bg-[#F9FAFB] transition-colors" data-testid={`skill-${key}`}>
                    <Icon size={22} className="text-[#002FA7] mb-3" />
                    <h3 className="font-bold text-[#0A0A0A] mb-1">{skill.label}</h3>
                    <p className="text-xs text-[#4B5563] mb-3">{skill.description}</p>
                    <p className="text-xs text-[#9CA3AF] italic">z.B. "{skill.example}"</p>
                  </button>
                );
              })}
            </div>
          </>
        )}

        {/* VIEW 2: SKILL INPUT */}
        {view === 'input' && selectedSkill && (
          <>
            <div className="flex items-center gap-3">
              <button onClick={handleBack} className="p-2 hover:bg-gray-100 transition-colors" data-testid="back-btn"><ArrowLeft size={20} /></button>
              <h1 className="font-clash text-2xl font-bold text-[#0A0A0A]">{skills[selectedSkill]?.label}</h1>
            </div>

            {/* Business Context */}
            {businessContext && (
              <div className="border border-gray-200 bg-[#F9FAFB]">
                <button onClick={() => setShowContext(!showContext)} className="w-full p-4 flex items-center justify-between text-left">
                  <span className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563]">{t.marketing.context_label}</span>
                  {showContext ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
                {showContext && (
                  <div className="px-4 pb-4 text-sm text-[#4B5563]">
                    <p className="font-bold">{businessContext.business_name}</p>
                    <p className="mt-1 text-xs line-clamp-4">{businessContext.faq_content?.slice(0, 300)}...</p>
                  </div>
                )}
              </div>
            )}

            {/* Main Input */}
            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.marketing.input_label}</label>
                <textarea
                  value={message}
                  onChange={e => setMessage(e.target.value)}
                  placeholder={skills[selectedSkill]?.example || ''}
                  className="w-full min-h-[120px] p-4 border border-gray-300 text-sm focus:border-[#002FA7] outline-none resize-y"
                  data-testid="marketing-input"
                />
              </div>
              <div>
                <button onClick={() => setShowContext(prev => !prev)} className="text-xs text-[#002FA7] font-bold mb-2">{t.marketing.additional_context}</button>
                <textarea
                  value={additionalContext}
                  onChange={e => setAdditionalContext(e.target.value)}
                  placeholder={t.marketing.additional_placeholder}
                  className="w-full min-h-[80px] p-4 border border-gray-200 text-sm focus:border-[#002FA7] outline-none resize-y"
                  data-testid="marketing-additional-input"
                />
              </div>
              <Button onClick={handleRun} disabled={loading || !message.trim()} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-8 py-3 font-bold" data-testid="run-skill-btn">
                <Crosshair size={16} className="mr-2" />
                {loading ? '...' : t.marketing.run_btn}
              </Button>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="border border-[#002FA7] bg-[#002FA7]/5 p-8 text-center" data-testid="marketing-loading">
                <div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-sm font-bold text-[#002FA7] animate-pulse">{LOADING_MESSAGES[loadingMsg]}</p>
              </div>
            )}
          </>
        )}

        {/* VIEW 3: RESULTS */}
        {view === 'result' && result && (
          <>
            <div className="flex items-center gap-3">
              <button onClick={handleBack} className="p-2 hover:bg-gray-100 transition-colors" data-testid="result-back-btn"><ArrowLeft size={20} /></button>
              <h1 className="font-clash text-2xl font-bold text-[#0A0A0A]">{skills[selectedSkill]?.label} — {t.marketing.result_title}</h1>
            </div>

            {/* Result Content */}
            <div className="border border-gray-200 bg-white p-8" data-testid="marketing-result">
              <div className="prose prose-sm max-w-none
                prose-headings:font-clash prose-headings:text-[#002FA7] prose-headings:tracking-tight
                prose-h2:text-lg prose-h2:font-bold prose-h2:mt-6 prose-h2:mb-3
                prose-h3:text-base prose-h3:font-bold prose-h3:mt-4 prose-h3:mb-2
                prose-p:text-[#0A0A0A] prose-p:leading-relaxed
                prose-li:text-[#0A0A0A]
                prose-strong:text-[#0A0A0A]
              ">
                <ReactMarkdown>{result.result}</ReactMarkdown>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              <Button onClick={handleCopy} variant="outline" className="rounded-none border-gray-300 font-bold text-sm gap-2" data-testid="copy-result-btn">
                {copied ? <><Check size={14} className="text-green-600" />Kopiert!</> : <><Copy size={14} />Kopieren</>}
              </Button>
              <Button onClick={handleSave} variant="outline" className="rounded-none border-gray-300 font-bold text-sm gap-2" data-testid="save-result-btn">
                {saved ? <><Check size={14} className="text-green-600" />Gespeichert!</> : <><Save size={14} />Speichern</>}
              </Button>
              <Button onClick={handleBack} variant="outline" className="rounded-none border-gray-300 font-bold text-sm gap-2" data-testid="new-analysis-btn">
                <RefreshCw size={14} />Neu
              </Button>
            </div>

            {/* Usage Info */}
            <p className="text-xs text-[#4B5563]">{result.used} / {result.limit} {t.marketing.usage_label}</p>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
