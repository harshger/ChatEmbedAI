import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import Header from '../components/Header';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

export default function VerifyEmail() {
  const { t } = useTranslation();
  const { checkAuth } = useAuth();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) { setStatus('error'); setError('No verification token provided.'); return; }
    api.verifyEmail(token)
      .then(() => { setStatus('success'); checkAuth(); })
      .catch(() => { setStatus('error'); setError('Invalid or expired verification token.'); });
  }, [token, checkAuth]);

  return (
    <div className="min-h-screen bg-[#F9FAFB]" data-testid="verify-email-page">
      <Header />
      <div className="flex items-center justify-center pt-32 pb-32 px-6">
        <div className="w-full max-w-md border border-gray-200 bg-white p-8 text-center">
          {status === 'loading' && (
            <div className="space-y-4">
              <Loader2 size={48} className="text-[#002FA7] mx-auto animate-spin" />
              <p className="text-[#4B5563]">Verifying your email...</p>
            </div>
          )}
          {status === 'success' && (
            <div className="space-y-4">
              <CheckCircle size={48} className="text-green-600 mx-auto" />
              <h1 className="font-clash text-2xl font-bold tracking-tight text-[#0A0A0A]">{t.auth.verify_success}</h1>
              <Link to="/dashboard" className="inline-block mt-4 bg-[#002FA7] text-white px-6 py-3 font-bold hover:bg-[#0040D6] transition-colors" data-testid="go-to-dashboard">
                Go to Dashboard
              </Link>
            </div>
          )}
          {status === 'error' && (
            <div className="space-y-4">
              <XCircle size={48} className="text-[#E60000] mx-auto" />
              <h1 className="font-clash text-2xl font-bold tracking-tight text-[#E60000]">Verification Failed</h1>
              <p className="text-sm text-[#4B5563]">{error}</p>
              <Link to="/login" className="inline-block mt-4 text-[#002FA7] font-bold hover:underline" data-testid="go-to-login">
                {t.auth.back_to_login}
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
