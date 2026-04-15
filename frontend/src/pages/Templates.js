import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Croissant, Stethoscope, UtensilsCrossed, Scissors, Building, Scale, ArrowRight } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

const ICON_MAP = {
  croissant: Croissant,
  stethoscope: Stethoscope,
  utensils: UtensilsCrossed,
  scissors: Scissors,
  building: Building,
  scale: Scale,
};

export default function Templates() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [businessName, setBusinessName] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    api.getTemplates().then(data => { setTemplates(data); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const handleUseTemplate = (template) => {
    setSelected(template);
    setBusinessName(template.business_name);
  };

  const handleCreate = async () => {
    if (!businessName.trim()) return;
    setCreating(true);
    try {
      const chatbot = await api.createFromTemplate({ template_id: selected.id, business_name: businessName });
      navigate(`/dashboard/chatbot/${chatbot.chatbot_id}`);
    } catch (err) {
      console.error('Template creation error:', err);
    }
    setCreating(false);
  };

  if (loading) {
    return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;
  }

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="templates-page">
        <div>
          <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]" data-testid="templates-title">{t.templates.title}</h1>
          <p className="text-[#4B5563] mt-1">{t.templates.subtitle}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border border-gray-200" data-testid="templates-grid">
          {templates.map(tmpl => {
            const Icon = ICON_MAP[tmpl.icon] || Building;
            return (
              <div key={tmpl.id} className="p-6 bg-white border border-gray-200 flex flex-col group hover:bg-[#F9FAFB] transition-colors" data-testid={`template-${tmpl.id}`}>
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-12 h-12 bg-[#002FA7]/5 flex items-center justify-center flex-shrink-0">
                    <Icon size={22} className="text-[#002FA7]" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-[#0A0A0A] text-base">{tmpl.name}</h3>
                    <p className="text-xs text-[#4B5563] uppercase tracking-wider mt-0.5">{tmpl.category}</p>
                  </div>
                </div>
                <p className="text-sm text-[#4B5563] leading-relaxed mb-4 flex-1 line-clamp-3">
                  {tmpl.faq_content.split('\n').slice(0, 3).join('. ').substring(0, 120)}...
                </p>
                <Button onClick={() => handleUseTemplate(tmpl)} className="w-full bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none py-2.5 font-bold text-sm mt-auto" data-testid={`use-template-${tmpl.id}`}>
                  {t.templates.use}
                  <ArrowRight size={14} className="ml-2" />
                </Button>
              </div>
            );
          })}
        </div>

        <div className="text-center pt-4">
          <p className="text-sm text-[#4B5563]">
            {t.templates.or_custom}{' '}
            <button onClick={() => navigate('/dashboard/new')} className="text-[#002FA7] font-bold underline" data-testid="custom-chatbot-link">{t.chatbot.create_title}</button>
          </p>
        </div>

        <Dialog open={!!selected} onOpenChange={() => setSelected(null)}>
          <DialogContent className="rounded-none max-w-md">
            <DialogHeader>
              <DialogTitle className="font-clash text-xl font-bold">{t.templates.customize}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.chatbot.business_name}</label>
                <Input value={businessName} onChange={e => setBusinessName(e.target.value)} className="rounded-none border-gray-300" data-testid="template-business-name" />
              </div>
              {selected && (
                <div className="bg-[#F9FAFB] border border-gray-200 p-4">
                  <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2">Vorlage: {selected.name}</p>
                  <p className="text-xs text-[#4B5563] max-h-32 overflow-y-auto font-mono whitespace-pre-wrap">{selected.faq_content.substring(0, 300)}...</p>
                </div>
              )}
              <div className="flex gap-3">
                <Button onClick={() => setSelected(null)} variant="outline" className="rounded-none flex-1">Cancel</Button>
                <Button onClick={handleCreate} disabled={creating || !businessName.trim()} className="rounded-none flex-1 bg-[#002FA7] text-white hover:bg-[#0040D6] font-bold" data-testid="create-from-template-btn">
                  {creating ? '...' : t.chatbot.save}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
