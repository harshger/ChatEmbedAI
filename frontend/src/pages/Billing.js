import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { CreditCard, FileText } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

const PLAN_NAMES = { free: 'Free', starter: 'Starter', pro: 'Pro', agency: 'Agentur' };

export default function Billing() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [billing, setBilling] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    const load = async () => {
      if (sessionId) {
        // Poll payment status
        for (let i = 0; i < 5; i++) {
          try {
            const status = await api.checkPaymentStatus(sessionId);
            if (status.payment_status === 'paid') break;
          } catch {}
          await new Promise(r => setTimeout(r, 2000));
        }
      }
      try {
        const data = await api.getBilling();
        setBilling(data);
      } catch {}
      setLoading(false);
    };
    load();
  }, [searchParams]);

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="billing-page">
        <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">Abonnement & Rechnungen</h1>

        <div className="border border-gray-200 bg-white p-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-1">Current Plan</p>
              <h2 className="font-clash text-2xl font-bold text-[#0A0A0A]">{PLAN_NAMES[billing?.plan || user?.plan || 'free']}</h2>
            </div>
            <Badge className="rounded-none bg-[#002FA7] text-white text-xs uppercase">{billing?.plan || 'free'}</Badge>
          </div>
          {billing?.subscription && (
            <div className="text-sm text-[#4B5563] space-y-1">
              <p>Messages used: {billing.subscription.messages_used_this_month}</p>
            </div>
          )}
        </div>

        {billing?.transactions?.length > 0 && (
          <div className="border border-gray-200 bg-white">
            <div className="p-6 border-b border-gray-200">
              <h2 className="font-clash text-xl font-bold text-[#0A0A0A]">Rechnungen</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {billing.transactions.map((tx, i) => (
                <div key={i} className="p-6 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <FileText size={18} className="text-[#4B5563]" />
                    <div>
                      <p className="font-bold text-sm text-[#0A0A0A]">{tx.plan} Plan</p>
                      <p className="text-xs text-[#4B5563]">{tx.created_at?.slice(0, 10)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-sm">€{tx.amount}</p>
                    <Badge variant={tx.payment_status === 'paid' ? 'default' : 'secondary'} className="text-xs rounded-none">{tx.payment_status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
