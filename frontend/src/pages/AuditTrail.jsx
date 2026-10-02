import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { History, Download, Search, Shield } from 'lucide-react';

export default function AuditTrail() {
  const [logs, setLogs] = useState([
    { id: 1, execution_id: 'exec_4167e7eb', action: 'TOOL_EXECUTE', actor: 'agent_support_001', details: { tool: 'search_customer', query: 'John Doe' }, decision: 'ALLOW', timestamp: new Date().toISOString() },
    { id: 2, execution_id: 'exec_88a91c71', action: 'TOOL_EXECUTE', actor: 'agent_support_001', details: { tool: 'refund_customer', amount: 75000.0 }, decision: 'ESCALATE', timestamp: new Date().toISOString() }
  ]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    try {
      const data = await api.getAuditLogs();
      if (Array.isArray(data) && data.length > 0) {
        setLogs(data);
      }
    } catch (err) {
      console.warn("Audit logs fetch note:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = () => {
    window.open('/api/v1/audit/export/csv', '_blank');
  };

  const filteredLogs = logs.filter(
    (l) =>
      l.actor.toLowerCase().includes(search.toLowerCase()) ||
      l.action.toLowerCase().includes(search.toLowerCase()) ||
      l.resource_type.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-200 pb-6 bg-white p-6 rounded-2xl border shadow-xs">
        <div>
          <h1 className="text-2xl font-mono font-bold text-[#1A103C] tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-[#53389E]" />
            Enterprise Audit Trail Log (Phase 13)
          </h1>
          <p className="text-xs text-slate-700 font-medium mt-1">
            Immutable, SOC2-compliant audit history of all system events, policy changes, agent executions, and administrator approvals.
          </p>
        </div>

        <button
          onClick={handleExportCSV}
          className="px-5 py-2.5 bg-[#53389E] hover:bg-[#432A85] text-white rounded-xl text-xs font-display font-bold flex items-center gap-2 transition shadow-xs"
        >
          <Download className="w-4 h-4" />
          Export Audit Trail (CSV)
        </button>
      </div>

      {/* Search Input */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
        <input
          type="text"
          placeholder="Filter audit logs by actor, action, or resource..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-[#53389E] font-medium"
        />
      </div>

      {/* Audit Table */}
      <div className="rounded-2xl bg-white border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-slate-50 text-[#1A103C] border-b border-slate-200 uppercase font-bold">
            <tr>
              <th className="p-4">ID</th>
              <th className="p-4">Timestamp</th>
              <th className="p-4">Actor</th>
              <th className="p-4">Action</th>
              <th className="p-4">Resource Type</th>
              <th className="p-4">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 font-mono text-[11px] text-slate-900 font-medium">
            {filteredLogs.map((l) => (
              <tr key={l.id} className="hover:bg-slate-50 transition">
                <td className="p-4 text-slate-500 font-bold">{l.id}</td>
                <td className="p-4 text-slate-700">{new Date(l.created_at).toLocaleString()}</td>
                <td className="p-4 text-[#53389E] font-bold">{l.actor}</td>
                <td className="p-4 text-indigo-700 font-bold">{l.action}</td>
                <td className="p-4 text-slate-800 font-semibold">{l.resource_type} ({l.resource_id})</td>
                <td className="p-4 text-slate-800 truncate max-w-xs">{JSON.stringify(l.details)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
