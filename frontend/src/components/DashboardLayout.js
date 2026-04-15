import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { useTranslation } from '../lib/i18n';
import { LayoutDashboard, Plus, BarChart3, CreditCard, FileText, Shield, LogOut, Globe, Users, BookTemplate, Cpu } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/dashboard', icon: LayoutDashboard, labelKey: 'Dashboard' },
  { path: '/dashboard/new', icon: Plus, labelKey: 'New Chatbot' },
  { path: '/dashboard/templates', icon: FileText, labelKey: 'Templates' },
  { path: '/dashboard/analytics', icon: BarChart3, labelKey: 'Analytics' },
  { path: '/dashboard/billing', icon: CreditCard, labelKey: 'Billing' },
  { path: '/dashboard/ai-settings', icon: Cpu, labelKey: 'AI Engine' },
  { path: '/dashboard/team', icon: Users, labelKey: 'Team' },
  { path: '/account/privacy', icon: Shield, labelKey: 'Privacy' },
];

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth();
  const { lang, setLang } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#F9FAFB] flex" data-testid="dashboard-layout">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 fixed h-full z-40 hidden md:block" data-testid="sidebar">
        <div className="p-6 border-b border-gray-200">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#002FA7] flex items-center justify-center"><span className="text-white font-black text-sm">CE</span></div>
            <span className="font-clash text-lg font-bold text-[#0A0A0A] tracking-tight">ChatEmbed AI</span>
          </Link>
        </div>
        <nav className="p-4 space-y-1">
          {NAV_ITEMS.map(item => (
            <Link key={item.path} to={item.path} className={`flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors ${location.pathname === item.path ? 'bg-[#002FA7] text-white' : 'text-[#4B5563] hover:bg-[#F3F4F6] hover:text-[#0A0A0A]'}`} data-testid={`nav-${item.labelKey.toLowerCase().replace(' ', '-')}`}>
              <item.icon size={18} />
              {item.labelKey}
            </Link>
          ))}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 space-y-2">
          <button onClick={() => setLang(lang === 'de' ? 'en' : 'de')} className="flex items-center gap-3 px-4 py-2 text-sm text-[#4B5563] hover:text-[#0A0A0A] w-full" data-testid="sidebar-lang-toggle">
            <Globe size={18} />
            {lang === 'de' ? 'English' : 'Deutsch'}
          </button>
          <button onClick={handleLogout} className="flex items-center gap-3 px-4 py-2 text-sm text-[#E60000] hover:text-red-700 w-full" data-testid="logout-btn">
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 md:ml-64">
        {/* Mobile header */}
        <div className="md:hidden bg-white border-b border-gray-200 p-4 flex items-center justify-between sticky top-0 z-30">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-6 h-6 bg-[#002FA7] flex items-center justify-center"><span className="text-white font-black text-xs">CE</span></div>
            <span className="font-clash text-sm font-bold">ChatEmbed AI</span>
          </Link>
        </div>
        <div className="p-6 md:p-12 max-w-6xl">
          {children}
        </div>
      </main>
    </div>
  );
}
