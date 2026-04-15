import React, { useEffect, useState } from 'react';
import { useTranslation } from '../lib/i18n';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Users, UserPlus, Trash2, Lock } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

export default function Team() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('member');
  const [inviting, setInviting] = useState(false);

  useEffect(() => {
    api.getTeam().then(data => { setMembers(data); setLoading(false); }).catch(() => { setError(t.team.agency_only); setLoading(false); });
  }, [t.team.agency_only]);

  const handleInvite = async () => {
    if (!email.trim()) return;
    setInviting(true);
    try {
      const member = await api.inviteTeamMember({ email, role });
      setMembers(prev => [...prev, member]);
      setEmail('');
    } catch (err) {
      console.error('Invite error:', err);
    }
    setInviting(false);
  };

  const handleRemove = async (memberId) => {
    if (!window.confirm('Remove this team member?')) return;
    try {
      await api.removeTeamMember(memberId);
      setMembers(prev => prev.filter(m => m.member_id !== memberId));
    } catch {}
  };

  if (loading) {
    return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 text-center" data-testid="team-locked">
          <Lock size={48} className="text-gray-300 mb-4" />
          <h2 className="font-clash text-xl font-bold text-[#0A0A0A] mb-2">{t.team.title}</h2>
          <p className="text-[#4B5563]">{error}</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="team-page">
        <div className="flex items-center justify-between">
          <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]">{t.team.title}</h1>
        </div>

        {/* Invite form */}
        <div className="border border-gray-200 bg-white p-6">
          <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#4B5563] mb-4">{t.team.invite}</h3>
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="text-xs text-[#4B5563] mb-1 block">{t.team.email}</label>
              <Input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="colleague@company.de" className="rounded-none border-gray-300" data-testid="team-invite-email" />
            </div>
            <div className="w-40">
              <label className="text-xs text-[#4B5563] mb-1 block">{t.team.role}</label>
              <Select value={role} onValueChange={setRole}>
                <SelectTrigger className="rounded-none border-gray-300" data-testid="team-role-select"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="member">{t.team.member}</SelectItem>
                  <SelectItem value="admin">{t.team.admin}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={handleInvite} disabled={inviting || !email.trim()} className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-6 py-2.5 font-bold" data-testid="team-invite-btn">
              <UserPlus size={16} className="mr-2" />
              {inviting ? '...' : t.team.invite}
            </Button>
          </div>
        </div>

        {/* Members list */}
        <div className="border border-gray-200 bg-white" data-testid="team-members-list">
          {members.length === 0 ? (
            <div className="p-12 text-center">
              <Users size={48} className="text-gray-300 mx-auto mb-4" />
              <p className="text-[#4B5563]">{t.team.empty}</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {members.map(member => (
                <div key={member.member_id} className="p-6 flex items-center justify-between" data-testid={`team-member-${member.member_id}`}>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-[#002FA7]/10 flex items-center justify-center">
                      <Users size={18} className="text-[#002FA7]" />
                    </div>
                    <div>
                      <p className="font-bold text-sm text-[#0A0A0A]">{member.email}</p>
                      <p className="text-xs text-[#4B5563] capitalize">{member.role}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant={member.status === 'active' ? 'default' : 'secondary'} className="text-xs rounded-none">
                      {member.status === 'active' ? t.team.active : t.team.invited}
                    </Badge>
                    <Button variant="outline" size="sm" className="rounded-none text-red-500 hover:text-red-700 hover:bg-red-50" onClick={() => handleRemove(member.member_id)} data-testid={`remove-member-${member.member_id}`}>
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
