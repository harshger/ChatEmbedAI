import React, { useEffect, useState } from 'react';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { BarChart3, Lock } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

export default function Analytics() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getAnalytics()
      .then(d => { setData(d); setLoading(false); })
      .catch(() => { setError('Analytics requires Pro plan or higher.'); setLoading(false); });
  }, []);

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 text-center" data-testid="analytics-locked">
          <Lock size={48} className="text-gray-300 mb-4" />
          <h2 className="font-clash text-xl font-bold text-[#0A0A0A] mb-2">Analytics (Pro+)</h2>
          <p className="text-[#4B5563]">{error}</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="analytics-page">
        <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">Statistiken</h1>
        <p className="text-xs text-[#4B5563] italic">Alle Daten werden anonymisiert gespeichert gemäß DSGVO</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0 border border-gray-200">
          <div className="p-8 bg-white border border-gray-200">
            <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-4">Total Messages</h3>
            <p className="text-4xl font-black text-[#0A0A0A]">{data?.total_messages || 0}</p>
          </div>
          <div className="p-8 bg-white border border-gray-200">
            <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-4">Total Chatbots</h3>
            <p className="text-4xl font-black text-[#0A0A0A]">{data?.total_chatbots || 0}</p>
          </div>
        </div>

        {data?.messages_per_day?.length > 0 && (
          <div className="border border-gray-200 bg-white p-8">
            <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-6">Messages per Day (Last 30 Days)</h3>
            <div className="flex items-end gap-1 h-48">
              {data.messages_per_day.slice(-30).map((d, i) => (
                <div key={i} className="flex-1 bg-[#002FA7] rounded-t-sm" style={{ height: `${Math.max(4, (d.count / Math.max(...data.messages_per_day.map(x => x.count))) * 100)}%` }} title={`${d.date}: ${d.count}`} />
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
