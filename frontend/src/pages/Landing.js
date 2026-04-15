import React, { useState } from 'react';
import { useTranslation } from '../lib/i18n';
import { Link } from 'react-router-dom';
import { Shield, Globe, Zap, Bot, Code, Server, ArrowRight, CheckCircle, Quote } from 'lucide-react';
import { Button } from '../components/ui/button';
import Header from '../components/Header';
import Footer from '../components/Footer';

const TESTIMONIAL_IMAGES = [
  'https://images.unsplash.com/photo-1773944449123-0089f239a4b3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMzN8MHwxfHNlYXJjaHwyfHxzbWFsbCUyMGJ1c2luZXNzJTIwb3duZXIlMjBwb3J0cmFpdHxlbnwwfHx8fDE3NzYyMzY4Mjl8MA&ixlib=rb-4.1.0&q=85&w=120&h=120',
  'https://images.unsplash.com/photo-1758887261865-a2b89c0f7ac5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMzN8MHwxfHNlYXJjaHwxfHxzbWFsbCUyMGJ1c2luZXNzJTIwb3duZXIlMjBwb3J0cmFpdHxlbnwwfHx8fDE3NzYyMzY4Mjl8MA&ixlib=rb-4.1.0&q=85&w=120&h=120',
  'https://images.pexels.com/photos/8422729/pexels-photo-8422729.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=120&w=120',
];

const FEATURE_ICONS = [Globe, Shield, Zap, Bot, Code, Server];

export default function Landing() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-white" data-testid="landing-page">
      <Header />

      {/* Hero */}
      <section className="relative overflow-hidden bg-white" data-testid="hero-section">
        <div className="absolute inset-0 bg-[#F9FAFB]" />
        <div className="relative max-w-7xl mx-auto px-6 md:px-12 pt-32 pb-24">
          <div className="max-w-4xl">
            <div className="flex items-center gap-3 mb-8">
              {t.hero.badges.map((badge, i) => (
                <span key={i} className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-bold uppercase tracking-[0.15em] border border-[#002FA7] text-[#002FA7]">
                  {i === 0 && <Shield size={12} />}
                  {i === 1 && <Globe size={12} />}
                  {i === 2 && <Zap size={12} />}
                  {badge}
                </span>
              ))}
            </div>
            <h1 className="font-clash text-5xl lg:text-6xl font-black tracking-tighter leading-none text-[#0A0A0A] mb-6" data-testid="hero-title">
              {t.hero.h1}
            </h1>
            <p className="text-lg text-[#4B5563] leading-relaxed max-w-2xl mb-10">
              {t.hero.h2}
            </p>
            <div className="flex items-center gap-4">
              <Link to="/signup">
                <Button className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-8 py-4 text-base font-bold" data-testid="hero-cta">
                  {t.hero.cta}
                  <ArrowRight size={18} className="ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Steps */}
      <section className="py-24 bg-white border-t border-gray-200" data-testid="steps-section">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#002FA7] mb-4">{t.steps.title}</p>
          <h2 className="font-clash text-3xl lg:text-4xl font-bold tracking-tight text-[#0A0A0A] mb-16">{t.steps.title}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[t.steps.s1, t.steps.s2, t.steps.s3].map((step, i) => (
              <div key={i} className="relative">
                <div className="text-6xl font-black text-[#002FA7] opacity-10 absolute -top-4 -left-2">0{i + 1}</div>
                <div className="relative pt-8">
                  <h3 className="text-xl font-bold text-[#0A0A0A] mb-3">{step.title}</h3>
                  <p className="text-[#4B5563] leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 bg-[#F9FAFB] border-t border-gray-200" data-testid="features-section">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#002FA7] mb-4">{t.features.title}</p>
          <h2 className="font-clash text-3xl lg:text-4xl font-bold tracking-tight text-[#0A0A0A] mb-16">{t.features.title}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border border-gray-200">
            {t.features.items.map((feat, i) => {
              const Icon = FEATURE_ICONS[i];
              return (
                <div key={i} className="p-8 bg-white border border-gray-200 hover:bg-[#F9FAFB] transition-colors duration-200" data-testid={`feature-${i}`}>
                  <Icon size={24} className="text-[#002FA7] mb-4" strokeWidth={2} />
                  <h3 className="text-lg font-bold text-[#0A0A0A] mb-2">{feat.title}</h3>
                  <p className="text-sm text-[#4B5563] leading-relaxed">{feat.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 bg-white border-t border-gray-200" data-testid="testimonials-section">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#002FA7] mb-4">{t.testimonials.title}</p>
          <h2 className="font-clash text-3xl lg:text-4xl font-bold tracking-tight text-[#0A0A0A] mb-16">{t.testimonials.title}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {t.testimonials.items.map((item, i) => (
              <div key={i} className="border border-gray-200 p-8 relative" data-testid={`testimonial-${i}`}>
                <Quote size={20} className="text-[#002FA7] opacity-30 mb-4" />
                <p className="text-[#0A0A0A] leading-relaxed mb-6">"{item.text}"</p>
                <div className="flex items-center gap-3">
                  <img src={TESTIMONIAL_IMAGES[i]} alt={item.author} className="w-10 h-10 rounded-full object-cover" />
                  <div>
                    <p className="font-bold text-sm text-[#0A0A0A]">{item.author}</p>
                    <p className="text-xs text-[#4B5563]">{item.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust */}
      <section className="py-24 bg-[#0A0A0A] text-white" data-testid="trust-section">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <h2 className="font-clash text-3xl lg:text-4xl font-bold tracking-tight mb-12">{t.trust.title}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {t.trust.items.map((item, i) => (
              <div key={i} className="flex items-start gap-3">
                <CheckCircle size={20} className="text-[#16a34a] mt-0.5 flex-shrink-0" />
                <p className="text-gray-300">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-white border-t border-gray-200">
        <div className="max-w-3xl mx-auto px-6 md:px-12 text-center">
          <h2 className="font-clash text-3xl lg:text-4xl font-bold tracking-tight text-[#0A0A0A] mb-6">{t.hero.cta}</h2>
          <Link to="/signup">
            <Button className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-8 py-4 text-base font-bold" data-testid="bottom-cta">
              {t.hero.cta}
              <ArrowRight size={18} className="ml-2" />
            </Button>
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
