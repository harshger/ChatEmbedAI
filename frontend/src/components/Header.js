import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { Globe } from 'lucide-react';

export default function Header() {
  const { t, lang, setLang } = useTranslation();
  const { user } = useAuth();
  const location = useLocation();

  return (
    <header className="bg-white/80 backdrop-blur-xl border-b border-gray-200 sticky top-0 z-50" data-testid="header">
      <div className="max-w-7xl mx-auto px-6 md:px-12 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2" data-testid="logo-link">
          <div className="w-8 h-8 bg-[#002FA7] flex items-center justify-center">
            <span className="text-white font-black text-sm">CE</span>
          </div>
          <span className="font-clash text-lg font-bold text-[#0A0A0A] tracking-tight">ChatEmbed AI</span>
        </Link>

        <nav className="flex items-center gap-6">
          <Link to="/pricing" className="text-sm font-bold text-[#4B5563] hover:text-[#0A0A0A] transition-colors" data-testid="nav-pricing">{t.nav.pricing}</Link>
          
          {user ? (
            <>
              <Link to="/dashboard" className="text-sm font-bold text-[#4B5563] hover:text-[#0A0A0A] transition-colors" data-testid="nav-dashboard">{t.nav.dashboard}</Link>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm font-bold text-[#4B5563] hover:text-[#0A0A0A] transition-colors" data-testid="nav-login">{t.nav.login}</Link>
              <Link to="/signup" className="bg-[#002FA7] text-white px-4 py-2 text-sm font-bold hover:bg-[#0040D6] transition-colors" data-testid="nav-signup">{t.nav.signup}</Link>
            </>
          )}

          <button onClick={() => setLang(lang === 'de' ? 'en' : 'de')} className="flex items-center gap-1.5 text-xs font-bold text-[#4B5563] hover:text-[#0A0A0A] border border-gray-200 px-3 py-1.5 transition-colors" data-testid="lang-toggle">
            <Globe size={14} />
            {lang === 'de' ? 'EN' : 'DE'}
          </button>
        </nav>
      </div>
    </header>
  );
}
