import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

export default function AGB() {
  return (
    <div className="min-h-screen bg-white" data-testid="agb-page">
      <Header />
      <div className="max-w-3xl mx-auto px-6 md:px-12 pt-32 pb-24">
        <h1 className="font-clash text-5xl font-black tracking-tighter text-[#0A0A0A] mb-12">Allgemeine Geschäftsbedingungen</h1>
        <div className="prose prose-gray max-w-none text-left space-y-6 text-[#0A0A0A] text-sm leading-relaxed">
          <h2 className="font-clash text-xl font-bold">§ 1 Geltungsbereich</h2>
          <p>Diese Allgemeinen Geschäftsbedingungen (AGB) gelten für alle Verträge zwischen [Company Name] (nachfolgend "Anbieter") und dem Kunden über die Nutzung der Plattform ChatEmbed AI. Es gilt deutsches Recht (BGB). Gerichtsstand ist Deutschland.</p>

          <h2 className="font-clash text-xl font-bold">§ 2 Vertragsschluss</h2>
          <p>Der Vertrag kommt durch die Registrierung und Bestätigung der E-Mail-Adresse zustande. Mit der Registrierung akzeptiert der Kunde diese AGB.</p>

          <h2 className="font-clash text-xl font-bold">§ 3 Abonnement und Kündigung</h2>
          <p>Kostenpflichtige Abonnements verlängern sich automatisch. Die Kündigung ist jederzeit zum Ende der aktuellen Abrechnungsperiode möglich.</p>

          <h2 className="font-clash text-xl font-bold">§ 4 Widerrufsrecht</h2>
          <p>Verbraucher haben ein 14-tägiges Widerrufsrecht gemäß EU-Verbraucherrecht. Um Ihr Widerrufsrecht auszuüben, müssen Sie uns mittels einer eindeutigen Erklärung (z.B. E-Mail an info@[domain].com) über Ihren Entschluss informieren.</p>
          <div className="border border-gray-200 p-4 bg-[#F9FAFB]">
            <p className="font-bold mb-2">Muster-Widerrufsformular</p>
            <p>An [Company Name], [Address]:<br />Hiermit widerrufe(n) ich/wir den von mir/uns abgeschlossenen Vertrag über die Erbringung der folgenden Dienstleistung: ChatEmbed AI Abonnement<br />Bestellt am: ___<br />Name des/der Verbraucher(s): ___<br />Unterschrift (nur bei Mitteilung auf Papier): ___<br />Datum: ___</p>
          </div>

          <h2 className="font-clash text-xl font-bold">§ 5 Haftungsbeschränkung</h2>
          <p>Der Anbieter haftet nur für vorsätzlich oder grob fahrlässig verursachte Schäden. Die Haftung ist auf vorhersehbare, vertragstypische Schäden beschränkt.</p>

          <h2 className="font-clash text-xl font-bold">§ 6 Unzulässige Nutzung</h2>
          <p>Die Nutzung des Dienstes für illegale Zwecke, Spam, irreführende Inhalte oder die Verarbeitung besonderer personenbezogener Daten ohne entsprechende Rechtsgrundlage ist untersagt.</p>

          <h2 className="font-clash text-xl font-bold">§ 7 Preisänderungen</h2>
          <p>Preisänderungen werden mindestens 6 Wochen vor Inkrafttreten per E-Mail angekündigt.</p>

          <h2 className="font-clash text-xl font-bold">§ 8 Schlussbestimmungen</h2>
          <p>Es gilt deutsches Recht. Sollten einzelne Bestimmungen unwirksam sein, bleibt die Wirksamkeit der übrigen Bestimmungen unberührt.</p>
        </div>
      </div>
      <Footer />
    </div>
  );
}
