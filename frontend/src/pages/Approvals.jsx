import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ShieldAlert, CheckCircle2, XCircle, Clock, AlertTriangle, User } from 'lucide-react';

export default function Approvals() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('PENDING');

  useEffect(() => {
    loadApprovals();
  }, [filter]);

  const loadApprovals = async () => {
    try {
      const data = await api.getApprovals(filter === 'ALL' ? null : filter);
      setApprovals(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (approvalId, action) => {
    const reason = action === 'REJECT' ? prompt('Enter reason for rejection:') : null;
    if (action === 'REJECT' && !reason) return;

    try {
      await api.respondApproval(approvalId, action, reason);
      loadApprovals();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-rillet-border pb-6">
        <div>
          <h1 className="text-2xl font-display font-bold text-white tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-amber-400" />
            Human Approval Queue (Phase 5)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Human-in-the-Loop security queue for high-risk AI agent tool calls requiring explicit authorization before execution.
          </p>
        </div>

        {/* Filter Buttons */}
        <div className="flex bg-rillet-card border border-rillet-border rounded-xl p-1 text-xs font-mono">
          {['PENDING', 'APPROVED', 'REJECTED', 'ALL'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-1.5 rounded-lg font-semibold transition ${
                filter === f ? 'bg-[#644EFF] text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 font-mono text-xs">Loading Escalation Queue...</div>
      ) : approvals.length === 0 ? (
        <div className="p-16 text-center text-slate-500 bg-rillet-card border border-rillet-border rounded-2xl text-xs font-mono">
          No approval requests found for filter: <span className="text-white font-bold">{filter}</span>.
        </div>
      ) : (
        <div className="space-y-5">
          {approvals.map((app) => (
            <div
              key={app.id}
              className="p-6 rounded-2xl bg-rillet-card border border-rillet-border hover:border-[#644EFF]/40 transition space-y-4 shadow-rillet-card"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rillet-border pb-4">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-[#8170FF] font-bold">{app.execution_id}</span>
                  <span className="text-sm font-display font-bold text-slate-100">{app.agent_name}</span>
                  <span className="text-xs text-slate-400 font-mono">({app.tool_name})</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    Risk Score: {app.risk_score} / 100
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-display font-bold uppercase ${
                    app.status === 'PENDING' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse' :
                    app.status === 'APPROVED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                    'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                  }`}>
                    {app.status}
                  </span>
                </div>
              </div>

              {/* Tool Payload Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                <div>
                  <span className="text-slate-400 text-[10px] uppercase tracking-wider block mb-1">Tool Input Parameters</span>
                  <pre className="p-4 bg-rillet-bg rounded-xl border border-rillet-border text-slate-300 text-[11px] overflow-x-auto">
                    {JSON.stringify(app.tool_input, null, 2)}
                  </pre>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] uppercase tracking-wider block mb-1">Audit & Timestamp</span>
                  <div className="p-4 bg-rillet-bg rounded-xl border border-rillet-border text-slate-400 space-y-1.5 text-[11px]">
                    <div><span className="text-slate-500">Requested At:</span> {new Date(app.requested_at).toLocaleString()}</div>
                    {app.responded_at && <div><span className="text-slate-500">Responded At:</span> {new Date(app.responded_at).toLocaleString()}</div>}
                    {app.approved_by && <div><span className="text-slate-500">Authorized By:</span> <span className="text-emerald-400">{app.approved_by}</span></div>}
                    {app.rejection_reason && <div><span className="text-slate-500">Rejection Reason:</span> <span className="text-rose-400">{app.rejection_reason}</span></div>}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              {app.status === 'PENDING' && (
                <div className="flex justify-end gap-3 pt-2">
                  <button
                    onClick={() => handleAction(app.id, 'REJECT')}
                    className="px-5 py-2.5 bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 font-display font-semibold rounded-xl text-xs transition flex items-center gap-2"
                  >
                    <XCircle className="w-4 h-4" />
                    Reject Action
                  </button>
                  <button
                    onClick={() => handleAction(app.id, 'APPROVE')}
                    className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-display font-bold rounded-xl text-xs transition flex items-center gap-2 shadow-lg shadow-emerald-500/20"
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
