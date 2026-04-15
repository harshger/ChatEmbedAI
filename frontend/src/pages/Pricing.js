import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Check } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const PLANS = [
  { id: 'free', chatbots: '1', messages: '500', features: ['ChatEmbed Branding', 'DSGVO-Hinweis Widget'] },
  { id: 'starter', chatbots: '3', messages: '2.000', features: ['Remove Branding', 'Email Support'], monthly: 29, yearly: 290 },
  { id: 'pro', chatbots: '10', messages: '10.000', features: ['White-label', 'Analytics Dashboard', 'AVV Download', 'Priority Support'], monthly: 79, yearly: 790, highlighted: true },
  { id: 'agency', chatbots: 'Unlimited', messages: 'Unlimited', features: ['White-label', 'Sub-Accounts', 'Dedicated Onboarding', 'SLA Guarantee'], monthly: 199, yearly: 1990 },
];

const PLAN_NAMES = { free: 'Free', starter: 'Starter', pro: 'Pro', agency: 'Agentur' };

export default function Pricing() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [billing, setBilling] = useState('monthly');
  const [loading, setLoading] = useState('');

  const handleUpgrade = async (planId) => {
    if (!user) { navigate('/signup'); return; }
    if (planId === 'free') return;
    setLoading(planId);
    try {
      const data = await api.createCheckout({ plan: planId, origin_url: window.location.origin });
      if (data.url) window.location.href = data.url;
    } catch (err) {
      console.error('Checkout error:', err);
    } finally {
      setLoading('');
    }
  };

  return (
    <div className="min-h-screen bg-white" data-testid="pricing-page">
      <Header />
      <div className="max-w-7xl mx-auto px-6 md:px-12 pt-32 pb-24">
        <div className="text-center mb-16">
          <h1 className="font-clash text-5xl lg:text-6xl font-black tracking-tighter text-[#0A0A0A] mb-4" data-testid="pricing-title">{t.pricing.title}</h1>
          <p className="text-[#4B5563] mb-8">{t.pricing.subtitle}</p>
          <div className="inline-flex border border-gray-200">
            <button onClick={() => setBilling('monthly')} className={`px-6 py-2 text-sm font-bold ${billing === 'monthly' ? 'bg-[#002FA7] text-white' : 'bg-white text-[#0A0A0A]'}`} data-testid="billing-monthly">{t.pricing.monthly}</button>
            <button onClick={() => setBilling('yearly')} className={`px-6 py-2 text-sm font-bold ${billing === 'yearly' ? 'bg-[#002FA7] text-white' : 'bg-white text-[#0A0A0A]'}`} data-testid="billing-yearly">{t.pricing.yearly}</button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0 border border-gray-200">
          {PLANS.map((plan) => (
            <div key={plan.id} className={`p-8 border border-gray-200 flex flex-col ${plan.highlighted ? 'bg-white border-2 border-[#002FA7] relative' : 'bg-white'}`} data-testid={`plan-${plan.id}`}>
              {plan.highlighted && <div className="absolute top-0 left-0 right-0 h-1 bg-[#002FA7]" />}
              <h3 className="font-clash text-xl font-bold text-[#0A0A0A] mb-2">{PLAN_NAMES[plan.id]}</h3>
              <div className="mb-6">
                {plan.monthly ? (
                  <>
                    <span className="text-4xl font-black text-[#0A0A0A]">
                      {billing === 'monthly' ? `€${plan.monthly}` : `€${plan.yearly}`}
                    </span>
                    <span className="text-sm text-[#4B5563] ml-1">
                      {billing === 'monthly' ? t.pricing.per_month : t.pricing.per_year}
                    </span>
                    <p className="text-xs text-[#4B5563] mt-1">(zzgl. MwSt.)</p>
                  </>
                ) : (
                  <span className="text-4xl font-black text-[#0A0A0A]">€0</span>
                )}
              </div>
              <div className="space-y-2 mb-8 text-sm">
                <p className="font-bold text-[#0A0A0A]">{plan.chatbots} Chatbot{plan.chatbots !== '1' ? 's' : ''}</p>
                <p className="font-bold text-[#0A0A0A]">{plan.messages} Nachrichten/Monat</p>
                {plan.features.map((f, i) => (
                  <p key={i} className="flex items-center gap-2 text-[#4B5563]">
                    <Check size={14} className="text-[#16a34a]" />{f}
                  </p>
                ))}
              </div>
              <div className="mt-auto">
                {user?.plan === plan.id ? (
                  <Button disabled className="w-full rounded-none py-3 font-bold" data-testid={`plan-${plan.id}-current`}>{t.pricing.current}</Button>
                ) : plan.id === 'free' ? (
                  <Link to="/signup"><Button variant="outline" className="w-full rounded-none py-3 font-bold border-gray-300" data-testid={`plan-${plan.id}-btn`}>{t.pricing.start_free}</Button></Link>
                ) : plan.id === 'agency' ? (
                  <Button variant="outline" className="w-full rounded-none py-3 font-bold border-gray-300" data-testid={`plan-${plan.id}-btn`}>{t.pricing.contact}</Button>
                ) : (
                  <Button onClick={() => handleUpgrade(plan.id)} disabled={loading === plan.id} className={`w-full rounded-none py-3 font-bold ${plan.highlighted ? 'bg-[#002FA7] text-white hover:bg-[#0040D6]' : 'bg-[#0A0A0A] text-white hover:bg-black'}`} data-testid={`plan-${plan.id}-btn`}>
                    {loading === plan.id ? '...' : t.pricing.upgrade}
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
        <p className="text-xs text-[#4B5563] text-center mt-6">{t.pricing.vat_note}</p>
      </div>
      <Footer />
    </div>
  );
}
