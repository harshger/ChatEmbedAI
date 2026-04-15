import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import Header from '../components/Header';
import { ArrowLeft, Lock, CheckCircle } from 'lucide-react';

export default function ResetPassword() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 8) { setError('Password must be at least 8 characters.'); return; }
    if (password !== confirmPassword) { setError('Passwords do not match.'); return; }
    setLoading(true);
    setError('');
    try {
      await api.resetPassword(token, password);
      setSuccess(true);
    } catch {
      setError('Invalid or expired token. Please request a new reset link.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-[#F9FAFB]" data-testid="reset-password-page">
        <Header />
        <div className="flex items-center justify-center pt-32 pb-32 px-6">
          <div className="w-full max-w-md border border-gray-200 bg-white p-8 text-center">
            <p className="text-[#4B5563] mb-4">No reset token provided.</p>
            <Link to="/forgot-password" className="text-[#002FA7] font-bold hover:underline">{t.auth.forgot_title}</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F9FAFB]" data-testid="reset-password-page">
      <Header />
      <div className="flex items-center justify-center pt-32 pb-32 px-6">
        <div className="w-full max-w-md">
          <div className="border border-gray-200 bg-white p-8" data-testid="reset-password-form">
            {success ? (
              <div className="text-center space-y-4">
                <CheckCircle size={48} className="text-green-600 mx-auto" />
                <h1 className="font-clash text-2xl font-bold tracking-tight text-[#0A0A0A]">{t.auth.reset_success}</h1>
                <Link to="/login" className="inline-flex items-center gap-2 text-[#002FA7] font-bold text-sm hover:underline" data-testid="go-to-login">
                  <ArrowLeft size={16} /> {t.auth.back_to_login}
                </Link>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-[#002FA7] flex items-center justify-center"><Lock size={20} className="text-white" /></div>
                  <h1 className="font-clash text-2xl font-bold tracking-tight text-[#0A0A0A]">{t.auth.reset_title}</h1>
                </div>
                {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 mb-6" data-testid="reset-error">{error}</div>}
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.auth.reset_new_password}</Label>
                    <Input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} className="rounded-none border-gray-300 focus:ring-2 focus:ring-[#002FA7] focus:border-transparent" data-testid="reset-new-password" />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.auth.reset_confirm}</Label>
                    <Input type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required minLength={8} className="rounded-none border-gray-300 focus:ring-2 focus:ring-[#002FA7] focus:border-transparent" data-testid="reset-confirm-password" />
                  </div>
                  <Button type="submit" disabled={loading} className="w-full bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none py-3 font-bold" data-testid="reset-submit-button">
                    {loading ? '...' : t.auth.reset_btn}
                  </Button>
                </form>
                <Link to="/login" className="inline-flex items-center gap-2 text-[#4B5563] text-sm hover:text-[#0A0A0A] mt-6" data-testid="back-to-login-link">
                  <ArrowLeft size={16} /> {t.auth.back_to_login}
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
