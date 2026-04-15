import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

export default function Impressum() {
  return (
    <div className="min-h-screen bg-white" data-testid="impressum-page">
      <Header />
      <div className="max-w-3xl mx-auto px-6 md:px-12 pt-32 pb-24">
        <h1 className="font-clash text-5xl font-black tracking-tighter text-[#0A0A0A] mb-12">Impressum</h1>
        <div className="prose prose-gray max-w-none text-left space-y-6 text-[#0A0A0A]">
          <h2 className="font-clash text-xl font-bold">Angaben gemäß § 5 TMG</h2>
          <p>[Full Name]<br />[Street]<br />[City], Germany</p>

          <h2 className="font-clash text-xl font-bold">Kontakt</h2>
          <p>E-Mail: info@[domain].com<br />Telefon: +49 [number]</p>

          <h2 className="font-clash text-xl font-bold">Umsatzsteuer-ID</h2>
          <p>Umsatzsteuer-Identifikationsnummer gemäß § 27a Umsatzsteuergesetz:<br />DE[VAT number]</p>

          <h2 className="font-clash text-xl font-bold">Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
          <p>[Full Name]<br />[Street]<br />[City], Germany</p>

          <h2 className="font-clash text-xl font-bold">EU-Streitschlichtung</h2>
          <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <a href="https://ec.europa.eu/consumers/odr" className="text-[#002FA7] underline" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr</a></p>
          <p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
        </div>
      </div>
      <Footer />
    </div>
  );
}
