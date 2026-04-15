import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import Header from '../components/Header';
import { ArrowLeft, Mail, CheckCircle } from 'lucide-react';

export default function ForgotPassword() {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [mockToken, setMockToken] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await api.forgotPassword(email);
      setSent(true);
      if (data.mock_token) setMockToken(data.mock_token);
    } catch {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F9FAFB]" data-testid="forgot-password-page">
      <Header />
      <div className="flex items-center justify-center pt-32 pb-32 px-6">
        <div className="w-full max-w-md">
          <div className="border border-gray-200 bg-white p-8" data-testid="forgot-password-form">
            {sent ? (
              <div className="text-center space-y-4">
                <CheckCircle size={48} className="text-green-600 mx-auto" />
                <h1 className="font-clash text-2xl font-bold tracking-tight text-[#0A0A0A]">{t.auth.forgot_success}</h1>
                <p className="text-sm text-[#4B5563]">Check your email for the reset link.</p>
                {mockToken && (
                  <div className="mt-6 bg-[#F9FAFB] border border-gray-200 p-4 text-left">
                    <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2">Demo Mode — Reset Link</p>
                    <Link to={`/reset-password?token=${mockToken}`} className="text-[#002FA7] text-sm font-bold hover:underline break-all" data-testid="mock-reset-link">
                      Click here to reset password
                    </Link>
                  </div>
                )}
                <Link to="/login" className="inline-flex items-center gap-2 text-[#002FA7] font-bold text-sm hover:underline mt-4" data-testid="back-to-login-link">
                  <ArrowLeft size={16} /> {t.auth.back_to_login}
                </Link>
              </div>
            ) : (
              <>
                <Link to="/login" className="inline-flex items-center gap-2 text-[#4B5563] text-sm hover:text-[#0A0A0A] mb-6" data-testid="back-link">
                  <ArrowLeft size={16} /> {t.auth.back_to_login}
                </Link>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-[#002FA7] flex items-center justify-center"><Mail size={20} className="text-white" /></div>
                  <h1 className="font-clash text-2xl font-bold tracking-tight text-[#0A0A0A]">{t.auth.forgot_title}</h1>
                </div>
                <p className="text-sm text-[#4B5563] mb-6">{t.auth.forgot_desc}</p>
                {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 mb-6" data-testid="forgot-error">{error}</div>}
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.auth.email}</Label>
                    <Input type="email" value={email} onChange={e => setEmail(e.target.value)} required className="rounded-none border-gray-300 focus:ring-2 focus:ring-[#002FA7] focus:border-transparent" data-testid="forgot-email" />
                  </div>
                  <Button type="submit" disabled={loading} className="w-full bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none py-3 font-bold" data-testid="forgot-submit-button">
                    {loading ? '...' : t.auth.forgot_btn}
                  </Button>
                </form>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
