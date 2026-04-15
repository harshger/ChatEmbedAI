import React, { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./lib/auth";
import CookieConsent from "./components/CookieConsent";

// Pages
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import AuthCallback from "./pages/AuthCallback";
import Dashboard from "./pages/Dashboard";
import ChatbotCreate from "./pages/ChatbotCreate";
import ChatbotEdit from "./pages/ChatbotEdit";
import Pricing from "./pages/Pricing";
import Impressum from "./pages/Impressum";
import Datenschutz from "./pages/Datenschutz";
import AGB from "./pages/AGB";
import AVV from "./pages/AVV";
import { PrivacyPolicy, Terms } from "./pages/LegalEN";
import Billing from "./pages/Billing";
import Analytics from "./pages/Analytics";
import PrivacyCenter from "./pages/PrivacyCenter";
import Templates from "./pages/Templates";
import Team from "./pages/Team";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import VerifyEmail from "./pages/VerifyEmail";
import AISettings from "./pages/AISettings";
import DomainVerification from "./pages/DomainVerification";
import Conversations from "./pages/Conversations";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F9FAFB] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function AppRouter() {
  const location = useLocation();

  // CRITICAL: Detect session_id in hash synchronously during render
  // This prevents race conditions with ProtectedRoute
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }

  return (
    <>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/impressum" element={<Impressum />} />
        <Route path="/datenschutz" element={<Datenschutz />} />
        <Route path="/agb" element={<AGB />} />
        <Route path="/avv" element={<AVV />} />
        <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/dashboard/new" element={<ProtectedRoute><ChatbotCreate /></ProtectedRoute>} />
        <Route path="/dashboard/chatbot/:id" element={<ProtectedRoute><ChatbotEdit /></ProtectedRoute>} />
        <Route path="/dashboard/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
        <Route path="/dashboard/billing" element={<ProtectedRoute><Billing /></ProtectedRoute>} />
        <Route path="/dashboard/templates" element={<ProtectedRoute><Templates /></ProtectedRoute>} />
        <Route path="/dashboard/team" element={<ProtectedRoute><Team /></ProtectedRoute>} />
        <Route path="/dashboard/ai-settings" element={<ProtectedRoute><AISettings /></ProtectedRoute>} />
        <Route path="/dashboard/conversations" element={<ProtectedRoute><Conversations /></ProtectedRoute>} />
        <Route path="/dashboard/verify-domain" element={<ProtectedRoute><DomainVerification /></ProtectedRoute>} />
        <Route path="/account/privacy" element={<ProtectedRoute><PrivacyCenter /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <CookieConsent />
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
