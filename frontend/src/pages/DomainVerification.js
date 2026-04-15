import React, { useEffect, useState } from 'react';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Globe, CheckCircle, XCircle, Copy, Check, AlertTriangle, Shield, Code, Server } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

export default function DomainVerification() {
  const { user, checkAuth } = useAuth();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [result, setResult] = useState(null);
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [initData, setInitData] = useState(null);
  const [copied, setCopied] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getDomainStatus()
      .then(d => { setStatus(d); setWebsiteUrl(d.website_url || ''); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handleSetWebsite = async () => {
    if (!websiteUrl.trim()) return;
    setSaving(true);
    try {
      const data = await api.initDomainVerification({ website_url: websiteUrl });
      setInitData(data);
      setStatus(prev => ({ ...prev, domain: data.domain, website_url: data.website_url, domain_verification_token: data.verification_token }));
      setResult(null);
    } catch {}
    setSaving(false);
  };

  const handleVerify = async (method) => {
    setVerifying(true);
    setResult(null);
    try {
      const data = await api.verifyDomain(method);
      setResult(data);
      if (data.verified) {
        setStatus(prev => ({ ...prev, domain_verified: true }));
        checkAuth();
      }
    } catch {
      setResult({ verified: false, details: 'Verification failed. Please try again.' });
    }
    setVerifying(false);
  };

  const handleCopy = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(''), 2000);
  };

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  const isVerified = status?.domain_verified;
  const token = initData?.verification_token || status?.domain_verification_token || '';
  const domain = initData?.domain || status?.domain || '';

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="domain-verification-page">
        <div>
          <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">Domain-Verifizierung</h1>
          <p className="text-sm text-[#4B5563] mt-1">Verify ownership of your website to activate your chatbot widget</p>
        </div>

        {/* Status Card */}
        <div className={`border-2 p-6 flex items-center gap-4 ${isVerified ? 'border-green-400 bg-green-50' : 'border-yellow-400 bg-yellow-50'}`} data-testid="domain-status-card">
          {isVerified ? (
            <>
              <CheckCircle size={32} className="text-green-600 flex-shrink-0" />
              <div>
                <p className="font-bold text-green-800">Domain Verified</p>
                <p className="text-sm text-green-700">{domain || status?.domain} — Your chatbot widget is active.</p>
              </div>
            </>
          ) : (
            <>
              <AlertTriangle size={32} className="text-yellow-600 flex-shrink-0" />
              <div>
                <p className="font-bold text-yellow-800">Domain Not Verified</p>
                <p className="text-sm text-yellow-700">{domain ? `Pending verification for ${domain}` : 'Set your website URL to begin verification.'}</p>
              </div>
            </>
          )}
        </div>

        {/* Step 1: Set Website */}
        <div className="border border-gray-200 bg-white p-8" data-testid="set-website-section">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 bg-[#002FA7] flex items-center justify-center text-white font-bold text-sm">1</div>
            <h2 className="font-clash text-xl font-bold text-[#0A0A0A]">Your Website</h2>
          </div>
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">Website URL</Label>
              <Input value={websiteUrl} onChange={e => setWebsiteUrl(e.target.value)} placeholder="https://www.ihre-firma.de" className="rounded-none border-gray-300" data-testid="website-url-input" disabled={isVerified} />
            </div>
            {!isVerified && (
              <Button onClick={handleSetWebsite} disabled={saving || !websiteUrl.trim()} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-6 py-3 font-bold" data-testid="set-website-btn">
                {saving ? '...' : (domain ? 'Update' : 'Set Domain')}
              </Button>
            )}
          </div>
        </div>

        {/* Step 2: Verify (only show if domain is set and not verified) */}
        {domain && !isVerified && (
          <div className="border border-gray-200 bg-white p-8" data-testid="verify-section">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 bg-[#002FA7] flex items-center justify-center text-white font-bold text-sm">2</div>
              <h2 className="font-clash text-xl font-bold text-[#0A0A0A]">Verify Ownership</h2>
            </div>
            <p className="text-sm text-[#4B5563] mb-6">Choose a verification method and follow the instructions. Then click "Verify".</p>

            <Tabs defaultValue="meta_tag">
              <TabsList className="rounded-none border border-gray-200 bg-white mb-6">
                <TabsTrigger value="meta_tag" className="rounded-none data-[state=active]:bg-[#002FA7] data-[state=active]:text-white">
                  <Code size={14} className="mr-2" />Meta Tag
                </TabsTrigger>
                <TabsTrigger value="dns_txt" className="rounded-none data-[state=active]:bg-[#002FA7] data-[state=active]:text-white">
                  <Server size={14} className="mr-2" />DNS TXT Record
                </TabsTrigger>
              </TabsList>

              <TabsContent value="meta_tag">
                <div className="space-y-4">
                  <div className="bg-[#F9FAFB] border border-gray-200 p-4">
                    <p className="text-sm text-[#0A0A0A] font-bold mb-2">Instructions:</p>
                    <ol className="text-sm text-[#4B5563] space-y-2 list-decimal list-inside">
                      <li>Copy the meta tag below</li>
                      <li>Paste it into the <code className="bg-gray-200 px-1">&lt;head&gt;</code> section of your homepage ({domain})</li>
                      <li>Click "Verify with Meta Tag"</li>
                    </ol>
                  </div>
                  <div className="relative">
                    <pre className="bg-[#0A0A0A] text-green-400 p-4 text-sm font-mono overflow-x-auto" data-testid="meta-tag-code">
{`<meta name="chatembed-verify" content="${token}">`}
                    </pre>
                    <Button onClick={() => handleCopy(`<meta name="chatembed-verify" content="${token}">`, 'meta')} variant="outline" size="sm" className="absolute top-2 right-2 rounded-none bg-white/10 border-white/20 text-white hover:bg-white/20" data-testid="copy-meta-btn">
                      {copied === 'meta' ? <><Check size={12} className="mr-1" />Copied</> : <><Copy size={12} className="mr-1" />Copy</>}
                    </Button>
                  </div>
                  <Button onClick={() => handleVerify('meta_tag')} disabled={verifying} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-6 py-3 font-bold" data-testid="verify-meta-btn">
                    {verifying ? 'Checking...' : 'Verify with Meta Tag'}
                  </Button>
                </div>
              </TabsContent>

              <TabsContent value="dns_txt">
                <div className="space-y-4">
                  <div className="bg-[#F9FAFB] border border-gray-200 p-4">
                    <p className="text-sm text-[#0A0A0A] font-bold mb-2">Instructions:</p>
                    <ol className="text-sm text-[#4B5563] space-y-2 list-decimal list-inside">
                      <li>Go to your domain's DNS settings (at your hosting provider)</li>
                      <li>Add a new TXT record with the value below</li>
                      <li>Wait 5-10 minutes for DNS propagation</li>
                      <li>Click "Verify with DNS"</li>
                    </ol>
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2">Record Type: TXT</p>
                    <p className="text-xs text-[#4B5563] mb-1">Host: <code className="bg-gray-200 px-1">@</code> or <code className="bg-gray-200 px-1">{domain}</code></p>
                  </div>
                  <div className="relative">
                    <pre className="bg-[#0A0A0A] text-green-400 p-4 text-sm font-mono overflow-x-auto" data-testid="dns-txt-code">
{`chatembed-verify=${token}`}
                    </pre>
                    <Button onClick={() => handleCopy(`chatembed-verify=${token}`, 'dns')} variant="outline" size="sm" className="absolute top-2 right-2 rounded-none bg-white/10 border-white/20 text-white hover:bg-white/20" data-testid="copy-dns-btn">
                      {copied === 'dns' ? <><Check size={12} className="mr-1" />Copied</> : <><Copy size={12} className="mr-1" />Copy</>}
                    </Button>
                  </div>
                  <Button onClick={() => handleVerify('dns_txt')} disabled={verifying} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-6 py-3 font-bold" data-testid="verify-dns-btn">
                    {verifying ? 'Checking DNS...' : 'Verify with DNS'}
                  </Button>
                </div>
              </TabsContent>
            </Tabs>

            {/* Verification Result */}
            {result && (
              <div className={`mt-6 border p-4 flex items-start gap-3 ${result.verified ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'}`} data-testid="verify-result">
                {result.verified ? <CheckCircle size={20} className="text-green-600 flex-shrink-0 mt-0.5" /> : <XCircle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />}
                <div>
                  <p className={`font-bold text-sm ${result.verified ? 'text-green-800' : 'text-red-800'}`}>
                    {result.verified ? 'Verification Successful!' : 'Verification Failed'}
                  </p>
                  <p className={`text-sm ${result.verified ? 'text-green-700' : 'text-red-700'}`}>{result.details}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Info Box */}
        <div className="border border-gray-200 bg-[#F9FAFB] p-6">
          <div className="flex items-start gap-3">
            <Shield size={20} className="text-[#002FA7] flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-sm text-[#0A0A0A] mb-1">Why domain verification?</p>
              <p className="text-sm text-[#4B5563]">Domain verification ensures that only legitimate website owners can create chatbots. Your embed widget will only load on your verified domain, preventing unauthorized use.</p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
