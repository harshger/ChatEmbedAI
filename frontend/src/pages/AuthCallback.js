import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';

export default function AuthCallback() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      const hash = window.location.hash;
      const sessionId = hash.split('session_id=')[1];
      if (!sessionId) {
        navigate('/login');
        return;
      }

      try {
        const data = await api.googleSession(sessionId);
        login(data, data.session_token);
        // Clean hash and navigate
        window.history.replaceState(null, '', '/dashboard');
        navigate('/dashboard', { state: { user: data }, replace: true });
      } catch (err) {
        console.error('Auth callback error:', err);
        navigate('/login');
      }
    };

    processAuth();
  }, [navigate, login]);

  return (
    <div className="min-h-screen bg-[#F9FAFB] flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-[#4B5563]">Authenticating...</p>
      </div>
    </div>
  );
}
