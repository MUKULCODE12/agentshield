import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ShieldAlert, CheckCircle2, XCircle, Clock, AlertTriangle, User } from 'lucide-react';

export default function Approvals() {
  const [approvals, setApprovals] = useState([
    { id: 1, execution_id: 'exec_88a91c71', agent_id: 1, agent_name: 'Customer Support AI Agent', tool_name: 'refund_customer', tool_input: { customer_id: 'CUST_9921', amount: 75000.0, reason: 'VIP Order refund request' }, risk_score: 85.0, status: 'PENDING', requested_at: new Date().toISOString() }
  ]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('PENDING');

  useEffect(() => {
    loadApprovals();
  }, [filter]);

  const loadApprovals = async () => {
    try {
      const data = await api.getApprovals(filter === 'ALL' ? null : filter);
      if (Array.isArray(data) && data.length > 0) {
        setApprovals(data);
      }
    } catch (err) {
      console.warn("Approvals fetch note:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (approvalId, action) => {
    const reason = action === 'REJECT' ? prompt('Enter reason for rejection:') : null;
    if (action === 'REJECT' && !reason) return;

    // Optimistic UI update
    const newStatus = action === 'APPROVE' ? 'APPROVED' : 'REJECTED';
    setApprovals(prev => prev.map(a => a.id === approvalId ? {
      ...a,
      status: newStatus,
      responded_at: new Date().toISOString(),
      approved_by: action === 'APPROVE' ? 'Security Admin' : undefined,
      rejection_reason: reason || undefined
    } : a));

    try {
      await api.respondApproval(approvalId, action, reason);
      loadApprovals();
    } catch (err) {
      console.warn("Approval action applied locally:", err);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-200 pb-6 bg-white p-6 rounded-2xl border shadow-xs">
        <div>
          <h1 className="text-2xl font-mono font-bold text-[#1A103C] tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-amber-600" />
            Human Approval Queue (Phase 5)
          </h1>
          <p className="text-xs text-slate-700 font-medium mt-1">
            Human-in-the-Loop security queue for high-risk AI agent tool calls requiring explicit authorization before execution.
          </p>
        </div>

        {/* Filter Buttons */}
        <div className="flex bg-slate-100 border border-slate-200 rounded-xl p-1 text-xs font-mono">
          {['PENDING', 'APPROVED', 'REJECTED', 'ALL'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-1.5 rounded-lg font-semibold transition ${
                filter === f ? 'bg-[#53389E] text-white shadow-sm' : 'text-slate-600 hover:text-[#1A103C]'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-500 font-mono text-xs">Loading Escalation Queue...</div>
      ) : approvals.length === 0 ? (
        <div className="p-16 text-center text-slate-600 bg-white border border-slate-200 rounded-2xl text-xs font-mono shadow-xs">
          No approval requests found for filter: <span className="text-[#1A103C] font-bold">{filter}</span>.
        </div>
      ) : (
        <div className="space-y-5">
          {approvals.map((app) => (
            <div
              key={app.id}
              className="p-6 rounded-2xl bg-white border border-slate-200 hover:border-[#53389E]/40 transition space-y-4 shadow-xs"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-4">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-[#53389E] font-bold">{app.execution_id}</span>
                  <span className="text-sm font-display font-bold text-[#1A103C]">{app.agent_name}</span>
                  <span className="text-xs text-slate-500 font-mono">({app.tool_name})</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-100 text-amber-800 border border-amber-300">
                    Risk Score: {app.risk_score} / 100
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-display font-bold uppercase ${
                    app.status === 'PENDING' ? 'bg-amber-100 text-amber-800 border border-amber-300 animate-pulse' :
                    app.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' :
                    'bg-rose-100 text-rose-800 border border-rose-300'
                  }`}>
                    {app.status}
                  </span>
                </div>
              </div>

              {/* Tool Payload Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                <div>
                  <span className="text-slate-500 text-[10px] uppercase tracking-wider block mb-1">Tool Input Parameters</span>
                  <pre className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 text-[11px] overflow-x-auto font-semibold">
                    {JSON.stringify(app.tool_input, null, 2)}
                  </pre>
                </div>
                <div>
                  <span className="text-slate-500 text-[10px] uppercase tracking-wider block mb-1">Audit & Timestamp</span>
                  <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-slate-700 space-y-1.5 text-[11px] font-medium">
                    <div><span className="text-slate-500">Requested At:</span> {new Date(app.requested_at).toLocaleString()}</div>
                    {app.responded_at && <div><span className="text-slate-500">Responded At:</span> {new Date(app.responded_at).toLocaleString()}</div>}
                    {app.approved_by && <div><span className="text-slate-500">Authorized By:</span> <span className="text-emerald-700 font-bold">{app.approved_by}</span></div>}
                    {app.rejection_reason && <div><span className="text-slate-500">Rejection Reason:</span> <span className="text-rose-700 font-bold">{app.rejection_reason}</span></div>}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              {app.status === 'PENDING' && (
                <div className="flex justify-end gap-3 pt-2">
                  <button
                    onClick={() => handleAction(app.id, 'REJECT')}
                    className="px-5 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-300 font-display font-semibold rounded-xl text-xs transition flex items-center gap-2"
                  >
                    <XCircle className="w-4 h-4" />
                    Reject Action
                  </button>
                  <button
                    onClick={() => handleAction(app.id, 'APPROVE')}
                    className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-display font-bold rounded-xl text-xs transition flex items-center gap-2 shadow-lg shadow-emerald-500/20"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    Approve & Authorize Execution
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
