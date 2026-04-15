import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { ArrowLeft, Copy, Save, RefreshCw, Check, Lock, ChevronDown, ChevronUp, PenTool, Pencil, Calendar, Share2, Target, TrendingUp, LogIn, GraduationCap, ClipboardList, MessageSquare, ArrowUpCircle, MailPlus, Mail, Magnet, Search, Cpu, Settings, MapPin, Tag, BarChart3, Banknote, FlaskConical, Wrench, Users, Lightbulb, Euro, Rocket, Swords, Brain, Building, FileText, Shield, Microscope, Crosshair } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import ReactMarkdown from 'react-markdown';

const ICON_MAP = {
  'pen-tool': PenTool, 'pencil': Pencil, 'calendar': Calendar, 'share-2': Share2,
  'target': Target, 'trending-up': TrendingUp, 'log-in': LogIn, 'graduation-cap': GraduationCap,
  'clipboard-list': ClipboardList, 'message-square': MessageSquare, 'arrow-up-circle': ArrowUpCircle,
  'mail-plus': MailPlus, 'mail': Mail, 'magnet': Magnet, 'search': Search, 'cpu': Cpu,
  'settings': Settings, 'sitemap': MapPin, 'tag': Tag, 'bar-chart-3': BarChart3,
  'banknote': Banknote, 'flask-conical': FlaskConical, 'wrench': Wrench, 'users': Users,
  'lightbulb': Lightbulb, 'euro': Euro, 'rocket': Rocket, 'swords': Swords, 'brain': Brain,
  'building': Building, 'file-text': FileText, 'shield': Shield, 'microscope': Microscope,
};

const LOADING_MESSAGES = [
  'Analysiere Ihren Kontext...',
  'Wende deutsche Marketing-Regeln an...',
  'Erstelle Ihren Text...',
  'Prüfe DSGVO-Konformität...',
  'Fast fertig...',
];

export default function MarketingAssistant() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [view, setView] = useState('grid');
  const [skills, setSkills] = useState({});
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState('all');
  const [usage, setUsage] = useState({ used: 0, limit: 50 });
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [message, setMessage] = useState('');
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
  const [profile, setProfile] = useState(null);
  const [showProfileSetup, setShowProfileSetup] = useState(false);
  const [profileForm, setProfileForm] = useState({ product_description: '', target_customer: '', usp: '', competitors: '' });
  const [showHistory, setShowHistory] = useState(false);

  const plan = user?.plan || 'free';
  const hasAccess = ['growth', 'agency'].includes(plan) || usage.trial_active;

  useEffect(() => {
    api.getMarketingSkills().then(data => {
      setSkills(data.skills || data);
      setCategories(data.categories || []);
    }).catch(() => {});
    api.getMarketingUsage().then(setUsage).catch(() => {});
    api.getChatbots().then(bots => {
      if (bots?.length > 0) setBusinessContext(bots[0]);
    }).catch(() => {});
    api.getMarketingProfile().then(p => {
      if (p && p.product_description) {
        setProfile(p);
      } else {
        setShowProfileSetup(true);
      }
    }).catch(() => setShowProfileSetup(true));
    api.getMarketingHistory().then(setHistory).catch(() => {});
  }, []);

  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setLoadingMsg(prev => (prev + 1) % LOADING_MESSAGES.length);
    }, 2500);
    return () => clearInterval(interval);
  }, [loading]);

  const handleSelectSkill = (skillName) => {
    if (!hasAccess) { setShowUpgrade(true); return; }
    setSelectedSkill(skillName);
    setMessage('');
    setResult(null);
    setView('input');
  };

  const handleRun = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setLoadingMsg(0);
    setView('loading');
    try {
      const data = await api.runMarketingSkill({ skillName: selectedSkill, message });
      setResult(data);
      setUsage(prev => ({ ...prev, used: data.used }));
      setView('result');
    } catch (err) {
      const errorData = await err.json?.().catch(() => null);
      alert(errorData?.detail || 'Fehler bei der Verarbeitung');
      setView('input');
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

  const handleSaveProfile = async () => {
    try {
      await api.saveMarketingProfile(profileForm);
      setProfile(profileForm);
      setShowProfileSetup(false);
    } catch {}
  };

  const handleBack = () => {
    setView('grid');
    setSelectedSkill(null);
    setResult(null);
  };

  const filteredSkills = Object.entries(skills).filter(([, skill]) =>
    activeCategory === 'all' || skill.category === activeCategory
  );

  const getIcon = (iconName) => ICON_MAP[iconName] || Crosshair;

  // ── PROFILE SETUP PROMPT ──
  if (showProfileSetup && hasAccess && view === 'grid') {
    return (
      <DashboardLayout>
        <div className="space-y-8 max-w-2xl mx-auto" data-testid="profile-setup">
          <div className="border-2 border-[#002FA7] bg-white p-8">
            <h2 className="font-clash text-2xl font-bold text-[#0A0A0A] mb-2">Einmalige Einrichtung (2 Minuten)</h2>
            <p className="text-sm text-[#4B5563] mb-6">Damit alle 34 Marketing-Tools optimal für Sie funktionieren, brauchen wir ein paar Details über Ihr Unternehmen. Das machen Sie nur einmal.</p>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-1 block">Was verkaufen Sie?</label>
                <textarea value={profileForm.product_description} onChange={e => setProfileForm(f => ({ ...f, product_description: e.target.value }))} placeholder="z.B. KI-Chatbot-Software für kleine Unternehmen" className="w-full p-3 border border-gray-300 text-sm focus:border-[#002FA7] outline-none min-h-[60px]" data-testid="profile-product" />
              </div>
              <div>
                <label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-1 block">Wer kauft bei Ihnen?</label>
                <textarea value={profileForm.target_customer} onChange={e => setProfileForm(f => ({ ...f, target_customer: e.target.value }))} placeholder="z.B. Bäckereien, Restaurants, Handwerker in Deutschland" className="w-full p-3 border border-gray-300 text-sm focus:border-[#002FA7] outline-none min-h-[60px]" data-testid="profile-customer" />
              </div>
              <div>
                <label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-1 block">Was macht Sie besonders?</label>
                <textarea value={profileForm.usp} onChange={e => setProfileForm(f => ({ ...f, usp: e.target.value }))} placeholder="z.B. DSGVO-konform, in 2 Minuten live, auf Deutsch" className="w-full p-3 border border-gray-300 text-sm focus:border-[#002FA7] outline-none min-h-[60px]" data-testid="profile-usp" />
              </div>
              <div>
                <label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-1 block">Wer sind Ihre Hauptwettbewerber?</label>
                <textarea value={profileForm.competitors} onChange={e => setProfileForm(f => ({ ...f, competitors: e.target.value }))} placeholder="z.B. moinAI, Tidio, Userlike" className="w-full p-3 border border-gray-300 text-sm focus:border-[#002FA7] outline-none min-h-[60px]" data-testid="profile-competitors" />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <Button onClick={handleSaveProfile} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-8 py-3 font-bold" data-testid="save-profile-btn">Jetzt einrichten</Button>
              <Button onClick={() => setShowProfileSetup(false)} variant="outline" className="rounded-none border-gray-300 font-bold" data-testid="skip-profile-btn">Später</Button>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // ── UPGRADE PROMPT (NON-GROWTH) ──
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
              {(t.marketing.unlock_features || []).map((f, i) => (
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
      <div className="space-y-6" data-testid="marketing-page">

        {/* ── VIEW 1: CATEGORY TABS + SKILL GRID ── */}
        {view === 'grid' && (
          <>
            <div className="flex items-center justify-between flex-wrap gap-3">
              <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">{t.marketing.title}</h1>
              {usage.trial_active && (
                <span className="text-xs bg-green-100 text-green-700 px-3 py-1 font-bold" data-testid="trial-badge">
                  {t.marketing.trial_active} — {t.marketing.trial_until} {usage.trial_end?.slice(0, 10)}
                </span>
              )}
            </div>

            {/* Usage Bar */}
            <div className={`border p-3 ${usage.used / usage.limit >= 0.8 ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 bg-white'}`} data-testid="marketing-usage-bar">
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs font-bold text-[#4B5563]">
                  {usage.used} / {usage.limit} {t.marketing.usage_label}
                  {usage.is_trial && <span className="ml-2 text-[#002FA7]">(Testphase — max. {usage.limit} Analysen)</span>}
                </p>
                {usage.is_trial && usage.used >= usage.limit && (
                  <a href="/dashboard/billing" className="text-xs font-bold text-[#002FA7] hover:underline" data-testid="upgrade-link">Upgrade für alle 34 Skills</a>
                )}
              </div>
              <Progress value={Math.min(usage.used / usage.limit * 100, 100)} className={`h-1.5 rounded-none ${usage.used / usage.limit >= 0.8 ? '[&>div]:bg-yellow-500' : '[&>div]:bg-[#002FA7]'}`} />
            </div>

            {/* Category Tabs */}
            <div className="flex gap-1.5 overflow-x-auto pb-1 -mx-1 px-1" data-testid="category-tabs">
              {categories.map(cat => (
                <button
                  key={cat.key}
                  onClick={() => setActiveCategory(cat.key)}
                  className={`px-4 py-2 text-xs font-bold whitespace-nowrap transition-colors ${activeCategory === cat.key ? 'bg-[#002FA7] text-white' : 'bg-white border border-gray-200 text-[#4B5563] hover:bg-[#F3F4F6]'}`}
                  data-testid={`tab-${cat.key}`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Skill Cards Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3" data-testid="skill-grid">
              {filteredSkills.map(([key, skill]) => {
                const Icon = getIcon(skill.icon);
                return (
                  <button
                    key={key}
                    onClick={() => handleSelectSkill(key)}
                    className="p-5 bg-white border border-gray-200 text-left hover:border-[#002FA7] hover:shadow-sm transition-all group"
                    data-testid={`skill-${key}`}
                  >
                    <Icon size={20} className="text-[#002FA7] mb-3 group-hover:scale-110 transition-transform" />
                    <h3 className="font-bold text-sm text-[#0A0A0A] mb-1 leading-tight">{skill.label}</h3>
                    <p className="text-xs text-[#4B5563] leading-snug">{skill.description}</p>
                  </button>
                );
              })}
            </div>

            {/* Edit Profile Link */}
            {profile && (
              <button onClick={() => { setProfileForm(profile); setShowProfileSetup(true); }} className="text-xs text-[#002FA7] font-bold hover:underline" data-testid="edit-profile-btn">
                Produkt-Profil bearbeiten
              </button>
            )}
          </>
        )}

        {/* ── VIEW 2: ONE-SCREEN INPUT ── */}
        {(view === 'input' || view === 'loading') && selectedSkill && (
          <>
            <div className="flex items-center gap-3">
              <button onClick={handleBack} className="p-2 hover:bg-gray-100 transition-colors" data-testid="back-btn"><ArrowLeft size={20} /></button>
              <div>
                <h1 className="font-clash text-2xl font-bold text-[#0A0A0A]">{skills[selectedSkill]?.label}</h1>
                <p className="text-xs text-[#4B5563]">{skills[selectedSkill]?.description}</p>
              </div>
            </div>

            {/* Auto-loaded Context */}
            {(businessContext || profile) && (
              <div className="border border-gray-200 bg-[#F9FAFB]">
                <button onClick={() => setShowContext(!showContext)} className="w-full p-3 flex items-center justify-between text-left" data-testid="context-toggle">
                  <span className="text-xs font-bold text-[#4B5563]">Ihr Kontext (automatisch geladen)</span>
                  {showContext ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>
                {showContext && (
                  <div className="px-3 pb-3 text-xs text-[#4B5563] space-y-1">
                    {businessContext && <p><strong>{businessContext.business_name}</strong></p>}
                    {businessContext?.faq_content && <p className="line-clamp-3">{businessContext.faq_content.slice(0, 200)}...</p>}
                    {profile?.product_description && <p>Produkt: {profile.product_description}</p>}
                    {profile?.target_customer && <p>Zielkunde: {profile.target_customer}</p>}
                  </div>
                )}
              </div>
            )}

            {/* Main Input */}
            {view === 'input' && (
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">Was soll ich erstellen?</label>
                  <textarea
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                    placeholder={skills[selectedSkill]?.placeholder || skills[selectedSkill]?.description || ''}
                    className="w-full min-h-[120px] p-4 border border-gray-300 text-sm focus:border-[#002FA7] outline-none resize-y"
                    data-testid="marketing-input"
                    autoFocus
                  />
                </div>
                <Button onClick={handleRun} disabled={loading || !message.trim()} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-10 py-3 font-bold text-sm" data-testid="run-skill-btn">
                  Erstellen
                </Button>
              </div>
            )}

            {/* Loading State */}
            {view === 'loading' && (
              <div className="border border-[#002FA7] bg-[#002FA7]/5 p-10 text-center" data-testid="marketing-loading">
                <p className="text-sm font-bold text-[#0A0A0A] mb-4">Erstelle Ihren {skills[selectedSkill]?.label}...</p>
                <Progress value={Math.min((loadingMsg + 1) / LOADING_MESSAGES.length * 100, 95)} className="h-2 rounded-none [&>div]:bg-[#002FA7] mb-4 max-w-md mx-auto" />
                <p className="text-xs text-[#002FA7] animate-pulse">{LOADING_MESSAGES[loadingMsg]}</p>
              </div>
            )}
          </>
        )}

        {/* ── VIEW 3: RESULTS ── */}
        {view === 'result' && result && (
          <>
            <div className="flex items-center gap-3">
              <button onClick={handleBack} className="p-2 hover:bg-gray-100 transition-colors" data-testid="result-back-btn"><ArrowLeft size={20} /></button>
              <div>
                <p className="text-xs font-bold text-green-600 flex items-center gap-1"><Check size={12} /> Fertig!</p>
                <h1 className="font-clash text-2xl font-bold text-[#0A0A0A]">{skills[selectedSkill]?.label}</h1>
              </div>
            </div>

            {/* Result Content */}
            <div className="border border-gray-200 bg-white p-6 md:p-8" data-testid="marketing-result">
              <div className="prose prose-sm max-w-none prose-headings:font-clash prose-headings:text-[#002FA7] prose-headings:tracking-tight prose-h2:text-lg prose-h2:font-bold prose-h2:mt-6 prose-h2:mb-3 prose-h3:text-base prose-h3:font-bold prose-h3:mt-4 prose-h3:mb-2 prose-p:text-[#0A0A0A] prose-p:leading-relaxed prose-li:text-[#0A0A0A] prose-strong:text-[#0A0A0A]">
                <ReactMarkdown>{result.result}</ReactMarkdown>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2 flex-wrap">
              <Button onClick={handleCopy} variant="outline" className="rounded-none border-gray-300 font-bold text-xs gap-1.5" data-testid="copy-result-btn">
                {copied ? <><Check size={12} className="text-green-600" />Kopiert!</> : <><Copy size={12} />Kopieren</>}
              </Button>
              <Button onClick={handleSave} variant="outline" className="rounded-none border-gray-300 font-bold text-xs gap-1.5" data-testid="save-result-btn">
                {saved ? <><Check size={12} className="text-green-600" />Gespeichert!</> : <><Save size={12} />Speichern</>}
              </Button>
              <Button onClick={handleBack} variant="outline" className="rounded-none border-gray-300 font-bold text-xs gap-1.5" data-testid="new-analysis-btn">
                <RefreshCw size={12} />Neu
              </Button>
            </div>

            {/* Recent Results */}
            {history.length > 0 && (
              <div>
                <button onClick={() => setShowHistory(!showHistory)} className="text-xs font-bold text-[#4B5563] flex items-center gap-1" data-testid="toggle-history">
                  {showHistory ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  Letzte gespeicherte Ergebnisse
                </button>
                {showHistory && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {history.slice(0, 5).map((h, i) => {
                      const sk = skills[h.skill_name];
                      const Icon = getIcon(sk?.icon);
                      const timeAgo = getTimeAgo(h.created_at);
                      return (
                        <span key={i} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#F3F4F6] text-xs font-medium text-[#4B5563]">
                          <Icon size={12} /> {sk?.label || h.skill_name} · {timeAgo}
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            <p className="text-xs text-[#4B5563]">{result.used} / {result.limit} {t.marketing.usage_label}</p>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

function getTimeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.floor(hours / 24)}d`;
}
