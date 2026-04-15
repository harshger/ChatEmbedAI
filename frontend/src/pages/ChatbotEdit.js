import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { useTranslation, LANGUAGES } from '../lib/i18n';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Copy, Check } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import ChatWidgetPreview from '../components/ChatWidgetPreview';

export default function ChatbotEdit() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const { t } = useTranslation();
  const [chatbot, setChatbot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'edit');

  useEffect(() => {
    api.getChatbot(id).then(data => { setChatbot(data); setLoading(false); }).catch(() => setLoading(false));
  }, [id]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await api.updateChatbot(id, chatbot);
      setChatbot(updated);
    } catch {}
    setSaving(false);
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;
  if (!chatbot) return <DashboardLayout><p>Chatbot not found.</p></DashboardLayout>;

  const appUrl = window.location.origin;
  const embedHtml = `<script src="${appUrl}/embed.js"\n  data-chatbot-id="${chatbot.chatbot_id}"\n  data-lang="${chatbot.primary_language}"></script>`;
  const embedWp = `<!-- Add to your WordPress theme's footer.php or use a plugin like "Insert Headers and Footers" -->\n${embedHtml}`;
  const embedWix = `<!-- In Wix: Settings > Custom Code > Add Custom Code -->\n<!-- Paste in the "Body - end" section -->\n${embedHtml}`;
  const embedShopify = `<!-- In Shopify: Online Store > Themes > Edit code > theme.liquid -->\n<!-- Paste before </body> -->\n${embedHtml}`;

  return (
    <DashboardLayout>
      <div data-testid="chatbot-edit-page">
        <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A] mb-8">{chatbot.business_name}</h1>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="rounded-none border border-gray-200 bg-white mb-8" data-testid="edit-tabs">
            <TabsTrigger value="edit" className="rounded-none data-[state=active]:bg-[#002FA7] data-[state=active]:text-white">{t.dashboard.edit}</TabsTrigger>
            <TabsTrigger value="embed" className="rounded-none data-[state=active]:bg-[#002FA7] data-[state=active]:text-white">{t.embed.title}</TabsTrigger>
            <TabsTrigger value="preview" className="rounded-none data-[state=active]:bg-[#002FA7] data-[state=active]:text-white">{t.dashboard.preview}</TabsTrigger>
          </TabsList>

          <TabsContent value="edit">
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
              <div className="lg:col-span-3 border border-gray-200 bg-white p-8 space-y-6">
                <div>
                  <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.chatbot.business_name}</Label>
                  <Input value={chatbot.business_name} onChange={e => setChatbot(c => ({ ...c, business_name: e.target.value }))} className="rounded-none border-gray-300" data-testid="edit-name" />
                </div>
                <div>
                  <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.chatbot.faq_label}</Label>
                  <Textarea value={chatbot.faq_content} onChange={e => setChatbot(c => ({ ...c, faq_content: e.target.value }))} rows={12} className="rounded-none border-gray-300 font-mono text-sm" data-testid="edit-faq" />
                  <p className="text-xs text-[#4B5563] mt-1">{chatbot.faq_content?.length || 0} / 100,000</p>
                </div>
                <div>
                  <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.chatbot.language}</Label>
                  <Select value={chatbot.primary_language} onValueChange={v => setChatbot(c => ({ ...c, primary_language: v }))}>
                    <SelectTrigger className="rounded-none border-gray-300"><SelectValue /></SelectTrigger>
                    <SelectContent>{LANGUAGES.map(l => <SelectItem key={l.code} value={l.code}>{l.flag} {l.name}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="flex items-center justify-between py-3 border-t border-gray-100">
                  <Label className="text-sm">{t.chatbot.auto_detect}</Label>
                  <Switch checked={chatbot.auto_detect_language} onCheckedChange={v => setChatbot(c => ({ ...c, auto_detect_language: v }))} />
                </div>
                <div className="flex items-center justify-between py-3 border-t border-gray-100">
                  <Label className="text-sm">{t.chatbot.gdpr_notice}</Label>
                  <Switch checked={chatbot.show_gdpr_notice} onCheckedChange={v => setChatbot(c => ({ ...c, show_gdpr_notice: v }))} />
                </div>
                <div>
                  <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">Widget Color</Label>
                  <Input type="color" value={chatbot.widget_color} onChange={e => setChatbot(c => ({ ...c, widget_color: e.target.value }))} className="w-16 h-10 p-1 rounded-none" />
                </div>
                <Button onClick={handleSave} disabled={saving} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-8 py-3 font-bold" data-testid="save-chatbot-btn">
                  {saving ? '...' : t.chatbot.save}
                </Button>
              </div>
              <div className="lg:col-span-2 sticky top-24">
                <ChatWidgetPreview businessName={chatbot.business_name} color={chatbot.widget_color} showGdpr={chatbot.show_gdpr_notice} chatbotId={chatbot.chatbot_id} interactive />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="embed">
            <div className="border border-gray-200 bg-white p-8" data-testid="embed-section">
              <Tabs defaultValue="html">
                <TabsList className="rounded-none border border-gray-200 bg-[#F9FAFB] mb-6">
                  <TabsTrigger value="html" className="rounded-none text-xs">{t.embed.html}</TabsTrigger>
                  <TabsTrigger value="wordpress" className="rounded-none text-xs">{t.embed.wordpress}</TabsTrigger>
                  <TabsTrigger value="wix" className="rounded-none text-xs">{t.embed.wix}</TabsTrigger>
                  <TabsTrigger value="shopify" className="rounded-none text-xs">{t.embed.shopify}</TabsTrigger>
                </TabsList>
                {[{ key: 'html', code: embedHtml }, { key: 'wordpress', code: embedWp }, { key: 'wix', code: embedWix }, { key: 'shopify', code: embedShopify }].map(tab => (
                  <TabsContent key={tab.key} value={tab.key}>
                    <div className="relative">
                      <pre className="bg-[#0A0A0A] text-green-400 p-6 text-sm overflow-x-auto font-mono">{tab.code}</pre>
                      <Button onClick={() => handleCopy(tab.code)} variant="outline" size="sm" className="absolute top-3 right-3 rounded-none bg-white/10 border-white/20 text-white hover:bg-white/20" data-testid={`copy-${tab.key}`}>
                        {copied ? <><Check size={12} className="mr-1" />{t.embed.copied}</> : <><Copy size={12} className="mr-1" />{t.embed.copy}</>}
                      </Button>
                    </div>
                  </TabsContent>
                ))}
              </Tabs>
            </div>
          </TabsContent>

          <TabsContent value="preview">
            <div className="flex justify-center p-12 bg-[#F9FAFB] border border-gray-200">
              <ChatWidgetPreview businessName={chatbot.business_name} color={chatbot.widget_color} showGdpr={chatbot.show_gdpr_notice} chatbotId={chatbot.chatbot_id} interactive />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
