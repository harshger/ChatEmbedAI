import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const today = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

export function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-white" data-testid="privacy-policy-page">
      <Header />
      <div className="max-w-3xl mx-auto px-6 md:px-12 pt-32 pb-24">
        <h1 className="font-clash text-5xl font-black tracking-tighter text-[#0A0A0A] mb-4">Privacy Policy</h1>
        <p className="text-sm text-[#4B5563] mb-12">Last updated: {today}</p>
        <div className="prose prose-gray max-w-none text-left space-y-6 text-[#0A0A0A] text-sm leading-relaxed">
          <h2 className="font-clash text-xl font-bold">1. Data Controller</h2>
          <p>[Company Name], [Street], [City], Germany<br />Email: datenschutz@[domain].com</p>
          <h2 className="font-clash text-xl font-bold">2. Data Collected</h2>
          <p>Email address, business name, FAQ text, chat messages, IP address (anonymized), browser info.</p>
          <h2 className="font-clash text-xl font-bold">3. Legal Basis (Art. 6 GDPR)</h2>
          <ul className="list-disc pl-6"><li>Contract performance for account data</li><li>Legitimate interest for analytics</li><li>Consent for marketing</li></ul>
          <h2 className="font-clash text-xl font-bold">4. Data Retention</h2>
          <ul className="list-disc pl-6"><li>Account data: 30 days after deletion</li><li>Chat messages: 90 days</li><li>Billing data: 10 years (German tax law)</li></ul>
          <h2 className="font-clash text-xl font-bold">5. Your Rights</h2>
          <p>Access, rectification, erasure, portability, objection, restriction. Contact: datenschutz@[domain].com</p>
          <h2 className="font-clash text-xl font-bold">6. Supervisory Authority</h2>
          <p>You have the right to lodge a complaint with a supervisory authority (Datenschutzbehörde).</p>
        </div>
      </div>
      <Footer />
    </div>
  );
}

export function Terms() {
  return (
    <div className="min-h-screen bg-white" data-testid="terms-page">
      <Header />
      <div className="max-w-3xl mx-auto px-6 md:px-12 pt-32 pb-24">
        <h1 className="font-clash text-5xl font-black tracking-tighter text-[#0A0A0A] mb-12">Terms of Service</h1>
        <div className="prose prose-gray max-w-none text-left space-y-6 text-[#0A0A0A] text-sm leading-relaxed">
          <h2 className="font-clash text-xl font-bold">1. Scope</h2>
          <p>These Terms of Service govern the use of ChatEmbed AI. German law (BGB) applies. Jurisdiction: Germany.</p>
          <h2 className="font-clash text-xl font-bold">2. Contract Formation</h2>
          <p>The contract is formed upon registration and email confirmation.</p>
          <h2 className="font-clash text-xl font-bold">3. Subscriptions & Cancellation</h2>
          <p>Paid subscriptions renew automatically. Cancellation is possible at any time for the end of the current billing period.</p>
          <h2 className="font-clash text-xl font-bold">4. Right of Withdrawal</h2>
          <p>EU consumers have a 14-day right of withdrawal. Contact info@[domain].com.</p>
          <h2 className="font-clash text-xl font-bold">5. Liability</h2>
          <p>Liability is limited to foreseeable, contract-typical damages per German law.</p>
          <h2 className="font-clash text-xl font-bold">6. Price Changes</h2>
          <p>Price changes will be communicated at least 6 weeks in advance.</p>
        </div>
      </div>
      <Footer />
    </div>
  );
}
