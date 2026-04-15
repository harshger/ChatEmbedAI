import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';

export default function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="bg-[#0A0A0A] text-white py-12 border-t border-gray-800" data-testid="footer">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-[#002FA7] flex items-center justify-center"><span className="text-white font-black text-xs">CE</span></div>
            <span className="font-clash font-bold text-sm tracking-tight">ChatEmbed AI</span>
          </div>
          <nav className="flex flex-wrap gap-6 text-xs text-gray-400">
            <Link to="/impressum" className="hover:text-white transition-colors" data-testid="footer-impressum">{t.footer.impressum}</Link>
            <Link to="/datenschutz" className="hover:text-white transition-colors" data-testid="footer-datenschutz">{t.footer.datenschutz}</Link>
            <Link to="/agb" className="hover:text-white transition-colors" data-testid="footer-agb">{t.footer.agb}</Link>
            <Link to="/avv" className="hover:text-white transition-colors" data-testid="footer-avv">{t.footer.avv}</Link>
            <button onClick={() => { localStorage.removeItem('cookie_consent'); window.location.reload(); }} className="hover:text-white transition-colors" data-testid="footer-cookies">{t.footer.cookies}</button>
          </nav>
        </div>
        <div className="border-t border-gray-800 pt-6 flex flex-col md:flex-row justify-between text-xs text-gray-500">
          <p>{t.footer.copyright}</p>
          <p>{t.footer.vat}</p>
        </div>
      </div>
    </footer>
  );
}
