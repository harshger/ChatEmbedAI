import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const today = new Date().toLocaleDateString('de-DE', { year: 'numeric', month: 'long', day: 'numeric' });

export default function Datenschutz() {
  return (
    <div className="min-h-screen bg-white" data-testid="datenschutz-page">
      <Header />
      <div className="max-w-3xl mx-auto px-6 md:px-12 pt-32 pb-24">
        <h1 className="font-clash text-5xl font-black tracking-tighter text-[#0A0A0A] mb-4">Datenschutzerklärung</h1>
        <p className="text-sm text-[#4B5563] mb-12">Zuletzt aktualisiert: {today}</p>
        <div className="prose prose-gray max-w-none text-left space-y-6 text-[#0A0A0A] text-sm leading-relaxed">
          <h2 className="font-clash text-xl font-bold">1. Verantwortlicher</h2>
          <p>[Company Name]<br />[Street]<br />[City], Germany<br />E-Mail: datenschutz@[domain].com</p>

          <h2 className="font-clash text-xl font-bold">2. Erhobene Daten</h2>
          <p>Wir erheben folgende personenbezogene Daten:</p>
          <ul className="list-disc pl-6 space-y-1">
            <li>E-Mail-Adresse</li><li>Unternehmensname</li><li>FAQ-Texte</li>
            <li>Chat-Nachrichten</li><li>IP-Adresse (anonymisiert)</li><li>Browser-Informationen</li>
          </ul>

          <h2 className="font-clash text-xl font-bold">3. Rechtsgrundlage (Art. 6 DSGVO)</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li><strong>Vertragserfüllung (Art. 6 Abs. 1 lit. b DSGVO):</strong> Kontodaten, Chatbot-Konfigurationen</li>
            <li><strong>Berechtigtes Interesse (Art. 6 Abs. 1 lit. f DSGVO):</strong> Analytik</li>
            <li><strong>Einwilligung (Art. 6 Abs. 1 lit. a DSGVO):</strong> Marketing</li>
          </ul>

          <h2 className="font-clash text-xl font-bold">4. Aufbewahrungsfristen</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li>Kontodaten: Löschung 30 Tage nach Kontolöschung</li>
            <li>Chat-Nachrichten: Automatische Löschung nach 90 Tagen</li>
            <li>Rechnungsdaten: 10 Jahre Aufbewahrung (§ 257 HGB)</li>
          </ul>

          <h2 className="font-clash text-xl font-bold">5. Auftragsverarbeiter</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li><strong>Anthropic (Claude AI)</strong> — USA, Standardvertragsklauseln</li>
            <li><strong>MongoDB</strong> — EU-Region</li>
            <li><strong>Stripe</strong> — EU-Datenverarbeitungsvertrag</li>
          </ul>

          <h2 className="font-clash text-xl font-bold">6. Ihre Rechte</h2>
          <p>Sie haben das Recht auf:</p>
          <ul className="list-disc pl-6 space-y-1">
            <li>Auskunft über Ihre gespeicherten Daten</li>
            <li>Berichtigung unrichtiger Daten</li>
            <li>Löschung Ihrer Daten</li>
            <li>Datenübertragbarkeit</li>
            <li>Widerspruch gegen die Verarbeitung</li>
            <li>Einschränkung der Verarbeitung</li>
          </ul>

          <h2 className="font-clash text-xl font-bold">7. Beschwerderecht</h2>
          <p>Sie haben das Recht, eine Beschwerde bei einer Datenschutzbehörde einzureichen.</p>

          <h2 className="font-clash text-xl font-bold">8. Kontakt</h2>
          <p>Für Datenschutzanfragen: datenschutz@[domain].com</p>
        </div>
      </div>
      <Footer />
    </div>
  );
}
