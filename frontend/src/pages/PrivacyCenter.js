import React, { useState } from 'react';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Download, Trash2, Settings, CheckCircle } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

export default function PrivacyCenter() {
  const { t } = useTranslation();
  const { logout } = useAuth();
  const [showDelete, setShowDelete] = useState(false);
  const [confirmation, setConfirmation] = useState('');
  const [exporting, setExporting] = useState(false);
  const [exported, setExported] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleExport = async () => {
    setExporting(true);
    setExported(false);
    try {
      const data = await api.exportData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chatembed-data-export-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      setExported(true);
    } catch {}
    setExporting(false);
  };

  const handleDelete = async () => {
    if (confirmation !== 'LÖSCHEN') return;
    setDeleting(true);
    try {
      await api.deleteAccount('LÖSCHEN');
      setShowDelete(false);
      logout();
    } catch {}
    setDeleting(false);
  };

  const openCookieSettings = () => {
    localStorage.removeItem('cookie_consent');
    window.location.reload();
  };

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="privacy-center-page">
        <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">{t.privacy_center.title}</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border border-gray-200">
          <div className="p-8 bg-white border border-gray-200">
            <Download size={24} className="text-[#002FA7] mb-4" />
            <h3 className="font-bold text-[#0A0A0A] mb-2">{t.privacy_center.export_btn}</h3>
            <p className="text-sm text-[#4B5563] mb-6">Export all your data as JSON.</p>
            <Button onClick={handleExport} disabled={exporting} variant="outline" className="rounded-none border-gray-300 font-bold" data-testid="export-data-btn">
              {exporting ? '...' : exported ? <><CheckCircle size={14} className="mr-1 text-green-600" />Exported</> : t.privacy_center.export_btn}
            </Button>
            {exported && <p className="text-xs text-green-700 mt-2" data-testid="export-success-msg">Art. 20 DSGVO — Data exported successfully.</p>}
          </div>
          <div className="p-8 bg-white border border-gray-200">
            <Trash2 size={24} className="text-[#E60000] mb-4" />
            <h3 className="font-bold text-[#0A0A0A] mb-2">{t.privacy_center.delete_btn}</h3>
            <p className="text-sm text-[#4B5563] mb-6">{t.privacy_center.delete_confirm}</p>
            <Button onClick={() => setShowDelete(true)} variant="outline" className="rounded-none border-[#E60000] text-[#E60000] hover:bg-red-50 font-bold" data-testid="delete-account-btn">
              {t.privacy_center.delete_btn}
            </Button>
          </div>
          <div className="p-8 bg-white border border-gray-200">
            <Settings size={24} className="text-[#002FA7] mb-4" />
            <h3 className="font-bold text-[#0A0A0A] mb-2">{t.privacy_center.consent_btn}</h3>
            <p className="text-sm text-[#4B5563] mb-6">Manage your cookie preferences.</p>
            <Button onClick={openCookieSettings} variant="outline" className="rounded-none border-gray-300 font-bold" data-testid="manage-consent-btn">
              {t.privacy_center.consent_btn}
            </Button>
          </div>
        </div>

        <Dialog open={showDelete} onOpenChange={setShowDelete}>
          <DialogContent className="rounded-none">
            <DialogHeader>
              <DialogTitle className="font-clash text-xl font-bold text-[#E60000]">{t.privacy_center.delete_btn}</DialogTitle>
              <DialogDescription>{t.privacy_center.delete_confirm}</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <p className="text-sm text-[#4B5563]">{t.privacy_center.type_confirm}</p>
              <Input value={confirmation} onChange={e => setConfirmation(e.target.value)} placeholder="LÖSCHEN" className="rounded-none border-gray-300" data-testid="delete-confirmation-input" />
              <div className="flex gap-3">
                <Button onClick={() => setShowDelete(false)} variant="outline" className="rounded-none">Cancel</Button>
                <Button onClick={handleDelete} disabled={confirmation !== 'LÖSCHEN' || deleting} className="rounded-none bg-[#E60000] text-white hover:bg-red-700" data-testid="confirm-delete-btn">
                  {deleting ? '...' : t.privacy_center.delete_btn}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
