import React, { useEffect, useState } from 'react';
import { useAuth } from '../lib/auth';
import { useTranslation } from '../lib/i18n';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { BarChart3, Lock, MessageSquare, Globe, Clock, HelpCircle, Download, ThumbsUp, ThumbsDown, AlertCircle } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const CHART_COLORS = ['#002FA7', '#0040D6', '#4B5563', '#9CA3AF', '#E5E7EB', '#0A0A0A'];

export default function Analytics() {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    api.getAnalytics()
      .then(d => { setData(d); setLoading(false); })
      .catch(() => { setError(t.analytics_page.locked_desc); setLoading(false); });
  }, [t]);

  const handleExportCsv = async () => {
    setExporting(true);
    try {
      const csv = await api.exportAnalyticsCsv();
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export error:', err);
    }
    setExporting(false);
  };

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 text-center" data-testid="analytics-locked">
          <Lock size={48} className="text-gray-300 mb-4" />
          <h2 className="font-clash text-xl font-bold text-[#0A0A0A] mb-2">{t.analytics_page.locked_title}</h2>
          <p className="text-[#4B5563]">{error}</p>
        </div>
      </DashboardLayout>
    );
  }

  const hasMessages = data?.messages_per_day?.length > 0;
  const hasLanguages = data?.language_distribution?.length > 0;
  const hasQuestions = data?.top_questions?.length > 0;
  const hasPeakHours = data?.peak_hours?.some(h => h.count > 0);
  const hasUnanswered = data?.unanswered_questions?.length > 0;
  const sat = data?.satisfaction || {};

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="analytics-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">{t.analytics_page.title}</h1>
            <p className="text-xs text-[#4B5563] italic mt-1">{t.analytics_page.gdpr_note}</p>
          </div>
          <Button onClick={handleExportCsv} disabled={exporting} variant="outline" className="rounded-none border-gray-300 font-bold text-xs gap-1" data-testid="analytics-export-csv-btn">
            <Download size={14} />
            {exporting ? '...' : t.analytics_page.export_csv}
          </Button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-0 border border-gray-200">
          <div className="p-6 bg-white border border-gray-200" data-testid="stat-total-messages">
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare size={16} className="text-[#002FA7]" />
              <span className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563]">{t.analytics_page.total_messages}</span>
            </div>
            <p className="text-3xl font-black text-[#0A0A0A]">{data?.total_messages || 0}</p>
          </div>
          <div className="p-6 bg-white border border-gray-200" data-testid="stat-total-chatbots">
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 size={16} className="text-[#002FA7]" />
              <span className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563]">{t.analytics_page.total_chatbots}</span>
            </div>
            <p className="text-3xl font-black text-[#0A0A0A]">{data?.total_chatbots || 0}</p>
          </div>
          <div className="p-6 bg-white border border-gray-200" data-testid="stat-languages">
            <div className="flex items-center gap-2 mb-3">
              <Globe size={16} className="text-[#002FA7]" />
              <span className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563]">{t.analytics_page.languages}</span>
            </div>
            <p className="text-3xl font-black text-[#0A0A0A]">{data?.language_distribution?.length || 0}</p>
          </div>
          <div className="p-6 bg-white border border-gray-200" data-testid="stat-satisfaction">
            <div className="flex items-center gap-2 mb-3">
              <ThumbsUp size={16} className="text-[#002FA7]" />
              <span className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563]">{t.analytics_page.satisfaction}</span>
            </div>
            <p className="text-3xl font-black text-[#0A0A0A]">{sat.total_ratings > 0 ? `${sat.avg_score}%` : '—'}</p>
            {sat.total_ratings > 0 && (
              <p className="text-xs text-[#4B5563] mt-1">{sat.positive} {t.analytics_page.positive} / {sat.negative} {t.analytics_page.negative}</p>
            )}
          </div>
        </div>

        {/* Messages Per Day Chart */}
        <div className="border border-gray-200 bg-white p-8" data-testid="messages-per-day-chart">
          <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-6">{t.analytics_page.messages_per_day}</h3>
          {hasMessages ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.messages_per_day.slice(-30)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#4B5563' }} tickFormatter={v => v.slice(5)} />
                <YAxis tick={{ fontSize: 11, fill: '#4B5563' }} allowDecimals={false} />
                <Tooltip contentStyle={{ border: '1px solid #E5E7EB', borderRadius: 0, fontSize: 12 }} />
                <Bar dataKey="count" fill="#002FA7" name={t.dashboard.stats.messages} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-[#4B5563] text-sm">{t.analytics_page.no_messages}</div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">
          {/* Language Distribution Pie Chart */}
          <div className="border border-gray-200 bg-white p-8" data-testid="language-distribution-chart">
            <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-6">{t.analytics_page.language_distribution}</h3>
            {hasLanguages ? (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={data.language_distribution} dataKey="count" nameKey="language" cx="50%" cy="50%" outerRadius={100} label={({ language, percent }) => `${language} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                    {data.language_distribution.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ border: '1px solid #E5E7EB', borderRadius: 0, fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-48 text-[#4B5563] text-sm">{t.analytics_page.no_languages}</div>
            )}
          </div>

          {/* Peak Hours */}
          <div className="border border-gray-200 bg-white p-8" data-testid="peak-hours-chart">
            <div className="flex items-center gap-2 mb-6">
              <Clock size={16} className="text-[#002FA7]" />
              <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563]">{t.analytics_page.peak_hours}</h3>
            </div>
            {hasPeakHours ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data.peak_hours}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="hour" tick={{ fontSize: 11, fill: '#4B5563' }} tickFormatter={v => `${v}:00`} />
                  <YAxis tick={{ fontSize: 11, fill: '#4B5563' }} allowDecimals={false} />
                  <Tooltip contentStyle={{ border: '1px solid #E5E7EB', borderRadius: 0, fontSize: 12 }} labelFormatter={v => `${v}:00 UTC`} />
                  <Bar dataKey="count" fill="#0A0A0A" name={t.dashboard.stats.messages} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-48 text-[#4B5563] text-sm">{t.analytics_page.no_peak}</div>
            )}
          </div>
        </div>

        {/* Top 10 Questions */}
        <div className="border border-gray-200 bg-white p-8" data-testid="top-questions-table">
          <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-6">{t.analytics_page.top_questions}</h3>
          {hasQuestions ? (
            <div className="space-y-0">
              {data.top_questions.map((q, i) => (
                <div key={i} className="flex items-center gap-4 py-3 border-b border-gray-100 last:border-0">
                  <span className="text-xs font-bold text-[#4B5563] w-6">{i + 1}.</span>
                  <span className="flex-1 text-sm text-[#0A0A0A] truncate">{q.question}</span>
                  <span className="text-xs font-bold text-[#002FA7] bg-[#F9FAFB] px-3 py-1">{q.count}x</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-[#4B5563] text-sm">{t.analytics_page.no_questions}</div>
          )}
        </div>

        {/* Unanswered Questions */}
        <div className="border border-gray-200 bg-white p-8" data-testid="unanswered-questions-table">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle size={16} className="text-yellow-600" />
            <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563]">{t.analytics_page.unanswered}</h3>
          </div>
          <p className="text-xs text-[#4B5563] mb-6">{t.analytics_page.unanswered_desc}</p>
          {hasUnanswered ? (
            <div className="space-y-0">
              {data.unanswered_questions.slice(0, 15).map((uq, i) => (
                <div key={i} className="flex items-center gap-4 py-3 border-b border-gray-100 last:border-0">
                  <span className="text-xs font-bold text-yellow-600 w-6">{i + 1}.</span>
                  <span className="flex-1 text-sm text-[#0A0A0A] truncate">{uq.question}</span>
                  <span className="text-xs text-[#4B5563]">{uq.created_at?.slice(0, 10)}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-24 text-[#4B5563] text-sm">{t.analytics_page.no_unanswered}</div>
          )}
        </div>

        {/* Per-Chatbot Stats */}
        {data?.chatbot_stats?.length > 0 && (
          <div className="border border-gray-200 bg-white p-8" data-testid="chatbot-stats-table">
            <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-6">{t.analytics_page.chatbot_performance}</h3>
            <div className="space-y-0">
              {data.chatbot_stats.map((bot, i) => (
                <div key={i} className="flex items-center gap-4 py-3 border-b border-gray-100 last:border-0">
                  <span className="flex-1 text-sm font-bold text-[#0A0A0A]">{bot.business_name}</span>
                  <span className="text-xs text-[#4B5563]">{bot.user_messages} {t.analytics_page.user_msgs}</span>
                  <span className="text-xs font-bold text-[#002FA7] bg-[#F9FAFB] px-3 py-1">{bot.total_messages} {t.analytics_page.total}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
