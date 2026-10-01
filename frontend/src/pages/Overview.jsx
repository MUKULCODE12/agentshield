import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import {
  Bot,
  Sliders,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Activity,
  Zap
} from 'lucide-react';

export default function Overview() {
  const [stats, setStats] = useState(null);
  const [recentExecutions, setRecentExecutions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [overviewData, execsData] = await Promise.all([
        api.getOverview(),
        api.getRecentExecutions()
      ]);
      setStats(overviewData);
      setRecentExecutions(execsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return (
      <div className="p-12 text-center text-slate-500 font-mono text-xs space-y-2">
        <Activity className="w-6 h-6 animate-spin mx-auto text-[#53389E]" />
        <p>Connecting to Sentinel Rillet Security Stream...</p>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto rillet-grid-bg min-h-screen">
      {/* Page Title & Subtitle */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-6 bg-white/80 p-6 rounded-2xl border">
        <div>
          <h1 className="text-2xl font-mono font-bold text-[#1A103C] tracking-tight">
            AI Fleet Security & Compliance Overview
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time zero-trust verification of autonomous AI agent tool executions, policy alignment, and threat prevention.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3.5 py-1.5 rounded-full bg-[#F4F0FF] border border-[#D8C7FF] text-[#53389E] text-xs font-mono font-bold">
            Live Stream Active
          </span>
        </div>
      </div>

      {/* Banner Notice if Pending Approvals Exist */}
      {stats.pending_approvals > 0 && (
        <div className="p-5 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 animate-bounce" />
            <div>
              <h3 className="font-display font-bold text-amber-900 text-sm">
                Human Approval Required ({stats.pending_approvals} High-Risk Request{stats.pending_approvals > 1 ? 's' : ''})
              </h3>
              <p className="text-xs text-amber-700 mt-0.5">
                Autonomous AI agent invoked high-value tool execution requiring manual security officer authorization.
              </p>
            </div>
          </div>
          <a
            href="/approvals"
            className="px-4 py-2 text-xs font-display font-bold rounded-xl bg-amber-500 text-white hover:bg-amber-600 transition shadow-xs"
          >
            Review Escalation Queue
          </a>
        </div>
      )}

      {/* Rillet-Style Light Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-6 rounded-2xl bg-white border border-slate-200 rillet-card-hover space-y-3">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider">Active AI Fleet</span>
            <Bot className="w-5 h-5 text-[#53389E]" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-mono font-bold text-[#1A103C] tracking-tight">{stats.total_agents}</span>
            <span className="text-xs text-emerald-600 font-mono font-semibold">100% Monitored</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-white border border-slate-200 rillet-card-hover space-y-3">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider">Verified Executions</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-mono font-bold text-emerald-600 tracking-tight">{stats.allowed_count}</span>
            <span className="text-xs text-slate-500 font-mono">Ground-Truth Pass</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-white border border-slate-200 rillet-card-hover space-y-3">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider">Blocked Threats</span>
            <XCircle className="w-5 h-5 text-rose-600" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-mono font-bold text-rose-600 tracking-tight">{stats.blocked_count}</span>
            <span className="text-xs text-rose-600 font-mono font-semibold">{stats.security_events_count} Threat Events</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-white border border-slate-200 rillet-card-hover space-y-3">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider">Composite Risk Index</span>
            <Activity className="w-5 h-5 text-amber-600" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-mono font-bold text-amber-700 tracking-tight">{stats.average_risk_score} <span className="text-xs text-slate-400 font-normal">/ 100</span></span>
            <span className="text-xs text-amber-700 font-mono font-semibold">Policy Guard On</span>
          </div>
        </div>
      </div>

      {/* Rillet-Style Light Execution Stream */}
      <div className="rounded-2xl bg-white border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Zap className="w-4 h-4 text-[#53389E]" />
            <h2 className="font-mono font-bold text-sm text-[#1A103C]">Live Agent Gateway Execution Stream</h2>
          </div>
          <span className="text-xs text-slate-400 font-mono">Polling every 5s...</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-mono border-b border-slate-200 uppercase">
              <tr>
                <th className="p-4">Execution ID</th>
                <th className="p-4">Agent Identity</th>
                <th className="p-4">Tool Invoked</th>
                <th className="p-4">Risk Score</th>
                <th className="p-4">Gateway Decision</th>
                <th className="p-4">Latency</th>
                <th className="p-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 font-mono text-[11px]">
              {recentExecutions.map((ex) => (
                <tr key={ex.id} className="hover:bg-slate-50 transition">
                  <td className="p-4 text-[#53389E] font-bold">{ex.id}</td>
                  <td className="p-4 font-sans font-semibold text-[#1A103C]">{ex.agent_name}</td>
                  <td className="p-4 text-indigo-600 font-bold">{ex.tool_name}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-full font-bold ${
                      ex.risk_score >= 70 ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                      ex.risk_score >= 40 ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                      'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    }`}>
                      {ex.risk_score.toFixed(1)} / 100
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-wide ${
                      ex.decision === 'ALLOW' ? 'bg-emerald-100 text-emerald-800' :
                      ex.decision === 'BLOCK' ? 'bg-rose-100 text-rose-800' :
                      'bg-amber-100 text-amber-800'
                    }`}>
                      {ex.decision}
                    </span>
                  </td>
                  <td className="p-4 text-slate-500">{ex.execution_time_ms} ms</td>
                  <td className="p-4 text-slate-400">{new Date(ex.created_at).toLocaleTimeString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
