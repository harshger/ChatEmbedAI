import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { CreditCard, FileText, ArrowUpRight, Check, Download, AlertTriangle, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

const PLAN_ORDER = ['free', 'starter', 'pro', 'growth', 'agency'];
const PLAN_PRICES = { free: 0, starter: 29, pro: 79, growth: 99, agency: 199 };

export default function Billing() {
  const { t } = useTranslation();
  const { user, checkAuth } = useAuth();
  const [billing, setBilling] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState('');
  const [downloadingPdf, setDownloadingPdf] = useState('');
  const [searchParams] = useSearchParams();

  // Cancel state
  const [showCancel, setShowCancel] = useState(false);
  const [cancelPreview, setCancelPreview] = useState(null);
  const [cancelling, setCancelling] = useState(false);
  const [cancelResult, setCancelResult] = useState(null);
  const [reverting, setReverting] = useState(false);
  const [serviceConsent, setServiceConsent] = useState(false);

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
      if (!window.confirm(t.billing.confirm_downgrade)) return;
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

  const handleShowCancel = async () => {
    setShowCancel(true);
    try {
      const preview = await api.getCancelPreview();
      setCancelPreview(preview);
    } catch {}
  };

  const handleCancel = async () => {
    setCancelling(true);
    try {
      const result = await api.cancelPlan({ service_consent: serviceConsent });
      setCancelResult(result);
      const data = await api.getBilling();
      setBilling(data);
    } catch (err) {
      const d = await err.json?.().catch(() => null);
      alert(d?.detail || 'Fehler bei der Kündigung');
    }
    setCancelling(false);
  };

  const handleRevert = async () => {
    setReverting(true);
    try {
      await api.revertCancel();
      setCancelResult(null);
      setCancelPreview(null);
      setShowCancel(false);
      const data = await api.getBilling();
      setBilling(data);
    } catch (err) {
      const d = await err.json?.().catch(() => null);
      alert(d?.detail || 'Fehler');
    }
    setReverting(false);
  };

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  const currentPlan = billing?.plan || user?.plan || 'free';
  const currentIndex = PLAN_ORDER.indexOf(currentPlan);

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="billing-page">
        <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">{t.billing.title}</h1>

        {/* Active Cancellation Banner */}
        {cancelResult && (
          <div className="border-2 border-yellow-400 bg-yellow-50 p-6" data-testid="cancel-banner">
            <div className="flex items-start gap-3">
              <AlertTriangle size={20} className="text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-bold text-sm text-[#0A0A0A] mb-1">Kündigung eingereicht</h3>
                <p className="text-xs text-[#4B5563] mb-1">{cancelResult.message}</p>
                {cancelResult.effective_date && (
                  <p className="text-xs text-[#4B5563]">Aktiv bis: {cancelResult.effective_date.slice(0, 10)}</p>
                )}
                <Button onClick={handleRevert} disabled={reverting} variant="outline" className="mt-3 rounded-none border-yellow-600 text-yellow-700 font-bold text-xs gap-1.5" data-testid="revert-cancel-btn">
                  <RotateCcw size={12} />
                  {reverting ? '...' : 'Kündigung widerrufen — Plan behalten'}
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Current Plan Card */}
        <div className="border border-gray-200 bg-white p-8" data-testid="current-plan-card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-1">{t.billing.current_plan}</p>
              <h2 className="font-clash text-2xl font-bold text-[#0A0A0A]">{t.billing.plan_names[currentPlan] || currentPlan}</h2>
            </div>
            <Badge className="rounded-none bg-[#002FA7] text-white text-xs uppercase" data-testid="current-plan-badge">{currentPlan}</Badge>
          </div>
          {billing?.subscription && (
            <div className="text-sm text-[#4B5563] space-y-1">
              <p>{t.billing.messages_used}: <strong>{billing.subscription.messages_used_this_month}</strong></p>
            </div>
          )}
        </div>

        {/* Plan Selection */}
        <div>
          <h2 className="font-clash text-xl font-bold text-[#0A0A0A] mb-4">{t.billing.change_plan}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0 border border-gray-200">
            {PLAN_ORDER.map((planId, idx) => {
              const isCurrent = planId === currentPlan;
              const isUpgrade = idx > currentIndex;
              const isDowngrade = idx < currentIndex;
              const features = t.billing.features[planId] || [];
              return (
                <div key={planId} className={`p-6 bg-white border border-gray-200 flex flex-col ${isCurrent ? 'ring-2 ring-[#002FA7] ring-inset' : ''}`} data-testid={`billing-plan-${planId}`}>
                  <h3 className="font-clash text-lg font-bold text-[#0A0A0A] mb-1">{t.billing.plan_names[planId] || planId}</h3>
                  <p className="text-2xl font-black text-[#0A0A0A] mb-4">
                    {PLAN_PRICES[planId] > 0 ? `${PLAN_PRICES[planId]} EUR` : '0 EUR'}
                    {PLAN_PRICES[planId] > 0 && <span className="text-xs font-normal text-[#4B5563]"> /Mo</span>}
                  </p>
                  <div className="space-y-2 mb-6 flex-1">
                    {features.map((f, i) => (
                      <p key={i} className="flex items-center gap-2 text-xs text-[#4B5563]">
                        <Check size={12} className="text-green-600 flex-shrink-0" />{f}
                      </p>
                    ))}
                  </div>
                  <div>
                    {isCurrent ? (
                      <Button disabled className="w-full rounded-none py-2 text-xs font-bold" data-testid={`plan-${planId}-current`}>{t.billing.current}</Button>
                    ) : isUpgrade ? (
                      <Button onClick={() => handleChangePlan(planId)} disabled={upgrading === planId} className="w-full rounded-none py-2 text-xs font-bold bg-[#002FA7] text-white hover:bg-[#0040D6]" data-testid={`plan-${planId}-upgrade`}>
                        {upgrading === planId ? '...' : <><ArrowUpRight size={12} className="mr-1" />{t.billing.upgrade}</>}
                      </Button>
                    ) : isDowngrade ? (
                      <Button onClick={() => handleChangePlan(planId)} disabled={upgrading === planId} variant="outline" className="w-full rounded-none py-2 text-xs font-bold border-gray-300" data-testid={`plan-${planId}-downgrade`}>
                        {upgrading === planId ? '...' : t.billing.downgrade}
                      </Button>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Transaction History */}
        {billing?.transactions?.length > 0 && (
          <div className="border border-gray-200 bg-white" data-testid="payment-history">
            <div className="p-6 border-b border-gray-200">
              <h2 className="font-clash text-xl font-bold text-[#0A0A0A]">{t.billing.invoices}</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {billing.transactions.map((tx, i) => (
                <div key={i} className="p-6 flex items-center justify-between" data-testid={`transaction-${i}`}>
                  <div className="flex items-center gap-4">
                    <FileText size={18} className="text-[#4B5563]" />
                    <div>
                      <p className="font-bold text-sm text-[#0A0A0A]">
                        {tx.amount < 0 ? 'Erstattung' : `${t.billing.plan_names[tx.plan] || tx.plan} Plan`}
                      </p>
                      <p className="text-xs text-[#4B5563]">{tx.created_at?.slice(0, 10)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className={`font-bold text-sm ${tx.amount < 0 ? 'text-green-600' : ''}`}>
                        {tx.amount < 0 ? `+${Math.abs(tx.amount)} EUR` : tx.amount > 0 ? `${tx.amount} EUR` : 'Free'}
                      </p>
                      <Badge variant={tx.payment_status === 'paid' ? 'default' : tx.payment_status === 'refunded' ? 'secondary' : 'secondary'} className="text-xs rounded-none">{tx.payment_status}</Badge>
                    </div>
                    {tx.payment_status === 'paid' && tx.transaction_id && tx.amount > 0 && (
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

        {/* Hidden Cancel Section — only for paid plans */}
        {currentPlan !== 'free' && !cancelResult && (
          <div className="pt-8 border-t border-gray-100">
            <button
              onClick={() => showCancel ? setShowCancel(false) : handleShowCancel()}
              className="text-xs text-[#9CA3AF] hover:text-[#4B5563] flex items-center gap-1"
              data-testid="show-cancel-btn"
            >
              {showCancel ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              Plan kündigen
            </button>

            {showCancel && cancelPreview && (
              <div className="mt-4 border border-gray-200 bg-[#FAFAFA] p-6 max-w-lg" data-testid="cancel-section">
                {cancelPreview.already_cancelled ? (
                  <div>
                    <p className="text-sm text-[#4B5563] mb-3">Sie haben bereits gekündigt.</p>
                    <Button onClick={handleRevert} disabled={reverting} variant="outline" className="rounded-none border-gray-300 font-bold text-xs gap-1.5" data-testid="revert-cancel-btn-2">
                      <RotateCcw size={12} />
                      {reverting ? '...' : 'Kündigung widerrufen'}
                    </Button>
                  </div>
                ) : (
                  <>
                    <h3 className="font-bold text-sm text-[#0A0A0A] mb-3">Plan kündigen</h3>

                    {/* Usage summary */}
                    <div className="space-y-2 mb-4 text-xs text-[#4B5563]">
                      <p>Aktueller Plan: <strong>{t.billing.plan_names[cancelPreview.plan]}</strong> ({cancelPreview.price} EUR/Mo)</p>
                      <p>Genutzte Analysen: <strong>{cancelPreview.usage_count}</strong></p>
                      {cancelPreview.within_14_days && (
                        <div className="bg-green-50 border border-green-200 p-3 mt-2">
                          <p className="font-bold text-green-700">14-Tage Widerrufsrecht (EU)</p>
                          <p className="text-green-600 mt-1">
                            Erstattung: <strong>{cancelPreview.refund_amount} EUR</strong> ({cancelPreview.refund_percent}% anteilig basierend auf Nutzung)
                          </p>
                        </div>
                      )}
                      {!cancelPreview.within_14_days && (
                        <p className="text-[#9CA3AF]">14-Tage-Frist abgelaufen. Keine Erstattung möglich.</p>
                      )}
                    </div>

                    {/* Service consent (EU requirement) */}
                    <label className="flex items-start gap-2 text-xs text-[#4B5563] mb-4 cursor-pointer">
                      <input type="checkbox" checked={serviceConsent} onChange={e => setServiceConsent(e.target.checked)} className="mt-0.5" data-testid="cancel-consent" />
                      Ich bestätige, dass die Leistung sofort begonnen hat und dass bei teilweiser Nutzung ein anteiliger Betrag berechnet wird.
                    </label>

                    <div className="flex gap-3">
                      <Button onClick={handleCancel} disabled={cancelling} variant="outline" className="rounded-none border-red-300 text-red-600 font-bold text-xs" data-testid="confirm-cancel-btn">
                        {cancelling ? '...' : 'Endgültig kündigen'}
                      </Button>
                      <Button onClick={() => setShowCancel(false)} variant="outline" className="rounded-none border-gray-300 font-bold text-xs" data-testid="keep-plan-btn">
                        Plan behalten
                      </Button>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
