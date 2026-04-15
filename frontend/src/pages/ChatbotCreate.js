import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation, LANGUAGES } from '../lib/i18n';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import DashboardLayout from '../components/DashboardLayout';
import ChatWidgetPreview from '../components/ChatWidgetPreview';

export default function ChatbotCreate() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    business_name: '', faq_content: '', primary_language: 'de',
    auto_detect_language: true, widget_color: '#6366f1', show_gdpr_notice: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.business_name || !form.faq_content) { setError('Please fill in all required fields.'); return; }
    setLoading(true);
    setError('');
    try {
      const chatbot = await api.createChatbot(form);
      navigate(`/dashboard/chatbot/${chatbot.chatbot_id}`);
    } catch (err) {
      setError('Failed to create chatbot. Check plan limits.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div data-testid="chatbot-create-page">
        <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A] mb-8">{t.chatbot.create_title}</h1>
        {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 mb-6" data-testid="create-error">{error}</div>}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Form */}
          <div className="lg:col-span-3">
            <form onSubmit={handleSubmit} className="border border-gray-200 bg-white p-8 space-y-6">
              <div>
                <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.chatbot.business_name}</Label>
                <Input value={form.business_name} onChange={e => setForm(f => ({ ...f, business_name: e.target.value }))} required className="rounded-none border-gray-300" data-testid="chatbot-name-input" />
              </div>
              <div>
                <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.chatbot.faq_label}</Label>
                <Textarea value={form.faq_content} onChange={e => setForm(f => ({ ...f, faq_content: e.target.value }))} rows={12} className="rounded-none border-gray-300 font-mono text-sm" data-testid="chatbot-faq-input" />
                <p className="text-xs text-[#4B5563] mt-1">{form.faq_content.length} / 50,000</p>
              </div>
              <div>
                <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.chatbot.language}</Label>
                <Select value={form.primary_language} onValueChange={v => setForm(f => ({ ...f, primary_language: v }))}>
                  <SelectTrigger className="rounded-none border-gray-300" data-testid="chatbot-lang-select"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {LANGUAGES.map(l => <SelectItem key={l.code} value={l.code}>{l.flag} {l.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center justify-between py-3 border-t border-gray-100">
                <Label className="text-sm text-[#0A0A0A]">{t.chatbot.auto_detect}</Label>
                <Switch checked={form.auto_detect_language} onCheckedChange={v => setForm(f => ({ ...f, auto_detect_language: v }))} data-testid="auto-detect-toggle" />
              </div>
              <div className="flex items-center justify-between py-3 border-t border-gray-100">
                <Label className="text-sm text-[#0A0A0A]">{t.chatbot.gdpr_notice}</Label>
                <Switch checked={form.show_gdpr_notice} onCheckedChange={v => setForm(f => ({ ...f, show_gdpr_notice: v }))} data-testid="gdpr-notice-toggle" />
              </div>
              <div>
                <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">Widget Color</Label>
                <Input type="color" value={form.widget_color} onChange={e => setForm(f => ({ ...f, widget_color: e.target.value }))} className="w-16 h-10 p-1 rounded-none border-gray-300" data-testid="widget-color-input" />
              </div>
              <Button type="submit" disabled={loading} className="w-full bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none py-3 font-bold" data-testid="create-chatbot-btn">
                {loading ? t.chatbot.creating : t.chatbot.save}
              </Button>
            </form>
          </div>
          {/* Preview */}
          <div className="lg:col-span-2">
            <div className="sticky top-24">
              <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-4">Live Preview</p>
              <ChatWidgetPreview businessName={form.business_name || 'Your Business'} color={form.widget_color} showGdpr={form.show_gdpr_notice} />
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
