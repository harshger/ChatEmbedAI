import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Cpu, Cloud, Server, CheckCircle, AlertTriangle } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

export default function AISettings() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.getAIConfig()
      .then(d => { setConfig(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await api.updateAIConfig({
        engine: config.engine,
        ollama_url: config.ollama_url,
        ollama_model: config.ollama_model,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {}
    setSaving(false);
  };

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="ai-settings-page">
        <div>
          <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">KI-Einstellungen</h1>
          <p className="text-sm text-[#4B5563] mt-1">Configure which AI engine powers your chatbots</p>
        </div>

        {saved && (
          <div className="border border-green-300 bg-green-50 p-4 flex items-center gap-3" data-testid="save-success">
            <CheckCircle size={18} className="text-green-600" />
            <p className="text-sm font-bold text-green-700">Settings saved successfully</p>
          </div>
        )}

        {/* Engine Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0 border border-gray-200">
          <button onClick={() => setConfig(c => ({ ...c, engine: 'claude' }))} className={`p-8 bg-white border border-gray-200 text-left transition-all ${config?.engine === 'claude' ? 'ring-2 ring-[#002FA7] ring-inset' : 'hover:bg-[#F9FAFB]'}`} data-testid="engine-claude">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-[#002FA7] flex items-center justify-center"><Cloud size={20} className="text-white" /></div>
              <div>
                <h3 className="font-bold text-[#0A0A0A]">Claude AI (Cloud)</h3>
                {config?.engine === 'claude' && <span className="text-xs text-[#002FA7] font-bold">Active</span>}
              </div>
            </div>
            <p className="text-sm text-[#4B5563]">Powered by Anthropic Claude Sonnet. High-quality responses, managed infrastructure, no setup required.</p>
            <div className="mt-4 flex gap-2">
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 font-bold">Recommended</span>
              <span className="text-xs bg-[#F9FAFB] text-[#4B5563] px-2 py-1">EU-compliant</span>
            </div>
          </button>

          <button onClick={() => setConfig(c => ({ ...c, engine: 'ollama' }))} className={`p-8 bg-white border border-gray-200 text-left transition-all ${config?.engine === 'ollama' ? 'ring-2 ring-[#002FA7] ring-inset' : 'hover:bg-[#F9FAFB]'}`} data-testid="engine-ollama">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-[#0A0A0A] flex items-center justify-center"><Server size={20} className="text-white" /></div>
              <div>
                <h3 className="font-bold text-[#0A0A0A]">Ollama (Self-Hosted)</h3>
                {config?.engine === 'ollama' && <span className="text-xs text-[#002FA7] font-bold">Active</span>}
              </div>
            </div>
            <p className="text-sm text-[#4B5563]">Run AI locally on your own server. Full data sovereignty, no external API calls. Requires Ollama setup.</p>
            <div className="mt-4 flex gap-2">
              <span className="text-xs bg-[#F9FAFB] text-[#4B5563] px-2 py-1">Self-hosted</span>
              <span className="text-xs bg-[#F9FAFB] text-[#4B5563] px-2 py-1">100% private</span>
            </div>
          </button>
        </div>

        {/* Ollama Configuration */}
        {config?.engine === 'ollama' && (
          <div className="border border-gray-200 bg-white p-8 space-y-6" data-testid="ollama-config">
            <div className="flex items-center gap-3">
              <Cpu size={20} className="text-[#0A0A0A]" />
              <h2 className="font-clash text-xl font-bold text-[#0A0A0A]">Ollama Configuration</h2>
            </div>

            <div className="border border-yellow-300 bg-yellow-50 p-4 flex items-start gap-3">
              <AlertTriangle size={18} className="text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <p className="font-bold mb-1">Self-Hosted Setup Required</p>
                <p>Make sure Ollama is running on your server and accessible from this application. Falls back to Claude if Ollama is unreachable.</p>
              </div>
            </div>

            <div>
              <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">Ollama Server URL</Label>
              <Input value={config.ollama_url || ''} onChange={e => setConfig(c => ({ ...c, ollama_url: e.target.value }))} placeholder="http://localhost:11434" className="rounded-none border-gray-300" data-testid="ollama-url-input" />
              <p className="text-xs text-[#4B5563] mt-1">Default: http://localhost:11434</p>
            </div>

            <div>
              <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">Model</Label>
              <Select value={config.ollama_model || 'llama3'} onValueChange={v => setConfig(c => ({ ...c, ollama_model: v }))}>
                <SelectTrigger className="rounded-none border-gray-300 w-64" data-testid="ollama-model-select"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="llama3">Llama 3 (8B)</SelectItem>
                  <SelectItem value="llama3:70b">Llama 3 (70B)</SelectItem>
                  <SelectItem value="mistral">Mistral (7B)</SelectItem>
                  <SelectItem value="mixtral">Mixtral (8x7B)</SelectItem>
                  <SelectItem value="gemma2">Gemma 2 (9B)</SelectItem>
                  <SelectItem value="phi3">Phi-3 (3.8B)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )}

        <Button onClick={handleSave} disabled={saving} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-8 py-3 font-bold" data-testid="save-ai-config-btn">
          {saving ? '...' : 'Save AI Settings'}
        </Button>
      </div>
    </DashboardLayout>
  );
}
