import React, { useEffect, useState, useCallback } from 'react';
import { useTranslation } from '../lib/i18n';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { MessageSquare, Search, Download, ChevronLeft, ChevronRight, Calendar, Bot, User, X, Filter } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

function ConversationThread({ session, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getConversation(session.session_id);
        setDetail(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [session.session_id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="w-6 h-6 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="conversation-thread">
      <div className="flex items-center justify-between border-b border-gray-200 pb-3">
        <div>
          <h3 className="font-bold text-[#0A0A0A]">{session.chatbot_name}</h3>
          <p className="text-xs text-[#4B5563] mt-0.5">{session.first_message_at?.slice(0, 16).replace('T', ' ')}</p>
        </div>
        <Badge variant="outline" className="rounded-none text-xs">{detail?.message_count || 0} messages</Badge>
      </div>
      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2" data-testid="message-list">
        {detail?.messages?.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role !== 'user' && (
              <div className="w-7 h-7 bg-[#002FA7] flex items-center justify-center flex-shrink-0">
                <Bot size={14} className="text-white" />
              </div>
            )}
            <div
              className={`max-w-[75%] px-3 py-2 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-[#002FA7] text-white'
                  : 'bg-[#F3F4F6] text-[#0A0A0A]'
              }`}
              data-testid={`msg-${msg.role}-${i}`}
            >
              {msg.content}
            </div>
            {msg.role === 'user' && (
              <div className="w-7 h-7 bg-[#4B5563] flex items-center justify-center flex-shrink-0">
                <User size={14} className="text-white" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Conversations() {
  const { t } = useTranslation();
  const [conversations, setConversations] = useState([]);
  const [chatbots, setChatbots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [chatbotFilter, setChatbotFilter] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [selectedSession, setSelectedSession] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const loadConversations = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (chatbotFilter && chatbotFilter !== 'all') params.append('chatbot_id', chatbotFilter);
      if (search) params.append('search', search);
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);
      params.append('page', page);
      params.append('limit', 15);

      const data = await api.getConversations(params.toString());
      setConversations(data.conversations || []);
      setTotalPages(data.pages || 1);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [chatbotFilter, search, dateFrom, dateTo, page]);

  useEffect(() => {
    const loadChatbots = async () => {
      try {
        const bots = await api.getChatbots();
        setChatbots(bots);
      } catch {}
    };
    loadChatbots();
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadConversations();
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const params = new URLSearchParams();
      if (chatbotFilter && chatbotFilter !== 'all') params.append('chatbot_id', chatbotFilter);
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);

      const response = await api.exportConversations(params.toString());
      const blob = new Blob([response], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `conversations-${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    } finally {
      setExporting(false);
    }
  };

  const clearFilters = () => {
    setSearch('');
    setChatbotFilter('all');
    setDateFrom('');
    setDateTo('');
    setPage(1);
  };

  const hasActiveFilters = search || (chatbotFilter && chatbotFilter !== 'all') || dateFrom || dateTo;

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="conversations-page">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-clash text-3xl font-bold tracking-tight text-[#0A0A0A]" data-testid="conversations-title">
              {t.conversations?.title || 'Conversations'}
            </h1>
            <p className="text-[#4B5563] text-sm mt-1">
              {total} {t.conversations?.total_label || 'conversations found'}
            </p>
          </div>
          <Button
            onClick={handleExport}
            disabled={exporting || total === 0}
            className="bg-[#002FA7] text-white hover:bg-[#0040D6] rounded-none px-5 py-2.5 font-bold text-sm"
            data-testid="export-csv-btn"
          >
            <Download size={16} className="mr-2" />
            {exporting ? '...' : (t.conversations?.export_btn || 'Export CSV')}
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white border border-gray-200 p-4 space-y-3">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t.conversations?.search_placeholder || 'Search conversations...'}
                className="pl-10 rounded-none border-gray-300 h-10 text-sm"
                data-testid="search-input"
              />
            </div>
            <Button type="submit" variant="outline" className="rounded-none border-gray-300 h-10 px-4" data-testid="search-btn">
              <Search size={16} />
            </Button>
            <Button
              type="button"
              variant="outline"
              className={`rounded-none border-gray-300 h-10 px-4 ${showFilters ? 'bg-[#002FA7] text-white' : ''}`}
              onClick={() => setShowFilters(!showFilters)}
              data-testid="toggle-filters-btn"
            >
              <Filter size={16} />
            </Button>
          </form>

          {showFilters && (
            <div className="flex flex-wrap gap-3 pt-2 border-t border-gray-100" data-testid="filter-panel">
              <div className="w-48">
                <label className="text-xs font-bold text-[#4B5563] uppercase tracking-wider mb-1 block">Chatbot</label>
                <Select value={chatbotFilter} onValueChange={(v) => { setChatbotFilter(v); setPage(1); }}>
                  <SelectTrigger className="rounded-none border-gray-300 h-9 text-sm" data-testid="chatbot-filter">
                    <SelectValue placeholder="All chatbots" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All chatbots</SelectItem>
                    {chatbots.map(bot => (
                      <SelectItem key={bot.chatbot_id} value={bot.chatbot_id}>{bot.business_name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-bold text-[#4B5563] uppercase tracking-wider mb-1 block">From</label>
                <Input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => { setDateFrom(e.target.value); setPage(1); }}
                  className="rounded-none border-gray-300 h-9 text-sm w-40"
                  data-testid="date-from"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#4B5563] uppercase tracking-wider mb-1 block">To</label>
                <Input
                  type="date"
                  value={dateTo}
                  onChange={(e) => { setDateTo(e.target.value); setPage(1); }}
                  className="rounded-none border-gray-300 h-9 text-sm w-40"
                  data-testid="date-to"
                />
              </div>
              {hasActiveFilters && (
                <div className="flex items-end">
                  <Button variant="ghost" size="sm" onClick={clearFilters} className="text-xs text-[#E60000] h-9" data-testid="clear-filters-btn">
                    <X size={14} className="mr-1" /> Clear
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Conversation List */}
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="w-8 h-8 border-2 border-[#002FA7] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : conversations.length === 0 ? (
          <div className="bg-white border border-gray-200 p-12 text-center" data-testid="empty-conversations">
            <MessageSquare size={48} className="text-gray-300 mx-auto mb-4" />
            <p className="text-[#4B5563] font-bold mb-1">{t.conversations?.empty || 'No conversations yet'}</p>
            <p className="text-sm text-[#9CA3AF]">{t.conversations?.empty_desc || 'Conversations will appear here once visitors use your chatbots.'}</p>
          </div>
        ) : (
          <div className="bg-white border border-gray-200 divide-y divide-gray-100" data-testid="conversation-list">
            {conversations.map((conv) => (
              <button
                key={conv.session_id}
                onClick={() => setSelectedSession(conv)}
                className="w-full text-left p-4 hover:bg-[#F9FAFB] transition-colors flex items-center gap-4 group"
                data-testid={`conv-${conv.session_id}`}
              >
                <div className="w-10 h-10 bg-[#002FA7]/10 flex items-center justify-center flex-shrink-0">
                  <MessageSquare size={18} className="text-[#002FA7]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="font-bold text-sm text-[#0A0A0A] truncate">{conv.chatbot_name}</span>
                    <Badge variant="outline" className="rounded-none text-[10px] flex-shrink-0">
                      {conv.message_count} msg
                    </Badge>
                  </div>
                  <p className="text-sm text-[#4B5563] truncate">{conv.first_message || '—'}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-xs text-[#9CA3AF]">
                    <Calendar size={12} className="inline mr-1" />
                    {conv.last_message_at?.slice(0, 10)}
                  </p>
                  <p className="text-[10px] text-[#9CA3AF] mt-0.5">
                    {conv.last_message_at?.slice(11, 16)}
                  </p>
                </div>
                <ChevronRight size={16} className="text-[#9CA3AF] group-hover:text-[#002FA7] flex-shrink-0 transition-colors" />
              </button>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between" data-testid="pagination">
            <p className="text-sm text-[#4B5563]">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="rounded-none"
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
                data-testid="prev-page-btn"
              >
                <ChevronLeft size={16} />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="rounded-none"
                disabled={page >= totalPages}
                onClick={() => setPage(p => p + 1)}
                data-testid="next-page-btn"
              >
                <ChevronRight size={16} />
              </Button>
            </div>
          </div>
        )}

        {/* Conversation Detail Dialog */}
        <Dialog open={!!selectedSession} onOpenChange={() => setSelectedSession(null)}>
          <DialogContent className="max-w-2xl rounded-none" data-testid="conversation-dialog">
            <DialogHeader>
              <DialogTitle className="font-clash text-xl font-bold text-[#0A0A0A]">
                {t.conversations?.detail_title || 'Conversation'}
              </DialogTitle>
            </DialogHeader>
            {selectedSession && (
              <ConversationThread session={selectedSession} onClose={() => setSelectedSession(null)} />
            )}
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
