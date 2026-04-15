import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { CreditCard, FileText, ArrowUpRight, Check, Download } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

const PLAN_NAMES = { free: 'Free', starter: 'Starter', pro: 'Pro', agency: 'Agentur' };
const PLAN_ORDER = ['free', 'starter', 'pro', 'agency'];
const PLAN_PRICES = { free: 0, starter: 29, pro: 79, agency: 199 };
const PLAN_FEATURES = {
  free: ['1 Chatbot', '500 Messages/month', 'ChatEmbed Branding'],
  starter: ['3 Chatbots', '2,000 Messages/month', 'Remove Branding', 'Email Support'],
  pro: ['10 Chatbots', '10,000 Messages/month', 'White-label', 'Analytics', 'Priority Support'],
  agency: ['Unlimited Chatbots', 'Unlimited Messages', 'Sub-Accounts', 'Dedicated Onboarding', 'SLA'],
};

export default function Billing() {
  const { t } = useTranslation();
  const { user, checkAuth } = useAuth();
  const [billing, setBilling] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState('');
  const [downloadingPdf, setDownloadingPdf] = useState('');
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    const load = async () => {
      if (sessionId) {
        for (let i = 0; i < 5; i++) {
          try {
            const status = await api.checkPaymentStatus(sessionId);
            if (status.payment_status === 'paid') { checkAuth(); break; }
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
  }, [searchParams, checkAuth]);

  const handleChangePlan = async (planId) => {
    if (planId === 'free') {
      if (!window.confirm('Are you sure you want to downgrade to the Free plan?')) return;
      setUpgrading(planId);
      try {
        await api.changePlan({ plan: 'free' });
        checkAuth();
        const data = await api.getBilling();
        setBilling(data);
      } catch {}
      setUpgrading('');
      return;
    }
    setUpgrading(planId);
    try {
      const data = await api.changePlan({ plan: planId, origin_url: window.location.origin });
      if (data.url) window.location.href = data.url;
    } catch (err) {
      console.error('Plan change error:', err);
    }
    setUpgrading('');
  };

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  const currentPlan = billing?.plan || user?.plan || 'free';
  const currentIndex = PLAN_ORDER.indexOf(currentPlan);

  const handleDownloadInvoice = async (transactionId) => {
    setDownloadingPdf(transactionId);
    try {
      const blob = await api.downloadInvoicePdf(transactionId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Rechnung-${transactionId.slice(0, 8).toUpperCase()}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF download error:', err);
    }
    setDownloadingPdf('');
  };

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="billing-page">
        <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">Abonnement & Rechnungen</h1>

        {/* Current Plan Card */}
        <div className="border border-gray-200 bg-white p-8" data-testid="current-plan-card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-1">Current Plan</p>
              <h2 className="font-clash text-2xl font-bold text-[#0A0A0A]">{PLAN_NAMES[currentPlan]}</h2>
            </div>
            <Badge className="rounded-none bg-[#002FA7] text-white text-xs uppercase" data-testid="current-plan-badge">{currentPlan}</Badge>
          </div>
          {billing?.subscription && (
            <div className="text-sm text-[#4B5563] space-y-1">
              <p>Messages used this month: <strong>{billing.subscription.messages_used_this_month}</strong></p>
            </div>
          )}
        </div>

        {/* Plan Comparison */}
        <div>
          <h2 className="font-clash text-xl font-bold text-[#0A0A0A] mb-4">Change Plan</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0 border border-gray-200">
            {PLAN_ORDER.map((planId, idx) => {
              const isCurrent = planId === currentPlan;
              const isUpgrade = idx > currentIndex;
              const isDowngrade = idx < currentIndex;
              return (
                <div key={planId} className={`p-6 bg-white border border-gray-200 flex flex-col ${isCurrent ? 'ring-2 ring-[#002FA7] ring-inset' : ''}`} data-testid={`billing-plan-${planId}`}>
                  <h3 className="font-clash text-lg font-bold text-[#0A0A0A] mb-1">{PLAN_NAMES[planId]}</h3>
                  <p className="text-2xl font-black text-[#0A0A0A] mb-4">
                    {PLAN_PRICES[planId] > 0 ? `€${PLAN_PRICES[planId]}` : '€0'}
                    {PLAN_PRICES[planId] > 0 && <span className="text-xs font-normal text-[#4B5563]"> /mo</span>}
                  </p>
                  <div className="space-y-2 mb-6 flex-1">
                    {PLAN_FEATURES[planId].map((f, i) => (
                      <p key={i} className="flex items-center gap-2 text-xs text-[#4B5563]">
                        <Check size={12} className="text-green-600 flex-shrink-0" />{f}
                      </p>
                    ))}
                  </div>
                  <div>
                    {isCurrent ? (
                      <Button disabled className="w-full rounded-none py-2 text-xs font-bold" data-testid={`plan-${planId}-current`}>Current Plan</Button>
                    ) : isUpgrade ? (
                      <Button onClick={() => handleChangePlan(planId)} disabled={upgrading === planId} className="w-full rounded-none py-2 text-xs font-bold bg-[#002FA7] text-white hover:bg-[#0040D6]" data-testid={`plan-${planId}-upgrade`}>
                        {upgrading === planId ? '...' : <><ArrowUpRight size={12} className="mr-1" />Upgrade</>}
                      </Button>
                    ) : isDowngrade ? (
                      <Button onClick={() => handleChangePlan(planId)} disabled={upgrading === planId} variant="outline" className="w-full rounded-none py-2 text-xs font-bold border-gray-300" data-testid={`plan-${planId}-downgrade`}>
                        {upgrading === planId ? '...' : 'Downgrade'}
                      </Button>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Payment History */}
        {billing?.transactions?.length > 0 && (
          <div className="border border-gray-200 bg-white" data-testid="payment-history">
            <div className="p-6 border-b border-gray-200">
              <h2 className="font-clash text-xl font-bold text-[#0A0A0A]">Rechnungen</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {billing.transactions.map((tx, i) => (
                <div key={i} className="p-6 flex items-center justify-between" data-testid={`transaction-${i}`}>
                  <div className="flex items-center gap-4">
                    <FileText size={18} className="text-[#4B5563]" />
                    <div>
                      <p className="font-bold text-sm text-[#0A0A0A]">{tx.plan} Plan</p>
                      <p className="text-xs text-[#4B5563]">{tx.created_at?.slice(0, 10)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-bold text-sm">{tx.amount > 0 ? `€${tx.amount}` : 'Free'}</p>
                      <Badge variant={tx.payment_status === 'paid' ? 'default' : 'secondary'} className="text-xs rounded-none">{tx.payment_status}</Badge>
                    </div>
                    {tx.payment_status === 'paid' && tx.transaction_id && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownloadInvoice(tx.transaction_id)}
                        disabled={downloadingPdf === tx.transaction_id}
                        className="rounded-none border-gray-300 text-xs font-bold gap-1"
                        data-testid={`download-invoice-${i}`}
                      >
                        <Download size={12} />
                        {downloadingPdf === tx.transaction_id ? '...' : 'PDF'}
                      </Button>
                    )}
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
