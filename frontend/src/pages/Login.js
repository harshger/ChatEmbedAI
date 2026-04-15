import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import Header from '../components/Header';

export default function Login() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await api.login({ email, password });
      login(data, data.session_token);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div className="min-h-screen bg-[#F9FAFB]" data-testid="login-page">
      <Header />
      <div className="flex items-center justify-center pt-32 pb-32 px-6">
        <div className="w-full max-w-md">
          <div className="border border-gray-200 bg-white p-8" data-testid="login-form">
            <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A] mb-8">{t.auth.login_title}</h1>

            {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 mb-6" data-testid="login-error">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.auth.email}</Label>
                <Input type="email" value={email} onChange={e => setEmail(e.target.value)} required className="rounded-none border-gray-300 focus:ring-2 focus:ring-[#002FA7] focus:border-transparent" data-testid="login-email" />
              </div>
              <div>
                <Label className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-2 block">{t.auth.password}</Label>
                <Input type="password" value={password} onChange={e => setPassword(e.target.value)} required className="rounded-none border-gray-300 focus:ring-2 focus:ring-[#002FA7] focus:border-transparent" data-testid="login-password" />
              </div>
              <Button type="submit" disabled={loading} className="w-full bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none py-3 font-bold" data-testid="login-submit-button">
                {loading ? '...' : t.auth.login_btn}
              </Button>
            </form>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-200" /></div>
              <div className="relative flex justify-center text-xs uppercase tracking-wider"><span className="bg-white px-3 text-[#4B5563]">{t.auth.or}</span></div>
            </div>

            <Button onClick={handleGoogle} variant="outline" className="w-full rounded-none border-gray-300 py-3 font-bold hover:bg-[#F3F4F6]" data-testid="google-login-button">
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
              {t.auth.google}
            </Button>

            <p className="mt-6 text-sm text-[#4B5563] text-center">
              {t.auth.no_account} <Link to="/signup" className="text-[#002FA7] font-bold hover:underline" data-testid="signup-link">{t.auth.signup_title}</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
