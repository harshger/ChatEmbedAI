import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

export default function AVV() {
  return (
    <div className="min-h-screen bg-white" data-testid="avv-page">
      <Header />
      <div className="max-w-3xl mx-auto px-6 md:px-12 pt-32 pb-24">
        <h1 className="font-clash text-5xl font-black tracking-tighter text-[#0A0A0A] mb-4">Auftragsverarbeitungsvertrag (AVV)</h1>
        <p className="text-[#4B5563] mb-12">Data Processing Agreement pursuant to Art. 28 GDPR</p>
        <div className="prose prose-gray max-w-none text-left space-y-6 text-[#0A0A0A] text-sm leading-relaxed">
          <h2 className="font-clash text-xl font-bold">1. Gegenstand und Dauer</h2>
          <p>Dieser AVV regelt die Verarbeitung personenbezogener Daten im Auftrag des Kunden durch ChatEmbed AI. Die Dauer entspricht der Laufzeit des Hauptvertrages.</p>

          <h2 className="font-clash text-xl font-bold">2. Art und Zweck der Verarbeitung</h2>
          <p>Verarbeitung von Chat-Nachrichten zwischen Website-Besuchern und dem KI-gestützten Chatbot zur Beantwortung von Kundenanfragen.</p>

          <h2 className="font-clash text-xl font-bold">3. Art der personenbezogenen Daten</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li>Chat-Nachrichten (Textinhalt)</li>
            <li>IP-Adressen (anonymisiert/gehasht)</li>
            <li>Spracherkennung</li>
            <li>Sitzungs-IDs (pseudonymisiert)</li>
          </ul>

          <h2 className="font-clash text-xl font-bold">4. Kategorien betroffener Personen</h2>
          <p>Website-Besucher des Kunden, die den Chat-Widget nutzen.</p>

          <h2 className="font-clash text-xl font-bold">5. Technische und organisatorische Maßnahmen (TOMs)</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li>Verschlüsselung der Daten bei Übertragung (TLS 1.3)</li>
            <li>Verschlüsselung der Daten im Ruhezustand</li>
            <li>Zugriffskontrolle und Authentifizierung</li>
            <li>Regelmäßige Sicherheitsüberprüfungen</li>
            <li>Automatische Datenlöschung nach 90 Tagen</li>
            <li>IP-Anonymisierung vor Speicherung</li>
            <li>EU-Serverstandort (Frankfurt)</li>
          </ul>

          <h2 className="font-clash text-xl font-bold">6. Unterauftragnehmer</h2>
          <ul className="list-disc pl-6 space-y-1">
            <li><strong>Anthropic, Inc.</strong> (Claude AI) — USA — Standardvertragsklauseln (SCC)</li>
            <li><strong>Stripe, Inc.</strong> — EU/USA — Datenverarbeitungsvertrag</li>
          </ul>

          <h2 className="font-clash text-xl font-bold">7. Pflichten des Auftragsverarbeiters</h2>
          <p>Der Auftragsverarbeiter verarbeitet die Daten ausschließlich nach dokumentierter Weisung des Auftraggebers und gewährleistet die Vertraulichkeit.</p>

          <div className="border border-gray-200 p-6 bg-[#F9FAFB] mt-8">
            <p className="font-bold text-[#0A0A0A] mb-2">Download</p>
            <p className="text-[#4B5563] mb-4">Laden Sie den vollständigen AVV als PDF herunter, um ihn zu unterzeichnen.</p>
            <button className="bg-[#002FA7] text-white px-6 py-3 font-bold hover:bg-[#0040D6] transition-colors" data-testid="download-avv-btn">AVV als PDF herunterladen</button>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
