import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Switch } from '../components/ui/switch';
import { Plus, MessageSquare, Bot, Activity, Globe, Edit, Code, Eye, Trash2, Mail, CheckCircle } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

export default function Dashboard() {
  const { t } = useTranslation();
  const { user, checkAuth } = useAuth();
  const [stats, setStats] = useState(null);
  const [chatbots, setChatbots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [verifyToken, setVerifyToken] = useState('');
  const [verified, setVerified] = useState(false);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Guten Morgen';
    if (h < 18) return 'Guten Tag';
    return 'Guten Abend';
  };

  useEffect(() => {
    const load = async () => {
      try {
        const [s, c] = await Promise.all([api.getStats(), api.getChatbots()]);
        setStats(s);
        setChatbots(c);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleToggle = async (chatbot) => {
    try {
      await api.updateChatbot(chatbot.chatbot_id, { is_active: !chatbot.is_active });
      setChatbots(prev => prev.map(c => c.chatbot_id === chatbot.chatbot_id ? { ...c, is_active: !c.is_active } : c));
    } catch {}
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure?')) return;
    try {
      await api.deleteChatbot(id);
      setChatbots(prev => prev.filter(c => c.chatbot_id !== id));
    } catch {}
  };

  const handleResendVerification = async () => {
    if (!user?.email) return;
    setVerifyLoading(true);
    try {
      const data = await api.resendVerification(user.email);
      if (data.mock_token) setVerifyToken(data.mock_token);
    } catch {}
    setVerifyLoading(false);
  };

  const handleQuickVerify = async () => {
    if (!verifyToken) return;
    setVerifyLoading(true);
    try {
      await api.verifyEmail(verifyToken);
      setVerified(true);
      setVerifyToken('');
      checkAuth();
    } catch {}
    setVerifyLoading(false);
  };

  if (loading) {
    return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;
  }

  const usagePercent = stats ? Math.round((stats.messages_this_month / stats.message_limit) * 100) : 0;

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="dashboard-page">
        {/* Email Verification Banner */}
        {user && !user.email_verified && !verified && (
          <div className="border-2 border-[#002FA7] bg-[#002FA7]/5 p-5 flex items-center justify-between" data-testid="verify-email-banner">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-[#002FA7] flex items-center justify-center flex-shrink-0"><Mail size={20} className="text-white" /></div>
              <div>
                <p className="font-bold text-sm text-[#0A0A0A]">{t.auth.verify_banner}</p>
                <p className="text-xs text-[#4B5563]">Check your inbox or use the button to verify.</p>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              {verifyToken ? (
                <Button onClick={handleQuickVerify} disabled={verifyLoading} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-4 py-2 text-xs font-bold" data-testid="quick-verify-btn">
                  {verifyLoading ? '...' : t.auth.verify_btn}
                </Button>
              ) : (
                <Button onClick={handleResendVerification} disabled={verifyLoading} variant="outline" className="rounded-none border-[#002FA7] text-[#002FA7] px-4 py-2 text-xs font-bold" data-testid="resend-verify-btn">
                  {verifyLoading ? '...' : t.auth.verify_resend}
                </Button>
              )}
            </div>
          </div>
        )}
        {verified && (
          <div className="border border-green-300 bg-green-50 p-4 flex items-center gap-3" data-testid="verify-success-banner">
            <CheckCircle size={20} className="text-green-600" />
            <p className="text-sm font-bold text-green-700">{t.auth.verify_success}</p>
          </div>
        )}

        {/* Welcome */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]" data-testid="dashboard-greeting">
              {greeting()}, {user?.full_name || user?.email}
            </h1>
            <p className="text-[#4B5563] mt-1">Plan: <span className="font-bold uppercase text-[#002FA7]">{stats?.plan || 'free'}</span></p>
          </div>
          <Link to="/dashboard/new">
            <Button className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-6 py-3 font-bold" data-testid="new-chatbot-btn">
              <Plus size={18} className="mr-2" />
              {t.dashboard.newChatbot}
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border border-gray-200" data-testid="stats-grid">
          {[
            { icon: Bot, label: t.dashboard.stats.chatbots, value: stats?.total_chatbots || 0, sub: `/ ${stats?.chatbot_limit}` },
            { icon: MessageSquare, label: t.dashboard.stats.messages, value: stats?.messages_this_month || 0, sub: `/ ${stats?.message_limit}` },
            { icon: Activity, label: t.dashboard.stats.sessions, value: stats?.active_sessions || 0, sub: '' },
            { icon: Globe, label: t.dashboard.stats.languages, value: '15', sub: '' },
          ].map((stat, i) => (
            <div key={i} className="p-6 bg-white border border-gray-200" data-testid={`stat-${i}`}>
              <div className="flex items-center gap-3 mb-2">
                <stat.icon size={18} className="text-[#002FA7]" />
                <span className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563]">{stat.label}</span>
              </div>
              <p className="text-2xl font-black text-[#0A0A0A]">{stat.value}<span className="text-sm font-normal text-[#4B5563] ml-1">{stat.sub}</span></p>
            </div>
          ))}
        </div>

        {/* Usage bar */}
        {usagePercent > 70 && (
          <div className={`border p-4 ${usagePercent >= 95 ? 'border-red-400 bg-red-50' : 'border-yellow-400 bg-yellow-50'}`} data-testid="usage-warning">
            <p className="text-sm font-bold">{usagePercent}% of monthly messages used. <Link to="/pricing" className="text-[#002FA7] underline">Upgrade plan</Link></p>
          </div>
        )}

        {/* Chatbot cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border border-gray-200" data-testid="chatbot-grid">
          {chatbots.map(bot => {
            const msgPercent = stats ? Math.round((bot.message_count / stats.message_limit) * 100) : 0;
            return (
              <div key={bot.chatbot_id} className="p-6 bg-white border border-gray-200 flex flex-col" data-testid={`chatbot-card-${bot.chatbot_id}`}>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-bold text-[#0A0A0A]">{bot.business_name}</h3>
                    <p className="text-xs text-[#4B5563] uppercase tracking-wider">{bot.primary_language}</p>
                  </div>
                  <Switch checked={bot.is_active} onCheckedChange={() => handleToggle(bot)} data-testid={`toggle-${bot.chatbot_id}`} />
                </div>
                <div className="mb-4">
                  <div className="flex items-center justify-between text-xs text-[#4B5563] mb-1">
                    <span>{bot.message_count} messages</span>
                    <Badge variant={bot.is_active ? 'default' : 'secondary'} className="text-xs rounded-none">
                      {bot.is_active ? t.dashboard.active : t.dashboard.inactive}
                    </Badge>
                  </div>
                  <Progress value={Math.min(msgPercent, 100)} className={`h-1.5 rounded-none ${msgPercent >= 95 ? '[&>div]:bg-red-500' : msgPercent >= 80 ? '[&>div]:bg-yellow-500' : '[&>div]:bg-[#002FA7]'}`} />
                </div>
                <div className="flex items-center gap-2 mt-auto pt-4 border-t border-gray-100">
                  <Link to={`/dashboard/chatbot/${bot.chatbot_id}`}>
                    <Button variant="outline" size="sm" className="rounded-none text-xs" data-testid={`edit-${bot.chatbot_id}`}><Edit size={12} className="mr-1" />{t.dashboard.edit}</Button>
                  </Link>
                  <Link to={`/dashboard/chatbot/${bot.chatbot_id}?tab=embed`}>
                    <Button variant="outline" size="sm" className="rounded-none text-xs"><Code size={12} className="mr-1" />{t.dashboard.embed}</Button>
                  </Link>
                  <Button variant="outline" size="sm" className="rounded-none text-xs ml-auto text-red-500 hover:text-red-700 hover:bg-red-50" onClick={() => handleDelete(bot.chatbot_id)} data-testid={`delete-${bot.chatbot_id}`}>
                    <Trash2 size={12} />
                  </Button>
                </div>
              </div>
            );
          })}
          {chatbots.length === 0 && (
            <div className="col-span-full p-12 text-center" data-testid="empty-chatbots">
              <Bot size={48} className="text-gray-300 mx-auto mb-4" />
              <p className="text-[#4B5563] mb-4">No chatbots yet.</p>
              <Link to="/dashboard/new">
                <Button className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none" data-testid="create-first-btn">{t.dashboard.newChatbot}</Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
